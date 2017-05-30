// script to auto complete location

function initMap() {

var defaultBounds = new google.maps.LatLngBounds(
new google.maps.LatLng(-90, 91), new google.maps.LatLng(-180, 80));
var options = {
types: ['(cities)'],
bounds: defaultBounds
};
var input = document.getElementById('google_city_search');

var autocomplete = new google.maps.places.Autocomplete(input, options);
}



