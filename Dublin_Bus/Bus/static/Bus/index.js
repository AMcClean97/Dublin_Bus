'use strict';//to enable the use of let
let map;
//TODO customise bus stop icon
//TODO group markers when map zoomed out
let infoWindow;
let directionsService;
let directionsRenderer;
let geocoder;
//list for storing reference to bus stop markers
let stopMarkers = {};
let stopMarkersArr = [];
let markerCluster;
let clusterStyles;
//Inputs
let inputOrigin = document.getElementById("inputOrigin");
let inputDestination = document.getElementById("inputDestin");
let inputFirstStop = document.getElementById('inputFirstStop');
let inputLastStop = document.getElementById("inputLastStop");
let inputTime = document.getElementById("time-dropdown")
let autocompleteOrigin;
let autocompleteDestin;
//Geolocation
let currentLocationOrigin = false;
let PositionOptions = {
		enableHighAccuracy: true,
		timeout: 5000,
		maximumAge: 0,
};
//Favourites
let isFavourite = false;
let currentFavourite;

function initMap (){

	let myLatLng = {lat: 53.350140, lng: -6.266155};//set the latitude and longitude to Dublin

  	map = new google.maps.Map(document.getElementById("map"), {
    	zoom: 14,
    	center: myLatLng,
    	mapTypeControl: false,
    	streetViewControl: false,
        styles: [
            { stylers: [{ saturation: -10 }] },
            {
             	featureType: "administrative.land_parcel",
             	elementType: "labels",
                stylers: [{ visibility: "off" }],
            },
            {
              	featureType: "landscape.man_made",
              	stylers: [{ visibility: "off" }],
            },
            {
              	featureType: "poi",
              	elementType: "labels.text",
              	stylers: [{ visibility: "off" }],
            },
            {
              	featureType: "poi",
              	elementType: "geometry",
              	stylers: [{ visibility: "off" }],
            },
            {
				featureType: "poi", stylers: [{ visibility: "off" }] },
            {
              	featureType: "road",
              	elementType: "labels.icon",
              	stylers: [{ visibility: "on" }],
            },
            {
              	featureType: "road.local",
              	elementType: "labels",
              	stylers: [{ visibility: "on" }],
            },
            {
              	featureType: "transit", stylers: [{ visibility: "off" }]
			},
            ],
  	});

    //will be used to restrict autocomplete search box options, radius can be increased or decreased as needed
    var dublin_bounds = new google.maps.Circle({ center: myLatLng, radius: 30000 });



  	// Setup Places Autocomplete Service
  	// Set options for service
  	// Need to add Dublin bounds to restrict search box
  	const autocompleteOptions = {
    	componentRestrictions: { country: ["IE"] },
    	bounds: dublin_bounds.getBounds(),
        strictBounds: true,
    	fields: ["name", "geometry", "place_id"], // Google charges per field
  	};

  	// Set idss of text-boxes attached to autocomplete
  	autocompleteOrigin = new google.maps.places.Autocomplete(
    	inputOrigin,
    	autocompleteOptions
  	);



  	autocompleteDestin = new google.maps.places.Autocomplete(
    	inputDestination,
    	autocompleteOptions
  	);

	//Make Directions Service object for getRoute
	directionsService = new google.maps.DirectionsService();
  	// Make Directions Renderer object for getRoute
  	directionsRenderer = new google.maps.DirectionsRenderer({
    	preserveViewport: false,
  	});

  	//make geocoder object for geolocation/journey planner feature
  	geocoder = new google.maps.Geocoder();


	//This should not be in init_map
  	//set minimum date field to current date so user can't plan journeys in the past
	var today = currentTime();
    document.getElementById("time-dropdown").setAttribute("min", today);

	//autocomplete listeners
	autocompleteOrigin.addListener("place_changed", checkFavourite, false);
	autocompleteDestin.addListener("place_changed", checkFavourite, false);

	if (typeof loadFavourite === "function") { 
		loadFavourite()
	}
}

