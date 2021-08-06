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
//journey planner
let predictionDisplay;
let journeyDescription;
//Polyline and icon options
let polylineCustomOptions;
let startIcon;
let endIcon;
let startMarker;
let endMarker;


//store csrftoken in a constant
const csrftoken = getCookie('csrftoken');

//enable tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})







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

    //set up Polyline
    polylineCustomOptions = {
    strokeColor: '#FFAE42',
    strokeOpacity: 1.0,
    strokeWeight: 4,
    };

    //set up startMarker
     startMarker = new google.maps.Marker({ label: {
            text: 'A',
            color: "white",
            fontSize: "12px",
            fontWeight: "bold",}});
    //set up endIcon
     endMarker = new google.maps.Marker({ label: {
            text: 'B',
            color: "white",
            fontSize: "12px",
            fontWeight: "bold",}});

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
	//make start icon
	startIcon = {
	    path: "M0-48c-9.8 0-17.7 7.8-17.7 17.4 0 15.5 17.7 30.6 17.7 30.6s17.7-15.4 17.7-30.6c0-9.6-7.9-17.4-17.7-17.4z",
	    fillColor: '#05386B',
	    fillOpacity: 1,
	    scale: 0.65,
	    labelOrigin: new google.maps.Point(0, -30),

	}
    //make end icon
	endIcon = {
	    path: "M0-48c-9.8 0-17.7 7.8-17.7 17.4 0 15.5 17.7 30.6 17.7 30.6s17.7-15.4 17.7-30.6c0-9.6-7.9-17.4-17.7-17.4z",
	    fillColor: '#05386B',
	    fillOpacity: 1,
	    scale: 0.65,
	    labelOrigin: new google.maps.Point(0, -30),

	}



  	// Make Directions Renderer object for getRoute
  	directionsRenderer = new google.maps.DirectionsRenderer(
  	    {
  	    polylineOptions: polylineCustomOptions,
        suppressMarkers:true,
    	preserveViewport: false,
  	});



  	// Make Directions Renderer object for getRoute
  	//directionsRenderer = new google.maps.DirectionsRenderer(
    //	{preserveViewport: false,
  	//});

  	//make geocoder object for geolocation/journey planner feature
  	geocoder = new google.maps.Geocoder();


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
    document.getElementById('route_suggestions').innerHTML = "";



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

            startMarker.setPosition(start);
            startMarker.setIcon(startIcon);
            startMarker.setMap(map);
            endMarker.setPosition(end);
            endMarker.setIcon(endIcon);
            endMarker.setMap(map);

			directionsRenderer.setDirections(response);
			directionsRenderer.setMap(map);
            infoWindow.close();


			var journey = response.routes[0].legs[0].steps; //journey is held in leg[0]
			console.log(journey);

            var route_suggestions = document.getElementById('route_suggestions');
            var divider = "<hr class='divider'>"
            //this variable is used to create ids for each step in a journey
            var i = 0;
            processJourney(journey);

			//extract useful journey info from response and post to journey planner
			async function processJourney(journey) {
			journey.forEach(async (journey) => {
			//increments id for each step of journey
			i++;
            //assigns id to p element
            route_suggestions.innerHTML += "<p id='" + i + "'</p>";


            if (journey.travel_mode == "TRANSIT" && journey.transit.line.agencies[0].name == "Dublin Bus") {
                journeyDescription = "<i class='fas fa-bus-alt'></i> " + journey.transit.line.short_name + '   |    ';


 				var routeDetails = {};
 				routeDetails['departure_time'] = journey.transit.departure_time.value;
 				routeDetails['line'] = journey.transit.line.short_name;
 				routeDetails['departure_stop'] = journey.transit.departure_stop.name;
 				routeDetails['arrival_stop'] = journey.transit.arrival_stop.name;
 				routeDetails['num_stops'] = journey.transit.num_stops;
 				routeDetails['dep_stop_lat'] = journey.transit.departure_stop.location.lat();
 				routeDetails['dep_stop_lng'] = journey.transit.departure_stop.location.lng();
 				routeDetails['arr_stop_lat'] = journey.transit.arrival_stop.location.lat();
 				routeDetails['arr_stop_lng'] = journey.transit.arrival_stop.location.lng();
 				routeDetails['google_pred'] = journey.duration.value;

                var predictionSpace = i.toString();
                document.getElementById(predictionSpace).innerHTML = journeyDescription;
                var numStops = routeDetails['num_stops'];
                var arrivalStop = routeDetails['arrival_stop'];
                var departureStop = routeDetails['departure_stop'];



 				//post details to Django view
 				await postData('/send_to_model', routeDetails).then(async (data) =>
                 await displayRoute(JSON.parse(data.current_pred), predictionSpace, {numStops: numStops}, {departureStop: departureStop}, {arrivalStop: arrivalStop}));
                 document.getElementById(predictionSpace).innerHTML += divider;

	} else if (journey.travel_mode == "WALKING") {
 				journeyDescription = "<i class='fas fa-walking'></i> " + journey.distance.text + "/" + journey.duration.text + "<br>"
 				journeyDescription += journey.instructions;
 				journeyDescription += divider;
 				route_suggestions.innerHTML += journeyDescription;

	} else if (journey.travel_mode == "TRANSIT" && journey.transit.line.agencies[0].name != "Dublin Bus") {
	            journeyDescription = "<i class='fas fa-bus-alt'></i> " + journey.transit.line.short_name + "   |   " + journey.transit.num_stops + ' stops/' + journey.duration.text + '<i class="fas fa-info-circle d-none d-sm-inline" data-toggle="tooltip" title="Prediction generated by Google" data-placement="auto"></i><br>';
 				journeyDescription += journey.transit.departure_stop.name + 'to ' + journey.transit.arrival_stop.name + "<br>";
 				journeyDescription += divider;
 				route_suggestions.innerHTML += journeyDescription;
	} else {
			journeyDescription = "This route is not served by Dublin Bus.<br>";
			journeyDescription += divider;
			route_suggestions.innerHTML += journeyDescription;
		   }


            })

			}
			}





 				async function displayRoute(journeyPrediction, predictionSpace, numStops, departureStop, arrivalStop) {
                    var pred;

 				    if (typeof journeyPrediction == 'string') {
 				        journeyPrediction = journeyPrediction.slice(1,-1);
 				        var predictionMins = parseInt(journeyPrediction);
 				        pred = numStops.numStops + ' stops/' + predictionMins.toString() + ' mins<i class="fas fa-info-circle d-none d-sm-inline" data-toggle="tooltip" title="Prediction generated by Bustimate" data-placement="auto"></i><br>';

 				    } else {
 				        var predictionMins = Math.round(journeyPrediction / 60);
 				        pred = numStops.numStops + ' stops/' + predictionMins.toString() + ' mins<i class="fas fa-info-circle d-none d-sm-inline" data-toggle="tooltip" title="Prediction generated by Google" data-placement="auto"><br>';
 				    }


 			    document.getElementById(predictionSpace).innerHTML += pred;
 			    document.getElementById(predictionSpace).innerHTML += 'From ' + departureStop.departureStop + ' to ' + arrivalStop.arrivalStop;
 			    //document.getElementById(predictionSpace).innerHTML += "From " + departureStop.departureStop + ' to ' arrivalStop.arrivalStop + '<br>';'
				}

		})
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
			getRouteFromCurrentPosition(destinationLatLon, time, false);
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
        endMarker.setVisible(false);
        startMarker.setVisible(false);

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
    displayInfoWindow(data.timetable, data.delays, marker.title.split(":")[0])))
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

