function add_mapycz(polylines){
var center = SMap.Coords.fromWGS84(14.41790, 50.12655);
var m = new SMap(JAK.gel("map"), center, 8);
m.addDefaultLayer(SMap.DEF_TURIST).enable();
m.addControl(new SMap.Control.Sync({bottomSpace:0})); /* Aby mapa reagovala na změnu velikosti průhledu */
m.addDefaultControls();


let layer = new SMap.Layer.Geometry();
m.addLayer(layer);
layer.enable();

    let encodedRoutes = polylines;
    let colours = ["#e41a1c", "#377eb8", "#5aaf00", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"];
    let i = 0
    for (let encoded of encodedRoutes) {
        let coordinates = L.Polyline.fromEncoded(encoded).getLatLngs();
        let testArray  = [];
        for (let coord of coordinates) {
            testArray.push(SMap.Coords.fromWGS84(coord["lng"], coord["lat"]))
        }
        let options1 = {
            color: colours[i],
            width: 5
        };
        let polyline = new SMap.Geometry(SMap.GEOMETRY_POLYLINE, null, testArray, options1);
        layer.addGeometry(polyline);

        i++
        if(i >= 8) {
            i = 0
        }
    }


}