# Dublin_Bus
A Dublin Bus Web Application (optimised for mobile devices) capable of predicting accurate journey times.  

This repository is in part fulfilment of the degree of MSc. in Computer Science (Conversion) for module COMP47360.

Group Name: Group 6 (the 3 amigos)

Group Members:
Rachel Courtney 
Amanda Hegarty 
Andrew McClean

URL: https://bustimate.com/ OR https://137.43.49.41 

Github Repository: https://github.com/rachelcourtney/Dublin_Bus.git 

## Project Specification:
Bus companies produce schedules which contain generic travel times. For example, in the Dublin Bus Schedule,  the  estimated  travel  time  from  Dun  Laoghaire  to  the  Phoenix  Park  is  61 minutes (http://dublinbus.ie/Your-Journey1/Timetables/All-Timetables/46a-1/).  Of  course,  there  are  many variables  which  determine  how  long  the  actual  journey  will  take.  Traffic  conditions  which  are affected  by  the  time  of  day, the day of  the  week, the month of  the year  and  the  weather  play  an important role in determining how long the journey will take. These factors along with the dynamic nature of the events on the road network make it difficult to efficiently plan trips on public transport modes which interact with other traffic.

## The Solution:
This project involves analysing historic Dublin Bus data and weather data in order to create dynamic travel  time  estimates.  Based  on  data analysis of  historic  Dublin  Bus data,  a  system  which  when presented  with  any  bus  route,  departure  time, the day of  the  week,  current  weather  condition, produces an accurate estimate of travel time for the complete route and sections of the route. Users  should  be  able  to  interact  with  the  system  via  a  web-based  interface  which is optimised  for mobile devices. When presented with any bus route, an origin stop and a destination stop, a time, a day  of  the  week,  current  weather,  the system  should  produce and  display  via  the  interface  an accurate estimate of travel time for the selected journey.

## Application Architecture:
Bustimate is a dynamic web application hosted by an apache server running on a Linux virtual machine provided by UCD for this purpose. The backend of the application was created using the python-based web framework, Django. The webpages that makeup the frontend of the application were made using the old reliables of HTML, Javascript, and CSS supplemented by the Bootstrap CSS framework and jQuery. 

The application makes use of several APIs to obtain real time information. Cron tabs are used to periodically activate scrapers which collect hourly weather data from the OpenWeather API. A similar system is used to call the General Transit Feed Specification-Realtime (GTFS-R) API every 5 minutes for real time data on bus arrivals. The Google Maps API is used directly by the applications frontend to provide services such as a map, geolocation and route planning.

A MySQL database, hosted on the same virtual machine is used to store Django models used by the back-end as well as data obtained from the aforementioned APIs. Journey time predictions are provided to the application using several XGBoost models correlating to each Dublin Bus Route. Weather data and other features are sent to the predictive models by the backend and journey time estimates are returned.

![tech_stack](https://user-images.githubusercontent.com/67108526/130132134-1e20eba6-8c2f-4419-9ef6-8033cea5089c.png)

## Demonstration of Application:

### Index Page
The index page features a journey planner that allows users to plan their Dublin Bus journey, including estimated travel time and arrival time as well as a fare calculator.

![index](https://user-images.githubusercontent.com/67108526/130132743-2f58ec97-5516-4773-8c90-4d785b12d8e0.gif)


### Login and Favourites Features
Users can create accounts with Bustimate and save their frequent routes.



