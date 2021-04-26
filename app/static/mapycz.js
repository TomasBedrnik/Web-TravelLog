let geometryIds;
let just_selected = false;
/* Add "activity_slected" CSS class to activity container when clicked to activity route */
let geometry_click_listener = function (e) {
    just_selected = false;
    if (e.target.constructor.NAME === "SMap.Geometry") {
        let index = geometryIds.indexOf(e.target.getId());
        let activity = document.getElementById("activity_" + index);
        if (activity.classList.contains("activity_selected")) {
            activity.classList.remove("activity_selected");
        } else {
            activity.classList.add("activity_selected");
            just_selected = true;
        }
    }
}
let all_click_listener = function (e) {
    if (just_selected === false) {
        let activities = document.getElementsByClassName("activity");
        for (let i = 0; i < activities.length; i++) {
            if (activities[i].classList.contains("activity_selected")) {
                activities[i].classList.remove("activity_selected");
            }
        }
    }
    just_selected = false;
}

function add_mapycz(polylines) {
    /* Create Map */
    let center = SMap.Coords.fromWGS84(15.478, 49.817);
    let m = new SMap(JAK.gel("map"), center, 8);
    m.addDefaultLayer(SMap.DEF_TURIST).enable();
    m.addControl(new SMap.Control.Sync({bottomSpace: 0})); /* Aby mapa reagovala na změnu velikosti průhledu */
    m.addDefaultControls();

    var signals = m.getSignals();
    signals.addListener(window, "geometry-click", geometry_click_listener);
    signals.addListener(window, "map-click", all_click_listener);

    let layer = new SMap.Layer.Geometry();
    m.addLayer(layer);
    layer.enable();

    let colours = ["#e41a1c", "#377eb8", "#5aaf00", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"];
    let array_coordinates = new Array(polylines.length);
    geometryIds = new Array(polylines.length);

    for (let y = polylines.length - 1; y >= 0; y--) {
        let coordinates = L.Polyline.fromEncoded(polylines[y]).getLatLngs();
        array_coordinates[y] = [];
        for (let coord of coordinates) {
            array_coordinates[y].push(SMap.Coords.fromWGS84(coord["lng"], coord["lat"]))
        }

        /* "title", "minDist", "color", "opacity", "width", "style", "outlineColor", "outlineOpacity", "outlineWidth", "outlineStyle" */
        let options = {
            color: colours[y % 8],
            width: 3,
            opacity: 1,
            outlineColor: 'black',
            outlineWidth: 1
        };
        let polyline = new SMap.Geometry(SMap.GEOMETRY_POLYLINE, null, array_coordinates[y], options);
        geometryIds[y] = polyline.getId();
        layer.addGeometry(polyline);
    }

    /* Listeners for Activity menu */
    let activities = document.getElementsByClassName("activity");
    let polyline;
    for (let i = 0; i < activities.length; i++) {
        /* Highlight activity on mouse hover */
        activities[i].addEventListener("mouseenter", function (event) {
            let options = {
                color: colours[i % 8],
                width: 10,
                opacity: 1,
                outlineColor: 'black',
                outlineWidth: 1
            };
            polyline = new SMap.Geometry(SMap.GEOMETRY_POLYLINE, null, array_coordinates[i], options);
            layer.addGeometry(polyline);
        }, false);
        activities[i].addEventListener("mouseleave", function (event) {
            layer.removeGeometry(polyline);
        }, false);

        /* Zoom to selected activity */
        activities[i].getElementsByClassName("zoom")[0]
            .addEventListener("click", function (event) {
                m.setCenter(array_coordinates[i][0], true);
                m.setZoom(11, array_coordinates[i][0], true);
            }, false);
    }
}