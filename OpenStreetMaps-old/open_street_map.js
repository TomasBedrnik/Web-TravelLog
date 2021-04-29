function create_map(polylines)
{
    var map = L.map('map').setView([49.817, 15.478], 8);
    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18,
      }).addTo(map);

    var encodedRoutes = polylines;
    var colours = ["#e41a1c", "#377eb8", "#5aaf00", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"];
    var i = 0
    for (let encoded of encodedRoutes) {
        var coordinates = L.Polyline.fromEncoded(encoded).getLatLngs();

        L.polyline(
            coordinates,
            {
                color: colours[i],
                weight: 3,
                opacity: 1,
                lineJoin: 'round'
            }
        ).addTo(map);
        i++
        if(i >= 8) {
            i = 0
        }
    }
}