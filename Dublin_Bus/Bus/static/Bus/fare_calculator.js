'use strict';//to enable the use of let
let map;
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

    //Get Radio Button Answers
   var flexRadioDefault1 = document.getElementById("flexRadioDefault1");
   var flexRadioDefault2 = document.getElementById("flexRadioDefault2");
   var flexRadioDefault3 = document.getElementById("flexRadioDefault3");
   var flexRadioDefault4 = document.getElementById("flexRadioDefault4");
   var flexRadioDefault5 = document.getElementById("flexRadioDefault5");

   if (flexRadioDefault1.checked == false && flexRadioDefault2.checked == false && flexRadioDefault3.checked == false){
       alert("Please Enter a Ticket Type.");
	   return;
   }

   if (flexRadioDefault4.checked == false && flexRadioDefault5.checked == false){
       alert("Please Enter Whether You have a Leap Card or Not");
	   return;
   }

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

	//make request and render route on map
	//need to fix to make sure agency is Dublin Bus?
	directionsService.route(request, function(response, status) {
		if (status == "OK") {
			directionsRenderer.setDirections(response);
			directionsRenderer.setMap(map);


			var route = document.getElementById("route_instructions");
			var journey = response.routes[0].legs[0].steps; //journey is held in leg[0]
			var journeyDescription = "<br>";
			var journeyCost = 0.00;


			//extract useful journey info from response and post to journey planner
			for (var i=0; i<journey.length; i++) {
				if (journey[i].travel_mode == "TRANSIT" && journey[i].transit.line.agencies[0].name == "Dublin Bus") {
    				journeyDescription += "<br>Bus Route: " + journey[i].transit.line.short_name + "<br>";
    				if (journey[i].transit.num_stops <= 3) {

                        if(flexRadioDefault1.checked == true && flexRadioDefault4.checked == true) {
                        journeyDescription += "Cost for this Journey is €1.55 <br>";
                        journeyCost += 1.55;
                        } else if (flexRadioDefault1.checked == true && flexRadioDefault5.checked == true){
                        journeyDescription += "Cost for this Journey is €2.15 <br>";
                        journeyCost += 2.15;
                        } else if (flexRadioDefault3.checked == true){
                        journeyDescription += "Children Under 5 Travel Free <br>";
                        journeyCost += 0.00;
                        }
                        else if (flexRadioDefault2.checked == true && flexRadioDefault4.checked == true){
                            if (new Date(time).getHours() > 19) {
                            journeyDescription += "Cost for this Journey is €0.80 <br>";
                            journeyCost += 0.80;
                            } else {
                            journeyDescription += "Cost for this Journey is €1.00 <br>";
                            journeyCost += 1.00;
                            }
                        }
                        else if (flexRadioDefault2.checked == true && flexRadioDefault5.checked == true){
                            if (new Date(time).getHours() > 19) {
                            journeyDescription += "Cost for this Journey is €1.00 <br>";
                            journeyCost += 1.00;
                            } else {
                            journeyDescription += "Cost for this Journey is €1.30 <br>";
                            journeyCost += 1.30;
                            }
                        }
    				}
    			    else if (4 <= journey[i].transit.num_stops && journey[i].transit.num_stops <= 13) {
    				if(flexRadioDefault1.checked == true && flexRadioDefault4.checked == true) {
                        journeyDescription += "Cost for this Journey is €2.25 <br>";
                        journeyCost += 2.25;
                        } else if (flexRadioDefault1.checked == true && flexRadioDefault5.checked == true){
                        journeyDescription += "Cost for this Journey is €3.00 <br>";
                        journeyCost += 3.00;
                        } else if (flexRadioDefault3.checked == true){
                        journeyDescription += "Children Under 5 Travel Free <br>";
                        journeyCost += 0.00;
                        }
                        else if (flexRadioDefault2.checked == true && flexRadioDefault4.checked == true){
                            if (new Date(time).getHours() > 19) {
                            journeyDescription += "Cost for this Journey is €0.80 <br>";
                            journeyCost += 0.80;
                            } else {
                            journeyDescription += "Cost for this Journey is €1.00 <br>";
                            journeyCost += 1.00;
                            }
                        }
                        else if (flexRadioDefault2.checked == true && flexRadioDefault5.checked == true){
                            if (new Date(time).getHours() > 19) {
                            journeyDescription += "Cost for this Journey is €1.00 <br>";
                            journeyCost += 1.00;
                            } else {
                            journeyDescription += "Cost for this Journey is €1.30 <br>";
                            journeyCost += 1.30;
                            }
                        }
    				}
    				else if (journey[i].transit.num_stops && journey[i].transit.num_stops > 13) {
    				if(flexRadioDefault1.checked == true && flexRadioDefault4.checked == true) {
                        journeyDescription += "Cost for this Journey is €2.50 <br>";
                        journeyCost += 2.50;
                        } else if (flexRadioDefault1.checked == true && flexRadioDefault5.checked == true){
                        journeyDescription += "Cost for this Journey is €3.30 <br>";
                        journeyCost += 3.30;
                        } else if (flexRadioDefault3.checked == true){
                        journeyDescription += "Children Under 5 Travel Free <br>";
                        journeyCost += 0.00;
                        }
                        else if (flexRadioDefault2.checked == true && flexRadioDefault4.checked == true){
                            if (new Date(time).getHours() > 19) {
                            journeyDescription += "Cost for this Journey is €0.80 <br>";
                            journeyCost += 0.80;
                            } else {
                            journeyDescription += "Cost for this Journey is €1.00 <br>";
                            journeyCost += 1.00;
                            }
                        }
                        else if (flexRadioDefault2.checked == true && flexRadioDefault5.checked == true){
                            if (new Date(time).getHours() > 19) {
                            journeyDescription += "Cost for this Journey is €1.00 <br>";
                            journeyCost += 1.00;
                            } else {
                            journeyDescription += "Cost for this Journey is €1.30 <br>";
                            journeyCost += 1.30;
                            }
                        }
    				}


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

				} else if (journey[i].travel_mode == "WALKING") {
				route.innerHTML = journeyDescription;

				} else if (journey[i].travel_mode == "TRANSIT" && journey[i].transit.line.agencies[0].name != "Dublin Bus") {
				    journeyDescription += "<br>Bus Route: " + journey[i].transit.line.short_name;
    				journeyDescription += "<br> This route is not served by Dublin Bus and will not be included in fare calculations.<br>";
    				route.innerHTML = journeyDescription;

				}

				else
				{
    				journeyDescription += "<br> This route is not served by Dublin Bus and will not be included in fare calculations. <br>";
 					route.innerHTML = journeyDescription;
 				}
			}

			route.innerHTML =  journeyDescription + "<br> Total Calculated Fare is: €" + journeyCost;

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


	}
	//Get New Route
	getRoute(originLatLon, destinationLatLon, time);
};



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


//function to reset journey planner - should also reset time dropdown???
function resetJourneyPlanner() {
    document.getElementById('route_instructions').innerHTML = "";
    directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);

	//Reset Inputs
	inputOrigin.placeholder = "Enter your start point";
    inputOrigin.value = "";
    inputDestination.value = "";

    //reset map center and zoom

    map.setZoom(14);
    map.setCenter({lat: 53.350140, lng: -6.266155});


	//Reset autocompletes
	autocompleteOrigin.set('place', null);
	autocompleteDestin.set('place', null);
	if (currentLocationOrigin) {
		toggleCurrentLocation();
	}

	//Reset radiobuttons
	document.getElementById("flexRadioDefault1").checked = false;
    document.getElementById("flexRadioDefault2").checked = false;
    document.getElementById("flexRadioDefault3").checked = false;
    document.getElementById("flexRadioDefault4").checked = false;
    document.getElementById("flexRadioDefault5").checked = false;



}

