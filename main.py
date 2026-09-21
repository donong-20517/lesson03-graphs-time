import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.title("영화 데이터 그래프 도감 1 - 시간")
st.write("1년치 일별 박스오피스 데이터를 이용해 영화의 시간에 따른 관객 변화를 살펴봅니다.")

# ─────────────────────────────────────────────
# 데이터 불러오기
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열을 실제 날짜(datetime)로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    # 숫자형 열 정리
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 영화코드는 문자열로 유지
    df["영화코드"] = df["영화코드"].astype(str)

    return df.dropna(subset=["날짜", "영화명"])


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# ─────────────────────────────────────────────
# 그래프 1. 날짜별 일관객 변화
# ─────────────────────────────────────────────
st.header("그래프 1. 영화별 날짜에 따른 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list,
    index=0,
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    .copy()
)

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        title="날짜",
    ),
    yaxis=dict(
        tickformat=",",
        title="일관객(명)",
    ),
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_input(
    "그래프 1 해석 문구",
    placeholder="예: 개봉 직후 관객이 크게 늘었다가 시간이 지나면서 감소하는 흐름을 볼 수 있다.",
    key="graph1_note",
    label_visibility="collapsed",
)


# ─────────────────────────────────────────────
# 그래프 2. 앞으로 추가할 공간
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 2. 추가 예정")

st.info("앞으로 시간과 관련된 새로운 그래프를 이 구역에 추가할 수 있습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_input(
    "그래프 2 해석 문구",
    placeholder="추가할 그래프의 해석 문구를 입력할 수 있는 자리입니다.",
    key="graph2_note",
    label_visibility="collapsed",
)
