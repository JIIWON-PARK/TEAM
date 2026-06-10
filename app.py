import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import os

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="혼공 — 자유인가, 고립인가?",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 색상 팔레트 ──────────────────────────────────────────
COLOR = {
    "자발 혼공자":       "#7F77DD",
    "비자발 혼공자":      "#1D9E75",
    "동행자 부족 관람 포기층": "#D85A30",
    "bg_purple": "#EEEDFE",
    "bg_teal":   "#E1F5EE",
    "bg_coral":  "#FAECE7",
}

# ── DB 연결 ──────────────────────────────────────────────
# Streamlit Cloud 호환: __file__ 대신 절대경로로 찾기
_here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
DB_PATH = os.path.join(_here, "HG_add.db")
# 못 찾으면 현재 작업 디렉토리에서 재시도
if not os.path.exists(DB_PATH):
    DB_PATH = "HG_add.db"

@st.cache_data
def load(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ── 데이터 로드 ───────────────────────────────────────────
grp   = load("SELECT * FROM result_group_comparison")
genre = load("SELECT * FROM result_genre_solo_isolation")
hh    = load("SELECT year, value FROM add_kosis_one_person_household_long WHERE region='전국' AND gender='계' AND item='1인가구' ORDER BY year")
barrier_income = load("SELECT class2 as 소득구간, value as 비율 FROM add_kosis_culture_barrier_long WHERE item='함께 관람할 사람 없음' AND year=2024 AND class1='가구소득별' ORDER BY value DESC")
barrier_age    = load("SELECT class2 as 연령대, value as 비율 FROM add_kosis_culture_barrier_long WHERE item='함께 관람할 사람 없음' AND year=2024 AND class1='연령별' ORDER BY value DESC")
barrier_hh     = load("SELECT class2 as 가구원수, value as 비율 FROM add_kosis_culture_barrier_long WHERE item='함께 관람할 사람 없음' AND year=2024 AND class1='동거가구원수별'")
grp_order = ["자발 혼공자", "비자발 혼공자", "동행자 부족 관람 포기층"]
grp["hongong_group"] = pd.Categorical(grp["hongong_group"], categories=grp_order, ordered=True)
grp = grp.sort_values("hongong_group")

# ── 사이드바 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎭 혼공 분석")
    st.divider()
    page = st.radio(
        "섹션 선택",
        ["📌 연구 개요","📈 배경 트렌드","📊 STEP 1 — 두 집단", "🔄 STEP 2 — 교차 패턴", "🚫 STEP 3 — 통계 밖"],
        index=0,
    )
    st.divider()
    st.caption("데이터 출처")
    st.caption("• 문화체육관광부 국민문화예술활동조사 2023")
    st.caption("• KOSSDA 한국인의식가치관조사")
    st.caption("• MDIS 국민여가활동조사 2018~2023")
    st.caption("• 통계청 사회조사 1인가구 통계")

# ── 헬퍼: 컬러 매핑 ──────────────────────────────────────
def grp_colors(groups):
    return [COLOR.get(g, "#888780") for g in groups]

# ════════════════════════════════════════════════════════════
# 페이지 1 — 연구 개요
# ════════════════════════════════════════════════════════════
if page == "📌 연구 개요":
    st.title("혼공 — 자유인가, 고립인가?")
    st.markdown("#### 같은 숫자, 다른 현실")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""<div style='background:{COLOR["bg_purple"]};border-left:4px solid {COLOR["자발 혼공자"]};
            border-radius:0 8px 8px 0;padding:14px 16px;'>
            <div style='font-size:11px;color:#888780;margin-bottom:4px'>STEP 1</div>
            <div style='font-size:14px;font-weight:600;color:#3C3489'>혼공자 안의 두 집단</div>
            <div style='font-size:12px;color:#5F5E5A;margin-top:6px'>자발 vs 비자발 — 같은 행위, 다른 맥락</div>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"""<div style='background:{COLOR["bg_teal"]};border-left:4px solid {COLOR["비자발 혼공자"]};
            border-radius:0 8px 8px 0;padding:14px 16px;'>
            <div style='font-size:11px;color:#888780;margin-bottom:4px'>STEP 2</div>
            <div style='font-size:14px;font-weight:600;color:#085041'>교차 패턴 발견</div>
            <div style='font-size:12px;color:#5F5E5A;margin-top:6px'>기능적·구조적 고립이 반대 방향으로 작용</div>
            </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(
            f"""<div style='background:{COLOR["bg_coral"]};border-left:4px solid {COLOR["동행자 부족 관람 포기층"]};
            border-radius:0 8px 8px 0;padding:14px 16px;'>
            <div style='font-size:11px;color:#888780;margin-bottom:4px'>STEP 3</div>
            <div style='font-size:14px;font-weight:600;color:#712B13'>통계 밖의 포기층</div>
            <div style='font-size:12px;color:#5F5E5A;margin-top:6px'>가장 고독한 사람은 혼공 통계에 없다</div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 핵심 연구 질문")
    st.markdown(
        """<div style='background:#1e1e2e;border-radius:8px;padding:20px 24px;'>
        <p style='color:#D3D1C7;font-style:italic;font-size:15px;line-height:1.8;margin:0'>
        "혼공 통계 뒤에 두 개의 다른 현실이 존재하는가?<br>
        그리고 가장 깊은 고독은 혼공 통계 밖에 있는가?"
        </p></div>""", unsafe_allow_html=True)

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 분석 대상")
        st.markdown("""
| 집단 | n | 정의 |
|---|---|---|
| 자발 혼공자 | 79명 | 동반자 있어도 혼자 선택 |
| 비자발 혼공자 | 13명 | 동반자 없어서 혼자 관람 |
| 동행자 부족 포기층 | 79명 | 동반자 없어 관람 포기 |
        """)
    with col_b:
        st.markdown("#### 데이터셋")
        st.markdown("""
| 데이터 | 용도 |
|---|---|
| 국민문화예술활동조사 2023 | 메인 분석 (n=10,182) |
| KOSSDA 한국인의식가치관조사 | 고립 수준 보조지표 |
| 국민여가활동조사 2018~2023 | 혼공 트렌드 배경 맥락 |
| 통계청 사회조사 1인가구 통계 | 고립점수 집계 매핑  |
        """)

# ════════════════════════════════════════════════════════════
# 페이지 2 — 배경 트렌드
# ════════════════════════════════════════════════════════════
elif page == "📈 배경 트렌드":
    st.title("배경 트렌드 — 1인가구 증가와 혼공률")
    st.divider()

    st.markdown("### 1인가구 수 추이 (전국, 2017~2024)")
    hh["만가구"] = (hh["value"] / 10000).round(1)
    fig_hh2 = go.Figure(go.Scatter(
        x=hh["year"], y=hh["만가구"],
        mode="lines+markers+text",
        line=dict(color=COLOR["자발 혼공자"], width=3),
        marker=dict(size=8, color=COLOR["자발 혼공자"]),
        fill="tozeroy",
        fillcolor="rgba(127,119,221,0.08)",
        text=[f"{v}만" for v in hh["만가구"]],
        textposition="top center",
    ))
    fig_hh2.update_layout(
        height=320,
        xaxis=dict(tickvals=hh["year"].tolist(), ticktext=[str(y) for y in hh["year"]]),
        yaxis=dict(range=[500, 870], title="만 가구"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"), margin=dict(l=60,r=20,t=20,b=40),
        showlegend=False,
    )
    st.plotly_chart(fig_hh2, use_container_width=True)
    st.caption("562만(2017) → 804만(2024) · 전체 가구의 35% · 출처: KOSIS")

    st.divider()
    st.markdown("### 문화예술관람 중 혼공 비율 추이 (국민여가활동조사 원시데이터 가중 집계)")

    trend_data = pd.DataFrame({
        "연도": [2018, 2019, 2020, 2021, 2022, 2023],
        "혼공률": [60.5, 57.0, 60.4, 66.8, 54.2, 51.1],
        "참여율": [70.4, 70.5, 64.3, 46.0, 47.2, 50.8],
        "코로나": [False, False, True, True, False, False],
    })

    fig_trend = go.Figure()
    # 코로나 구간 음영
    fig_trend.add_vrect(x0=2019.5, x1=2021.5,
                        fillcolor="rgba(216,90,48,0.08)",
                        layer="below", line_width=0,
                        annotation_text="코로나", annotation_position="top left",
                        annotation_font_color="#D85A30")
    # 추세선 (코로나 제외)
    fig_trend.add_trace(go.Scatter(
        x=[2018,2019,None,2022,2023], y=[60.5,57.0,None,54.2,51.1],
        mode="lines", line=dict(color=COLOR["동행자 부족 관람 포기층"], width=1.5, dash="dot"),
        name="코로나 제외 추세", hoverinfo="skip",
    ))
    # 실제 혼공률
    fig_trend.add_trace(go.Scatter(
        x=trend_data["연도"], y=trend_data["혼공률"],
        mode="lines+markers+text",
        line=dict(color=COLOR["자발 혼공자"], width=3),
        marker=dict(size=[10 if c else 8 for c in trend_data["코로나"]],
                    color=[COLOR["동행자 부족 관람 포기층"] if c else COLOR["자발 혼공자"]
                           for c in trend_data["코로나"]]),
        text=[f"{v}%" for v in trend_data["혼공률"]],
        textposition="top center",
        name="혼공률 (가중)",
    ))
    fig_trend.update_layout(
        height=340,
        xaxis=dict(tickvals=trend_data["연도"].tolist()),
        yaxis=dict(range=[44,72], title="혼공 비율 (%)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=60,r=20,t=30,b=80),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown(
        f"""<div style='background:{COLOR["bg_purple"]};border-left:4px solid {COLOR["자발 혼공자"]};
        border-radius:0 8px 8px 0;padding:12px 16px;'>
        <strong style='color:#3C3489'>반전 포인트:</strong>
        <span style='color:#3C3489'> 코로나를 제외하면 혼공률은 2018→2023 꾸준히 하락(60.5%→51.1%).
        1인가구는 우상향인데 혼공은 감소 — "혼공 증가" 담론 이면에 구조적 원인이 있다.</span>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 문화예술관람 참여율 변화")
    fig_part = go.Figure(go.Bar(
        x=trend_data["연도"],
        y=trend_data["참여율"],
        marker_color=[COLOR["동행자 부족 관람 포기층"] if c else COLOR["비자발 혼공자"]
                      for c in trend_data["코로나"]],
        text=[f"{v}%" for v in trend_data["참여율"]],
        textposition="outside",
    ))
    fig_part.update_layout(
        height=260, yaxis=dict(range=[38,80], title="참여율 (%)"),
        xaxis=dict(tickvals=trend_data["연도"].tolist()),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"), showlegend=False,
        margin=dict(l=60,r=20,t=10,b=40),
    )
    st.plotly_chart(fig_part, use_container_width=True)
    st.caption("2021년 참여율 46%로 급락 (코로나 영향) — 이때 관람 포기층이 대량 발생했을 가능성")

# ════════════════════════════════════════════════════════════
# 페이지 3 — STEP 1
# ════════════════════════════════════════════════════════════
elif page == "📊 STEP 1 — 두 집단":
    st.title("STEP 1 — 혼공자 안의 두 집단")
    st.markdown("혼공자 306명(전체 3%) 안에서 **12.4%가 동반자 부재를 어려움으로 응답** — 같은 혼공, 다른 현실")
    st.divider()

    # 1인가구 비율 가로 막대
    st.markdown("### 1인가구 비율 — 집단별 비교")
    one_p = grp[["hongong_group","one_person_rate"]].copy()
    # 비혼공자 추가
    extra = pd.DataFrame({"hongong_group":["비혼공자(참고)"], "one_person_rate":[15.94]})
    one_p = pd.concat([one_p, extra], ignore_index=True)
    colors_1p = grp_colors(one_p["hongong_group"]) + ["#B4B2A9"]

    fig1 = go.Figure(go.Bar(
        x=one_p["one_person_rate"],
        y=one_p["hongong_group"],
        orientation="h",
        marker_color=[COLOR.get(g, "#B4B2A9") for g in one_p["hongong_group"]],
        text=[f"{v:.1f}%" for v in one_p["one_person_rate"]],
        textposition="outside",
    ))
    fig1.update_layout(
        height=250, xaxis_title="1인가구 비율 (%)",
        xaxis=dict(range=[0, 60]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=60,t=10,b=10),
        font=dict(family="Arial"),
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("혼공자는 비혼공자 대비 1인가구 비율 약 2.6배 높음")

    st.divider()
    st.markdown("### 5개 지표 레이더 — 3집단 프로파일")

    categories = ["구조적 고립점수\n(×25배 스케일)", "1인가구 비율(%)", "저소득 비율(%)",
                  "사회건강 취약(%)", "정신건강 취약(%)"]

    def radar_vals(row):
        return [
            row["avg_structural_isolation_score"] * 25,
            row["one_person_rate"],
            row["low_income_rate"],
            row["low_social_health_rate"],
            row["low_mental_health_rate"],
        ]

    fig2 = go.Figure()
    for _, row in grp.iterrows():
        g = row["hongong_group"]
        vals = radar_vals(row)
        fig2.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=g,
            line_color=COLOR.get(g, "#888780"),
            fillcolor=COLOR.get(g, "#888780"),
            opacity=0.15 if g != "동행자 부족 관람 포기층" else 0.2,
            line_width=2.5 if g == "동행자 부족 관람 포기층" else 2,
        ))
    fig2.update_layout(
        height=420,
        polar=dict(radialaxis=dict(visible=True, range=[0, 50])),
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=60,r=60,t=20,b=60),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("### 집단별 세부 지표 비교")
    metrics = ["one_person_rate","low_income_rate","low_social_health_rate","low_mental_health_rate"]
    labels  = ["1인가구(%)", "저소득(%)", "사회건강취약(%)", "정신건강취약(%)"]

    fig3 = go.Figure()
    for _, row in grp.iterrows():
        g = row["hongong_group"]
        fig3.add_trace(go.Bar(
            name=g,
            x=labels,
            y=[row[m] for m in metrics],
            marker_color=COLOR.get(g, "#888780"),
            text=[f"{row[m]:.1f}%" for m in metrics],
            textposition="outside",
        ))
    fig3.update_layout(
        height=350, barmode="group",
        yaxis_title="비율 (%)", yaxis=dict(range=[0,60]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=0,r=0,t=10,b=80),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.info("**주목:** 포기층의 사회건강 취약(18.99%)은 자발 혼공자(8.86%)의 2.1배, 정신건강 취약(15.19%)은 4.0배 수준")

# ════════════════════════════════════════════════════════════
# 페이지 4 — STEP 2
# ════════════════════════════════════════════════════════════
elif page == "🔄 STEP 2 — 교차 패턴":
    st.title("STEP 2 — 두 고립 축의 교차 패턴")
    st.markdown("기능적·구조적 고립이 세 집단에서 **정반대 순위**를 보인다")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 구조적 고립점수 (D1 단독, 0~4점)")
        st.caption("저소득 + 사회건강취약 + 정신건강취약 + 1인가구 합산")
        fig_s = go.Figure(go.Bar(
            x=grp["hongong_group"],
            y=grp["avg_structural_isolation_score"],
            marker_color=grp_colors(grp["hongong_group"]),
            text=[f"{v:.2f}" for v in grp["avg_structural_isolation_score"]],
            textposition="outside",
        ))
        fig_s.update_layout(
            height=280, yaxis=dict(range=[0,1.4], title="점수"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial"), margin=dict(l=0,r=0,t=10,b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_s, use_container_width=True)
        st.caption("**포기층 > 자발 > 비자발** — 구조적으로 가장 취약한 집단이 관람을 포기")

    with col2:
        st.markdown("#### 기능적 고립점수 (KOSSDA 집계 매핑)")
        st.caption("도움 요청 가능 대상 없음 응답 기반 — 성별×연령×가구형태 16개 셀 평균")
        fig_k = go.Figure(go.Bar(
            x=grp["hongong_group"],
            y=grp["avg_kossda_group_isolation_score"],
            marker_color=grp_colors(grp["hongong_group"]),
            text=[f"{v:.2f}" for v in grp["avg_kossda_group_isolation_score"]],
            textposition="outside",
        ))
        fig_k.update_layout(
            height=280, yaxis=dict(range=[2.0, 2.45], title="점수"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial"), margin=dict(l=0,r=0,t=10,b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_k, use_container_width=True)
        st.caption("**자발 ≈ 비자발 > 포기층** — 기능적으로 고립된 사람이 오히려 혼공을 함")

    st.divider()
    st.markdown("### 두 축의 교차 — 집단별 순위가 반전된다")

    fig_cross = go.Figure()
    x_labels = ["구조적 고립점수", "기능적 고립점수 (KOSSDA)"]
    for _, row in grp.iterrows():
        g = row["hongong_group"]
        fig_cross.add_trace(go.Scatter(
            x=x_labels,
            y=[row["avg_structural_isolation_score"], row["avg_kossda_group_isolation_score"]],
            mode="lines+markers+text",
            name=g,
            line=dict(color=COLOR.get(g,"#888780"), width=3,
                      dash="dot" if g=="비자발 혼공자" else "solid"),
            marker=dict(size=12, color=COLOR.get(g,"#888780")),
            text=[f"{row['avg_structural_isolation_score']:.2f}",
                  f"{row['avg_kossda_group_isolation_score']:.2f}"],
            textposition=["middle left","middle right"],
            textfont=dict(size=12, color=COLOR.get(g,"#888780")),
        ))
    fig_cross.update_layout(
        height=360, yaxis_title="점수",
        xaxis=dict(tickfont=dict(size=13)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=60,r=80,t=20,b=80),
    )
    st.plotly_chart(fig_cross, use_container_width=True)

    st.markdown(
        f"""<div style='background:{COLOR["bg_coral"]};border-left:4px solid {COLOR["동행자 부족 관람 포기층"]};
        border-radius:0 8px 8px 0;padding:14px 16px;'>
        <strong style='color:#712B13'>핵심 역설:</strong>
        <span style='color:#712B13'> 기능적으로 고립(관계망 없음)된 사람은 오히려 공연장을 찾는다.
        구조적으로 취약(저소득·건강)한 사람은 공연장 자체를 못 간다.
        두 차원이 문화 접근에 정반대로 작용한다. — Cacioppo & Patrick (2008)</span>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 장르별 혼공률 vs 고립점수")
    fig_genre = go.Figure()
    for _, row in genre.iterrows():
        fig_genre.add_trace(go.Scatter(
            x=[row["solo_rate"]], y=[row["avg_kossda_group_isolation_score"]],
            mode="markers+text",
            name=row["genre_name"],
            marker=dict(size=row["viewed_n"]**0.45, opacity=0.7),
            text=[row["genre_name"]],
            textposition="top center",
        ))
    fig_genre.update_layout(
        height=350,
        xaxis_title="혼공 관람률 (%)",
        yaxis_title="기능적 고립점수 (KOSSDA)",
        xaxis=dict(range=[0, 15]),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"),
        margin=dict(l=60,r=20,t=20,b=60),
    )
    st.plotly_chart(fig_genre, use_container_width=True)
    st.caption("버블 크기 = 관람자 수 · 무용(11.76%)·서양음악(9.13%)이 혼공률 높음")

# ════════════════════════════════════════════════════════════
# 페이지 5 — STEP 3
# ════════════════════════════════════════════════════════════
elif page == "🚫 STEP 3 — 통계 밖":
    st.title("STEP 3 — 가장 고독한 사람은 통계 밖에 있다")
    st.markdown("동행자 부족 포기층(79명) — 혼공 통계에 포착되지 않는 집단")
    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("사회건강 취약", "18.99%", delta="자발 대비 +10.13%p", delta_color="inverse")
    with c2:
        st.metric("정신건강 취약", "15.19%", delta="자발 대비 +11.39%p", delta_color="inverse")
    with c3:
        st.metric("저소득 비율", "39.24%", delta="3집단 중 최고 수준", delta_color="inverse")

    st.divider()
    st.markdown("### 포기층 vs 자발 혼공자 — 4개 지표 직접 비교")

    포기 = grp[grp["hongong_group"]=="동행자 부족 관람 포기층"].iloc[0]
    자발 = grp[grp["hongong_group"]=="자발 혼공자"].iloc[0]
    metrics = ["low_social_health_rate","low_mental_health_rate","low_income_rate","one_person_rate"]
    labels  = ["사회건강취약(%)","정신건강취약(%)","저소득(%)","1인가구(%)"]

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        name="동행자 부족 관람 포기층", x=labels,
        y=[포기[m] for m in metrics],
        marker_color=COLOR["동행자 부족 관람 포기층"],
        text=[f"{포기[m]:.1f}%" for m in metrics], textposition="outside",
    ))
    fig_cmp.add_trace(go.Bar(
        name="자발 혼공자", x=labels,
        y=[자발[m] for m in metrics],
        marker_color=COLOR["자발 혼공자"],
        text=[f"{자발[m]:.1f}%" for m in metrics], textposition="outside",
    ))
    fig_cmp.update_layout(
        height=360, barmode="group",
        yaxis=dict(range=[0,56], title="비율 (%)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=0,r=0,t=10,b=80),
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.divider()
    st.markdown("### '함께 관람할 사람 없음' 장벽 — 소득별")
    fig_inc = go.Figure(go.Bar(
        x=barrier_income["비율"],
        y=barrier_income["소득구간"],
        orientation="h",
        marker_color=[COLOR["동행자 부족 관람 포기층"] if v >= 9.0 else "#B4B2A9"
                      for v in barrier_income["비율"]],
        text=[f"{v}%" for v in barrier_income["비율"]],
        textposition="outside",
    ))
    fig_inc.update_layout(
        height=280, xaxis=dict(range=[0,20], title="응답 비율 (%)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial"), margin=dict(l=0,r=60,t=10,b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_inc, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 가구원수별")
        fig_hh = go.Figure(go.Bar(
            x=barrier_hh["가구원수"], y=barrier_hh["비율"],
            marker_color=[COLOR["동행자 부족 관람 포기층"] if g=="1인" else "#B4B2A9"
                          for g in barrier_hh["가구원수"]],
            text=[f"{v}%" for v in barrier_hh["비율"]], textposition="outside",
        ))
        fig_hh.update_layout(
            height=220, yaxis=dict(range=[0,16]),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial"), margin=dict(l=0,r=0,t=10,b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_hh, use_container_width=True)

    with col_b:
        st.markdown("#### 연령별")
        fig_age = go.Figure(go.Bar(
            x=barrier_age["연령대"], y=barrier_age["비율"],
            marker_color=[COLOR["동행자 부족 관람 포기층"] if v >= 5.0 else "#B4B2A9"
                          for v in barrier_age["비율"]],
            text=[f"{v}%" for v in barrier_age["비율"]], textposition="outside",
        ))
        fig_age.update_layout(
            height=220, yaxis=dict(range=[0,14]),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial"), margin=dict(l=0,r=0,t=10,b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_age, use_container_width=True)

    st.markdown(
        f"""<div style='background:#1e1e2e;border-radius:8px;padding:16px 20px;margin-top:12px'>
        <p style='color:#9FE1CB;font-style:italic;font-size:14px;line-height:1.8;margin:0'>
        "혼공 증가는 가장 고독한 집단의 배제를 은폐할 수 있다"
        </p></div>""", unsafe_allow_html=True)


