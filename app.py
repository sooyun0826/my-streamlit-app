from collections import Counter
from typing import Dict, List

import requests
import streamlit as st

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #2b0b0b 0%, #120606 60%, #050101 100%);
        color: #f7f1e1;
    }
    .app-shell {
        background: rgba(14, 7, 7, 0.72);
        border: 1px solid rgba(255, 215, 150, 0.2);
        border-radius: 24px;
        padding: 24px 28px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.55);
    }
    .marquee {
        font-size: 0.95rem;
        letter-spacing: 0.2em;
        color: #f6d365;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .poster-frame {
        border: 6px solid #f6d365;
        border-radius: 16px;
        padding: 8px;
        background: #1b0c0c;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.4);
        width: fit-content;
    }
    .poster-frame img {
        display: block;
        border-radius: 12px;
        max-width: 320px;
    }
    .ticket {
        background: linear-gradient(145deg, #3b1111, #2a0a0a);
        border: 1px dashed rgba(246, 211, 101, 0.6);
        border-radius: 18px;
        padding: 12px 18px;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 제목 & 소개
st.markdown("<div class='app-shell'>", unsafe_allow_html=True)
st.markdown("<div class='marquee'>CINEMA NIGHT</div>", unsafe_allow_html=True)
st.title("🎬 나와 어울리는 영화는?")
st.write("5가지 질문에 답하면, 오늘 밤 영화관에서 보고 싶은 무드를 찾아드려요. 🎞️🍿")
st.caption("조명이 은은하게 켜지고, 스크린이 열리는 순간을 떠올리며 골라보세요.")

st.divider()

with st.sidebar:
    st.header("TMDB 설정")
    api_key = st.text_input("TMDB API Key", type="password")
    st.caption("TMDB에서 발급받은 API Key를 입력하세요.")

# 질문 & 선택지 (일상 속 선택)
questions = [
    {
        "q": "Q1. 바쁜 하루를 마친 저녁, 지금 가장 하고 싶은 건?",
        "options": [
            "A. 잔잔한 음악과 함께 조용히 하루를 정리한다",
            "B. 친구들과 즉흥적으로 신나는 계획을 세운다",
            "C. 집에서 몰입할 콘텐츠로 다른 세계에 빠진다",
            "D. 가볍게 웃을 수 있는 것부터 찾는다",
        ],
    },
    {
        "q": "Q2. 누군가와 하루를 함께 보낸 뒤, 가장 중요하게 느끼는 건?",
        "options": [
            "A. 서로의 감정이 편안했는지, 분위기가 좋았는지",
            "B. 함께한 시간이 알차고 성과가 있었는지",
            "C. 새로운 아이디어나 색다른 경험이 있었는지",
            "D. 기억에 남는 웃긴 순간이 있었는지",
        ],
    },
    {
        "q": "Q3. 새로운 한 주가 시작될 때, 은근히 기대하는 건?",
        "options": [
            "A. 사람들과 자연스럽게 가까워지는 순간",
            "B. 새로운 도전 속에서 에너지가 솟는 느낌",
            "C. 낯선 환경에서 신선한 자극을 받는 경험",
            "D. 예상치 못한 유쾌한 만남",
        ],
    },
    {
        "q": "Q4. 오늘 밤 내가 주인공이라면, 가장 끌리는 분위기는?",
        "options": [
            "A. 감정의 흐름 속에서 성장하는 인물",
            "B. 스피드하게 위기를 돌파하는 인물",
            "C. 미지의 세계를 탐험하는 인물",
            "D. 분위기를 유쾌하게 만드는 인물",
        ],
    },
    {
        "q": "Q5. 오늘 밤 한 편을 고른다면, 기준은?",
        "options": [
            "A. 여운이 남고 마음을 울리는 이야기",
            "B. 몰입감이 강하고 에너지가 폭발하는 전개",
            "C. 현실을 잠시 잊게 해주는 몰입형 설정",
            "D. 편하게 웃으며 즐길 수 있는 분위기",
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
                    st.markdown(
                        f"<div class='ticket'>이 영화를 추천하는 이유: {GENRE_REASON.get(selected_genre, '당신의 선택과 잘 어울려요!')}</div>",
                        unsafe_allow_html=True,
                    )

                st.divider()

st.markdown("</div>", unsafe_allow_html=True)
