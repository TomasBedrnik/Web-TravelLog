function create_map(polylines)
{
    var map = L.map('map').setView([49.817, 15.478], 8);
    L.tileLayer(
      'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18,
      }).addTo(map);

    var encodedRoutes = polylines;

    for (let encoded of encodedRoutes) {
    var coordinates = L.Polyline.fromEncoded(encoded).getLatLngs();

    L.polyline(
        coordinates,
        {
            color: 'blue',
            weight: 2,
            opacity: .7,
            lineJoin: 'round'
        }
    ).addTo(map);
    }
}