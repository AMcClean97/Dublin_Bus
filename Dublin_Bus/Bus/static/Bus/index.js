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
let originLatLon;
let destinationLatLon;
let inputOrigin;
let inputDestination;
let departureTime;
let markerCluster;



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

//store csrftoken in a constant
const csrftoken = getCookie('csrftoken');


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




// function to initialise map and markers
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
          { featureType: "poi.attraction", stylers: [{ visibility: "off" }] },
          { featureType: "poi.business", stylers: [{ visibility: "off" }] },
          { featureType: "poi.government", stylers: [{ visibility: "off" }] },
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
          { featureType: "transit", stylers: [{ visibility: "off" }] },
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
  	inputOrigin = document.getElementById("inputOrigin");
  	inputDestination = document.getElementById("inputDestin");

  	const autocompleteOrigin = new google.maps.places.Autocomplete(
    	inputOrigin,
    	autocompleteOptions
  	);

  	const autocompleteDestin = new google.maps.places.Autocomplete(
    	inputDestination,
    	autocompleteOptions
  	);

  //event listeners for autocomplete boxes

 	autocompleteOrigin.addListener("place_changed", () => {
    	const origin = autocompleteOrigin.getPlace();

    	// will alert user if request fails or if they enter invalid place
    	if (!origin.geometry || !origin.geometry.location) {
      		window.alert( "Hmmmmm...we are not familiar with " + origin.name + ". Choose an option from the searchbox dropdown.");
      		return;
    	}

    	originLatLon = {
    	lat: origin.geometry.location.lat(),
    	lng: origin.geometry.location.lng(),
    	}

    	const origin_name = origin.name;
    })

 	autocompleteDestin.addListener("place_changed", () => {
    const destination = autocompleteDestin.getPlace();


      if (!destination.geometry || !destination.geometry.location) {
      window.alert("Hmmmm, we are not familiar with " + destination.name + ". Choose an option from the searchbox dropdown.");
      return;
    }

    destinationLatLon = {
    	lat: destination.geometry.location.lat(),
    	lng: destination.geometry.location.lng(),
    };

    const destination_name = destination.name;


})

	//Make Directions Service object for getRoute
	directionsService = new google.maps.DirectionsService();
  	// Make Directions Renderer object for getRoute
  	directionsRenderer = new google.maps.DirectionsRenderer({
    	preserveViewport: false,
  	});


  	//set minimum date field to current date so user can't plan journeys in the past
    var today = new Date();
    var date = today.getDate();
    var month = today.getMonth() + 1;
    var year = today.getFullYear();
    var hour = today.getHours();
    var minute = today.getMinutes();

    if(date<10) {
    date = '0' + date};
    if (month<10) {
    month='0' + month};
    if (hour<10) {
    hour='0' + hour};
    if (minute<10) {
    minute='0' + minute};

    today = year + '-' + month + '-' + date + 'T' + hour + ':' + minute;
    document.getElementById("time-dropdown").setAttribute("min", today);


  	//event listener to get time value from time/date dropdown
    const selectElement = document.getElementById('time-dropdown');

    selectElement.addEventListener('change', (event) => {
    departureTime = event.target.value;

});

    const submitButton = document.getElementById('submitJourneyPlanner');
    submitButton.addEventListener('click', (event) => {
    getRoute(originLatLon, destinationLatLon, departureTime);

});
}


function getRoute(start, end, time) {
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

//adds markers to map
function addMarkers(stops_data) {

    infoWindow = new google.maps.InfoWindow();
    //create marker icon
     var busStopIcon = {
        url: '../static/Bus/DBIcon.png',
        scaledSize: new google.maps.Size(25, 25),
      };

    for (var i=0; i<stops_data.length; i++) {
        const marker = new google.maps.Marker({
        icon: busStopIcon,
        position: {lat: stops_data[i].fields.stop_lat, lng: stops_data[i].fields.stop_lon},
        map: map,
        title: stops_data[i].pk + ":" + stops_data[i].fields.stop_name, //store stop_id and stop_name as title in marker for access
    });



    //add reference to each marker in stopMarkers, probably don't need this if we do stopMarkerArr
    stopMarkers[stops_data[i].pk] = marker;

    //array to hold markers
    stopMarkersArr.push(marker);


    //add listener: when marker is clicked, the stop_id is sent to the front end to grab latest arrival details
    marker.addListener("click", () =>
    postData('/fetch_arrivals/', marker.title.split(":")[0]).then((data) =>
    displayInfoWindow(data.timetable, marker.title.split(":")[0])))
    }

    //clusters added, need to be styles
    var clusterStyles = {
styles: [{
    height: 40,
    width: 40,
    anchorText: [20, 26],
    textColor: 'black',
    textSize: 10,
    url: "../static/Bus/marker_clusters/m1.png",
},
{ height: 60,
    width: 60,
    anchorText: [21, 27],
    textColor: 'black',
    textSize: 10,
    url: "../static/Bus/marker_clusters/m2.png",
    },

 { height: 80,
    width: 80,
    anchorText: [27, 35],
    textColor: 'black',
    textSize: 10,
    url: "../static/Bus/marker_clusters/m3.png",
    },

],
};


    markerCluster = new MarkerClusterer(map, stopMarkersArr, clusterStyles);
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
  	for (var marker in stopMarkers) {
    	stopMarkers[marker].setVisible(false);
    	markerCluster.setMap(null);
  	}
}

 //function to make stop markers visible again
function showMarkers() {
 	for (var marker in stopMarkers) {
 		stopMarkers[marker].setVisible(true);
 		markerCluster.setMap(map);
 	}

}

//function to reset journey planner - should also reset time dropdown???
function resetJourneyPlanner() {
    document.getElementById('route_instructions').innerHTML = "";
    directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);
    inputOrigin.value = "";
    inputDestination.value = "";
    showMarkers();
    //reset map center and zoom
    map.setCenter({lat: 53.350140, lng: -6.266155});
    map.setZoom(14);


}




