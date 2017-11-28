from flask import Flask, send_file, jsonify
from flask import request
from igraph import *
from ResponseBuilder import *
import json

app = Flask(__name__)

school_community_graph = Graph()
school_community_graph.to_directed()

interest_based_community_graph = Graph()
interest_based_community_graph.to_directed()


def load_graph():
    graph = Graph.Read_GML("/Users/ChandanaRao/Desktop/ChandanaRao/SJSU/Academics/Sem4/CMPE295/Dataset/DS_Ver5.gml")
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


@app.route('/showSignUp')
def show_sign_up():
    return send_file('signup.html')


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
    #query = request.data
    #query = json.loads(query)
    #school =  query['school']
    #interests = query['interests']

    school = 'sjsu'
    interests = 'sports'

    school_nodes = []

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

    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(school_community_graph)
    edges = response_builder.return_edge_list(school_community_graph)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=5000)