from flask import Flask, send_file, jsonify
from igraph import *
from ResponseBuilder import *

app = Flask(__name__)


def load_graph():
    graph = Graph.Read_GML("/PersonalFiles/MSSE/MasterProject/Dataset/DS_Ver5.gml")
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
def showSignUp():
    return send_file('signup.html')


# School community detection based on network structure
@app.route('/api/schoolCommunity', methods=['GET'])
def get_school_communities():
    u_social_network_graph = d_social_network_graph
    u_social_network_graph.to_undirected()
    school_community_graph = u_social_network_graph.community_multilevel()

    for idx, community in enumerate(school_community_graph):
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

    interest_based_community = Graph()
    interest_based_community.to_directed()

    nodes_list = []

    for v in d_social_network_graph.vs:
        if v["school"] == "SJSU":
            interest_based_community.add_vertex(v.index)
            nodes_list.append(v)

    i = 0
    for v in interest_based_community.vs:
        v["id"] = nodes_list[i]["id"]
        v["groupId"] = -1
        v['interestedNode']=False
        v['influentialNode']=False
        v["interest"] = nodes_list[i]["interest"]
        i += 1

    for e in d_social_network_graph.es:
        source = e.source
        destination = e.target
        if d_social_network_graph.vs[source]["school"] == "SJSU" and d_social_network_graph.vs[destination][
            "school"] == "SJSU":
            interest_based_community.add_edge(source, destination)

    interested_nodes_list = []

    for v in interest_based_community.vs:
        if "sports" in v["interest"]:
            v["interestedNode"] = True
            interested_nodes_list.append(v)

    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(interest_based_community)
    edges = response_builder.return_edge_list(interest_based_community)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=5000)