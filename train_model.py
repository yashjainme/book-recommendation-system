import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle
import os

# Create 'model' directory if it doesn't exist
os.makedirs('model', exist_ok=True)

def load_and_preprocess():
    # Load datasets
    books = pd.read_csv('dataset/BX-Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    books = books[['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher']]
    books.rename(columns={'Book-Title': 'title', 'Book-Author': 'author',
                          'Year-Of-Publication': 'year', 'Publisher': 'publisher'}, inplace=True)

    users = pd.read_csv('dataset/BX-Users.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    users.rename(columns={'User-ID': 'user_id', 'Location': 'location', 'Age': 'age'}, inplace=True)

    ratings = pd.read_csv('dataset/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    ratings.rename(columns={'User-ID': 'user_id', 'Book-Rating': 'rating'}, inplace=True)

    # Filter users with more than 200 ratings
    active_users = ratings['user_id'].value_counts()
    ratings = ratings[ratings['user_id'].isin(active_users[active_users > 200].index)]

    # Merge and filter ratings
    ratings_with_books = ratings.merge(books, on='ISBN')
    number_rating = ratings_with_books.groupby('title')['rating'].count().reset_index()
    number_rating.rename(columns={'rating': 'number_of_ratings'}, inplace=True)

    final_rating = ratings_with_books.merge(number_rating, on='title')
    final_rating = final_rating[final_rating['number_of_ratings'] >= 50]

    new_final_rating = final_rating.drop_duplicates(['user_id', 'title'])
    book_pivot = new_final_rating.pivot_table(columns='user_id', index='title', values='rating').fillna(0)

    return book_pivot

def train_and_save_model(book_pivot):
    book_sparse = csr_matrix(book_pivot)

    model = NearestNeighbors(algorithm='brute', metric='cosine')
    model.fit(book_sparse)

    # Save pivot and model
    pickle.dump(model, open('model/book_model.pkl', 'wb'))
    book_pivot.to_pickle('model/book_pivot.pkl')

    print("Model and pivot table saved to 'model/' folder.")

if __name__ == '__main__':
    book_pivot = load_and_preprocess()
    train_and_save_model(book_pivot)
