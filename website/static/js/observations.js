$(function () {
  $('#toggleTable').bind('click', function () {
    console.log('button clicked')
    $.getJSON('/stations/KTOL/_get_observations', {}, function (data) {
      if ($('#obsList').text() != '') {
        $('#obsList').text('');
      } else {
        //let datetimes = JSON.parse(data.datetimes);
        //let temps = JSON.parse(data.temps);
        $('#obsList').text(data.temps);
      }
    });
    return false;
  });
});