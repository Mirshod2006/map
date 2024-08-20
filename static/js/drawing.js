$(document).ready(function(){
var d0='';
    d1='';
    d2='';
    d3='';
    d4='';
d0=$('#d01');
d1=$('#d02');
d2=$('#d03');
d3=$('#d04');

$("#d0").hide();
$("#d01").remove();
$("#d02").remove();
$("#d03").remove();
$("#d04").remove();

var drawnItems = L.featureGroup().addTo(map);
new L.Control.Draw({
draw : {
marker: true,
polygon : false,
circle :false,        // Circles disabled
circlemarker : false,// Circle markers disabled
rectangle : false,     // Rectangles disabled
polyline : true,


},
edit:{
featureGroup: drawnItems
}
}).addTo(map);

function createFormPopup() {
var popupContent =
'<form style="width:160px;">' +
'<div class="form-group">'+
'<label class="col-sm-12 control-label"> Obekt turini tanlang:</label>'+
'<select class="form-control" type="text" id="input_desc">'+
'<option>Telekomunikasiya obekti</option>'+
'<option>Ko'+"'"+'p qavatli turar-joy obekti</option>'+
'<option>Noturar-joy obekti</option>'+
'<option>Xususiy turar-joy obekti</option>'+
'</select> <br>' +
'<input type="button" class="btn form-control btn-primary" id="submit" value="Tanlash"</input>'+
' </div>'+
'</form>';
///$.get(" ", {lat: map.getCenter().lat, long: map.getCenter().lng, zoom:map.getZoom()});

drawnItems.bindPopup(popupContent).openPopup();

}


map.on("draw:created", function(e) {
    var type = e.layerType,
        layer = e.layer;
    e.layer.addTo(drawnItems);
    if (type === 'marker'){
     createFormPopup();    }
    drawnItems.eachLayer(function(layer) {
    var geojson = JSON.stringify(layer.toGeoJSON().geometry);
    if (type === "polyline") {
     $("#linya").val(geojson)    };
    console.log(geojson);

  //  console.log(geojson);
});
});
$("body").on("click", "#submit", setData);
$("#submit").on("click", setData);
function setData() {
// Get user name and description
var enteredUsername = $("#input_name").val();
var enteredDescription = $("#input_desc").val();

drawnItems.eachLayer(function(layer) {
var drawing = JSON.stringify(layer.toGeoJSON().geometry);
var drawing0 = JSON.stringify(layer.toGeoJSON().geometry.coordinates);
//var drawtype = JSON.stringify(layer.toGeoJSON().geometry.type);



if (enteredDescription=='Telekomunikasiya obekti') {
$('#d0').empty();
$('#d0').append(d0);
$("#d0").show(1000);
};
if (enteredDescription=="Ko'p qavatli turar-joy obekti") {
$('#d0').empty();
$("#d0").show(1000);
$('#d0').append(d1);


};
if (enteredDescription=="Noturar-joy obekti") {
$('#d0').empty();
$("#d0").show(1000);
$('#d0').append(d2);

};
if (enteredDescription=="Xususiy turar-joy obekti") {
$('#d0').empty();
$("#d0").show(1000);
$('#d0').append(d3);
};

$("#lat").val(map.getCenter().lat);
$("#lon").val(map.getCenter().lng);
$("#zoom").val(map.getZoom());

//$("#koor").val(drawing1);

if (layer.toGeoJSON().geometry.type === "Point" ) {
$("#koor").val(drawing);
}else{
$("#linya").val(drawing);
};

});
// Clear drawn items layer
drawnItems.closePopup();
}


map.on("draw:editstart", function(e) {
drawnItems.closePopup();
});
map.on("draw:deletestart", function(e) {
drawnItems.closePopup();
});
map.on("draw:editstop", function(e) {
drawnItems.openPopup();
});
map.on("draw:deletestop", function(e) {
if(drawnItems.getLayers().length > 0) {
drawnItems.openPopup();
}
});

///$.get(" ", {lat: map.getCenter().lat, long: map.getCenter().lng, zoom:map.getZoom()});
///map.setView([map.getCenter().lat, map.getCenter().lng], map.getZoom());
///};
});

$("body").on("click", "#hided0", hideData);
$("#hided0").on("click", hideData);
function hideData(){
        $('#d0').hide(500);};

$(document).bind('keyup change', function () {
$('#iptvn').val($('#iptv').val()*4);
$('#vpnn').val($('#vpn').val()*10);
$('#internetn').val($('#internet').val()*4);
$('#telefonn').val($('#telefon').val()*1);
$('#servern').val($('#server').val()*100);
$('#videon').val($('#video').val()*4);
$('#umumiyn1').val(parseInt($('#internetn').val())+parseInt($('#vpnn').val())+parseInt($('#iptvn').val())+parseInt($('#telefonn').val()));
$('#umumiyn2').val(parseInt($('#internetn').val())+parseInt($('#vpnn').val())+parseInt($('#iptvn').val())+parseInt($('#telefonn').val())+parseInt($('#videon').val())+parseInt($('#servern').val()));
$('#umumiyn3').val(parseInt($('#internetn').val())+parseInt($('#vpnn').val())+parseInt($('#iptvn').val())+parseInt($('#telefonn').val())+parseInt($('#videon').val())+parseInt($('#servern').val()));
});



 function onZoomend() {
    var currentZoom = map.getZoom();
    $("#nom21").val(currentZoom);
	 $("#nom2").val(map.getCenter().lat);
	/// $("#d2").hide();
	 ///$.set("/admin/", {'lat': map.getCenter().lat, 'long': map.getCenter().lng, 'zoom':map.getZoom()});
 };

map.on('zoomend', onZoomend);
