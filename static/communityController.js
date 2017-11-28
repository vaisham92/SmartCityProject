wardroberapp.controller('communityController', function ($scope, $http, $location, $routeParams) {

    function getUrlParameter(param, dummyPath) {
        var sPageURL = dummyPath || window.location.search.substring(1),
            sURLVariables = sPageURL.split(/[&||?]/),
            res;

        for (var i = 0; i < sURLVariables.length; i += 1) {
            var paramName = sURLVariables[i],
                sParameterName = (paramName || '').split('=');

            if (sParameterName[0] === param) {
                res = sParameterName[1];
            }
        }

        return res;
    }

    var modifyNodes = function(data) {

            for(index in data.nodes) {
                if(data.nodes[index].interestedNode)
                	data.nodes[index].group = 1;
                else
                	data.nodes[index].group = 0;
            }
            return data.nodes;

        };

    var visualize = function() {

        var school = $routeParams.school;
        var interests = $routeParams.interests;

    	var graphResponse = $http.get('/api/interest-based-community?school=' + school + '&interests=' + interests);
		graphResponse.success(function(response) {
			var nodes = modifyNodes(response);
			var edges = response.edges;
			create_network_graph(nodes, edges);
		});

		var create_network_graph = function(nodes, edges) {
			// create a network
			var color = 'gray';
			var len = undefined;
			var container = document.getElementById('communityGraph');
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
    visualize();

});