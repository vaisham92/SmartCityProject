/**
 * Created by Student on 5/18/17.
 */

var wardroberapp = angular.module('wardroberapp', ['ngRoute']);
//console.log(history.config);
wardroberapp.config(['$routeProvider', '$locationProvider',
    function ($routeProvider, $locationProvider, $routeParams, $location) {
        $routeProvider
            .when('/', {
                templateUrl: '../static/search.html',
                controller: 'searchController'
            }).when('/graph', {
                templateUrl: '../static/graph.html',
                controller: 'graphController'
            }).when('/community', {
                templateUrl: '../static/community.html',
                controller: 'communityController'
            }).when('/influential', {
                templateUrl: '../static/influential.html',
                controller: 'influentialController'
            })
            .otherwise({
                templateUrl: '../static/search.html',
                controller: 'searchController'
            });
        $locationProvider.html5Mode(true);
    }
]);