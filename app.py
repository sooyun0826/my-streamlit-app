from collections import Counter
from typing import Dict, List

import requests
import streamlit as st

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬", layout="centered")

st.markdown(
    """
    <style>
    .poster-frame {
        border: 6px solid #f0f0f0;
        border-radius: 16px;
        padding: 8px;
        background: #ffffff;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
        width: fit-content;
    }
    .poster-frame img {
        display: block;
        border-radius: 12px;
        max-width: 320px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 제목 & 소개
st.title("🎬 나와 어울리는 영화는?")
st.write("5가지 질문에 답하면, 당신의 영화 취향 성향을 바탕으로 어울리는 영화 타입을 찾아드려요! 🎞️🍿")

st.divider()

with st.sidebar:
    st.header("TMDB 설정")
    api_key = st.text_input("TMDB API Key", type="password")
    st.caption("TMDB에서 발급받은 API Key를 입력하세요.")

# 질문 & 선택지 (장르 성향을 반영)
questions = [
    {
        "q": "Q1. 시험이 끝난 날, 드디어 하루가 비었다. 지금 가장 하고 싶은 건?",
        "options": [
            "A. 잔잔한 음악 틀어두고 카페에 앉아 하루를 정리한다 (로맨스/드라마)",
            "B. 친구들이랑 즉흥 여행이나 액티비티를 바로 잡는다 (액션/어드벤처)",
            "C. 집에서 영화·드라마 몰아보며 다른 세계로 도피한다 (SF/판타지)",
            "D. 아무 생각 안 나게 웃긴 콘텐츠부터 찾아본다 (코미디)",
        ],
    },
    {
        "q": "Q2. 팀플이 끝났을 때, 당신이 가장 중요하게 생각하는 건?",
        "options": [
            "A. 과정에서 서로 상처받지 않았는지, 분위기가 좋았는지 (로맨스/드라마)",
            "B. 결과물의 완성도와 성과 (액션/어드벤처)",
            "C. 아이디어의 새로움과 컨셉의 독창성 (SF/판타지)",
            "D. 회의하면서 웃긴 에피소드가 남았는지 (코미디)",
        ],
    },
    {
        "q": "Q3. 새 학기가 시작됐다. 당신이 은근히 기대하는 건?",
        "options": [
            "A. 사람들과 자연스럽게 가까워지는 순간들 (로맨스/드라마)",
            "B. 새로운 도전, 바빠질수록 살아있다는 느낌 (액션/어드벤처)",
            "C. 완전히 새로운 환경과 세계관 같은 전공/수업 (SF/판타지)",
            "D. 예상치 못한 웃긴 사람들과의 만남 (코미디)",
        ],
    },
    {
        "q": "Q4. 영화 속 주인공이 된다면, 이 중 가장 끌리는 역할은?",
        "options": [
            "A. 관계 속에서 성장하고 감정을 깊이 겪는 인물 (로맨스/드라마)",
            "B. 위기마다 몸으로 돌파하는 해결사 (액션/어드벤처)",
            "C. 세계의 비밀을 파헤치는 선택받은 존재 (SF/판타지)",
            "D. 사건을 더 꼬이게 만들지만 결국 분위기를 살리는 인물 (코미디)",
        ],
    },
    {
        "q": "Q5. 힘든 하루 끝, 영화 한 편을 고른다면 기준은?",
        "options": [
            "A. 여운이 오래 남고 생각할 거리를 주는 이야기 (로맨스/드라마)",
            "B. 속도감 있고 몰입해서 스트레스가 풀리는 전개 (액션/어드벤처)",
            "C. 현실을 잠시 잊게 만드는 설정과 비주얼 (SF/판타지)",
            "D. 그냥 아무 생각 없이 웃을 수 있는지 (코미디)",
        ],
    },
]

GENRE_OPTIONS = {
    "A": "로맨스",
    "B": "액션",
    "C": "SF",
    "D": "코미디",
}

GENRE_IDS = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

GENRE_REASON = {
    "액션": "스릴과 속도감이 있는 전개를 즐기는 선택이 많았어요.",
    "코미디": "웃음과 가벼운 분위기를 선호하는 답변이 눈에 띄었어요.",
    "드라마": "감정선과 깊은 여운을 중시하는 성향이 드러났어요.",
    "SF": "새로운 세계관과 상상력을 즐기는 답변이 많았어요.",
    "로맨스": "관계와 감정의 흐름을 중요하게 생각하는 모습이에요.",
    "판타지": "현실을 넘어서는 서사에 끌리는 선택이 두드러졌어요.",
}


# 사용자 응답 저장
answers = []

for idx, item in enumerate(questions, start=1):
    st.subheader(f"질문 {idx}")
    choice = st.radio(
        item["q"],
        item["options"],
        index=None,  # 아무 것도 선택 안 한 상태 허용
        key=f"q{idx}",
    )
    answers.append(choice)
    st.write("")  # spacing

st.divider()


def analyze_answers(selected: List[str]) -> str:
    counts: Counter[str] = Counter()
    for answer in selected:
        label = answer.split(".")[0].strip()
        genre = GENRE_OPTIONS.get(label)
        if genre:
            counts[genre] += 1

    if not counts:
        return "드라마"

    max_score = max(counts.values())
    top_genres = [genre for genre, score in counts.items() if score == max_score]
    priority = ["로맨스", "드라마", "액션", "SF", "판타지", "코미디"]
    for genre in priority:
        if genre in top_genres:
            return genre
    return top_genres[0]


def fetch_movies(api_key_value: str, genre_id: int) -> List[Dict[str, str]]:
    response = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        params={
            "api_key": api_key_value,
            "with_genres": genre_id,
            "language": "ko-KR",
            "sort_by": "popularity.desc",
        },
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[:5]


# 결과 보기 버튼
if st.button("결과 보기", type="primary", use_container_width=True):
    # 미선택 질문 체크(선택 안 했으면 안내)
    if any(a is None for a in answers):
        st.warning("모든 질문에 답해줘야 결과를 볼 수 있어요! 😊")
    elif not api_key:
        st.warning("사이드바에 TMDB API Key를 입력해주세요!")
    else:
        with st.spinner("답변을 분석하고 추천 영화를 찾고 있어요..."):
            selected_genre = analyze_answers(answers)
            genre_id = GENRE_IDS.get(selected_genre, GENRE_IDS["드라마"])
            try:
                movies = fetch_movies(api_key, genre_id)
            except requests.RequestException:
                st.error("TMDB API 호출에 실패했습니다. API Key를 확인해주세요.")
                st.stop()

        st.subheader(f"당신의 추천 장르: {selected_genre}")
        st.write(GENRE_REASON.get(selected_genre, "당신의 취향에 맞춘 추천입니다."))
        st.divider()

        if not movies:
            st.info("추천할 영화가 아직 없어요. 잠시 후 다시 시도해주세요.")
        else:
            for movie in movies:
                title = movie.get("title") or movie.get("name") or "제목 없음"
                rating = movie.get("vote_average")
                overview = movie.get("overview") or "줄거리 정보가 없습니다."
                poster_path = movie.get("poster_path")
                poster_url = (
                    f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                )

                st.markdown(f"### {title}")
                if rating is not None:
                    st.write(f"⭐ 평점: {rating:.1f}")
                else:
                    st.write("⭐ 평점: 정보 없음")

                cols = st.columns([1, 2])
                with cols[0]:
                    if poster_url:
                        st.markdown(
                            f"""
                            <div class="poster-frame">
                                <img src="{poster_url}" alt="{title} 포스터" />
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.write("포스터가 없습니다.")
                with cols[1]:
                    st.write(overview)
                    st.write(
                        f"이 영화를 추천하는 이유: {GENRE_REASON.get(selected_genre, '당신의 선택과 잘 어울려요!')}"
                    )

                st.divider()
