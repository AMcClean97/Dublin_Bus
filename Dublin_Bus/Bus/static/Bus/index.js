'use strict'; //to enable the use of let
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
let PositionOptions = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0,
};
//Favourites
let isFavourite = false;
let currentFavourite;
//Journey planner
let predictionDisplay;
let journeyDescription;
//Polyline and icon options
let polylineCustomOptions;
let startIcon;
let endIcon;
let startMarker;
let endMarker;
//Check if Logged in
let current_user = null;
//Bus fares for calculator
let fares = false;
// currentFavourite
let postedFavourite = false
//stores bus departure time and travel time values for estimate arrival time
let time_tracker;
let duration_tracker = {};
let latest_departure = {};
let no_route = false;



$.getJSON("./static/Bus/bus_fares.json", function(data) {
    fares = data
})

function initMap() {

    let myLatLng = {
        lat: 53.350140,
        lng: -6.266155
    }; //set the latitude and longitude to Dublin

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: myLatLng,
        mapTypeControl: false,
        streetViewControl: false,
        styles: [{
                stylers: [{
                    saturation: -10
                }]
            },
            {
                featureType: "administrative.land_parcel",
                elementType: "labels",
                stylers: [{
                    visibility: "off"
                }],
            },
            {
                featureType: "landscape.man_made",
                stylers: [{
                    visibility: "off"
                }],
            },
            {
                featureType: "poi",
                elementType: "labels.text",
                stylers: [{
                    visibility: "off"
                }],
            },
            {
                featureType: "poi",
                elementType: "geometry",
                stylers: [{
                    visibility: "off"
                }],
            },
            {
                featureType: "poi",
                stylers: [{
                    visibility: "off"
                }]
            },
            {
                featureType: "road",
                elementType: "labels.icon",
                stylers: [{
                    visibility: "on"
                }],
            },
            {
                featureType: "road.local",
                elementType: "labels",
                stylers: [{
                    visibility: "on"
                }],
            },
            {
                featureType: "transit",
                stylers: [{
                    visibility: "off"
                }]
            },
        ],
    });

    //will be used to restrict autocomplete search box options, radius can be increased or decreased as needed
    var dublin_bounds = new google.maps.Circle({
        center: myLatLng,
        radius: 30000
    });

    //set up Polyline
    polylineCustomOptions = {
        strokeColor: '#05386B',
        strokeOpacity: 1.0,
        strokeWeight: 4,
    };

    //set up startMarker
    startMarker = new google.maps.Marker({
        label: {
            text: 'A',
            color: "#05386B",
            fontSize: "12px",
            fontWeight: "bold",
        }
    });
    //set up endIcon
    endMarker = new google.maps.Marker({
        label: {
            text: 'B',
            color: "#05386B",
            fontSize: "12px",
            fontWeight: "bold",
        }
    });

    // Setup Places Autocomplete Service
    // Set options for service
    // Need to add Dublin bounds to restrict search box
    const autocompleteOptions = {
        componentRestrictions: {
            country: ["IE"]
        },
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
        fillColor: '#FFAE42',
        fillOpacity: 1,
        scale: 0.65,
        labelOrigin: new google.maps.Point(0, -30),

    }
    //make end icon
    endIcon = {
        path: "M0-48c-9.8 0-17.7 7.8-17.7 17.4 0 15.5 17.7 30.6 17.7 30.6s17.7-15.4 17.7-30.6c0-9.6-7.9-17.4-17.7-17.4z",
        fillColor: '#FFAE42',
        fillOpacity: 1,
        scale: 0.65,
        labelOrigin: new google.maps.Point(0, -30),

    }



    // Make Directions Renderer object for getRoute
    directionsRenderer = new google.maps.DirectionsRenderer({
        polylineOptions: polylineCustomOptions,
        suppressMarkers: true,
        preserveViewport: false,
    });

    //make geocoder object for geolocation/journey planner feature
    geocoder = new google.maps.Geocoder();


    //This should not be in init_map

    //autocomplete listeners
    autocompleteOrigin.addListener("place_changed", checkFavourite, false);
    autocompleteDestin.addListener("place_changed", checkFavourite, false);

    if (typeof loadFavourite === "function") {
        loadFavourite()
    }
}