function getRouteData(warning=true){
	var active_tab = document.querySelector('.tab-content .active');
	var route = {
		user : current_user
	}
	if (active_tab['id'] == "locations-tab"){
		route['stops'] = 0;
		route['origin_name'] = inputOrigin.value;
		route['destin_name'] = inputDestination.value;

		var destination = autocompleteDestin.getPlace();
		var origin = autocompleteOrigin.getPlace();
		if (!origin) {
			if (warning) {alert("Please use a valid starting point.")};
			return false;
		} else if (!destination){
			if (warning) {alert("Please use a valid destination.")};
			return false;
		}

		route['origin_lat'] = origin.geometry.location.lat();
		route['origin_lon'] = origin.geometry.location.lng();

		route['destin_lat'] = destination.geometry.location.lat();
		route['destin_lon'] = destination.geometry.location.lng();
	} else {
		route['stops'] = 1;
		route['origin_name'] = inputFirstStop.value;
		route['destin_name'] = inputLastStop.value;

		var originLatLon = getStopData(route['origin_name'], stops);
		var destinationLatLon = getStopData(route['destin_name'], stops);
		if (!originLatLon) {
			if (warning) {alert("Please input a valid First Stop")};
			return false;
		} else if (!destinationLatLon) {
			if (warning) {alert("Please input a valid Last Stop")};
			return false;
		}

		route['origin_lat'] = originLatLon['lat'];
		route['origin_lon'] = originLatLon['lng'];

		route['destin_lat'] = destinationLatLon['lat'];
		route['destin_lon'] = destinationLatLon['lng'];
	}
	return route
}



function currentTime(){
    var today = new Date();
    var date = today.getDate();
    var month = today.getMonth() + 1;
    var year = today.getFullYear();
    var hour = today.getHours();
    var minute = today.getMinutes();

    if(date<10) { date = '0' + date};
    if (month<10) { month='0' + month};
    if (hour<10) { hour='0' + hour};
    if (minute<10) { minute='0' + minute};

    today = year + '-' + month + '-' + date + 'T' + hour + ':' + minute;
	return today;
}

function getStopData(name, stop_list) {
	for (var i=0; i < stop_list.length; i++){
		if(stop_list[i]['fields']['stop_name'].replace("&#x27;","'") == name){
			var StopLatLon = {
				lat: stop_list[i]['fields']['stop_lat'],
				lng: stop_list[i]['fields']['stop_lon'],
			};
			return StopLatLon;
		}
	}
	return false;
};

function getRoute(start, end, time) {
	//Clear Previous Route
	directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);

	//request to Google Directions API
	const request = {
		origin: start,
		destination: end,
		travelMode: 'TRANSIT',
		transitOptions: {
			modes: ['BUS'],
			routingPreference: 'FEWER_TRANSFERS',
			departureTime: new Date(time),
		},
		unitSystem: google.maps.UnitSystem.METRIC
	}

	//clear markers from map so route can be seen
	clearMarkers();

	//make request and render route on map
	//need to fix to make sure agency is Dublin Bus?
	directionsService.route(request, function(response, status) {
		if (status == "OK") {
			directionsRenderer.setDirections(response);
			directionsRenderer.setMap(map);
            infoWindow.close();

			var route = document.getElementById("route_instructions");
			var journey = response.routes[0].legs[0].steps; //journey is held in leg[0]
			var journeyDescription = "<br>";


			//extract useful journey info from response and post to journey planner
			for (var i=0; i<journey.length; i++) {
				if (journey[i].travel_mode == "TRANSIT" && journey[i].transit.line.agencies[0].name == "Dublin Bus") {
    				journeyDescription += "<br>Ride the " + journey[i].transit.line.short_name + " from ";
    				journeyDescription += journey[i].transit.departure_stop.name + " toward " + journey[i].transit.headsign + " for " + journey[i].transit.num_stops + " stops.<br>";
    				journeyDescription += "Get off at " + journey[i].transit.arrival_stop.name + ".<br>";
    				var routeDetails = {};
    				routeDetails['departure_time'] = journey[i].transit.departure_time.value;
    				routeDetails['line'] = journey[i].transit.line.short_name;
    				routeDetails['departure_stop'] = journey[i].transit.departure_stop.name;
    				routeDetails['arrival_stop'] = journey[i].transit.arrival_stop.name;
    				routeDetails['num_stops'] = journey[i].transit.num_stops;
    				routeDetails['dep_stop_lat'] = journey[i].transit.departure_stop.location.lat();
    				routeDetails['dep_stop_lng'] = journey[i].transit.departure_stop.location.lng();
    				routeDetails['arr_stop_lat'] = journey[i].transit.arrival_stop.location.lat();
    				routeDetails['arr_stop_lng'] = journey[i].transit.arrival_stop.location.lng();
    				routeDetails['google_pred'] = journey[i].duration.value;
    				var journeyPrediction;

    				//post details to Django view
    				postData('/send_to_model', routeDetails).then((data) =>
                    displayRoute(JSON.parse(data.current_pred)));

				
				} else if (journey[i].travel_mode == "WALKING") {
    				journeyDescription += "<br>" + journey[i].instructions + ": " + journey[i].distance.text + " (" + journey[i].duration.text + ")<br>";
    				route.innerHTML = journeyDescription;


				} else if (journey[i].travel_mode == "TRANSIT" && journey[i].transit.line.agencies[0].name != "Dublin Bus") {
				    journeyDescription += "<br>Ride the " + journey[i].transit.line.short_name + " from ";
    				journeyDescription += journey[i].transit.departure_stop.name + " toward " + journey[i].transit.headsign + " for " + journey[i].transit.num_stops + " stops.<br>";
    				journeyDescription += "Get off at " + journey[i].transit.arrival_stop.name + ".<br>";
    				displayRoute(journey[i].duration.value);

				}

				else
				{
 					journeyDescription = "<br> This route is not served by Dublin Bus.";
 					route.innerHTML = journeyDescription;
 				}

 				function displayRoute(journeyPrediction) {
 				if (typeof journeyPrediction == 'string') {
 				    journeyPrediction = journeyPrediction.slice(1,-1);
 				    journeyDescription += 'ESTIMATED TRAVEL TIME ON BUS: ' + journeyPrediction + '<br>';
 				    }
 				else {
 				    journeyDescription += 'ESTIMATED TRAVEL TIME ON BUS: ' + journeyPrediction.toString() + '<br>';
 				}
 				route.innerHTML = journeyDescription;

				}
			}
		}
	});
}

