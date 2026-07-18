import streamlit as st
import pickle


st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


@st.cache_resource
def load_models():

    with open("knn.pkl","rb") as f:
        model1 = pickle.load(f)

    with open("model2.pkl","rb") as f:
        model2 = pickle.load(f)

    with open("matrix.pkl","rb") as f:
        matrix = pickle.load(f)

    return model1,model2,matrix

model1,model2,matrix = load_models()

movie_list=list(matrix.columns)


if "history" not in st.session_state:
    st.session_state.history=[]

if "recommendations" not in st.session_state:
    st.session_state.recommendations=movie_list[:6]



def get_recommendations():

    """
    Replace this later with your
    Content + Collaborative model.
    """

    if len(st.session_state.history)<5:

        return movie_list[:6]

    else:

        # Replace this later

        return movie_list[10:16]


# ---------------- TITLE ---------------- #

st.title("🎬 Movie Recommendation System")

st.write(
    "Search movies, rate them and build your own recommendations."
)

st.divider()


st.subheader("🔍 Search Movie")

search=st.text_input("Search")

if search=="":

    filtered=movie_list

else:

    filtered=[movie
              for movie in movie_list
              if search.lower() in movie.lower()
             ]


selected_movie=st.selectbox(
    "Select Movie",
    filtered
)

rating=st.slider(
    "Rate Movie",
    1,
    5,
    3
)

if st.button("⭐ Rate & Watch"):

    st.session_state.history.append({

        "movie":selected_movie,
        "rating":rating

    })

    st.session_state.recommendations=get_recommendations()

    st.success("Movie Added Successfully!")

st.divider()


left,right=st.columns([1,2])


with left:

    st.subheader("📚 Watch History")

    if len(st.session_state.history)==0:

        st.info("No movies watched.")

    else:

        for movie in reversed(st.session_state.history):

            st.write(
                f"🎬 {movie['movie']} ⭐ {movie['rating']}"
            )


with right:

    st.subheader("🎯 Recommended Movies")

    cols=st.columns(3)

    for i,movie in enumerate(st.session_state.recommendations):

        with cols[i%3]:

            st.container(border=True)

            st.image(
                "https://placehold.co/250x350?text=Movie",
                use_container_width=True
            )

            st.markdown(f"### {movie}")

            st.button(
                "Watch",
                key=f"watch_{movie}"
            )