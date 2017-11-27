#!flask/bin/python
from flask import Flask, jsonify, send_from_directory, render_template
from igraph import *
import os

from ResponseBuilder import *

app = Flask(__name__)

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')


def load_graph():
    d_social_network_graph = Graph.Read_GML("/Users/ChandanaRao/Desktop/ChandanaRao/SJSU/Academics/Sem4/CMPE295/Dataset/DS_Ver5.gml")
    for node in d_social_network_graph.vs:
        node['groupId']=-1
        node['interestedNode']=False
        node['influentialNode']=False
    return d_social_network_graph

d_social_network_graph = load_graph()

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
    interested_nodes_list = []
    for v in d_social_network_graph.vs:
        if "sports" in v["interest"] and v["school"] == "SJSU":
            v["interestedNode"] = True
            interested_nodes_list.append(v)

    response_builder = ResponseBuilder()
    nodes = response_builder.return_node_list(d_social_network_graph)
    edges = response_builder.return_edge_list(d_social_network_graph)

    response = dict()
    response["nodes"] = nodes
    response['edges'] = edges

    return jsonify(response)



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(debug=True)