//Press submit button
function submitRoute(){
	var time = inputTime.value;
	if (!time){
		time = currentTime();
	}

	var route = getRouteData();

	if (route){
		var destinationLatLon = {
			lat: route['origin_lat'],
			lng: route['origin_lon'] ,
		};
		var originLatLon = {
			lat: route['destin_lat'] ,
			lng: route['destin_lon'] ,
		}
		getRoute(originLatLon, destinationLatLon, time);
	}
}

//swaps tabs
function changeTabs(tab_id){
	var active_tab = document.querySelector('.tab-content .active');
	//
	if (active_tab['id'] == tab_id){
		return
	}else {
		var tab_list = document.querySelectorAll('.tab-content .tab-pane');
		var tab_valid = false;
		tab_list.forEach( function(tab){
			if (tab_id == tab['id']){
				tab_valid = true;
			}
		})
		if (tab_valid){
			
			var new_tab = document.getElementById(tab_id)
			//Change tabs
			new_tab.classList.add("active");
			new_tab.classList.add("show");
			active_tab.classList.remove("active");
			active_tab.classList.remove("show");

			//Change buttons
			var new_tab_button = document.getElementById(tab_id+"-btn");
			var active_tab_button = document.getElementById(active_tab['id']+"-btn");

			new_tab_button.classList.add("active");
			active_tab_button.classList.remove("active");

			new_tab_button.setAttribute("aria-selected", "true");
			active_tab_button.setAttribute("aria-selected", "false");


		}else{
			console.log("ERROR: "+ tab + " not found");
		}
	}
	checkFavourite();
}

