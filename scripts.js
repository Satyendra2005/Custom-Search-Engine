document
  .getElementById("searchForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    const query = document.getElementById("searchInput").value;

    fetch(
      "https://your-backend-url.com/api/search?query=" +
        encodeURIComponent(query)
    )
      .then((response) => response.json())
      .then((data) => {
        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";
        data.forEach((user) => {
          const userResults = document.createElement("div");
          userResults.innerHTML = `<h3>${user.user}</h3>`;
          user.results.forEach((item) => {
            userResults.innerHTML += `<p><a href="${item.link}" target="_blank">${item.title}</a> (Score: ${item.score})</p>`;
          });
          resultsDiv.appendChild(userResults);
        });
      })
      .catch((error) => console.error("Error:", error));
  });
