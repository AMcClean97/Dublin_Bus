'use strict';//to enable the use of let
let map;
//TODO customise bus stop icon
//TODO group markers when map zoomed out
let infoWindow;
let directionsService;
let directionsRenderer;
//list for storing reference to bus stop markers
let stopMarkers = {};
let originLatLon;
let destinationLatLon;
let inputOrigin;
let inputDestination;


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





function initMap (){

  let myLatLng = {lat: 53.350140, lng: -6.266155};//set the latitude and longitude to Dublin
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: myLatLng,
    mapTypeControl: false,
    streetViewControl: false,
  });

  // Setup Places Autocomplete Service
  // Set options for service
  const autocompleteOptions = {
    componentRestrictions: { country: ["IE"] },
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

    getRoute(originLatLon, destinationLatLon);

})

//Make Directions Service object for getRoute
directionsService = new google.maps.DirectionsService();
  // Make Directions Renderer object for getRoute
  directionsRenderer = new google.maps.DirectionsRenderer({
    preserveViewport: false,
  });
  }


function getRoute(start, end) {
//request to Google Directions API

const request = {
origin: start,
destination: end,
travelMode: 'TRANSIT',
transitOptions: {
modes: ['BUS'],
routingPreference: 'FEWER_TRANSFERS',
},
unitSystem: google.maps.UnitSystem.METRIC
}

//clear markers from map so route can be seen
clearMarkers();

//make request and render route on map
directionsService.route(request, function(response, status) {
if (status == "OK") {
directionsRenderer.setDirections(response);
directionsRenderer.setMap(map);


var route = document.getElementById("route_instructions");
var journey = response.routes[0].legs[0].steps; //journey is held in leg[0]
var journey_description = "<br>";

//extract useful journey info from response and post to journey planner
for (var i=0; i<journey.length; i++) {
if (journey[i].travel_mode == "TRANSIT") {
    journey_description += "<br>Ride the " + journey[i].transit.line.short_name + " from ";
    journey_description += journey[i].transit.departure_stop.name + " toward " + journey[i].transit.headsign + " for " + journey[i].transit.num_stops + " stops.<br>";
    journey_description += "Get off at " + journey[i].transit.arrival_stop.name + ".<br>";
}
else if (journey[i].travel_mode == "WALKING") {
    journey_description += "<br>" + journey[i].instructions + ": " + journey[i].distance.text + " (" + journey[i].duration.text + ")";
} else {
 journey_description = "<br> This route is not served by Dublin Bus.";
 }

route.innerHTML = journey_description;
}
}
});
}

//adds markers to map
 function addMarkers(stops_data) {

    infoWindow = new google.maps.InfoWindow();

    for (var i=0; i<stops_data.length; i++) {
        const marker = new google.maps.Marker({
        position: {lat: stops_data[i].fields.stop_lat, lng: stops_data[i].fields.stop_lon},
        map: map,
        title: stops_data[i].pk + ":" + stops_data[i].fields.stop_name, //store stop_id and stop_name as title in marker for access
    });

    //add reference to each marker in stopMarkers
    stopMarkers[stops_data[i].pk] = marker;


    //add listener: when marker is clicked, the stop_id is sent to the front end to grab latest arrival details
    marker.addListener("click", () =>
    postData('/bus/ajax/', marker.title.split(":")[0]).then((data) =>
    displayInfoWindow(data.timetable, marker.title.split(":")[0])))
    }
 }


//displays infoWindow content
 function displayInfoWindow(timetable, stop_id) {
    var arrivals = JSON.parse(timetable);
    const marker = stopMarkers[stop_id];
    let infoWindowContent = "<h4>" + marker.title.split(":")[1] + "</h4>";

    //if no buses are due at the stop that day
    if (arrivals.length == 0) {
    infoWindowContent += "<br>No buses due at this stop in the next 2 hours.";
    }

    ///if less than 3 buses due to stop that day
    else if (arrivals.length <= 3) {
    for (var each in arrivals) {
    infoWindowContent += "<br>Line: " + arrivals[each].fields.route_short_name + " (to " + arrivals[each].fields.stop_headsign + ")<br>";
        infoWindowContent += "Arrival time: " + arrivals[each].fields.arrival_time + "<br>";
    }
    }

    //else list 3 buses? Maybe more?
    else {
    for (var i=0; i<3; i++) {
        infoWindowContent += "<br>Line: " + arrivals[i].fields.route_short_name + " (to " + arrivals[i].fields.stop_headsign + ")<br>";
        infoWindowContent += "Arrival time: " + arrivals[i].fields.arrival_time + "<br>";
        }
        }

    infoWindow.setContent(infoWindowContent);
    infoWindow.open(map, marker);
    }


  //function to clear stop markers from map
function clearMarkers() {
  for (var marker in stopMarkers) {
    stopMarkers[marker].setVisible(false);
  }
  }

 //function to make stop markers visible again
 function showMarkers() {
 for (var marker in stopMarkers) {
 stopMarkers[marker].setVisible(true);
 }
 }

//function to reset journey planner - should also zoom back out on map?
function resetJourneyPlanner() {
    document.getElementById('route_instructions').innerHTML = "";
    directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);
    inputOrigin.value = "";
    inputDestination.value = "";
    showMarkers();
    }







