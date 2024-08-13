from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle

app = Flask(__name__)

def load_data():
    # Load datasets
    books = pd.read_csv('dataset/BX-Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    books = books[['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher']]
    books.rename(columns={'Book-Title': 'title', 'Book-Author': 'author', 'Year-Of-Publication': 'year', 'Publisher': 'publisher'}, inplace=True)

    users = pd.read_csv('dataset/BX-Users.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    users.rename(columns={'User-ID': 'user_id', 'Location': 'location', 'Age': 'age'}, inplace=True)

    ratings = pd.read_csv('dataset/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    ratings.rename(columns={'User-ID': 'user_id', 'Book-Rating': 'rating'}, inplace=True)

    # Filter users with more than 200 ratings
    active_users = ratings['user_id'].value_counts()
    ratings = ratings[ratings['user_id'].isin(active_users[active_users > 200].index)]

    # Merge ratings with books
    ratings_with_books = ratings.merge(books, on='ISBN')
    number_rating = ratings_with_books.groupby('title')['rating'].count().reset_index()
    number_rating.rename(columns={'rating': 'number_of_ratings'}, inplace=True)
    final_rating = ratings_with_books.merge(number_rating, on='title')
    final_rating = final_rating[final_rating['number_of_ratings'] >= 50]

    # Drop duplicates and create pivot table
    new_final_rating = final_rating.drop_duplicates(['user_id', 'title'])
    book_pivot = new_final_rating.pivot_table(columns='user_id', index='title', values='rating').fillna(0)

    # Create sparse matrix
    book_sparse = csr_matrix(book_pivot)
    
    return book_pivot, book_sparse

def train_model(book_sparse):
    # Train the model
    model = NearestNeighbors(algorithm='brute', metric='cosine')
    model.fit(book_sparse)
    return model

# Load and preprocess data, train model
book_pivot, book_sparse = load_data()
model = train_model(book_sparse)
book_titles_lower = [title.lower() for title in book_pivot.index.tolist()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suggest', methods=['POST'])
def suggest():
    query = request.json.get('query', '').strip().lower()
    suggestions = [title for title in book_pivot.index if query in title.lower()]
    return jsonify(suggestions)

@app.route('/recommend', methods=['POST'])
def recommend():
    selected_title = request.json.get('selected_title', '').strip().lower()
    if selected_title in book_titles_lower:
        book_id = book_titles_lower.index(selected_title)
        distances, suggestions = model.kneighbors(book_sparse[book_id], n_neighbors=6)
        recommended_books = [book_pivot.index[suggestions[0][i]] for i in range(1, len(suggestions[0]))]
        return jsonify(recommended_books)
    else:
        return jsonify([])  # Return empty list if book not found

if __name__ == '__main__':
    app.run(debug=True)
