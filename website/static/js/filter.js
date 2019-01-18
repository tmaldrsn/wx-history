$('#stationFilter').keyup(function () {
  let value = this.value.toUpperCase();
  $('#stations').find('tr').each(function (index) {
    if (!index) return;
    let id = $(this).find('td').first().text();
    $(this).toggle(id.indexOf(value) !== -1);
  });
});