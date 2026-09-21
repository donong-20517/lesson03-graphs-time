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
# 그래프 2. 기간 일관객 합계 상위 5편 비교
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 2. 기간 일관객 합계 상위 5편")

# 이 기간에 기록된 일관객의 합계를 영화별로 계산하여 상위 5편을 선정
top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화명"]
    .tolist()
)

top5_df = (
    df[df["영화명"].isin(top5_movies)]
    .groupby(["날짜", "영화명"], as_index=False)["일관객"]
    .sum()
    .sort_values(["날짜", "영화명"])
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=False,
    title="일관객 합계 상위 5편의 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객",
        "영화명": "영화",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
        "영화명": True,
    },
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}<br>"
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명<extra></extra>"
    )
)

fig2.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        title="날짜",
    ),
    yaxis=dict(
        tickformat=",",
        title="일관객(명)",
    ),
    legend=dict(
        title="영화",
    ),
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_input(
    "그래프 2 해석 문구",
    placeholder="예: 기간 전체에서 관객이 많이 든 영화들의 일별 관객 변화 흐름을 비교할 수 있다.",
    key="graph2_note",
    label_visibility="collapsed",
)


# ─────────────────────────────────────────────
# 그래프 3. 날짜별 10위권 일관객 합계
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

# 합계가 가장 큰 날짜 3일
top3_days = (
    daily_total.nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    markers=False,
    title="날짜별 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계",
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

# 상위 3일을 그래프 위에 날짜와 함께 표시
for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=f"{row['날짜']:%Y-%m-%d}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-45,
        font=dict(size=12),
    )

fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 일관객 합계: %{y:,}명<extra></extra>"
)

fig3.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        title="날짜",
    ),
    yaxis=dict(
        tickformat=",",
        title="10위권 일관객 합계(명)",
    ),
    margin=dict(l=20, r=20, t=80, b=20),
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_input(
    "그래프 3 해석 문구",
    placeholder="예: 날짜에 따라 전체적인 영화 관객 규모가 어떻게 달라지는지 볼 수 있다.",
    key="graph3_note",
    label_visibility="collapsed",
)


# ─────────────────────────────────────────────
# 그래프 4. 기간 일관객 TOP 10
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 4. 기간 일관객 TOP 10")

movie_summary = (
    df.groupby("영화명")
    .agg(
        기간_일관객=("일관객", "sum"),
        10위권_등장일수=("날짜", "nunique"),
    )
    .reset_index()
    .sort_values("기간_일관객", ascending=False)
    .head(10)
    .sort_values("기간_일관객", ascending=True)
)

fig4 = px.bar(
    movie_summary,
    x="기간_일관객",
    y="영화명",
    orientation="h",
    title="영화별 기간 일관객 TOP 10",
    labels={
        "기간_일관객": "기간 일관객 합계",
        "영화명": "영화",
    },
    hover_data={
        "기간_일관객": ":,",
        "10위권_등장일수": True,
    },
)

fig4.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "기간 일관객 합계: %{x:,}명<br>"
        "10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    ),
    customdata=movie_summary[["10위권_등장일수"]].to_numpy(),
)

fig4.update_layout(
    xaxis=dict(
        tickformat=",",
        title="기간 일관객 합계(명)",
    ),
    yaxis=dict(
        title="",
    ),
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_input(
    "그래프 4 해석 문구",
    placeholder="예: 이 기간 동안 누적해서 가장 많은 관객을 모은 영화와 그 영화가 10위권에 머문 날수를 비교할 수 있다.",
    key="graph4_note",
    label_visibility="collapsed",
)


# ─────────────────────────────────────────────
# 그래프 5. 월 × 요일별 일관객 합계
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 5. 월 × 요일별 일관객 합계")

weekday_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month
heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek.map(
    dict(enumerate(weekday_order))
)

heatmap_data = (
    heatmap_df.groupby(["월", "요일"])["일관객"]
    .sum()
    .unstack(fill_value=0)
    .reindex(columns=weekday_order)
    .sort_index()
)

# Plotly heatmap은 행/열 순서를 데이터프레임의 순서대로 사용
fig5 = px.imshow(
    heatmap_data,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계",
    },
    x=weekday_order,
    y=[f"{month}월" for month in heatmap_data.index],
    color_continuous_scale="Blues",
    aspect="auto",
    title="월 × 요일별 10위권 일관객 합계",
)

fig5.update_traces(
    hovertemplate=(
        "월: %{y}<br>"
        "요일: %{x}<br>"
        "일관객 합계: %{z:,}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    xaxis=dict(
        title="요일",
        categoryorder="array",
        categoryarray=weekday_order,
    ),
    yaxis=dict(
        title="월",
    ),
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_input(
    "그래프 5 해석 문구",
    placeholder="예: 어떤 월과 요일에 영화관객이 상대적으로 많이 몰렸는지 한눈에 비교할 수 있다.",
    key="graph5_note",
    label_visibility="collapsed",
)
