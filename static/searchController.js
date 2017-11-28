/**
 * Created by Student on 5/18/17.
 */
wardroberapp.controller('searchController', function ($scope, $http, $location) {
    $scope.search = function() {
        // var query = {};
        // var queryString = $scope.queryString;
        //
        // var school = queryString.split(';');
        // query['school'] = school[0];
        // var interests = school[1].split(',');
        // query['interests'] = interests;

        //window.location = '/graph/community/' + query['school'] + '/' + getCommaSeparated(query['interests']);
    };

    var getCommaSeparated = function(data) {
    	var result = "";
    	for(index in data) {
    		result += data[index].trim() + ",";
		}
		return result.substring(0, result.length - 1);
	};

    var modifyNodes = function(data) {

        // for(index in data.nodes) {
    		// if(data.nodes[index].interestedNode)
    		// 	data.nodes[index].group = 1;
    		// else
    		// 	data.nodes[index].group = 0;
		// }
		return data.nodes;

	};

    $scope.visualize = function() {
    	var graphResponse = $http.get('/api/schoolCommunity');
		graphResponse.success(function(response) {
			var nodes = modifyNodes(response);
			var edges = response.edges;
			create_network_graph(nodes, edges);
		});

		var create_network_graph = function(nodes, edges) {
			// create a network
			var color = 'gray';
			var len = undefined;
			var container = document.getElementById('firstGraph');
			var data = {
				nodes: nodes,
				edges: edges
			};
			var options = {
				groups: {
				failure: {
				   color: {
					  background: 'red'
				   }
				},
				state: {
				   color: {
					  background: 'lime'
				   }
				},
				startstate: {
				   font: {
					  size: 33,
					  color: 'white'
				   },
				   color: {
					  background: 'blueviolet'
				   }
				},
				finalstate: {
				   font: {
					  size: 33,
					  color: 'white'
				   },
				   color: {
					  background: 'blue'
				   }
				}
				},
				edges: {
				arrows: {
				   to: {
					  enabled: true
				   }
			},
			smooth: {
			   enabled: false,
				   type: 'continuous'
				}
			 },
			physics: {
					stabilization: false,
				 },
				 layout: {
					randomSeed: 191006,
					improvedLayout: true
				 }
  			};
			network = new vis.Network(container, data, options);

			network.on("click", function (params) {

				if(undefined !== this.getNodeAt(params.pointer.DOM)) {
					document.getElementById('eventSpan').innerHTML = '<h4>Profile for Node: ' + this.getNodeAt(params.pointer.DOM) + '</h4>';
				}

				// params.event = "[original event]";
				// document.getElementById('eventSpan').innerHTML = '<h2>Click event:</h2>' + JSON.stringify(params, null, 4);
				// console.log('click event, getNodeAt returns: ' + this.getNodeAt(params.pointer.DOM));
			});
    	};
	};


});