//Returns Data from origin/FirstStop and destination/LastStop inputs
function getRouteData(warning = true) {
    var active_tab = document.querySelector('.tab-content .active');
    var route = {
        user: current_user
    }
    if (active_tab['id'] == "locations-tab") {
        route['stops'] = 0;
        route['origin_name'] = inputOrigin.value;
        route['destin_name'] = inputDestination.value;

        var destination = autocompleteDestin.getPlace();
        var origin = autocompleteOrigin.getPlace();

        if (!origin) {
            if (warning) {
                showWarning("Please use a valid starting point.")
            };
            return false;
        } else if (!destination) {
            if (warning) {
                showWarning("Please use a valid destination.")
            };
            return false;
        } else if (origin.place_id == destination.place_id) {
            if (warning) {
                showWarning("Origin and destination are identical.")
            };
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
            if (warning) {
                showWarning("Please input a valid first stop.")
            };
            return false;
        } else if (!destinationLatLon) {
            if (warning) {
                showWarning("Please input a valid last stop.")
            };
            return false;
        } else if (route['origin_name'] == route['destin_name']) {
            if (warning) {
                showWarning("First and last stops are identical.")
            };
            return false;
        }

        route['origin_lat'] = originLatLon['lat'];
        route['origin_lon'] = originLatLon['lng'];

        route['destin_lat'] = destinationLatLon['lat'];
        route['destin_lon'] = destinationLatLon['lng'];
    }
    return route
}

function formatTime(time) {
    var date = time.getDate();
    var month = time.getMonth() + 1;
    var year = time.getFullYear();
    var hour = time.getHours();
    var minute = time.getMinutes();

    if (date < 10) {
        date = '0' + date
    };
    if (month < 10) {
        month = '0' + month
    };
    if (hour < 10) {
        hour = '0' + hour
    };
    if (minute < 10) {
        minute = '0' + minute
    };

    time = year + '-' + month + '-' + date + 'T' + hour + ':' + minute;
    return time;
}

//Displays a warning message beneath button-group
function showWarning(text) {
    var warningBox = document.getElementById('warning');
    warningBox.innerHTML = text;
    warningBox.style.display = 'block';
}

//Returns Co-ordinates of a stop when given it's name
function getStopData(name, stop_list) {
    for (var i = 0; i < stop_list.length; i++) {
        if (stop_list[i]['fields']['stop_name'].replace("&#x27;", "'") == name) {
            var StopLatLon = {
                lat: stop_list[i]['fields']['stop_lat'],
                lng: stop_list[i]['fields']['stop_lon'],
            };
            return StopLatLon;
        }
    }
    return false;
};

