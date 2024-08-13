// Updated JavaScript with minor UX improvements
function getSuggestions() {
    let query = document.getElementById('book-title').value;
    let suggestionsDiv = document.getElementById('suggestions');

    if (query.length > 0) {
        fetch('/suggest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
            .then(response => response.json())
            .then(data => {
                suggestionsDiv.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(title => {
                        let a = document.createElement('a');
                        a.href = '#';
                        a.textContent = title;
                        a.onclick = function (e) {
                            e.preventDefault();
                            document.getElementById('book-title').value = title;
                            getRecommendations(title);
                            suggestionsDiv.style.display = 'none';
                        };
                        suggestionsDiv.appendChild(a);
                    });
                    suggestionsDiv.style.display = 'block';
                } else {
                    suggestionsDiv.innerHTML = '<a class="not-found">No books found</a>';
                    suggestionsDiv.style.display = 'block';
                }
            });
    } else {
        suggestionsDiv.innerHTML = '';
        suggestionsDiv.style.display = 'none';
    }
}

function getRecommendations(selected_title) {
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ selected_title: selected_title })
    })
        .then(response => response.json())
        .then(data => {
            let recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = `<p>Recommendations based on "${selected_title}":</p>`;
            if (data.length > 0) {
                data.forEach(book => {
                    let p = document.createElement('p');
                    p.textContent = `- ${book}`;
                    recommendationsDiv.appendChild(p);
                });
            } else {
                let p = document.createElement('p');
                p.textContent = "No recommendations available for this book.";
                p.className = "not-found";
                recommendationsDiv.appendChild(p);
            }
        });
}

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('#book-title')) {
        document.getElementById('suggestions').style.display = 'none';
    }
}
