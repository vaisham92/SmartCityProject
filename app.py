from flask import Flask, send_file, jsonify
from flask import request
from igraph import *
from ResponseBuilder import *
import louvain

app = Flask(__name__)

def load_graph():
    graph = Graph.Read_GML("/Users/ChandanaRao/Desktop/ChandanaRao/SJSU/Academics/Sem4/CMPE295/Dataset/graph_500.gml")
    for node in graph.vs:
        node['groupId']=-1
        node['interestedNode']=False
        node['influentialNode']=False
    return graph

d_social_network_graph = load_graph()


@app.route('/')
def main():
    return send_file('templates/index.html')


# social network graph
@app.route('/api/graph', methods=['GET'])
def get_graph():
    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(d_social_network_graph)
    edges = response_builder.return_edge_list(d_social_network_graph)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges

    return jsonify(response)


# School community detection based on network structure
@app.route('/api/schoolCommunity', methods=['GET'])
def get_school_communities():
    multi_school_community_graph = louvain.find_partition(d_social_network_graph, louvain.CPMVertexPartition,
                                       resolution_parameter=0.0005)
    for idx, community in enumerate(multi_school_community_graph):
        for node in community:
            v = d_social_network_graph.vs[node]
            v["groupId"] = idx

    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(d_social_network_graph)
    edges = response_builder.return_edge_list(d_social_network_graph)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges

    return jsonify(response)

@app.route('/api/nodeInfo', methods=['GET'])
def get_node_info():
    nodes = []
    nodeIds = request.args.get('nodeIds')
    nodeIds = nodeIds.split(',')

    for nodeId in nodeIds:
        node = d_social_network_graph.vs.select(lambda vertex:vertex["id"] == int(nodeId))[0]
        nodeObject = dict()
        nodeObject["firstname"] = node["firstname"]
        nodeObject["lastname"] = node["lastname"]
        nodeObject["dob"] = node["dob"]
        nodeObject["school"] = node["school"]
        nodeObject["profession"] = node["profession"]
        nodeObject["interest"] = node["interest"]
        nodes.append(nodeObject)
    return jsonify(nodes)

