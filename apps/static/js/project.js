const modal = new bootstrap.Modal(document.getElementById("modal"))

htmx.on("htmx:afterSwap", (e) => {
  // Response targeting #dialog => show the modal
  if (e.detail.target.id === "dialog") {
    modal.show()
  }
})

htmx.on("htmx:beforeSwap", (e) => {
  // Empty response targeting #dialog => hide the modal
  if (e.detail.target.id === "dialog" && !e.detail.xhr.response) {
    modal.hide()
    e.detail.shouldSwap = false
  }
})

htmx.on("hidden.bs.modal", () => {
  // When modal is hidden => reset the form
  document.getElementById("dialog").innerHTML = ""
})

htmx.on("mapListChanged", (e) => {
  modal.hide()
})

htmx.on("characterListChanged", (e) => {
  modal.hide()
})

htmx.on("campaignListChanged", (e) => {
  modal.hide()
})

htmx.on("mapChanged", (e) => {
  modal.hide()
})

htmx.on("characterChanged", (e) => {
  modal.hide()
})

htmx.on("campaignChanged", (e) => {
  modal.hide()
})

htmx.on("userChanged", (e) => {
  modal.hide()
})

htmx.on("locationChanged", (e) => {
  modal.hide()
})

htmx.on("locationListChanged", (e) => {
  modal.hide()
})

const STICKY_OFFSET = 240;

document.addEventListener("htmx:after-swap", (event) => {
  if (!(event.target instanceof HTMLElement)) {
    return;
  }
  window.scrollTo(0, event.target.offsetTop - STICKY_OFFSET);
});
