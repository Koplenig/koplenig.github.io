"use strict";
/* All publication records, including Under Review, are in static HTML.
 * Search filters those records without requiring an external request. */
(() => {
  const input = document.getElementById("publication-search");
  const clear = document.getElementById("clear-search");
  const pubCount = document.getElementById("publication-count");
  const reviewCount = document.getElementById("under-review-count");
  const pubHeading = document.getElementById("published-heading-row");
  const reviewHeading = document.getElementById("under-review-heading-row");
  const pubList = document.getElementById("publication-list");
  const reviewList = document.getElementById("under-review-list");
  if (!input || !clear || !pubCount || !reviewCount || !pubList || !reviewList) return;
  const published = Array.from(pubList.querySelectorAll(".publication"));
  const reviewed = Array.from(reviewList.querySelectorAll(".publication"));
  const all = [...reviewed, ...published];
  const apply = () => {
    const query = input.value.trim().toLocaleLowerCase();
    for (const article of all) {
      article.hidden = !!query && !article.textContent.toLocaleLowerCase().includes(query);
    }
    for (const group of pubList.querySelectorAll(".year-group")) {
      group.hidden = !Array.from(group.querySelectorAll(".publication")).some(p => !p.hidden);
    }
    const pubsVisible = published.filter(p => !p.hidden).length;
    const reviewsVisible = reviewed.filter(p => !p.hidden).length;
    const filtering = !!query;
    pubCount.textContent = filtering ? `${pubsVisible} of ${published.length} works` : `${published.length} works`;
    reviewCount.textContent = filtering ? `${reviewsVisible} of ${reviewed.length} manuscripts` : `${reviewed.length} manuscripts`;
    clear.hidden = !filtering;
    if (reviewHeading) reviewHeading.hidden = filtering && reviewsVisible === 0;
    if (pubHeading) pubHeading.hidden = filtering && pubsVisible === 0;
    reviewList.hidden = filtering && reviewsVisible === 0;
    pubList.hidden = filtering && pubsVisible === 0;
    const empty = document.getElementById("search-empty-state");
    if (empty) empty.hidden = !filtering || pubsVisible + reviewsVisible > 0;
  };
  input.addEventListener("input", apply);
  clear.addEventListener("click", () => { input.value = ""; apply(); input.focus(); });
})();
