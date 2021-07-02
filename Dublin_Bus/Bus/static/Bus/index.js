'use strict';//to enable the use of let
let map;
//TODO customise bus stop icon
let infoWindow;
//list for storing reference to bus stop markers
let stopMarkers = {};

function initMap (){

  let myLatLng = {lat: 53.350140, lng: -6.266155};//set the latitude and longitude to Dublin
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: myLatLng,
  });
  }


 function addMarkers(stops_data) {

    infoWindow = new google.maps.InfoWindow();

    for (var i=0; i<stops_data.length; i++) {

    const marker = new google.maps.Marker({
    position: {lat: stops_data[i].fields.stop_lat, lng: stops_data[i].fields.stop_lng},
    map: map,
    });

    //add reference to each marker in stopMarkers - either pk or short_id?
    stopMarkers[stops_data[i].fields.short_id] = marker;
    let current_marker = stops_data[i].fields;
    console.log(current_marker);
    marker.addListener("click", () =>
    displayInfoWindow(current_marker))
    }
 }

//displays infoWindow content
 function displayInfoWindow(stop_data) {
    const marker = stopMarkers[stop_data.short_id];
    let infoWindowContent = "<h4>" + stop_data.stop_name + " (" + stop_data.short_id + "):</h4>";
    infoWindow.setContent(infoWindowContent);
    infoWindow.open(map, marker);
    }

