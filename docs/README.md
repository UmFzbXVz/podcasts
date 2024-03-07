<link rel="stylesheet" href="style.css">

<div id="search-bar">
  <input type="text" placeholder="Søg i podcasts..." id="search-input">
</div>
<ul id="results"></ul>

<script>
// Hent alle RSS-feed-filer
const feeds = await fetch("https://api.github.com/repos/UmFzbXVz/podcasts/contents/")
  .then((response) => response.json())
  .then((data) => data.map((file) => file.download_url));

// Opret et Fuse.js-indeks
const fuse = new Fuse(feeds, {
  keys: ["title", "description"],
});

// Opdater resultaterne baseret på brugerens søgning
document.getElementById("search-input").addEventListener("input", (event) => {
  const results = fuse.search(event.target.value);
  const resultsList = document.getElementById("results");
  resultsList.innerHTML = "";

  results.forEach((result) => {
    const listItem = document.createElement("li");
    listItem.innerHTML = `
      <a href="${result.item.download_url}">${result.item.title}</a>
      <p>${result.item.description}</p>
    `;

    resultsList.appendChild(listItem);
  });
});
</script>
