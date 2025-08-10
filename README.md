# 📚 Unbound – Book Recommendation System

Unbound is a **content-based & collaborative filtering** book recommendation system built with **Python (Flask)** for the backend and a lightweight **HTML/CSS/JavaScript** frontend.  
It suggests books based on user-selected titles using **K-Nearest Neighbors (KNN)** on a sparse ratings matrix.

---

## 🚀 Features

- **Real-time book search** with autocomplete suggestions
- **Personalized recommendations** using collaborative filtering
- **Data preprocessing & filtering** for cleaner results
- **Responsive frontend** for smooth user experience
- **Architecture page** with dataset & filtering insights

---

## 📊 Dataset

We use the **[Book-Crossing dataset](https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset)** which contains:

- **Books metadata** (`BX-Books.csv`)
- **User information** (`BX-Users.csv`)
- **Ratings data** (`BX-Book-Ratings.csv`)

---

## 🧹 Data Filtering Approach

To ensure high-quality recommendations, the dataset is filtered in two stages:

| Step | Filter Condition       | Reason | Before | After |
|------|------------------------|--------|--------|-------|
| 1    | Users with > **200** ratings | Keep only active readers with enough preference data | 105,283 | 899 |
| 2    | Books with ≥ **50** ratings  | Keep only popular books for reliable similarity | 160,269 | 742 |

> **Note:** These thresholds remove sparse and noisy data, improving recommendation accuracy.

---

## 🏗 Architecture

### Workflow:
1. **Load & Clean Data** – from CSVs (books, users, ratings)
2. **Filter Users & Books** – remove low-activity users & low-rated books
3. **Create Pivot Table** – books × users with ratings
4. **Convert to Sparse Matrix** – for efficiency
5. **Train KNN Model** – cosine similarity for nearest neighbors
6. **Save Model & Data** – serialized with `pickle`
7. **Serve via Flask** – API for `/suggest` & `/recommend`
8. **Frontend UI** – search & view recommendations

### Tech Stack:
- **Backend:** Python, Flask
- **ML:** pandas, scikit-learn, SciPy
- **Frontend:** HTML, CSS, JavaScript
- **Data:** Book-Crossing dataset

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yashjainme/book-recommendation-system.git
cd book-recommendation-system
```
### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Train the Model

```bash
python train.py
```

### 4️⃣ Run the Flask App
```bash
python app.py
```