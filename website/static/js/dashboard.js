function showCurrent() {
  console.log('button clicked')
  let currentFrame = document.getElementById("currentObsGraph");
  if (currentFrame.style.display == "none") {
    currentFrame.style.display = "block";
  } else if (currentFrame.style.display == "") {
    currentFrame.style.display = "block";
  } else {
    currentFrame.style.display = "none";
  }
}