//adds markers to map
function addMarkers(stops_data) {

    infoWindow = new google.maps.InfoWindow();
    //create stop icon
    var busStopIcon = {
        url: '../static/Bus/bus-stop.png',
        scaledSize: new google.maps.Size(30, 30),
      };

    for (var i=0; i<stops_data.length; i++) {
        const marker = new google.maps.Marker({
        icon: busStopIcon,
        position: {lat: stops_data[i].fields.stop_lat, lng: stops_data[i].fields.stop_lon},
        map: map,
        title: stops_data[i].pk + ":" + stops_data[i].fields.stop_name, //store stop_id and stop_name as title in marker for access
    });

    	//add reference to each marker in stopMarkers
    	stopMarkers[stops_data[i].pk] = marker;

        //array to hold markers
        stopMarkersArr.push(marker);


    //add listener: when marker is clicked, the stop_id is sent to the front end to grab latest arrival details
    marker.addListener("click", () =>
    postData('/fetch_arrivals/', marker.title.split(":")[0]).then((data) =>
    displayInfoWindow(data.timetable, marker.title.split(":")[0])))
    }

    //clusters added, need to be styles
    clusterStyles = {
    ignoreHidden: true,
    gridSize: 70,
    maxZoom: 15,
    styles: [{
    height: 30,
    width: 30,
    anchorText: [10, 15],
    textColor: 'white',
    textSize: 10,
    url: "../static/Bus/marker_clusters/icons8-filled-circle-30.png",
},
{ height: 50,
    width: 50,
    anchorText: [18, 24],
    textColor: 'white',
    textSize: 12,
    fontWeight: 'bold',
    url: "../static/Bus/marker_clusters/icons8-filled-circle-50.png",
    },

 { height: 65,
    width: 65,
    anchorText: [25, 33],
    textColor: 'white',
    textSize: 14,
    url: "../static/Bus/marker_clusters/icons8-filled-circle-70.png",
    },

],
};


    markerCluster = new MarkerClusterer(map, stopMarkersArr, clusterStyles);
}

function swapInputs(){
	var active_tab = $('.tab-content .active').attr('id');

	if(active_tab == "locations-tab"){
	
		//Store Origin Locations
		var temp = inputOrigin.value;
		var tempPlace = autocompleteOrigin.getPlace();

		//Turn off geo-location button
		if(currentLocationOrigin){
			toggleCurrentLocation();
		}

		inputOrigin.value = inputDestination.value;
		inputDestination.value = temp;

		autocompleteOrigin.set('place', autocompleteDestin.getPlace());
		autocompleteDestin.set('place', tempPlace);
	} else {
		var temp = inputFirstStop.value;
		inputFirstStop.value = inputLastStop.value;
		inputLastStop.value = temp;
	}
	checkFavourite();
}

//Activates Current Location as origin
function toggleCurrentLocation(){
	if('geolocation' in navigator){
        currentLocationOrigin = !currentLocationOrigin;
        inputOrigin.disabled = !inputOrigin.disabled;

		//Aesthetic Changes - placeholder while waiting for geolocation/geocoding to return current location
		if (currentLocationOrigin) {
		    $('#currentLocationButton').attr('class','btn btn-info');
		    inputOrigin.value = "";
		    inputOrigin.placeholder = "retrieving current location...";
			var geo_promise = getPosition()
			if (!geo_promise){
				alert("Browser is unable to use Geolocation services");
			} else {
				geo_promise.then(
					function(value){
						var originLatLon = {
							lat: value['coords']['latitude'],
							lng: value['coords']['longitude']
						}

						geocoder.geocode({ location: originLatLon }, (results, status) => {
							if (status === "OK") {
								var location_description = results[0].address_components[0].long_name + ' ' + results[0].address_components[1].long_name;
								inputOrigin.value = location_description;
								autocompleteOrigin.set('place', results[0]);
								checkFavourite();
							}
						});
					},
					function(error){
						console.log(error)
					}
				)
			}
		} else {
            inputOrigin.value = "";
            inputOrigin.placeholder = "Enter your start point";
			autocompleteOrigin.set('place', null);
			$('#currentLocationButton').attr('class','btn btn-secondary');
		}
		//checkFavourite() //Check if current values are a favourite
	} else{
		alert("Browser is unable to use Geolocation services");
	}
}

//Get Promise for current location
function getPosition(options = PositionOptions) {
    return new Promise((resolve, reject) => 
        navigator.geolocation.getCurrentPosition(resolve, reject, options)
    );
}

