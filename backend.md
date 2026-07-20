# CineMatch
## Backend Design Specification (backend.md)

**Version:** 1.0

**Framework:** Flask

**Machine Learning Framework:** Scikit-Learn

**Recommendation Algorithm:** User-Based Collaborative Filtering

**Model:** K-Nearest Neighbors (KNN)

**Learning Type:** Unsupervised Learning

---

# 1. Project Overview

## Description

The backend is responsible for serving movie recommendations through a REST API.

The recommendation engine uses a **User-Based Collaborative Filtering** approach implemented using Scikit-Learn's **NearestNeighbors** model.

The backend loads all required machine learning models and datasets during application startup and exposes API endpoints that are consumed by the Streamlit frontend.

The backend must be lightweight, modular, scalable, and optimized for inference.

---

# 2. Technology Stack

Framework

- Flask

Machine Learning

- Scikit-Learn
- NearestNeighbors

Data Processing

- Pandas
- NumPy

Serialization

- Pickle

Communication

- REST API
- JSON

---

# 3. Recommendation Algorithm

Recommendation Type

**User-Based Collaborative Filtering**

Learning Type

**Unsupervised Learning**

Model

```python
NearestNeighbors(
    metric="cosine",
    algorithm="brute"
)
```

Similarity Metric

Cosine Similarity

Neighbor Search

Brute Force

The number of nearest neighbours (**K**) is supplied dynamically by the frontend for every recommendation request.

---

# 4. Backend Responsibilities

The backend is responsible for

- Loading ML models
- Loading datasets
- Validating requests
- Finding similar users
- Generating recommendations
- Removing already watched movies
- Returning recommendation results
- Returning dataset statistics
- Monitoring backend health

---

# 5. Project Structure

```
backend/

│

├── app.py

├── config.py

│

├── routes/

│   ├── recommend.py

│   ├── stats.py

│   ├── health.py

│

├── services/

│   ├── recommender.py

│   ├── data_loader.py

│   ├── recommendation_engine.py

│

├── utils/

│   ├── validators.py

│   ├── logger.py

│   ├── helpers.py

│

├── models/

│   ├── knn_loader.py

│

├── data/

│   ├── knn.pkl

│   ├── matrix.pkl

│   ├── movies.csv

│   ├── ratings.csv

│   ├── links.csv

│   ├── tags.csv

│

└── requirements.txt
```

---

# 6. Data Files

## knn.pkl

Contains

- Trained KNN model

Model Type

```
NearestNeighbors
```

Used for

- Finding similar users

---

## matrix.pkl

Contains

User-Item Matrix

Structure

Rows

```
Users
```

Columns

```
Movies
```

Values

```
Ratings
```

The matrix is loaded once during application startup.

---

## movies.csv

Contains

- Movie ID
- Title
- Genres

Used for displaying recommendation information.

---

## ratings.csv

Contains

Original user ratings.

Used for

- Validation
- Future analytics
- Statistics

---

## links.csv

Contains

Movie mapping

MovieLens ID

TMDB ID

IMDb ID

Reserved for future enhancements.

---

## tags.csv

Contains

Movie tags

Reserved for future enhancements.

---

# 7. Startup Behaviour

When Flask starts

```
Start Server

↓

Load Configuration

↓

Load knn.pkl

↓

Load matrix.pkl

↓

Load movies.csv

↓

Load ratings.csv

↓

Load links.csv

↓

Load tags.csv

↓

Store Everything In Memory

↓

Server Ready
```

No dataset should be loaded during API requests.

Everything should remain in memory.

---

# 8. API Architecture

The backend exposes REST endpoints.

Communication format

JSON

Stateless requests.

---

# 9. API Endpoints

## Health Check

GET

```
/health
```

Purpose

Returns backend status.

Example Response

```json
{
    "status":"healthy",
    "model_loaded":true,
    "dataset_loaded":true
}
```

---

## Dataset Statistics

GET

```
/stats
```

Returns

- Active Users
- Movies
- Ratings
- Average Rating

Example

```json
{
    "users":943,
    "movies":1682,
    "ratings":100000
}
```

---

## Generate Recommendation

POST

```
/recommend
```

---

Request

```json
{
    "user_id":4,
    "k":6,
    "recommendations":10
}
```

The frontend dynamically supplies

- User ID
- Number of neighbours
- Number of recommendations

---

Response

