/* Project specific Javascript goes here. */
document.addEventListener("click", event => {
    document.getElementById("modal1").classList.add("is-visible");
})

document.addEventListener("click", event => {
  if (event.target === document.querySelector(".modal.is-visible")) {
    document.querySelector(".modal.is-visible").classList.remove("is-visible");
  }
});

document.addEventListener("keyup", event => {
  if (event.key === "Escape") {
    document.getElementById("modal1").classList.remove("is-visible");
  }
});
