

class ResponseBuilder:
    def __init__(self):
        pass

    def return_node_list(self, network_graph):
        # parse nodes to create object
        nodes = []
        index = 0
        for network_graph_object in network_graph.vs:
            node = dict()
            node['id'] = int(network_graph_object['id'])
            node['label'] = index
            node['group'] = int(network_graph_object['groupId'])
            node['influentialNode'] = bool(network_graph_object['influentialNode'])
            node['interestedNode'] = bool(network_graph_object['interestedNode'])
            nodes.append(node)
            index += 1
        return nodes


    def return_edge_list(self, network_graph):
        # parse edges to create object
        edges = []
        for network_graph_object in network_graph.es:
            edge = dict()
            edge['from'] = int(network_graph.vs[network_graph_object.source]['id'])
            edge['to'] = int(network_graph.vs[network_graph_object.target]['id'])
            edges.append(edge)
        return edges
