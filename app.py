import requests
import streamlit as st

st.title("🎬 심리테스트 기반 영화 추천")

st.write(
    """
    간단한 심리테스트로 당신의 현재 분위기를 파악하고, 그에 어울리는 영화를 추천해 드립니다.
    아래 질문에 답변한 뒤 추천 버튼을 눌러주세요.
    """
)

# 사이드바에서 API 키 입력
TMDB_API_KEY = st.sidebar.text_input("TMDB API Key", type="password")

questions = {
    "오늘 당신의 에너지는 어떤가요?": [
        "활력이 넘쳐요!",
        "평범해요.",
        "조용히 쉬고 싶어요.",
    ],
    "지금 가장 끌리는 감정은 무엇인가요?": [
        "설렘",
        "감동",
        "웃음",
    ],
    "오늘의 분위기에 어울리는 장소는?": [
        "도시의 밤거리",
        "아늑한 집",
        "자연 속 풍경",
    ],
}

genre_options = {
    "상관없음": None,
    "액션": 28,
    "모험": 12,
    "코미디": 35,
    "로맨스": 10749,
    "SF": 878,
    "판타지": 14,
    "드라마": 18,
    "애니메이션": 16,
}

genre_mapping = {
    ("활력이 넘쳐요!", "설렘", "도시의 밤거리"): (28, "액션"),
    ("활력이 넘쳐요!", "웃음", "도시의 밤거리"): (35, "코미디"),
    ("활력이 넘쳐요!", "감동", "자연 속 풍경"): (12, "어드벤처"),
    ("평범해요.", "설렘", "도시의 밤거리"): (10749, "로맨스"),
    ("평범해요.", "웃음", "아늑한 집"): (35, "코미디"),
    ("평범해요.", "감동", "아늑한 집"): (18, "드라마"),
    ("조용히 쉬고 싶어요.", "감동", "아늑한 집"): (18, "드라마"),
    ("조용히 쉬고 싶어요.", "설렘", "자연 속 풍경"): (14, "판타지"),
    ("조용히 쉬고 싶어요.", "웃음", "아늑한 집"): (35, "코미디"),
}

answers = []
for question, options in questions.items():
    answers.append(st.radio(question, options, horizontal=True))

preferred_genre = st.selectbox(
    "원하는 영화 장르를 선택해주세요.",
    list(genre_options.keys()),
)

if TMDB_API_KEY:
    if st.button("심리테스트 결과로 영화 추천 받기"):
        selected_key = tuple(answers)
        genre_id, genre_label = genre_mapping.get(selected_key, (18, "드라마"))

        if preferred_genre != "상관없음":
            genre_id = genre_options[preferred_genre]
            genre_label = preferred_genre

        st.subheader(f"🎯 추천 장르: {genre_label}")
        url = (
            "https://api.themoviedb.org/3/discover/movie"
            f"?api_key={TMDB_API_KEY}"
            "&language=ko-KR"
            f"&with_genres={genre_id}"
            "&sort_by=popularity.desc"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        raw_movies = data.get("results", [])
        movies = [
            movie
            for movie in raw_movies
            if movie.get("vote_average", 0) >= 7.5
            or movie.get("popularity", 0) >= 50
        ][:3]

        if not movies:
            st.warning("추천할 영화를 찾지 못했어요. 다른 답변으로 다시 시도해 주세요.")
        else:
            st.markdown("### 🌟 우선순위별 추천 영화 3편")
            for idx, movie in enumerate(movies, start=1):
                st.markdown(f"#### {idx}순위: {movie['title']}")
                st.write(f"⭐ 평점: {movie['vote_average']}/10")
                st.write(f"📅 개봉일: {movie['release_date']}")
                overview = movie.get("overview") or "줄거리 정보가 없습니다."
                st.write(f"📝 줄거리: {overview}")
                st.divider()
else:
    st.info("사이드바에 TMDB API Key를 입력해주세요.")
