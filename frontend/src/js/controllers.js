

angular.module('controllers', [])

.controller('LoginCtrl', ['$scope', 'API', 'Auth', 'Storage', 'ngNotify', '$location', 'PATHS',
	function ($scope, API, Auth, Storage, ngNotify, $location, PATHS) {
	$scope.validUser = false;
	$scope.answered = false;

	$scope.submit = function(user){
		$scope.answered = false;
		API.login(user).then(
		function(login_response){
			//Success
			API.fetchNewApplications().then(
			function(apps_response) {
				// Success
				console.log("Fetched the new applications");
				$scope.answered = true;
				$scope.validUser = true;
				var userObj = {
					name: user.name,
					token: login_response.token,
					admin: login_response.admin
				};
				console.log(userObj);
				Auth.login(userObj);
				ngNotify.set("Welcome, "+user.name+"!", 'success');
				if(user.remember)
					Storage.set("user", userObj);
				$location.path(PATHS.judgement);
			},
			function(error) {
				console.log("Error fetching new applications");
			});
		},
		function(error){
			//Rejected
			$scope.answered = true;
		});
	};

	//If is already logged in, get out
	if(Auth.isLoggedIn())
	{
		$location.path(PATHS.judgement);
	}

}])
.controller('JudgementCtrl', ['$scope', 'API', 'current', '$location', 'ngNotify', '$window', 'PATHS',
	function ($scope, API, current, $location, ngNotify, $window, PATHS) {

	$scope.current = current;

	$scope.goToLastRated = function(){
		$location.path(PATHS.last);
	};

	function isValidLink(link){
		return link !== "" && link != "http://";
	}

	function rate(rating){
		API.rate(rating).then(function(response){
			if(response.data.status)
			{
				if(response.data.status == "ok")
				{
					ngNotify.set("Rated!", {
						type: 'success',
						position:'top',
						duration:500
					});
					$window.document.querySelector('.application').scrollTop = 0;
				}
				else
				{
					ngNotify.set("Error! Try again", {
						type:'error',
						position:'top',
						duration:1000
					});
				}

			}
		});
		API.getPending().then(function(person){
			$scope.current = person;
		});
	}
	$scope.better = function(){
		rate('better');
	};

	$scope.worse = function(){
		rate('worse');
	};

	/* Redundant code, this could be a directive (see LastRatedCtrl, PersonCtrl)*/
	$scope.web = function(obj, name){
		if(obj[name] !== undefined)
		{
			return isValidLink(obj[name]);
		}
	};

	$scope.openLink = function(link){
		if(isValidLink(link))
			$window.open(link);
	};

}])
.controller('LastRatedCtrl', ['$scope', 'lastRated', '$window',
	function($scope, lastRated, $window){
	$scope.back = function(){
		$window.history.back();
	};

	function isValidLink(link){
		return link !== "" && link != "http://";
	}

	$scope.web = function(obj, name){
		if(obj[name] !== undefined)
		{
			return isValidLink(obj[name]);
		}
	};

	$scope.openLink = function(link){
		if(isValidLink(link))
			$window.open(link);
	};

	$scope.lastRated = lastRated;
}])
.controller('PeopleCtrl', ['$scope', 'Auth', 'ngNotify', 'API', 'people', 'PATHS', '$location',
	function ($scope, Auth, ngNotify, API, people, PATHS, $location) {
		$scope.people = people;
		$scope.f ={
			query: '',
			accepted: false,
			tbd: false,
			onlyNewcomers: false,
			rejected: false
		};
		$scope.optClosed = true;

		function searchMatch(element)
		{
			var reg = new RegExp($scope.f.query, "gi");
			return (element.name.match(reg) !== null) ||
					(element.email.match(reg) !== null);
		}

		function noSelector()
		{
			return $scope.f.accepted === false && 
					$scope.f.tbd === false  &&
					$scope.f.rejected === false;
		}

		function selectorMatch(element)
		{

			if($scope.f.tbd)
			{
				if(element.state == "tbd")
				{
					return true;
				}
			}
			if($scope.f.accepted)
			{
				if(element.state == "accepted")
				{
					return true;
				}
			}
			if($scope.f.rejected)
			{
				if(element.state == "rejected")
				{
					return true;
				}
			}

			return false;
		}
		function filterMatch(element){
			if($scope.f.onlyNewcomers)
				return (element.newbie === '1');

			return true;
		}
		$scope.viewPerson = function(id){
			$location.path(PATHS.people+"/"+id);
		};

		$scope.changeStatus = function(person, state){
			if(Auth.isAdmin())
			{
				var old = person.state;
				person.state = state;
				API.changeStatus(person.id, state).then(function(){
					//Success
				}, function(){
					person.state = old;
				});
				
			}
			else
			{
				ngNotify.set('Only admins can force a state', 'info');
			}
		};

		$scope.aeople = function(element){
			return searchMatch(element) && filterMatch(element) && (noSelector() || selectorMatch(element));
		};

		$scope.toggleOptions = function(){
			$scope.optClosed = !$scope.optClosed;
		};

}])
.controller('PersonCtrl', ['$scope','Auth', 'ngNotify', 'person', 'API', '$window',
	function($scope, Auth, ngNotify, person, API, $window){
		$scope.person = person;

			
		function isValidLink(link){
			return link !== "" && link != "http://";
		}

		$scope.web = function(obj, name){
			if(obj[name] !== undefined)
			{
				return isValidLink(obj[name]);
			}
		};

		$scope.openLink = function(link){
			if(isValidLink(link))
				$window.open(link);
		};

		$scope.back = function(){
			$window.history.back();
		};

		$scope.changeStatus = function(person, state){
			if(Auth.isAdmin())
			{
				var old = person.state;
				person.state = state;
				API.changeStatus(person.id, state).then(function(){
					//Success
				}, function(){
					person.state = old;
				});
				
			}
			else
			{
				ngNotify.set('Only admins can force a state', 'info');
			}
		};
}]);