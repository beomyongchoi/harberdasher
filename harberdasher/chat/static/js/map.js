// map
var map = new naver.maps.Map('map', {
    center: new naver.maps.LatLng(37.566535, 126.9779692),
    zoom: 10,
    mapTypeId: 'normal',
    scaleControl: false,
    logoControl: false,
    mapDataControl: false,
    zoomControl: false,
});

// check overlap marker
var recognizer = new MarkerOverlappingRecognizer({
    highlightRect: false,
    tolerance: 10
});

recognizer.setMap(map);

//get current location
function onSuccessGeolocation(position) {
    var location = new naver.maps.LatLng(position.coords.latitude,
        position.coords.longitude);

    map.setCenter(location);
}

function onErrorGeolocation() {
    alert("Geolocation Permission not Allowed")
}

$(document).ready(function() {
    updateMarkers(map, markers);

    // if (navigator.geolocation && window.location.protocol == "https:")
    //     navigator.geolocation.getCurrentPosition(onSuccessGeolocation, onErrorGeolocation);

    $("#current").click(function() {
        if (navigator.geolocation)
            navigator.geolocation.getCurrentPosition(onSuccessGeolocation, onErrorGeolocation);
    });

});

function highlightMarker(marker) {
    var icon = marker.getIcon();

    if (icon.url !== STARBUCKS_HIGHLIGHT_ICON_URL) {
        icon.url = STARBUCKS_HIGHLIGHT_ICON_URL;
        marker.setIcon(icon);
    }

    marker.setZIndex(1000);
}

function unhighlightMarker(marker) {
    var icon = marker.getIcon();

    if (icon.url === STARBUCKS_HIGHLIGHT_ICON_URL) {
        icon.url = STARBUCKS_ICON_URL;
        marker.setIcon(icon);
    }

    marker.setZIndex(100);
}

var markers = [];

for (var i = 0, starbucks; starbucks = starbucksList[i]; i++) {
    var position = new naver.maps.Point(
        starbucks.mapx,
        starbucks.mapy
    );

    var marker = new naver.maps.Marker({
        map: null,
        position: naver.maps.TransCoord.fromTM128ToLatLng(position),
        name: starbucks.name,
        id: starbucks.id,
        icon: {
            url: STARBUCKS_ICON_URL,
            size: new naver.maps.Size(40, 40),
            origin: new naver.maps.Point(0, 0),
            anchor: new naver.maps.Point(20, 20)
        },
        zIndex: 100
    });

    // marker.id = starbucks.id;

    marker.addListener('mouseover', function(e) {
        highlightMarker(e.overlay);
    });

    marker.addListener('mouseout', function(e) {
        unhighlightMarker(e.overlay);
    });

    marker.addListener('click', function(e) {
        var m = e.overlay;

        if (!currentUser){
            //login required
            console.log("please login");
            window.location = URL + 'users/login'
            return
        } else if ($(".chat-body").attr("id") == m.id && $("#chatbox").css("display") != "none") {
            //same room clicked
            console.log("nothing");
        } else if ($(".chat-body[id]").length) {
            socket.send(JSON.stringify({
                "command": "leave",
                "room": $(".chat-body").attr("id")
            }));
            socket.send(JSON.stringify({
                "command": "join",
                "room": m.id
            }));
        } else {
            // Join room
            socket.send(JSON.stringify({
                "command": "join",
                "room": m.id
            }));
        }

        if($("#noRoomSelected").css("display") != "none") {
            $("#floatWindow").css({
                "width": "500",
                "height": "700",
            });
            $("#noRoomSelected").css("display", "none");
        }

        $("#roomList").css("display", "none");
        $("#chatbox").css("display", "block");

        $(".list-table").children().remove();

        $("#floatWindow").fadeIn();
    });

    recognizer.add(marker);

    markers.push(marker);
};

naver.maps.Event.addListener(map, 'idle', function() {
    updateMarkers(map, markers);
});

var searchHTML = '<input id="pac-input" class="controls" type="text" placeholder="Enter a location">';
var searchControl = new naver.maps.CustomControl(searchHTML, {
    position: naver.maps.Position.TOP_RIGHT
});
searchControl.setMap(map);

var currentLocationHTML = '<button id="current"><i class="fa fa-location-arrow fa-2x" style="line-height: 35px;" aria-hidden="true"></i></button>';
var currentLocationControl = new naver.maps.CustomControl(currentLocationHTML, {
    position: naver.maps.Position.BOTTOM_RIGHT
});
currentLocationControl.setMap(map);

var input = /** @type {!HTMLInputElement} */ (
    document.getElementById('pac-input'));
var options = {
    bounds: new google.maps.LatLngBounds(
        new google.maps.LatLng(33, 125),
        new google.maps.LatLng(38, 131)
    )
};
var searchBox = new google.maps.places.SearchBox(input, options);

google.maps.event.addListener(searchBox, 'places_changed', function() {
    var place = searchBox.getPlaces()[0];
    if (!place.geometry) return;

    if (place.geometry.viewport) {
        var location = new naver.maps.LatLngBounds(
            new naver.maps.LatLng(place.geometry.viewport.getSouthWest().lat(),
                place.geometry.viewport.getSouthWest().lng()),
            new naver.maps.LatLng(place.geometry.viewport.getNorthEast().lat(),
                place.geometry.viewport.getNorthEast().lng()));
        map.fitBounds(location); // 좌표 경계 이동
    } else {
        var location = new naver.maps.LatLng(place.geometry.location.lat(),
            place.geometry.location.lng());
        map.setCenter(location);
        map.setZoom(10);
    }
});

function updateMarkers(map, markers) {
    var bounds = map.getBounds();
    var marker, position;

    for (var i = 0; i < markers.length; i++) {

        marker = markers[i]
        position = marker.getPosition();

        if (bounds.hasLatLng(position)) {
            showMarker(map, marker);
        } else {
            hideMarker(map, marker);
        }
    }
}

function showMarker(map, marker) {

    if (marker.setMap()) return;
    marker.setMap(map);
}

function hideMarker(map, marker) {

    if (!marker.setMap()) return;
    marker.setMap(null);
}

var overlapCoverMarker = null;

naver.maps.Event.addListener(recognizer, 'overlap', function(list) {
    if (overlapCoverMarker) {
        unhighlightMarker(overlapCoverMarker);
    }

    overlapCoverMarker = list[0].marker;

    naver.maps.Event.once(overlapCoverMarker, 'mouseout', function() {
        highlightMarker(overlapCoverMarker);
    });
});

naver.maps.Event.addListener(recognizer, 'clickItem', function(e) {
    recognizer.hide();

    if (overlapCoverMarker) {
        unhighlightMarker(overlapCoverMarker);

        overlapCoverMarker = null;
    }
});
