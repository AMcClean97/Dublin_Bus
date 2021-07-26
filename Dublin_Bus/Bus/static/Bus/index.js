'use strict';//to enable the use of let
let map;
//TODO customise bus stop icon
//TODO group markers when map zoomed out
let infoWindow;
let directionsService;
let directionsRenderer;
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

//store csrftoken in a constant
const csrftoken = getCookie('csrftoken');

//function to retrieve Django CSRF token for POST requests - adapted from https://engineertodeveloper.com/how-to-use-ajax-with-django/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
            }
        }
    }
    return cookieValue;
}


//function to post data from frontend to Django
async function postData(url="", data={}) {

  	const response = await fetch(url, {
    	method: "POST",
    	headers: {
    		"X-CSRFToken": csrftoken,
    	},
    	body: JSON.stringify(data),
    });

    return response.json();
}





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


	//This should not be in init_map
  	//set minimum date field to current date so user can't plan journeys in the past
	var today = currentTime();
    document.getElementById("time-dropdown").setAttribute("min", today);
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
			console.log(journey);
			var journeyDescription = "<br>";


			//extract useful journey info from response and post to journey planner
			for (var i=0; i<journey.length; i++) {
				if (journey[i].travel_mode == "TRANSIT") {
    				journeyDescription += "<br>Ride the " + journey[i].transit.line.short_name + " from ";
    				journeyDescription += journey[i].transit.departure_stop.name + " toward " + journey[i].transit.headsign + " for " + journey[i].transit.num_stops + " stops.<br>";
    				journeyDescription += "Get off at " + journey[i].transit.arrival_stop.name + ".<br>";
    				var routeDetails = {};
    				routeDetails['departure_time'] = journey[i].transit.departure_time.value;
    				routeDetails['line'] = journey[i].transit.line.short_name;
    				routeDetails['departure_stop'] = journey[i].transit.departure_stop.name;
    				routeDetails['num_stops'] = journey[i].transit.num_stops;
    				var journeyPrediction;

    				//post details to Django view
    				postData('/send_to_model', routeDetails).then((data) =>
                    displayRoute(JSON.parse(data.current_pred)));

				
				} else if (journey[i].travel_mode == "WALKING") {
    				journeyDescription += "<br>" + journey[i].instructions + ": " + journey[i].distance.text + " (" + journey[i].duration.text + ")";
    				route.innerHTML = journeyDescription;
				} else {
 					journeyDescription = "<br> This route is not served by Dublin Bus.";
 					route.innerHTML = journeyDescription;
 				}

 				function displayRoute(journeyPrediction) {
 				journeyPrediction = journeyPrediction.slice(1,-1);
 				journeyDescription += '<br>ESTIMATED TRAVEL TIME FOR WHOLE JOURNEY: ' + journeyPrediction;
				route.innerHTML = journeyDescription;
				}
			}
		}
	});
}

//Press submit button
function submitRoute() {

	//Get DepartureTime Here
	var time = inputTime.value;
	if (!time){
		time = currentTime();
	}

	var id = $('.tab-content .active').attr('id');
	if(id == "locations-tab"){
		//Get Destination
		var destination = autocompleteDestin.getPlace();
		if (destination == undefined) {
			alert("Please use a valid destination.");
			return;
		}
		var destinationLatLon = {
			lat: destination.geometry.location.lat(),
			lng: destination.geometry.location.lng(),
		};

		//Check if Origin is Current Location
		if (currentLocationOrigin){
			getRoutefromCurrentPosition(destinationLatLon, time)
			return;
		// If Origin is not current Location Check Origin
		} else {
			var origin = autocompleteOrigin.getPlace();
		
			if (origin == undefined){
				alert("Please use a valid starting point.");
				return;
			}
	
			var originLatLon = {
				lat: origin.geometry.location.lat(),
				lng: origin.geometry.location.lng(),
			}
		}
	} else {
		var origin = inputFirstStop.value;
		var destination = inputLastStop.value;

		var originLatLon = getStopData(origin, stops);
		var destinationLatLon = getStopData(destination, stops);

		if (!originLatLon) {
			alert("Please input a valid First Stop")
			return;
		} else if (!destinationLatLon) {
			alert("Please input a valid Last Stop")
			return;
		}


	}
	//Get New Route
	getRoute(originLatLon, destinationLatLon, time);
};

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
    gridSize: 80,
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

//Swaps Origin and Destination
function swapInputs(){
	var id = $('.tab-content .active').attr('id');
	if(id == "locations-tab"){
		//Swap Input values
		var temp = inputOrigin.value;
		inputOrigin.value = inputDestination.value;
		inputDestination.value = temp;

		//Swap autocomplete Places
		var tempPlace = autocompleteOrigin.getPlace();
		autocompleteOrigin.set('place', autocompleteDestin.getPlace());
		autocompleteDestin.set('place', tempPlace);
	} else {
		var temp = inputFirstStop.value;
		inputFirstStop.value = inputLastStop.value;
		inputLastStop.value = temp;
	}
}

//Activates Current Location as origin
function toggleCurrentLocation(){
	if('geolocation' in navigator){
		currentLocationOrigin = !currentLocationOrigin;
		inputOrigin.disabled = !inputOrigin.disabled

		//Aesthetic Changes
		if (currentLocationOrigin){
			$('#currentLocationButton').attr('class','btn btn-info');
		} else {
			$('#currentLocationButton').attr('class','btn btn-secondary');
		}
	} else{
		alert("Browser is unable to use Geolocation services");
	}

}

//Handle Geo Location
function getRoutefromCurrentPosition(destinationLatLon, time){

	//var return_value;
	//Options regarding accuracy and speed
	var options = {
		enableHighAccuracy: true,
		timeout: 5000,
		maximumAge: 0
	};

	function success(pos){
		var originLatLon = {
			lat: pos.coords.latitude,
			lng: pos.coords.longitude,
		}
		getRoute(originLatLon, destinationLatLon, time);
	}

	function error(err){
		console.warn(`ERROR(${err.code}): ${err.message}`);
	}

	if('geolocation' in navigator){
		navigator.geolocation.getCurrentPosition(success, error, options);
	} else {
		alert("Browser is unable to use Geolocation services");
	}

}


//displays infoWindow content
function displayInfoWindow(timetable, stop_id) {
	var arrivals = timetable;
    const marker = stopMarkers[stop_id];
    let infoWindowContent = "<h4>" + marker.title.split(":")[1] + "</h4>";

    //if no buses are due at the stop that day
    if (arrivals.length == 0) {
    	infoWindowContent += "<br>No buses stopping here in the next 2 hours.";

	//if less than 3 buses due to stop that day
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
    inputOrigin.value = "";
    inputDestination.value = "";
	infoWindow.close();
	inputFirstStop.value ="";
	inputLastStop.value ="";
    showMarkers();
    //reset map center and zoom

    map.setZoom(14);
    map.setCenter({lat: 53.350140, lng: -6.266155});
    showMarkers();

	//Reset autocompletes
	autocompleteOrigin.set('place', null);
	autocompleteDestin.set('place', null);
}



