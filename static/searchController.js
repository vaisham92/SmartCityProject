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
			if(data.status === 200) {
				window.location = '/graph';
			}
			else {
			}
		});
    };
});