//displays infoWindow content
function displayInfoWindow(timetable, stop_id) {
	var arrivals = timetable;
    const marker = stopMarkers[stop_id];
    let infoWindowContent = "<h4>" + marker.title.split(":")[1] + "</h4>";

    //if no buses are due at the stop in next 2 hours
    if (arrivals.length == 0) {
    	infoWindowContent += "<br>No buses stopping here in the next 2 hours.";

	//if less than 3 buses due to stop in next 2 hours
    } else if (arrivals.length <= 3) {
    	for (var each in arrivals) {
			infoWindowContent += "<br>Line: " + arrivals[each].trip_id.route_id.route_short_name + " (to " + arrivals[each].stop_headsign + ")<br>";
			infoWindowContent += "Arrival time: " + arrivals[each].arrival_time + "<br>";
		}

	//else list 3 buses? Maybe more?
	} else {
    	for (var i=0; i<3; i++) {
        	infoWindowContent += "<br>Line: " + arrivals[i].trip_id.route_id.route_short_name + " (to " + arrivals[i].stop_headsign + ")<br>";
        	infoWindowContent += "Arrival time: " + arrivals[i].arrival_time + "<br>";
    	}
    }

    infoWindow.setContent(infoWindowContent);
    infoWindow.open(map, marker);
}


  //function to clear stop markers from map
function clearMarkers() {
  	for (var i=0; i < stopMarkersArr.length; i++) {
    	stopMarkersArr[i].setVisible(false);
  	}
}

 //function to make stop markers visible again
function showMarkers() {
 	for (var marker in stopMarkers) {
 		stopMarkers[marker].setVisible(true);
    }

}

//function to reset journey planner - should also reset time dropdown???
function resetJourneyPlanner() {
    document.getElementById('route_instructions').innerHTML = "";
    directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);

	//Reset Inputs
	inputOrigin.placeholder = "Enter your start point";
    inputOrigin.value = "";
    inputDestination.value = "";
	infoWindow.close();
	inputFirstStop.value ="";
	inputLastStop.value ="";

    //reset map center and zoom

    map.setZoom(14);
    map.setCenter({lat: 53.350140, lng: -6.266155});
    showMarkers();


	//Reset autocompletes
	autocompleteOrigin.set('place', null);
	autocompleteDestin.set('place', null);
	if (currentLocationOrigin) {
		toggleCurrentLocation();
	}

}

function toggleFavourite(){
	//Remove From Favourites
	if(isFavourite){
		var data = {
			id : currentFavourite
		}
		var promise = postData(remove_favourite_URL, data);

		promise.then(
			function(value){
				if (value['success'] == true){
					for(var i = 0; i < favourites.length; i++){
						if(favourites[i].id == currentFavourite){
							favourites.splice(i, 1);
							break;
						}
					}
					checkFavourite()
				}
			}
		)
	//Add to favourites
	}else{
		var promise = postData(create_favourite_URL, getRouteData(false));

		if (typeof promise.then === "function"){
			promise.then(
				function(value){
					if (value['success'] == true){
						favourites.push( value['favourite'])
						checkFavourite()
					}
				}
			)
		}
	}
};



//Checks if the current input is a favourite and alters DOM elements accordingly
var checkFavourite = function(evt) {
	var currentRoute = getRouteData(false);
	var match = false;
	var pk = 0;
	var co_ords = {
		origin_lat : currentRoute.origin_lat,
		origin_lon : currentRoute.origin_lon,
		destin_lat : currentRoute.destin_lat,
		destin_lon : currentRoute.destin_lon
	}
	for(var i = 0; i < favourites.length; i++){
		var fav_co_ords = {
			origin_lat : favourites[i].origin_lat,
			origin_lon : favourites[i].origin_lon,
			destin_lat : favourites[i].destin_lat,
			destin_lon : favourites[i].destin_lon
		}
		if(JSON.stringify(co_ords) === JSON.stringify(fav_co_ords)){
			match = true;
			currentFavourite = favourites[i].id;
			isFavourite = true;
			$('#favouriteButton').attr('class','btn btn-info');
			break;
		}
	}
	if (!match){
		isFavourite = false;
		$('#favouriteButton').attr('class','btn btn-secondary');
	}
}

//Check if current values are on the favourites list, triggered on changes to bus inputs
inputFirstStop.addEventListener('input', checkFavourite, false);
inputLastStop.addEventListener('input', checkFavourite, false);

//When
$('#locations-tab-btn').on('shown.bs.tab', function() {
	checkFavourite();
})
$('#stops-tab-btn').on('shown.bs.tab', function() {
	checkFavourite();
})