# Interest based community detection
@app.route('/api/interest-based-community', methods=['GET'])
def get_interest_based_communities():

    target_school = request.args.get('school')
    interests = request.args.get('interests').split(',')

    # Level 1 - School Community Detection
    multi_school_community_graph = louvain.find_partition(d_social_network_graph, louvain.CPMVertexPartition,
                                                        resolution_parameter=0.0005)
    school_community_id_map = {}
    for community_id,community in enumerate(multi_school_community_graph):
        min_check = len(community)*0.1
        if min_check >= 1:
            for i,node in enumerate(community):
                school_name = d_social_network_graph.vs[node]['school']
                if school_name in school_community_id_map:
                    school_community_id_map[school_name] += ","+str(community_id)
                else:
                    school_community_id_map[school_name] = str(community_id)
                i += 1
                if i > min_check:
                    break

    for school, community_id in school_community_id_map.iteritems():
        community_ids = community_id.split(",")
        school_community_id_map[school] = max(set(community_ids), key=community_ids.count)

    target_community_id = school_community_id_map.get(target_school)
    school_nodes = multi_school_community_graph[int(target_community_id)]

    # Level 2 Interest-based Community Detection
    school_community_graph = Graph()
    school_community_graph.to_directed()

    interest_based_community_graph = Graph()
    interest_based_community_graph.to_directed()

    updated_school_nodes = []

    for node in school_nodes:
        school_community_graph.add_vertex(d_social_network_graph.vs[node].index)
        updated_school_nodes.append(d_social_network_graph.vs[node])

    updated_school_node_ids=[]

    for i,v in enumerate(school_community_graph.vs):
        v["id"] = updated_school_nodes[i]["id"]
        v["label"] = updated_school_nodes[i]["label"]
        v["groupId"] = -1
        v['interestedNode']=False
        v['influentialNode']=False
        v["interest"] = updated_school_nodes[i]["interest"]
        updated_school_node_ids.append(updated_school_nodes[i]["id"])

    for e in d_social_network_graph.es:
        src = e.source
        dest = e.target
        if d_social_network_graph.vs[src]['id'] in updated_school_node_ids \
                and d_social_network_graph.vs[dest]['id'] in updated_school_node_ids:

            id_src = d_social_network_graph.vs[src]['id']
            id_dest = d_social_network_graph.vs[dest]['id']
            sg_src = school_community_graph.vs.find(id=id_src).index
            sg_dest = school_community_graph.vs.find(id=id_dest).index
            school_community_graph.add_edge(sg_src, sg_dest)

    interested_nodes = []

    for v in school_community_graph.vs:
        is_interested = False
        for interest in interests:
            if interest in v["interest"]:
                is_interested = True
            else:
                is_interested = False
                break
        if is_interested:
            v["interestedNode"] = True
            interested_nodes.append(v)


    # Compute shortest paths among sub-community nodes usinf Dijkstra's shortest path algorithm
    influenceFactorAdjGrid = d_social_network_graph.shortest_paths_dijkstra(interested_nodes, interested_nodes, None, OUT)
    interest_based_community_graph = Graph.Weighted_Adjacency(influenceFactorAdjGrid, ADJ_DIRECTED, "weight", False)
    interest_based_community_graph.simplify(combine_edges='sum')

    i = 0
    for v in interest_based_community_graph.vs:
        node = interested_nodes[i]
        v["id"] = node["id"]
        i += 1

    influentials_object = get_influential_node(interest_based_community_graph, school_community_graph)
    if len(influentials_object) > 0:
        for node_id in influentials_object[len(influentials_object)-1][2]:
            node_id["influentialNode"] = True

    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(school_community_graph)
    edges = response_builder.return_edge_list(school_community_graph)

    # Json object for coverage graph
    nodes_coverage = []
    for item in influentials_object:
        temp_json = dict()
        temp_json["no_of_influencers"] = item[0]
        temp_json["coverage"] = item[1]
        temp_json["node_info"] = []
        for node in item[2]:
            curr_node = dict()
            curr_node["id"] = node["id"]
            curr_node["interest"] = node["interest"]
            curr_node["influentialNode"] = node["influentialNode"]
            curr_node["groupId"] = node["groupId"]
            curr_node["influence"] = node["influence"]
            curr_node["interestedNode"] = node["interestedNode"]
            curr_node["name"] = node["name"]
            temp_json["node_info"].append(curr_node)
        nodes_coverage.append(temp_json)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges
    response['coverageObject'] = nodes_coverage

    return jsonify(response)


# Influential Node detection
def get_influential_node(interest_based_community_graph, school_community_graph):
    node_list = []
    edge_list = []
    for i in range(0, len(interest_based_community_graph.vs)):
        node_list.append(0)
    for node in interest_based_community_graph.vs:
        node_list[node.index] = node["id"]
    max_weight = 0.0
    for edge in interest_based_community_graph.es:
        if math.isinf(edge["weight"]) or edge["weight"] <= max_weight:
            continue
        else:
            max_weight = edge["weight"]
    for edge in interest_based_community_graph.es:
        if math.isinf(edge["weight"]):
            continue
        edge["weight"] = max_weight / edge["weight"]
        edge_list.append((edge.source, edge.target))
    subCommunityGraph = Graph(vertex_attrs={"id": node_list}, edges=edge_list, directed=True)
    for edge in subCommunityGraph.es:
        edges = interest_based_community_graph.es.select(_between=([edge.source], [edge.target]))
        for e in edges:
            if e.source==edge.source and e.target==edge.target:
                edge["weight"] = e["weight"]
                break
    # Calculate the Betweenness centrality, Degree, Pagerank
    influencer_list = []
    for node in subCommunityGraph.vs:
        node["betweenness"] = node.betweenness(weights=subCommunityGraph.es["weight"])
        node["pagerank"] = node.pagerank()
        node["degree"] = node.indegree()
        node["influence"] = node["betweenness"] + node["pagerank"] + node["degree"]
        school_community_graph.vs.select(lambda vertex: vertex["id"] == node["id"])[0]["influence"] = node["influence"]
        influencer_list.append(node)
    sort_nodes(influencer_list)

    # Calculating the coverage
    return get_coverage(node_list, influencer_list, school_community_graph)

