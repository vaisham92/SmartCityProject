wardroberapp.controller('communityController', function ($scope, $http, $location, $routeParams) {

    $scope.influentialCoverage = function () {

        $scope.dataProvider = [];
        var index = 0;
        if ($scope.influentialNodesData === undefined)
            fetchData();
        for (index in $scope.influentialNodesData.coverageObject) {
            coverageObject = $scope.influentialNodesData.coverageObject[index];
            var dataObject = {};
            dataObject['influencers'] = coverageObject.no_of_influencers;
            dataObject['coverage'] = coverageObject.coverage;
            $scope.dataProvider.push(dataObject);
        }
        visualizeLinearChart($scope.dataProvider);
    };

    var visualizeLinearChart = function (dataProvider) {
        var chart = AmCharts.makeChart("chartdiv", {
            "type": "serial",
            "theme": "light",
            "dataProvider": dataProvider,
            "valueAxes": [{
                "gridColor": "#FFFFFF",
                "gridAlpha": 0.2,
                "dashLength": 0
            }],
            "gridAboveGraphs": true,
            "startDuration": 1,
            "graphs": [{
                "balloonText": "[[category]]: <b>[[value]]</b>",
                "fillAlphas": 0.8,
                "lineAlpha": 0.2,
                "type": "column",
                "valueField": "coverage"
            }],
            "chartCursor": {
                "categoryBalloonEnabled": false,
                "cursorAlpha": 0,
                "zoomable": false
            },
            "categoryField": "influencers",
            "categoryAxis": {
                "gridPosition": "start",
                "gridAlpha": 0,
                "tickPosition": "start",
                "tickLength": 20
            },
            "export": {
                "enabled": true
            },
            "listeners": [{
                "event": "clickGraphItem",
                "method": function (event) {
                    console.log("here 1");
                    for (var index in $scope.influentialNodesData.coverageObject) {
                        var coverageObject = $scope.influentialNodesData.coverageObject[index];
                        console.log("here 2");
                        console.log(coverageObject.no_of_influencers);
                        console.log(event.item.category);
                        if (Math.floor(coverageObject.no_of_influencers) === Math.floor(event.item.category)) {
                            var nodeInfo = coverageObject.node_info;
                            var nodeIds = "";
                            for (var nodeIndex in nodeInfo) {
                                console.log("here 3");
                                nodeIds += Math.floor(nodeInfo[nodeIndex].id) + ","
                            }
                            nodeIds = nodeIds.substr(0, nodeIds.length - 1);
                            var nodeProfileResponse = $http.get('/api/nodeInfo?nodeIds=' + nodeIds);
                            nodeProfileResponse.success(function (data) {
                                $scope.nodes = data;
                            });
                        }
                    }
                }
            }]
        });
    };

    var fetchData = function (success) {
        var school = $routeParams.school;
        var interests = $routeParams.interests;

        var graphResponse = $http.get('/api/interest-based-community?school=' + school + '&interests=' + interests);
        graphResponse.success(function (response) {
            $scope.influentialNodesData = response;
            console.log($scope.influentialNodesData.nodes);
            success();
        });
    };

    var modifyNodes = function (data) {
        for (index in data.nodes) {
            if (data.nodes[index].interestedNode)
                data.nodes[index].group = 1;
            else
                data.nodes[index].group = 0;
        }
        return data.nodes;
    };

    var visualize = function () {
        fetchData(function () {
            var nodes = modifyNodes($scope.influentialNodesData);
            var edges = $scope.influentialNodesData.edges;
            create_network_graph(nodes, edges);
        });
    };
    visualize();

    var create_network_graph = function (nodes, edges) {
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

            if (undefined !== this.getNodeAt(params.pointer.DOM)) {
                document.getElementById('eventSpan').innerHTML = '<h4>Profile for Node: ' + this.getNodeAt(params.pointer.DOM) + '</h4>';
            }

            // params.event = "[original event]";
            // document.getElementById('eventSpan').innerHTML = '<h2>Click event:</h2>' + JSON.stringify(params, null, 4);
            // console.log('click event, getNodeAt returns: ' + this.getNodeAt(params.pointer.DOM));
        });
    };

});