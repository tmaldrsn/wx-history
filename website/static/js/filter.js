$('#querySubmit').click(function () {
  let id, state, name, minLat, maxLat, minLon, maxLon;
  id = $('#idFilter').val().toUpperCase();
  state = $('#stateFilter').val().toUpperCase();
  name = $('#nameFilter').val().toUpperCase();
  minLat = Number($('#minLatFilter').val());
  maxLat = Number($('#maxLatFilter').val());
  minLon = Number($('#minLonFilter').val());
  maxLon = Number($('#maxLonFilter').val());
  if (minLat == 0) minLat = -90
  if (maxLat == 0) maxLat = 90
  if (minLon == 0) minLon = -180;
  if (maxLon == 0) maxLon = 180;

  $('#stations').find('tr').each(function (index) {
    if (!index) return;
    let elId = $(this).find('td:nth-child(1)').text().toUpperCase();
    let elState = $(this).find('td:nth-child(2)').text().toUpperCase();
    let elName = $(this).find('td:nth-child(3)').text().toUpperCase();
    let elLat = Number($(this).find('td:nth-child(4)').text());
    let elLon = Number($(this).find('td:nth-child(5)').text());

    let nameConditional = (elId.indexOf(id) !== -1) && (elState.indexOf(state) !== -1) && (elName.indexOf(name) !== -1);
    let coordConditional = (minLat < elLat) && (elLat < maxLat) && (minLon < elLon) && (elLon < maxLon);
    let fullConditional = nameConditional && coordConditional;
    $(this).toggle(fullConditional);
  });

  $('#numResults').text($('#stations').find('tr:visible').length - 1);
});