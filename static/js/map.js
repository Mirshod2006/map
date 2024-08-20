$(document).ready(function(){

var map = L.map("map", {center:[{{lat}}, {{long}}], zoom:{{zoom}}});
L.tileLayer(
"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
{attribution: '&copy; <a href="http://' +
'www.openstreetmap.org/copyright">OpenStreetMap</a>'}
).addTo(map);

});
