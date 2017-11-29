/**
 * Created by Student on 5/18/17.
 */

var wardroberapp = angular.module('wardroberapp', ['ngRoute']);
//console.log(history.config);
wardroberapp.config(['$routeProvider', '$locationProvider',
    function ($routeProvider, $locationProvider, $routeParams, $location, $window) {
        $routeProvider
            .when('/', {
                templateUrl: '../static/search.html',
                controller: 'searchController'
                // community/SJSU/school,sports
            }).when('/community/:school/:interests', {
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