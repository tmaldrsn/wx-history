$(function () {
  $('#toggleGraph').bind('click', function () {
    $.getJSON('./_get_observations', {}, function (data) {
      if ($('#currentObsGraph')[0].style.display == "block") {
        $('#currentObsGraph')[0].style.display = "none";
        $('#toggleGraph').text("Show Graph");
      } else {
        $('#currentObsGraph')[0].style.display = "block";
        $('#toggleGraph').text("Hide Graph");
      }

      let datetimes = data.datetimes;
      let temps = data.temps;

      let trace = {
        x: datetimes,
        y: temps,
        type: 'line'
      };

      Plotly.newPlot('currentObsGraph', [trace]);
    });
    return false;
  });
});