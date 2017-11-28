/**
 * Created by Student on 5/18/17.
 */
wardroberapp.controller('searchController', function ($scope, $http, $location) {
    $scope.search = function() {
        var query = {};
        var queryString = $scope.queryString;

        var school = queryString.split(';');
        query['school'] = school[0];
        var interests = school[1].split(',');
        query['interests'] = interests;

        $http({
			method : 'POST',
			url : '/api/interest-based-community',
			data : query,
			headers : {
					'Content-Type' : 'application/json'
			}
		}).success(function(data) {
			if(data) {
				window.location = '/community';
			}
			else {
			}
		});
    };

    $scope.visualize = function() {
    	var graphResponse = $http.get('/api/schoolCommunity');
		graphResponse.success(function(response) {
			var nodes = response.nodes;
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
				nodes: {
					shape: 'dot',
					size: 30,
					font: {
						size: 32,
						color: '#000000'
					},
					borderWidth: 2
				},
				edges: {
					width: 2
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