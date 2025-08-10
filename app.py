from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
from scipy.sparse import csr_matrix
import re



# Initialize Flask app
app = Flask(__name__)

# Load pre-trained model and pivot table
model = pickle.load(open('model/book_model.pkl', 'rb'))
book_pivot = pd.read_pickle('model/book_pivot.pkl')
book_sparse = csr_matrix(book_pivot)

book_titles_lower = [title.lower() for title in book_pivot.index.tolist()]


# Load metadata (author info) from your books dataset
books_metadata = pd.read_csv('dataset/BX-Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
books_metadata = books_metadata[['ISBN', 'Book-Title', 'Book-Author']]
books_metadata.rename(columns={'Book-Title': 'title', 'Book-Author': 'author'}, inplace=True)
books_metadata.drop_duplicates(subset=['title'], inplace=True)
books_metadata['title_lower'] = books_metadata['title'].str.lower()

# Create a dict for fast author lookup by title
title_to_author = dict(zip(books_metadata['title_lower'], books_metadata['author']))

# Helper function to normalize titles for duplicate detection
def normalize_title(title):
    return re.sub(r'\W+', '', title.lower())

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/architecture')
def architecture():
    return render_template('architecture.html')

@app.route('/suggest', methods=['POST'])
def suggest():
    query = request.json.get('query', '').strip().lower()
    suggestions = [title for title in book_pivot.index if query in title.lower()]
    return jsonify(suggestions)

@app.route('/recommend', methods=['POST'])
def recommend():
    selected_title = request.json.get('selected_title', '').strip().lower()
    top_n = request.json.get('n', 5)

    if selected_title not in book_titles_lower:
        return jsonify([])

    book_id = book_titles_lower.index(selected_title)
    distances, suggestions = model.kneighbors(book_sparse[book_id], n_neighbors=20)

    input_author = title_to_author.get(selected_title, '').lower()

    recs = []
    seen_titles = set()

    for i in range(1, len(suggestions[0])):
        title = book_pivot.index[suggestions[0][i]]
        norm_title = normalize_title(title)
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)

        dist = distances[0][i]
        author = title_to_author.get(title.lower(), '').lower()
        if author and input_author and author == input_author:
            dist *= 0.9

        recs.append((title, dist))

    recs.sort(key=lambda x: x[1])
    filtered_recs = [r for r in recs if r[1] < 0.4]

    if len(filtered_recs) < top_n:
        needed = top_n - len(filtered_recs)
        additional = [r for r in recs if r[1] >= 0.4][:needed]
        filtered_recs.extend(additional)

    # Return title + confidence
    recommended_books = [
        {"title": title, "confidence": 1 - dist}
        for title, dist in filtered_recs[:top_n]
    ]

    return jsonify(recommended_books)


if __name__ == '__main__':
    app.run(debug=True)