```json
{
    "success":true,

    "recommendations":[

        {

            "title":"Toy Story",

            "genres":"Animation|Comedy",

            "rating":4.82

        }

    ]

}
```

---

# 10. Recommendation Pipeline

The backend follows the following pipeline.

```
Receive Request

↓

Validate User ID

↓

Locate User Row

↓

Query KNN Model

↓

Find K Similar Users

↓

Collect Movies Rated By Neighbours

↓

Remove Already Rated Movies

↓

Rank Movies

↓

Return Top N Movies
```

---

# 11. Recommendation Engine

Step 1

Receive

- User ID
- K
- Recommendation Count

---

Step 2

Retrieve the selected user's vector from the User-Item Matrix.

---

Step 3

Pass the vector into the trained KNN model.

---

Step 4

Find the K nearest neighbours using cosine similarity.

---

Step 5

Retrieve movies rated by those neighbours.

---

Step 6

Exclude every movie already rated by the selected user.

This prevents recommending movies the user has already watched.

---

Step 7

Aggregate candidate movies.

The recommendation ranking strategy should be implemented within the recommendation engine and may evolve without changing the API contract.

---

Step 8

Return only the requested number of movies.

---

# 12. Validation

Validate

User ID

Must exist.

Recommendation Count

Must be greater than zero.

K

Must be greater than zero.

Invalid requests return

HTTP 400

---

# 13. Error Handling

Invalid User

```json
{
    "success":false,
    "message":"Invalid User ID."
}
```

---

Recommendation Failure

```json
{
    "success":false,
    "message":"Recommendation generation failed."
}
```

---

Backend Failure

HTTP

500

---

# 14. Logging

Log

Server startup

Model loading

Dataset loading

Recommendation requests

Execution time

Errors

Warnings

Logs should include timestamps.

---

# 15. Configuration

Store configurable values inside

```
config.py
```

Example

```
HOST

PORT

DEBUG

DEFAULT_K

DEFAULT_RECOMMENDATIONS
```

---

# 16. Performance

Load every dataset only once.

Never reload

- pickle files
- CSV files

for every request.

Keep models cached in memory.

Use efficient DataFrame indexing.

---

# 17. Security

Enable CORS.

Validate every request.

Never expose pickle paths.

Never expose stack traces to users.

Return only JSON responses.

---

# 18. Streamlit Integration

The frontend communicates only through REST APIs.

The frontend should never directly access

- Pickle files
- CSV files
- Recommendation model

The backend is solely responsible for ML inference.

---

# 19. Future Improvements

Possible future enhancements include

- Matrix Factorization (SVD)
- Neural Collaborative Filtering
- Explainable recommendations
- Recommendation confidence scores
- User authentication
- Recommendation history
- Recommendation caching
- Docker deployment
- API versioning
- JWT authentication
- Rate limiting
- TMDB poster integration
- Monitoring and metrics

---

# 20. Backend Flow Diagram

```
                Streamlit Frontend

                        │

                        │ HTTP POST

                        ▼

                 Flask Recommendation API

                        │

            Validate Request Parameters

                        │

                        ▼

               Load User Vector

                        │

                        ▼

              Query KNN Model

                        │

                        ▼

           Find Similar Users

                        │

                        ▼

      Aggregate Neighbour Ratings

                        │

                        ▼

     Remove Already Rated Movies

                        │

                        ▼

         Rank Recommendation List

                        │

                        ▼

        Return Top N Recommendations

                        │

                        ▼

              Streamlit Frontend
```

---

# 21. Design Principles

The backend should be

- Modular
- Scalable
- Lightweight
- Maintainable
- Fast
- RESTful
- Well documented
- Easily extensible
- Optimized for inference
- Independent of the frontend implementation

---

# 22. Summary

The CineMatch backend provides a modular Flask-based REST API for serving personalized movie recommendations using a User-Based Collaborative Filtering approach. It loads a pre-trained KNN model and a user-item matrix during startup, performs nearest-neighbour search using cosine similarity, filters previously rated movies, and returns ranked recommendations to the Streamlit frontend. All machine learning logic remains isolated within the backend, allowing the frontend to remain lightweight and focused solely on user interaction.

This document serves as the implementation specification for the Flask backend. All modules, API contracts, data loading strategies, validation rules, and recommendation workflows described here should be followed to ensure a maintainable, scalable, and production-ready backend.