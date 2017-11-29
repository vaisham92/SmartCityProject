from flask import Flask, send_file, jsonify
from flask import request
from igraph import *
from ResponseBuilder import *
import json

app = Flask(__name__)

def load_graph():

    graph = Graph.Read_GML("/Users/vpathuri/Desktop/CODE/SmartCityProject/Dataset/graph.gml")
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
    u_social_network_graph = d_social_network_graph
    u_social_network_graph.to_undirected()
    multi_school_community_graph = u_social_network_graph.community_multilevel()

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


# Interest based community detection
@app.route('/api/interest-based-community', methods=['GET'])
def get_interest_based_communities():
    school =  request.args.get('school')
    interests = request.args.get('interests')
    # interests = interests.split(',')

    school = 'sjsu'
    interests = ['sports']

    school_nodes = []

    school_community_graph = Graph()
    school_community_graph.to_directed()

    interest_based_community_graph = Graph()
    interest_based_community_graph.to_directed()

    for v in d_social_network_graph.vs:
        if v["school"] == str(school).upper():
            school_community_graph.add_vertex(v.index)
            school_nodes.append(v)

    i = 0
    for v in school_community_graph.vs:
        v["id"] = school_nodes[i]["id"]
        v["groupId"] = -1
        v['interestedNode']=False
        v['influentialNode']=False
        v["interest"] = school_nodes[i]["interest"]
        i += 1

    for e in d_social_network_graph.es:
        src = e.source
        dest = e.target
        if d_social_network_graph.vs[src]["school"] == str(school).upper() and d_social_network_graph.vs[dest]["school"] == str(school).upper():
            school_community_graph.add_edge(src, dest)

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

    influential_list = get_influential_node(interest_based_community_graph, school_community_graph)
    for node in school_community_graph.vs:
        if node["id"] in influential_list:
            node["influentialNode"] = True

    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(school_community_graph)
    edges = response_builder.return_edge_list(school_community_graph)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges

    return jsonify(response)

def get_influential_node(interest_based_community_graph, school_community_graph):
    #plot(interest_based_community_graph)
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
        influencer_list.append(node)
    sort_nodes(influencer_list)

    # Calculating the coverage
    print len(influencer_list)
    return get_coverage(node_list, influencer_list, school_community_graph)

def get_coverage(node_list, influencer_list, school_community_graph):
    depth_threshold = 3
    no_of_influencers = 0
    coverage = 0.0
    leader_nodes = set()
    follower_nodes = set()
    coverage_grid = school_community_graph.shortest_paths(school_community_graph.vs, school_community_graph.vs, None, OUT)
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
    return leader_nodes
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