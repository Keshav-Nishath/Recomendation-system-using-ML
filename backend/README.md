# CineMatch — Flask Backend

AI-Powered Collaborative Movie Recommendation System

---

## Quick Start

```bash
# From the project root
cd backend
python app.py
```

Server starts at `http://localhost:5000`

---

## Requirements

Install dependencies (from the project root, using your virtualenv):

```bash
pip install flask flask-cors scikit-learn pandas numpy
```

---

## Data Files

The following files must be present in the **project root** (one level above `backend/`):

| File | Description |
|------|-------------|
| `knn.pkl` | Trained KNN model (NearestNeighbors, cosine, brute) |
| `matrix.pkl` | User-item rating matrix — DataFrame (7977 × 9087) |
| `movies.csv` | Movie metadata: movieId, title, genres |
| `ratings.csv` | All user ratings: userId, movieId, rating, timestamp |
| `links.csv` | TMDB / IMDb ID mapping |
| `tags.csv` | Movie tags |

---

## API Endpoints

### `GET /health`

Returns backend subsystem status.

```json
{
  "success": true,
  "status": "healthy",
  "recommendation_engine": true,
  "similarity_matrix": true,
  "dataset": true,
  "system": true
}
```

---

### `GET /stats`

Returns dataset statistics for the frontend sidebar.

```json
{
  "success": true,
  "users": 7977,
  "movies": 9087,
  "total_ratings": 22884377,
  "avg_rating": 3.53,
  "active_users": 7977,
  "ratings": 22884377
}
```

---

### `POST /recommend`

Generate personalized movie recommendations.

**Request:**

```json
{
  "user_id": 17,
  "k": 6,
  "recommendations": 10
}
```

**Response:**

```json
{
  "success": true,
  "recommendations": [
    {
      "title": "12 Angry Men (1957)",
      "year": 1957,
      "genres": "Drama",
      "genres_list": ["Drama"],
      "rating": 5.0,
      "similar_users": 3
    }
  ],
  "user_id": 17,
  "k": 6,
  "count": 10,
  "elapsed_ms": 42.3
}
```

**Error (user not in matrix):**

```json
{
  "success": false,
  "message": "User ID 4 does not exist in the recommendation matrix..."
}
```

---

## Important Note on User IDs

Only **7,977 users** appear in the recommendation matrix (`matrix.pkl`).
These are users with enough rating history to be included at training time.

To find valid user IDs, run:

```python
import pickle
with open("matrix.pkl", "rb") as f:
    matrix = pickle.load(f)
print(list(matrix.index[:20]))
# [17, 106, 114, 178, 198, 206, 241, 247, 277, 373, ...]
```

Valid sample IDs: `17, 106, 114, 178, 198, 206, 241, 247, 277, 373`

---

## Project Structure

```
backend/
├── app.py                      # Flask entry point
├── config.py                   # All configurable values
├── requirements.txt
├── README.md
├── routes/
│   ├── health.py               # GET /health
│   ├── stats.py                # GET /stats
│   └── recommend.py            # POST /recommend
├── services/
│   ├── data_loader.py          # CSV loading + lookup tables
│   ├── recommendation_engine.py # Core KNN pipeline
│   └── recommender.py          # Orchestration layer
├── models/
│   └── knn_loader.py           # knn.pkl + matrix.pkl loader
└── utils/
    ├── logger.py               # Centralised logging
    ├── helpers.py              # Response builders, timer, helpers
    └── validators.py           # Request validation
```

---

## Algorithm

**User-Based Collaborative Filtering**

1. Retrieve the target user's rating vector from the matrix
2. Query KNN (cosine similarity, brute force) for k nearest neighbours
3. Collect all movies rated by those neighbours
4. Remove movies already rated by the target user
5. Score remaining movies using **similarity-weighted mean rating**
6. Return the top-N movies sorted by predicted rating

---

## Configuration

All tunable values are in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `5000` | HTTP port |
| `DEBUG` | `False` | Flask debug mode |
| `DEFAULT_K` | `6` | Default neighbour count |
| `DEFAULT_RECOMMENDATIONS` | `10` | Default result count |
| `MAX_K` | `50` | Upper bound on k |
| `MAX_RECOMMENDATIONS` | `100` | Upper bound on result count |