//Swaps Origin and Destination
function swapInputs(){
	var id = $('.tab-content .active').attr('id');

	//if origin is current location, use geocoder to get Place
	if(id == "locations-tab" && currentLocationOrigin){
        var temp = inputOrigin.value;
		geocoder.geocode({ address: temp}, (results, status) => {
	    if (status === "OK") {
	        //swap input values
		    inputOrigin.value = inputDestination.value;
		    inputDestination.value = temp;

            //swap autocomplete Places
	        var tempPlace = results[0];
	        autocompleteOrigin.set('place', autocompleteDestin.getPlace());
		    autocompleteDestin.set('place', tempPlace);
            }
            });
            //switch off currentLocation button (as current location is no longer origin)
            toggleCurrentLocation();
	}

	else if(id == "locations-tab"){
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
        inputOrigin.disabled = !inputOrigin.disabled;

		//Aesthetic Changes - placeholder while waiting for geolocation/geocoding to return current location
		if (currentLocationOrigin) {
		    $('#currentLocationButton').attr('class','btn btn-info');
		    inputOrigin.value = "";
		    inputOrigin.placeholder = "retrieving current location...";
			getRouteFromCurrentPosition(null, null, true);
		} else {
            inputOrigin.value = "";
            inputOrigin.placeholder = "Enter your start point";
			$('#currentLocationButton').attr('class','btn btn-secondary');
		}

	} else{
		alert("Browser is unable to use Geolocation services");
	}

}

