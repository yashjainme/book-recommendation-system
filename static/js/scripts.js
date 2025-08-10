// Elements
const suggestionsDiv = document.getElementById('suggestions');
const recommendationsDiv = document.getElementById('recommendations');
const input = document.getElementById('book-title');

const navHome = document.getElementById('nav-home');
const navArchitecture = document.getElementById('nav-architecture');

const homePage = document.getElementById('home-page');
const architecturePage = document.getElementById('architecture-page');

let currentSelectedTitle = '';

// Navigation SPA logic
navHome.addEventListener('click', (e) => {
  e.preventDefault();
  showPage('home');
});

navArchitecture.addEventListener('click', (e) => {
  e.preventDefault();
  showPage('architecture');
});

function showPage(page) {
  if (page === 'home') {
    homePage.classList.add('active');
    architecturePage.classList.remove('active');
    navHome.classList.add('active');
    navArchitecture.classList.remove('active');
  } else {
    homePage.classList.remove('active');
    architecturePage.classList.add('active');
    navHome.classList.remove('active');
    navArchitecture.classList.add('active');
  }
}

// Fetch suggestions for search input
function getSuggestions() {
  let query = input.value.trim();

  if (query.length === 0) {
    suggestionsDiv.innerHTML = '';
    suggestionsDiv.style.display = 'none';
    return;
  }

  fetch('/suggest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
    .then((res) => res.json())
    .then((data) => {
      suggestionsDiv.innerHTML = '';
      if (data.length > 0) {
        data.forEach((title) => {
          let a = document.createElement('a');
                    a.href = '#';
          a.textContent = title;
          a.onclick = function (e) {
            e.preventDefault();
            input.value = title;
            currentSelectedTitle = title;
            suggestionsDiv.style.display = 'none';
            getRecommendations(title);
          };
          suggestionsDiv.appendChild(a);
        });
        suggestionsDiv.style.display = 'block';
      } else {
        let noResult = document.createElement('a');
        noResult.textContent = 'No books found';
        noResult.className = 'not-found';
        noResult.href = '#';
        noResult.onclick = (e) => e.preventDefault();
        suggestionsDiv.appendChild(noResult);
        suggestionsDiv.style.display = 'block';
      }
    })
    .catch(() => {
      suggestionsDiv.innerHTML = '';
      suggestionsDiv.style.display = 'none';
    });
}

// Trigger recommendation when user clicks Search button or presses Enter
function searchSelected() {
  const title = input.value.trim();
  if (title.length > 0) {
    currentSelectedTitle = title;
    suggestionsDiv.style.display = 'none';
    getRecommendations(title);
  }
}

// Also allow pressing Enter in input to trigger recommendation
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    searchSelected();
  }
});

// Fetch recommendations and show confidence scores
function getRecommendations(selected_title) {
  fetch('/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ selected_title }),
  })
    .then((res) => res.json())
    .then((data) => {
      recommendationsDiv.innerHTML = `<p>Recommendations based on "<strong>${selected_title}</strong>":</p>`;

      if (data.length > 0) {
        // data is now assumed to be array of { title: string, confidence: number }
        // If your backend doesn't send confidence, you need to update it accordingly.
        // For now, assuming it's an array of titles only:
        // We'll show titles only. To show confidence, backend must send it.

        data.forEach((item) => {
          let bookTitle, confidence;
          if (typeof item === 'string') {
            bookTitle = item;
            confidence = null;
          } else {
            bookTitle = item.title;
            confidence = item.confidence;
          }
          let p = document.createElement('p');
          p.className = 'recommendation-item';

          let titleSpan = document.createElement('span');
          titleSpan.textContent = `- ${bookTitle}`;
          p.appendChild(titleSpan);

          if (confidence !== null) {
            let confSpan = document.createElement('span');
            confSpan.className = 'confidence-score';
            confSpan.textContent = `Confidence: ${(confidence * 100).toFixed(0)}%`;
            p.appendChild(confSpan);
          }

          recommendationsDiv.appendChild(p);
        });
      } else {
        let p = document.createElement('p');
        p.textContent = 'No recommendations available for this book.';
        p.className = 'not-found';
        recommendationsDiv.appendChild(p);
      }
    })
    .catch(() => {
      recommendationsDiv.innerHTML = '';
      let p = document.createElement('p');
      p.textContent = 'Failed to load recommendations. Please try again later.';
      p.className = 'not-found';
      recommendationsDiv.appendChild(p);
    });
}

// Close the suggestions dropdown if clicked outside input
window.onclick = function (event) {
  if (event.target !== input) {
    suggestionsDiv.style.display = 'none';
  }
};

