$(function () {
  $.getJSON('./_get_extremes', {},
    function (data) {
      $("#natHigh")[0].innerHTML = `${data.high} <a href="/stations/${data.high_station}">(${data.high_station})</a>`;
      $("#natLow")[0].innerHTML = `${data.low} <a href="/stations/${data.low_station}">(${data.low_station})</a>`;
    }
  );
});