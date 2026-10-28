// Client-side only, for the Characters tab: "Select all shown" ticks every candidate; the Add button counts the ticked ones.
// Listeners sit on the document so they survive htmx swapping the tab card.
function countTicked(form) {
  const n = form.querySelectorAll("input[name=chars]:checked").length;
  document.querySelectorAll("[data-count]").forEach((b) => { if (b.form === form) b.textContent = `Add ${n} to lesson`; });
}
document.addEventListener("click", (e) => {
  const button = e.target.closest("[data-select-all]");
  if (!button || !button.form) return;
  button.form.querySelectorAll("input[name=chars]").forEach((c) => { c.checked = true; });
  countTicked(button.form);
});
document.addEventListener("change", (e) => {
  if (e.target.name === "chars" && e.target.form) countTicked(e.target.form);
});
