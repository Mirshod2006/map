 var theMarker = {};

 map.on('click',function(e){
    lat = e.latlng.lat;
    lon = e.latlng.lng;

        if (theMarker != undefined) {
              map.removeLayer(theMarker);
        };
    //Add a marker to show where you clicked.
     theMarker = L.marker([lat,lon]).addTo(map);
     koor0 = JSON.stringify(theMarker.toGeoJSON().geometry.coordinates[0])
     koor1 = JSON.stringify(theMarker.toGeoJSON().geometry.coordinates[1])
     $("#koor0").val(koor0);
     $("#koor1").val(koor1);
     

     var csrfToken = getCookie('csrftoken'); // получение CSRF-токена из куки
     var data = {
        koor0: koor0, // здесь указывается значение вашей переменной JavaScript
        koor1: koor1,
      };
  
    $.ajax({
      url: '/your_view_name/',
      type: 'POST',
      headers: { 'X-CSRFToken': csrfToken }, // передача CSRF-токена в заголовках запроса
      data: data,
      success: function(response) {
        console.log(response);
      },
      error: function(xhr, status, error) {
        console.log(error);
      }
    });
  
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  

});



L_NO_TOUCH = false;
L_DISABLE_3D = false;
var map = L.map("map", {
  center: [41.0, 64.0],
  crs: L.CRS.EPSG3857,
  zoom: 7,
  zoomControl: false,
  preferCanvas: true,
});

var tile_layer_4fa23d6762e421b77b21558ed31c4920 = L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  {
    attribution:
      'Data by &copy;<a target="_blank" href="http://openstreetmap.org">OpenStreetMap</a>, under <a target="_blank" href="http://www.openstreetmap.org/copyright">ODbL</a>.',
    detectRetina: false,
    maxNativeZoom: 18,
    maxZoom: 18,
    minZoom: 6,
    noWrap: false,
    opacity: 1,
    subdomains: "abc",
    tms: false,
  }
).addTo(map);

var myIcon = L.icon({
  iconUrl: "../static/images/icon-marker.png", // Путь к изображению иконки
  iconSize: [38, 38], // Размер иконки
  iconAnchor: [19, 38], // Точка якоря иконки
  popupAnchor: [0, -38], // Точка якоря всплывающего окна иконки
});

var places = [];

{% for meteo in meteos %}
places.push({ name: "{{ meteo.meteoName }}", coordinates: [{{ meteo.lon }}, {{ meteo.lat }}] });
{% endfor %}

var yourGeoJSONData = {
  type: "FeatureCollection",
  features: [],
};

places.forEach(function (place) {
  var feature = {
    type: "Feature",
    properties: {
      name: place.name,
    },
    geometry: {
      type: "Point",
      coordinates: place.coordinates,
    },
  };

  yourGeoJSONData.features.push(feature);
});

// Создаем экземпляр поисковой системы
var markersLayer = L.geoJSON(yourGeoJSONData, {
  pointToLayer: function (feature, latlng) {
    return L.marker(latlng, {
      title: feature.properties.name,
      icon: myIcon,
    }).on("click", function (e) {
      $("#search0").val(feature.properties.name);
    });
  },
});

var markerCluster = L.markerClusterGroup();
markerCluster.addLayer(markersLayer);
map.addLayer(markerCluster);

var searchControl = new L.Control.Search({
  layer: markerCluster,
  propertyName: "name",
  marker: false,
  moveToLocation: function (latlng, title, map) {
    map.setView(latlng, 12);
  },
});

map.addControl(searchControl);

// Обработчик события нажатия кнопки "Search"
$(".search-button").click(function (event) {
  event.preventDefault();

  var searchText = $("#search0").val();

  searchControl.search(searchText);
});
