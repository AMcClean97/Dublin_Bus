'use strict';//to enable the use of let
let map;
//TODO customise bus stop icon
//TODO group markers when map zoomed out
let infoWindow;
//list for storing reference to bus stop markers
let stopMarkers = {};


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

//initialises map
function initMap (){

  let myLatLng = {lat: 53.350140, lng: -6.266155};//set the latitude and longitude to Dublin
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: myLatLng,
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
    displayInfoWindow(data.timetable)))
    }
 }


//displays infoWindow content
 function displayInfoWindow(timetable) {
   var arrivals = JSON.parse(timetable);
   const marker = stopMarkers[arrivals[0].fields.stop_id];
    let infoWindowContent = "<h4>" + marker.title.split(":")[1] + "</h4>";

    //show next 5 arrivals?
    for (var i=0; i<5; i++) {
        infoWindowContent += "<br>Line: " + arrivals[i].fields.route_short_name + " (to " + arrivals[i].fields.stop_headsign + ")<br>";
        infoWindowContent += "Arrival time: " + arrivals[i].fields.arrival_time + "<br>";
        }
    infoWindow.setContent(infoWindowContent);
    infoWindow.open(map, marker);
    }