//Displays route and time estimates
async function getRoute(start, end, time) {
    //Clear Previous Route
    directionsRenderer.set('directions', null);
    directionsRenderer.setMap(null);
    document.getElementById('route_suggestions').innerHTML = "";
    document.getElementById('route_suggestions').style.visibility = "hidden";



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

    //Check if fare Calculator is on and get data if it is
    var CalcOn = (fare_suggestions.style.display === "block")
    if (CalcOn) {
        if (!fares) {
            showWarning("Unable to access fare data")
            return;
        }

        var age = $('input[name="age"]:checked').val();
        var payment = $('input[name="payment"]:checked').val();

        if (!age) {
            showWarning("Enter Ticket Type.")
            return;
        } else if (!payment) {
            showWarning("Do you have a leap card?")
            return;
        }

        var total_cost = 0;
    }


    //make request and render route on map
    directionsService.route(request, async function(response, status) {
        if (status == "OK") {

            //set custom markers
            startMarker.setPosition(start);
            startMarker.setIcon(startIcon);
            startMarker.setMap(map);
            startMarker.setVisible(true);
            endMarker.setPosition(end);
            endMarker.setIcon(endIcon);
            endMarker.setMap(map);
            endMarker.setVisible(true);


            directionsRenderer.setDirections(response);
            directionsRenderer.setMap(map);
            infoWindow.close();


            var entire_journey = response.routes[0].legs[0].steps; //journey is held in leg[0]
            console.log(entire_journey);
            var route_suggestions = document.getElementById('route_suggestions');
            var divider = "<hr class='divider'>"
            //this variable is used to create ids for each step in a journey
            var i = 0;
            // used to store values for estimated arrival time
            latest_departure = {};
            duration_tracker = {};




            async function asyncForEach(array, callback) {
                for (let i = 0; i < array.length; i++) {
                    if (no_route == true) {
                        journeyDescription = "This route is not served by Dublin Bus.<br>";
                        journeyDescription += divider;
                        route_suggestions.innerHTML = journeyDescription;
                        console.error("Doesn't Exist!");
                        directionsRenderer.set('directions', null);
                        directionsRenderer.setMap(null);
                        console.log(no_route);
                        break;
                    } else {
                        await callback(array[i], i, array);
                    }
                }


            }

            if (entire_journey.length == 1 && entire_journey[0].travel_mode == "WALKING") {
                await processJourney(entire_journey);
                document.getElementById('route_suggestions').style.visibility = "visible";
            }
            else {
            await processJourney(entire_journey).then((travel_time_values) =>
                displayEstimatedArrival(travel_time_values[0], travel_time_values[1], no_route));}




            //extract useful journey info from response and post to journey planner
            async function processJourney(entire_journey) {
                await asyncForEach(entire_journey, async (journey) => {
                    //increments id for each step of journey
                    i++;
                    //assigns id to p element
                    route_suggestions.innerHTML += "<p id='" + i + "'</p>";


                    if (journey.travel_mode == "TRANSIT" && journey.transit.line.agencies[0].name == "Dublin Bus") {
                        journeyDescription = "<img src='../static/Bus/logo-smaller.png' class='img-fluid><i class='fas fa-bus-alt'></i> " + journey.transit.line.short_name + '   |    ';
                        journeyDescription += "<i class='fas fa-clock'></i> " + journey.transit.departure_time.text + '    |    ';

                        var routeDetails = {};
                        routeDetails['departure_time'] = journey.transit.departure_time.value.toISOString();
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
                        var departureTime = journey.transit.departure_time.value;


                        if (CalcOn) {
                            var cost = fareCalc(age, payment, journey, time);
                            total_cost += cost;
                        } else {
                            var cost = false;
                        }


                        //post details to Django view
                        await postData(query_model_URL, routeDetails).then(async (data) =>
                            await displayRoute(JSON.parse(data.current_pred), predictionSpace, {
                                numStops: numStops
                            }, {
                                departureStop: departureStop
                            }, {
                                arrivalStop: arrivalStop
                            }, {
                                departureTime: departureTime
                            }, cost));



                    } else if (journey.travel_mode == "WALKING") {
                        journeyDescription = "<i class='fas fa-walking'></i> " + journey.distance.text + "/" + journey.duration.text + "<br>"
                        journeyDescription += journey.instructions;
                        journeyDescription += divider;
                        route_suggestions.innerHTML += journeyDescription;

                        duration_tracker[i] = Math.round(journey.duration.value / 60);


                    } else if (journey.travel_mode == "TRANSIT" && journey.transit.line.vehicle.type == "BUS" || journey.travel_mode == "TRANSIT" && journey.transit.line.vehicle.type == "INTERCITY_BUS") {
                        if (!journey.transit.line.short_name) {
                            var name = journey.transit.line.name;
                        } else {
                            var name = journey.transit.line.short_name;
                        }
                        journeyDescription = "<i class='fas fa-bus-alt'></i> " + name + "   |   ";
                        journeyDescription += "<i class='fas fa-clock'></i> " + journey.transit.departure_time.text + '    |    ';
                        journeyDescription += journey.transit.num_stops + ' stops/' + journey.duration.text + ' <i class="fas fa-info-circle d-none d-sm-inline" data-toggle="tooltip" title="Prediction generated by Google" data-placement="auto"></i>';
                        time_tracker = new Date(journey.transit.departure_time.value);
                        time_tracker.setSeconds(0);
                        time_tracker.setSeconds(time_tracker.getSeconds() + journey.duration.value);
                        time_tracker.setSeconds(0);
                        latest_departure[i] = time_tracker;




                        if (CalcOn) {
                            journeyDescription += " €?";
                        }
                        journeyDescription += '<br>' + journey.transit.departure_stop.name + ' to ' + journey.transit.arrival_stop.name + "<br>";
                        journeyDescription += "<span id = 'not-db'>* Not a Dublin Bus Route</span>";
                        journeyDescription += divider;
                        route_suggestions.innerHTML += journeyDescription;
                    } else {
                        no_route = true;


                    }
                })
                //Write Total Cost
                if (CalcOn) {
                    route_suggestions.innerHTML += '<p>Total Fare: €' + total_cost.toFixed(2).toString() + '</p>';
                }

                return [latest_departure, duration_tracker];
            }
        } else {
            showWarning("No route could be found. Please try again.");
            return;
        }




        async function displayRoute(journeyPrediction, predictionSpace, numStops, departureStop, arrivalStop, departureTime, cost) {
            var pred;

            if (typeof journeyPrediction == 'string') {
                journeyPrediction = journeyPrediction.slice(1, -1);
                var predictionMins = parseInt(journeyPrediction);

                time_tracker = new Date(departureTime.departureTime);
                time_tracker.setSeconds(0);
                time_tracker.setSeconds(time_tracker.getSeconds() + (predictionMins * 60));
                time_tracker.setSeconds(0);
                latest_departure[predictionSpace] = time_tracker;
                pred = numStops.numStops + ' stops/' + predictionMins.toString() + ' mins <i class="fas fa-info-circle d-none d-sm-inline" data-toggle="tooltip" title="Prediction generated by Bustimate" data-placement="auto"></i>';


            } else {

                time_tracker = new Date(departureTime.departureTime);
                time_tracker.setSeconds(0);
                time_tracker.setSeconds(time_tracker.getSeconds() + journeyPrediction);
                time_tracker.setSeconds(0);
                latest_departure[predictionSpace] = time_tracker;
                var predictionMins = Math.round(journeyPrediction / 60);
                pred = numStops.numStops + ' stops/' + predictionMins.toString() + ' mins <i class="fas fa-info-circle d-none d-sm-inline" data-toggle="tooltip" title="Prediction generated by Google" data-placement="auto"></i>';
            }

            if (cost) {
                pred += ' €' + cost.toFixed(2).toString();
            }
            document.getElementById(predictionSpace).innerHTML += pred;
            document.getElementById(predictionSpace).innerHTML += '<br>' + departureStop.departureStop + ' to ' + arrivalStop.arrivalStop + "<br>" + divider;
        }
    })
}


