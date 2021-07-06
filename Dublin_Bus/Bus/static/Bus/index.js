'use strict';//to enable the use of let
let map;

function initMap (){

  let myLatLng = {lat: 53.350140, lng: -6.266155};//set the latitude and longitude to Dublin
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: myLatLng,
    mapTypeControl: false,
    streetViewControl: false,
  });
  }

