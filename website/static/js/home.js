$(function () {
  $.getJSON('./api/get_extremes', {},
    function (data) {
      $("#natHigh")[0].innerHTML = `${data.high} <a href="/stations/${data.high_station}">(${data.high_station})</a>`;
      $("#natLow")[0].innerHTML = `${data.low} <a href="/stations/${data.low_station}">(${data.low_station})</a>`;
    }
  );
});

/* Set the width of the side navigation to 250px */
function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
  document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
}

/* Set the width of the side navigation to 0 */
function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
  document.body.style.backgroundColor = "white";
}

function toggleFilterOptions() {
  let filterElement = document.getElementById("filters")
  if (filterElement.style.display == "") filterElement.style.display = "block";
  else if (filterElement.style.display == "block") filterElement.style.display = "";
}

function redirectToStationPage(zipcode) {
  if (!isZipCode(zipcode)) {
    return;
  }

  $.getJSON('./api/search_zipcode?zip=' + zipcode, {}, function (data) {
    window.location.href = './stations/' + data[0];
  });
}

function isZipCode(station) {
  let zipCodeRegex = /^[0-9]{5}$/;
  if (station.search(zipCodeRegex) == 0) {
    return true;
  } else {
    return false;
  }
}