async function displayEstimatedArrival(latest_departure, duration_tracker, no_route) {
    if (no_route) {
        document.getElementById('route_suggestions').style.visibility = "visible";
    } else {
        var minutes_to_add = 0;
        //get latest bus time_tracker (time of bus departure + time of prediction/duration)

        var key;
        var intKey;
        var latest = 0;

        for (key in latest_departure) {
            intKey = parseInt(key);
            if (intKey > latest) {
                latest = intKey;
            }
        }



        //find durations after latest departures
        Object.keys(duration_tracker).forEach(key => {
            if (key > latest) {
                minutes_to_add += duration_tracker[key]
            }
        });


        //add walking durations after latest bus journey

        latest_departure[latest].setMinutes(latest_departure[latest].getMinutes() + minutes_to_add);
        var min;
        if (latest_departure[latest].getHours() > 11) {
            min = 'pm';
        } else {
            min = 'am';
        }
        if (latest_departure[latest].getSeconds() > 30) {
            var minutes = latest_departure[latest].getMinutes() + 1
        } else {
            minutes = latest_departure[latest].getMinutes()
        }
        //convert hours from 24 hour to 12 hour clock
        var hours = ((latest_departure[latest].getHours() + 11) % 12 + 1);

        route_suggestions.innerHTML += 'Estimated arrival time: ' + hours + ':' + String(minutes).padStart(2, '0') + min;
        document.getElementById('route_suggestions').style.visibility = "visible";

    }
}