# Influence coverage
def get_coverage(node_list, influencer_list, school_community_graph):
    depth_threshold = 3
    no_of_influencers = 0
    coverage = 0.0
    leader_nodes = set()
    follower_nodes = set()
    coverage_grid = school_community_graph.shortest_paths(school_community_graph.vs, school_community_graph.vs, None, OUT)
    resultObject = []
    while no_of_influencers < len(influencer_list) and coverage < 100.0:
        no_of_influencers += 1
        for i in range(0, no_of_influencers):
            node = influencer_list[i]
            if node["id"] in leader_nodes:
                continue
            leader_nodes.add(node["id"])
            if node["id"] in follower_nodes:
                follower_nodes.remove(node["id"])
            node_index = school_community_graph.vs.select(lambda vertex: vertex["id"] == node["id"])[0].index
            for i in range(0, len(school_community_graph.vs)):
                if math.isinf(coverage_grid[i][node_index]) or coverage_grid[i][node_index] == 0:
                    continue
                if coverage_grid[i][node_index] <= depth_threshold:
                    follower_nodes.add(school_community_graph.vs.select(lambda vertex: vertex.index == i)[0]["id"])
            coverage = float((float(len(follower_nodes) + len(leader_nodes)) / float(len(school_community_graph.vs))) * 100.0)
            print "NoOfInfluencers: " + str(no_of_influencers) + " ; Coverage: " + str(coverage) + "; InfluentialNodes: " + str(leader_nodes) + "; FollowerNodes: " + str(follower_nodes) + "; TotalNodes: " + str(len(school_community_graph.vs))
            x = []
            for y in leader_nodes:
                x.append(school_community_graph.vs.select(lambda vertex: vertex["id"] == y)[0])
            resultObject.append([no_of_influencers, coverage, x])
    return resultObject
    # while no_of_influencers < len(influencer_list) and coverage < 100.0:
    #     no_of_influencers += 1
    #     for i in range(0, no_of_influencers):
    #         node = influencer_list[i]
    #         if node["id"] in leader_nodes:
    #             continue
    #         leader_nodes.add(node["id"])
    #         if node["id"] in follower_nodes:
    #             follower_nodes.remove(node["id"])
    #         edge_target = school_community_graph.vs.select(lambda vertex: vertex["id"] == node["id"])[0]
    #         for edge in school_community_graph.es.select(lambda edge: edge.target == edge_target.index):
    #             edge_source = school_community_graph.vs.select(lambda vertex: vertex.index == edge.source)[0]
    #             if node["id"] in node_list and edge_source["id"] not in leader_nodes:
    #                 follower_nodes.add(edge_source["id"])
    #         coverage = float((float(len(follower_nodes) + len(leader_nodes)) / float(len(school_community_graph.vs))) * 100.0)
    #     print "NoOfInfluencers: " + str(no_of_influencers) + " ; Coverage: " + str(
    #                         coverage) + "; InfluentialNodes: " + str(leader_nodes) + "; FollowerNodes: " + str(
    #                         follower_nodes) + "; TotalNodes: " + str(len(school_community_graph.vs))

def sort_nodes(node_list):
    for i in range(1, len(node_list)):
        curr_node = node_list[i]
        index = i
        while index > 0 and node_list[index - 1]["influence"] > curr_node["influence"]:
            node_list[index] = node_list[index - 1]
            index = index - 1
        node_list[index] = curr_node
    node_list.reverse()

if __name__ == "__main__":
    app.run(port=5000)