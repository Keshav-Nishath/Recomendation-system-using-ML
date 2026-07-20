# CineMatch
## Frontend Design Specification

Version: 1.0

Framework: Streamlit

Backend: Flask REST API

Project Type: Collaborative Filtering Movie Recommendation System

---

# 1. Project Overview

## Application Name

**CineMatch**

### Tagline

> AI-Powered Collaborative Movie Recommendation System

## Description

CineMatch is a web-based movie recommendation system that uses **Collaborative Filtering** to recommend movies to existing users based on the preferences of users with similar movie tastes.

The frontend is built using **Streamlit** and communicates with a Flask backend through REST APIs.

The primary objective of the frontend is to provide a clean, modern, and interactive interface that allows users to generate personalized movie recommendations with minimal effort.

---

# 2. Design Goals

The frontend should be:

- Modern
- Minimalistic
- Easy to understand
- Responsive
- Professional
- Interactive
- Fast
- Modular
- Easily extendable

The interface should resemble an AI dashboard rather than a traditional website.

---

# 3. Overall Layout

The application consists of two primary sections.

```
+--------------------------------------------------------------+
|                                                              |
| Sidebar |                 Main Content                       |
|         |                                                    |
|         |                                                    |
|         |                                                    |
|         |                                                    |
+--------------------------------------------------------------+
```

Layout Ratio

Sidebar

22%

Main Content

78%

The sidebar remains visible throughout the application.

---

# 4. Color Palette

## Background

Primary

#0F1117

Sidebar

#1B1E27

Cards

#202433

Borders

#30384A

---

## Accent Colors

Primary

Purple

#C026FF

Secondary

Blue

#4DA3FF

Success

Green

#34C759

Warning

Orange

#FF9500

Error

Red

#FF3B30

---

## Text

Primary

White

Secondary

Light Gray

Muted

Gray

---

# 5. Typography

Application Title

Large

Bold

Center aligned

Section Titles

Bold

White

Card Titles

Semi Bold

Statistics

Large Numbers

Descriptions

Regular

---

# 6. Sidebar

The sidebar acts as a permanent dashboard.

---

## Logo Section

Display

🎬 CineMatch

Subtitle

AI-Powered Collaborative Movie Recommendation System

---

## Divider

Horizontal separator.

---

## System Status

Display four status cards.

✓ Recommendation Engine Ready

✓ Similarity Matrix Loaded

✓ Dataset Loaded

✓ System Online

Each status card should be displayed using a green success color.

The status values are fetched from the backend.

---

## Dataset Statistics

Display statistics retrieved from Flask.

Example

Active Users

92,391

Movies

3,706

Ratings

1,000,209

Average Rating

3.58

These values should be displayed using Streamlit metric components.

---

# 7. Main Content

The main content contains every interactive element.

Everything should be vertically aligned.

Maximum content width

1200px

---

# 8. Header

Display

# CineMatch

Subtitle

AI-Powered Collaborative Movie Recommendation System

Below the subtitle

"Discover movies loved by users with tastes similar to yours."

The header should be centered.

---

# 9. User Mode Selection

Display radio buttons.

Options

• Existing User

• New User (Coming Soon)

The "New User" option should be disabled or display a message stating:

"Cold-start recommendations are not available in the current version."

This clearly communicates the current scope of the project.

---

# 10. Existing User Input

Display

User ID input field.

Placeholder

Example

4

Below the input

Display sample IDs

4

11

12

13

14

15

17

20

Only integer values are accepted.

Invalid IDs should display an error.

---

# 11. Recommendation Controls

Two sliders.

## Number of Recommendations

Minimum

5

Maximum

20

Default

10

---

## Number of Similar Users (K)

Minimum

1

Maximum

10

Default

6

The selected values should update immediately.

---

# 12. Generate Recommendation Button

Large

Centered

Purple

Contains movie icon.

Text

Generate Recommendations

When clicked

Disable the button

Show loading spinner

Call Flask API

Display results

---

# 13. Loading State

Display Streamlit spinner.

Loading Messages

Finding users with similar preferences...

Calculating recommendation scores...

Ranking movies...

Preparing recommendations...

The interface should remain responsive.

---

# 14. Results Layout

Once recommendations are generated

Divide the page into two sections.

```
---------------------------------------------------------

Profile Context

|

Recommended Movies

---------------------------------------------------------
```

Column Width

35%

65%

---

# 15. Profile Context

Display

User ID

Highly Rated Movies

Average User Rating