function fareCalc(age, payment, journey, time) {
    var ticket

    if (journey.transit.line.short_name.includes("X")) {
        ticket = "Xpresso"
        //Check if 90 or 40E
    } else if (journey.transit.line.short_name === "90" || journey.transit.line.short_name === "40E") {
        ticket = "90_OR_40E"
        //If adult check route length
    } else if (age === "adult") {
        if (journey.transit.num_stops <= 3) {
            ticket = "1-3"
        } else if (journey.transit.num_stops <= 13) {
            ticket = "4-13"
        } else {
            ticket = "13<"
        }

        //If child check if it's school hours
    } else {
        if (schoolHours(time)) {
            ticket = "school"
        } else {
            ticket = "all"
        }
    }

    return fares[age][payment][ticket]
}


function schoolHours(timeString) {
    var date = new Date(timeString);

    switch (date.getDay()) {
        case 0:
            return false;
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
            if (date.getHours() < 19) {
                return true;
            } else {
                return false;
            }
            default:
                if (date.getHours() < 13 || (date.getHours() == 13 && date.getMinutes() < 30)) {
                    return true;
                } else {
                    return false;
                }
    }
}


//Triggered by pressing submit button. Gets route and current time and sends it to getRoute
function submitRoute() {
    no_route = false;
    //get rid of warning
    document.getElementById('warning').style.display = 'none';

    var time = inputTime.value;
    if (!time) {
        time = formatTime(new Date());
    }

    var route = getRouteData();

    if (route) {
        var destinationLatLon = {
            lat: route['destin_lat'],
            lng: route['destin_lon'],
        };
        var originLatLon = {
            lat: route['origin_lat'],
            lng: route['origin_lon'],
        }
        getRoute(originLatLon, destinationLatLon, time);
    }
}

//Swaps active tabs
function changeTabs(tab_id) {
    var active_tab = document.querySelector('.tab-content .active');
    //
    if (active_tab['id'] == tab_id) {
        return
    } else {
        var tab_list = document.querySelectorAll('.tab-content .tab-pane');
        var tab_valid = false;
        tab_list.forEach(function(tab) {
            if (tab_id == tab['id']) {
                tab_valid = true;
            }
        })
        if (tab_valid) {

            var new_tab = document.getElementById(tab_id)
            //Change tabs
            new_tab.classList.add("active");
            new_tab.classList.add("show");
            active_tab.classList.remove("active");
            active_tab.classList.remove("show");

            //Change buttons
            var new_tab_button = document.getElementById(tab_id + "-btn");
            var active_tab_button = document.getElementById(active_tab['id'] + "-btn");

            new_tab_button.classList.add("active");
            active_tab_button.classList.remove("active");

            new_tab_button.setAttribute("aria-selected", "true");
            active_tab_button.setAttribute("aria-selected", "false");


        } else {
            console.log("ERROR: " + tab + " not found");
        }
    }
    checkFavourite();
}

