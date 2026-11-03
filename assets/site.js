"use strict";
/* Progressive enhancement: all publications and citation links are static HTML. */
(() => {
  const input = document.getElementById("publication-search");
  const clear = document.getElementById("clear-search");
  const count = document.getElementById("publication-count");
  const list = document.getElementById("publication-list");
  const empty = document.getElementById("search-empty-state");
  if (!input || !clear || !count || !list) return;
  const groups = Array.from(list.querySelectorAll(".year-group"));
  const entries = Array.from(list.querySelectorAll(".publication"));
  const total = entries.length;
  const update = () => {
    const query = input.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const entry of entries) {
      const matches = !query || entry.textContent.toLocaleLowerCase().includes(query);
      entry.hidden = !matches;
      if (matches) visible++;
    }
    for (const group of groups) {
      group.hidden = !Array.from(group.querySelectorAll(".publication")).some(p => !p.hidden);
    }
    count.textContent = query ? `${visible} of ${total} works` : `${total} works`;
    clear.hidden = !query;
    if (empty) empty.hidden = !query || visible > 0;
  };
  input.addEventListener("input", update);
  clear.addEventListener("click", () => {
    input.value = "";
    update();
    input.focus();
  });
})();