Number of Movies Rated

These values help explain the recommendation context.

---

# 16. Highly Rated Movies

Display movies the selected user has rated highly.

Each movie card displays

Movie Title

Release Year

User Rating

Genres

These cards explain the user's interests.

---

# 17. Recommendation Grid

Display recommendation cards in a responsive grid.

Desktop

Three cards per row.

Tablet

Two cards.

Mobile

Single column.

---

# 18. Recommendation Card

Each recommendation card contains

Movie Poster

Movie Title

Release Year

Predicted Rating

Number of Similar Users

Genres

Recommendation Reason

TMDB Link (optional)

---

Card Style

Rounded corners

Dark background

Purple accent border

Padding

Shadow

Hover animation

---

# 19. Recommendation Explanation

Every recommendation should explain why it was generated.

Examples

Liked by 5 users with similar preferences.

Highly rated by your nearest neighbours.

Frequently watched by users with similar tastes.

Strong collaborative filtering score.

This makes recommendations more transparent.

---

# 20. Movie Posters

Movie posters should appear at the top of every recommendation card.

Poster Ratio

2:3

If unavailable

Display placeholder image.

---

# 21. Genre Badges

Genres should appear as colored badges.

Example

Drama

Comedy

Thriller

Action

Romance

Science Fiction

Each badge should have rounded corners.

---

# 22. Rating Badge

Display

⭐ 4.8

Green badge.

---

# 23. Hover Effects

Recommendation Cards

Scale

1.03

Increase shadow.

Movie poster slightly enlarges.

Buttons

Increase brightness.

---

# 24. Notifications

Success

Recommendations Generated Successfully

Green

---

Warning

User has rated very few movies.

Recommendations may be less accurate.

Orange

---

Error

Invalid User ID.

Backend unavailable.

Recommendation generation failed.

Red

---

# 25. Empty State

Before recommendations are generated

Display

🎬

"No recommendations generated yet."

Click **Generate Recommendations** to begin.

---

# 26. Session State

Store

User ID

Recommendation Count

K Value

Generated Recommendations

Profile Context

Sidebar Statistics

Avoid unnecessary reruns.

---

# 27. Streamlit Components

The frontend should primarily use

- st.sidebar
- st.container
- st.columns
- st.text_input
- st.radio
- st.slider
- st.button
- st.metric
- st.spinner
- st.success
- st.warning
- st.error
- st.markdown
- st.image
- st.session_state

Custom CSS should be injected using `st.markdown()`.

---

# 28. Custom Styling

Custom CSS should be used to style

Cards

Buttons

Sidebar

Section headers

Movie cards

Genre badges

Status cards

Hover effects

Spacing

Rounded corners

Shadows

Animations

---

# 29. Folder Structure

frontend/

│

├── app.py

├── assets/

│ ├── logo.png

│ ├── placeholder.jpg

│

├── styles/

│ └── style.css

│

├── components/

│ ├── sidebar.py

│ ├── header.py

│ ├── controls.py

│ ├── profile_panel.py

│ ├── recommendation_card.py

│ ├── recommendation_grid.py

│

├── api/

│ └── client.py

│

├── utils/

│ └── helpers.py

│

└── config.py

---

# 30. User Flow

```
Application Starts

↓

Load Sidebar

↓

Check Backend Status

↓

Load Dataset Statistics

↓

User Selects Existing User

↓

Enter User ID

↓

Select Recommendation Count

↓

Select Number of Neighbours (K)

↓

Click Generate Recommendations

↓

Send Request to Flask API

↓

Receive Recommendation Results

↓

Display User Profile Context

↓

Display Recommended Movies
```

---

# 31. Future Enhancements

The following features are outside the scope of the current version but should be considered for future releases.

- Cold-start recommendation support
- User authentication
- Watchlist
- Favourite movies
- Movie search with autocomplete
- Recommendation history
- Explainable AI dashboard
- Matrix Factorization (SVD)
- Neural Collaborative Filtering
- Implicit Feedback models
- Export recommendations to PDF
- TMDB integration for richer movie details
- User analytics dashboard

---

# 32. Summary

The CineMatch frontend should provide a clean, professional, and intuitive interface for interacting with a collaborative filtering recommendation engine. It should clearly present user information, recommendation controls, and personalized movie suggestions while maintaining a responsive, modern dashboard experience.

This document serves as the implementation specification for the Streamlit frontend. All layouts, components, interactions, styling, and user flows described here should be followed to ensure a consistent, maintainable, and scalable application.