//Handle Geo Location
function getRouteFromCurrentPosition(destinationLatLon, time, positionOnly=false){

	//var return_value;
	//Options regarding accuracy and speed
	var options = {
		enableHighAccuracy: true,
		timeout: 5000,
		maximumAge: 0,
	};

	function success(pos){
		var originLatLon = {
			lat: pos.coords.latitude,
			lng: pos.coords.longitude,
		}

		geocoder.geocode({ location: originLatLon }, (results, status) => {
	    	if (status === "OK") {
	        	const location_description = results[0].address_components[0].long_name + ' ' + results[0].address_components[1].long_name;
            	inputOrigin.value = location_description;
        	}
		});


        if (positionOnly) {
            return;
        } else {
			getRoute(originLatLon, destinationLatLon, time);
		}
	}


	function error(err){
		console.warn(`ERROR(${err.code}): ${err.message}`);
	}

	if('geolocation' in navigator) {
		inputOrigin.placeholder = "retrieving current location...";
		navigator.geolocation.getCurrentPosition(success, error, options);
	} else {
		alert("Browser is unable to use Geolocation services");
	}

}


//displays infoWindow content
function displayInfoWindow(timetable, delays, stop_id) {
	var arrivals = timetable;
    const marker = stopMarkers[stop_id];
    var arrival_time;

    function factorDelay(duration, delay){
    //takes time as string, converts it to seconds, adds delay, reconverts to string and returns
    let [hours, minutes, seconds] = duration.split(':');
    seconds = (Number(hours) * 60 * 60 + Number(minutes) * 60 + Number(seconds)) + delay;
    var date = new Date(1970,0,1);
    date.setSeconds(seconds);
    return date.toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1");
};



    let infoWindowContent = "<div id='info_window'><h6>" + marker.title.split(":")[1] + "</h6>";

    //if no buses are due at the stop in next 2 hours
    if (arrivals.length == 0) {
    	infoWindowContent += "<br>No buses stopping here in the next 2 hours.";

	//if less than 3 buses due to stop in next 2 hours
    } else if (arrivals.length <= 3) {
    	for (var each in arrivals) {
			infoWindowContent += "<br><i class='fas fa-bus-alt'></i> " + arrivals[each].trip_id.route_id.route_short_name + " (to " + arrivals[each].stop_headsign + ") - ";
			if (delays[each] != 0) {
			    arrival_time = factorDelay(arrivals[each].arrival_time, delays[each])
                console.log(arrival_time);
            } else {
                arrival_time = arrivals[each].arrival_time;
            }

			infoWindowContent += arrival_time.slice(0,5) + "<br>";
		}

	}
    infoWindowContent += "</div>"
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
    document.getElementById('route_suggestions').innerHTML = "";
    directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);
    endMarker.setVisible(false);
    startMarker.setVisible(false);

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