//adds markers to map
function addMarkers(stops_data) {

    infoWindow = new google.maps.InfoWindow();
    //create stop icon
    var busStopIcon = {
        url: '../static/Bus/bus-stop-60.png',
        scaledSize: new google.maps.Size(30, 30),
    };

    for (var i = 0; i < stops_data.length; i++) {
        const marker = new google.maps.Marker({
            icon: busStopIcon,
            position: {
                lat: stops_data[i].fields.stop_lat,
                lng: stops_data[i].fields.stop_lon
            },
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
            {
                height: 50,
                width: 50,
                anchorText: [18, 24],
                textColor: 'white',
                textSize: 12,
                fontWeight: 'bold',
                url: "../static/Bus/marker_clusters/icons8-filled-circle-50.png",
            },
            {
                height: 65,
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

//Swaps Input values
function swapInputs() {
    var active_tab = $('.tab-content .active').attr('id');

    if (active_tab == "locations-tab") {

        //Store Origin Locations
        var temp = inputOrigin.value;
        var tempPlace = autocompleteOrigin.getPlace();

        //Turn off geo-location button
        if (currentLocationOrigin) {
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
function toggleCurrentLocation() {
    if ('geolocation' in navigator) {
        currentLocationOrigin = !currentLocationOrigin;
        inputOrigin.disabled = !inputOrigin.disabled;

        //Aesthetic Changes - placeholder while waiting for geolocation/geocoding to return current location
        if (currentLocationOrigin) {
            $('#currentLocationButton').attr('class', 'btn btn-info');
            inputOrigin.value = "";
            inputOrigin.placeholder = "retrieving current location...";
            var geo_promise = getPosition()
            if (!geo_promise) {
                alert("Browser is unable to use Geolocation services");
            } else {
                geo_promise.then(
                    function(value) {
                        var originLatLon = {
                            lat: value['coords']['latitude'],
                            lng: value['coords']['longitude']
                        }

                        geocoder.geocode({
                            location: originLatLon
                        }, (results, status) => {
                            if (status === "OK") {
                                var location_description = results[0].address_components[0].long_name + ' ' + results[0].address_components[1].long_name;
                                inputOrigin.value = location_description;
                                autocompleteOrigin.set('place', results[0]);
                                checkFavourite();
                            }
                        });
                    },
                    function(error) {
                        console.log(error)
                    }
                )
            }
        } else {
            inputOrigin.value = "";
            inputOrigin.placeholder = "Enter your start point";
            autocompleteOrigin.set('place', null);
            $('#currentLocationButton').attr('class', 'btn btn-secondary');
        }
        //checkFavourite() //Check if current values are a favourite
    } else {
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
function displayInfoWindow(timetable, delays, stop_id) {
    var arrivals = timetable;
    const marker = stopMarkers[stop_id];
    var arrival_time;

    function factorDelay(duration, delay) {
        //takes time as string, converts it to seconds, adds delay, reconverts to string and returns
        let [hours, minutes, seconds] = duration.split(':');
        seconds = (Number(hours) * 60 * 60 + Number(minutes) * 60 + Number(seconds)) + delay;
        var date = new Date(1970, 0, 1);
        date.setSeconds(seconds);
        return date.toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1");
    };



    let infoWindowContent = "<div id='info_window'><h6>" + marker.title.split(":")[1] + "</h6>";

    //if no buses are due at the stop in next 2 hours
    if (arrivals.length == 0) {
        infoWindowContent += "<br>No buses stopping here today.";

        //if less than 3 buses due to stop in next 2 hours
    } else if (arrivals.length <= 3) {
        for (var each in arrivals) {
            infoWindowContent += "<br><i class='fas fa-bus-alt'></i> " + arrivals[each].trip_id.route_id.route_short_name + " (to " + arrivals[each].stop_headsign + ") - ";
            if (delays[each] != 0) {
                arrival_time = factorDelay(arrivals[each].arrival_time, delays[each])
            } else {
                arrival_time = arrivals[each].arrival_time;
            }

            infoWindowContent += arrival_time.slice(0, 5) + "<br>";
        }

    }
    infoWindowContent += "</div>"
    infoWindow.setContent(infoWindowContent);
    infoWindow.open(map, marker);
}


//function to clear stop markers from map
function clearMarkers() {
    for (var i = 0; i < stopMarkersArr.length; i++) {
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
    no_route = false;

    //Delete Warning
    document.getElementById('warning').style.display = 'none';

    //Reset Inputs
    inputOrigin.placeholder = "Enter your start point";
    inputOrigin.value = "";
    inputDestination.value = "";
    infoWindow.close();
    inputFirstStop.value = "";
    inputLastStop.value = "";
    inputTime.value = "";
    //reset map center and zoom

    map.setZoom(14);
    map.setCenter({
        lat: 53.350140,
        lng: -6.266155
    });
    showMarkers();


    //Reset autocompletes
    autocompleteOrigin.set('place', null);
    autocompleteDestin.set('place', null);
    if (currentLocationOrigin) {
        toggleCurrentLocation();
    }

    //reset fare calculator
    document.getElementById('fare_suggestions').style.display = "none";
    $('#fareCalculator').attr('class', 'btn btn-secondary');
}


function displayFareButtons() {
    var fare_suggestions = document.getElementById('fare_suggestions');
    if (fare_suggestions.style.display == "none") {
        $('#fareCalculator').attr('class', 'btn btn-info');
        fare_suggestions.style.display = "block";
    } else {
        fare_suggestions.style.display = "none";
        $('#fareCalculator').attr('class', 'btn btn-secondary');
    }
}

function toggleFavourite() {
    //Remove From Favourites
    if (current_user != null) {
        if (isFavourite) {
            var data = {
                id: currentFavourite
            }
            var promise = postData(remove_favourite_URL, data);

            promise.then(
                function(value) {
                    if (value['success'] == true) {
                        for (var i = 0; i < favourites.length; i++) {
                            if (favourites[i].id == currentFavourite) {
                                favourites.splice(i, 1);
                                break;
                            }
                        }
                        checkFavourite()
                    }
                }
            )
            //Add to favourites
        } else {
            //remove warning
            document.getElementById('warning').style.display = 'none';
            var promise = postData(create_favourite_URL, getRouteData());
            if (typeof promise.then === "function") {
                promise.then(
                    function(value) {
                        if (value['success'] == true) {
                            favourites.push(value['favourite'])
                            checkFavourite()
                        }
                    }
                )
            }
        }
    }
};



//Checks if the current input is a favourite and alters DOM elements accordingly
var checkFavourite = function(evt) {
    if (current_user != null) {
        var currentRoute = getRouteData(false);
        var match = false;
        var co_ords = {
            origin_lat: currentRoute.origin_lat,
            origin_lon: currentRoute.origin_lon,
            destin_lat: currentRoute.destin_lat,
            destin_lon: currentRoute.destin_lon
        }
        for (var i = 0; i < favourites.length; i++) {
            var fav_co_ords = {
                origin_lat: favourites[i].origin_lat,
                origin_lon: favourites[i].origin_lon,
                destin_lat: favourites[i].destin_lat,
                destin_lon: favourites[i].destin_lon
            }
            if (JSON.stringify(co_ords) === JSON.stringify(fav_co_ords)) {
                match = true;
                currentFavourite = favourites[i].id;
                isFavourite = true;
                $('#favouriteButton').attr('class', 'btn btn-info');
                break;
            }
        }
        if (!match) {
            isFavourite = false;
            $('#favouriteButton').attr('class', 'btn btn-secondary');
        }
    }
}
//set minimum date field to current date so user can't plan journeys in the past
document.getElementById("time-dropdown").setAttribute("min", formatTime(new Date()));

//Check if current values are on the favourites list, triggered on changes to bus inputs
inputFirstStop.addEventListener('input', checkFavourite, false);
inputLastStop.addEventListener('input', checkFavourite, false);

//Listeners that trigger on input change
$('#locations-tab-btn').on('shown.bs.tab', function() {
    checkFavourite();
})
$('#stops-tab-btn').on('shown.bs.tab', function() {
    checkFavourite();
})