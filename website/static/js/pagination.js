for (let pg of document.getElementsByClassName("pageLink")) {
  let pageNum = Number(pg.textContent);
  let nums = getPaginationNumbers(pageNum);
  pg.addEventListener("click", () => {
    renderPagination(nums);
  });
}

function getPaginationNumbers(pageNum) {
  if (pageNum > 3) {
    return [
      pageNum - 2,
      pageNum - 1,
      pageNum,
      pageNum + 1,
      pageNum + 2,
      pageNum
    ];
  } else {
    return [1, 2, 3, 4, 5, pageNum];
  }
}

function renderPagination(pageNums) {
  let pagNav = document.getElementsByClassName("pagination")[0];

  // Remove all pagination nav children to do a reset
  while (pagNav.firstChild) {
    pagNav.firstChild.remove();
  }

  let activePage = pageNums[5];
  if (activePage == 1) {
    pagNav.innerHTML =
      `
          <a id="prevPage" href="#">&laquo;</a>
          <a class="pageLink" href="./` + pageNums[0] + `" id="activePage">` +
      pageNums[0] +
      `</a>
          <a class="pageLink" href="./` + pageNums[1] + `">` +
      pageNums[1] +
      `</a>
          <a class="pageLink" href="./` + pageNums[2] + `">` +
      pageNums[2] +
      `</a>
          <a class="pageLink" href="./` + pageNums[3] + `">` +
      pageNums[3] +
      `</a>
          <a class="pageLink" href="./` + pageNums[4] + `">` +
      pageNums[4] +
      `</a>
          <a id="nextPage" href="#">&raquo;</a>
      `;
  } else if (activePage == 2) {
    pagNav.innerHTML =
      `
          <a id="prevPage" href="#">&laquo;</a>
          <a class="pageLink" href="./` + pageNums[0] + `">` +
      pageNums[0] +
      `</a>
          <a class="pageLink" href="./` + pageNums[1] + `">` +
      pageNums[1] +
      `</a>
          <a class="pageLink" href="./` + pageNums[2] + `" id="activePage">` +
      pageNums[2] +
      `</a>
          <a class="pageLink" href="./` + pageNums[3] + `">` +
      pageNums[3] +
      `</a>
          <a class="pageLink" href="./` + pageNums[4] + `">` +
      pageNums[4] +
      `</a>
          <a id="nextPage" href="#">&raquo;</a>
      `;
  } else {
    pagNav.innerHTML =
      `
          <a id="prevPage" href="#">&laquo;</a>
          <a class="pageLink" href="./` + pageNums[0] + `">` +
      pageNums[0] +
      `</a>
          <a class="pageLink" href="./` + pageNums[1] + `">` +
      pageNums[1] +
      `</a>
          <a class="pageLink" href="./` + pageNums[2] + `" id="activePage">` +
      pageNums[2] +
      `</a>
          <a class="pageLink" href="./` + pageNums[3] + `">` +
      pageNums[3] +
      `</a>
          <a class="pageLink" href="./` + pageNums[4] + `">` +
      pageNums[4] +
      `</a>
          <a id="nextPage" href="#">&raquo;</a>
      `;
  }

  for (let pg of document.getElementsByClassName("pageLink")) {
    let pageNum = Number(pg.textContent);
    let nums = getPaginationNumbers(pageNum);
    pg.addEventListener("click", () => {
      renderPagination(nums);
    });
  }
}