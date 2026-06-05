import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="혼공 시각화 대시보드", layout="wide")

# --- 색상 팔레트 설정 ---
COLORS = {
    '자발': '#534AB7',      # 퍼플
    '비자발': '#1D9E75',    # 틸
    '포기': '#D85A30',      # 코랄
    '배경': '#F1EFE8',
    '다크': '#2C2C2A'
}

FONT_FAMILY = "Malgun Gothic, AppleGothic, sans-serif"

# --- DB 연결 함수 ---
def get_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

@st.cache_data
def load_data(db_file, query):
    try:
        conn = get_connection(db_file)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()

# --- 사이드바: DB 업로드 및 필터 ---
st.sidebar.title("📊 Data Control")
uploaded_file = st.sidebar.file_uploader("HG_add.db 파일을 업로드하세요", type=["db"])

db_path = "HG_add.db"
if uploaded_file is not None:
    with open("temp_db.db", "wb") as f:
        f.write(uploaded_file.getbuffer())
    db_path = "temp_db.db"

if not os.path.exists(db_path):
    st.warning("DB 파일이 없습니다. 파일을 업로드하거나 HG_add.db를 같은 경로에 두세요.")
    st.stop()

# --- 메인 타이틀 ---
st.title("혼공(混空): 자유인가, 고립인가?")
st.markdown("### “같은 숫자, 다른 현실: 혼자 공연 관람 뒤에 숨겨진 사회적 맥락”")
st.divider()

# --- 섹션 1: Overview ---
st.header("📈 Overview: 1인가구의 증가와 질문")
col1, col2 = st.columns([2, 1])

with col1:
    # 1인가구 추이 데이터 로드
    q1 = "SELECT year, value FROM add_kosis_one_person_household_long WHERE region='전국' AND gender='계' AND item='1인가구' ORDER BY year ASC"
    df_hh = load_data(db_path, q1)
    
    if not df_hh.empty:
        fig1 = px.line(df_hh, x='year', y='value', title="연도별 1인가구 수 추이 (전국)", markers=True)
        fig1.update_traces(line_color=COLORS['다크'], line_width=3)
        fig1.update_layout(font_family=FONT_FAMILY, template="plotly_white", yaxis_title="가구 수 (명)")
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("2017년 약 562만 → 2024년 약 804만으로 급격히 증가했습니다.")

with col2:
    st.info("#### 핵심 질문")
    st.markdown("- **혼공 통계 뒤에 두 개의 다른 현실이 존재하는가?**")
    st.markdown("- **가장 깊은 고독은 혼공 통계 밖에 있는가?**")
    st.write("1인가구는 증가했지만, 모든 혼공이 자발적 선택에 의한 '자유'는 아닐 수 있습니다.")

# --- 섹션 2: STEP 1 ---
st.divider()
st.header("STEP 1. 혼공자 안의 두 집단")

q2 = "SELECT * FROM result_group_comparison"
df_group = load_data(db_path, q2)

if not df_group.empty:
    # n값 시각화
    fig_n = px.bar(df_group, x='hongong_group', y='n', color='hongong_group', 
                   color_discrete_map={'자발 혼공자': COLORS['자발'], '비자발 혼공자': COLORS['비자발'], '동행자 부족 관람 포기층': COLORS['포기']},
                   text_auto=True, title="집단별 규모 (n)")
    st.plotly_chart(fig_n, use_container_width=True)
    st.warning("⚠️ 비자발 혼공자 표본 수가 13명으로 작으므로 해석 시 주의가 필요합니다.")

    # 취약지표 비교
    metrics = ['one_person_rate', 'low_income_rate', 'low_social_health_rate', 'low_mental_health_rate']
    df_melted = df_group.melt(id_vars='hongong_group', value_vars=metrics, var_name='indicator', value_name='percentage')
    
    fig_metrics = px.bar(df_melted, x='indicator', y='percentage', color='hongong_group', barmode='group',
                         color_discrete_map={'자발 혼공자': COLORS['자발'], '비자발 혼공자': COLORS['비자발'], '동행자 부족 관람 포기층': COLORS['포기']},
                         title="집단별 사회·경제적 취약성 비교")
    fig_metrics.update_layout(yaxis_title="비율 (%)", font_family=FONT_FAMILY)
    st.plotly_chart(fig_metrics, use_container_width=True)
    st.write("**“같은 혼공이지만 이면의 사회적 맥락은 확연히 다릅니다.”** 자발 혼공자는 1인가구 비율(44.3%)이 높지만 다른 취약성은 낮은 반면, 포기층은 사회·정신건강 취약율이 상대적으로 높습니다.")

# --- 섹션 3: STEP 2 ---
st.divider()
st.header("STEP 2. 예상 밖 교차 패턴")

if not df_group.empty:
    df_iso = df_group.melt(id_vars='hongong_group', 
                           value_vars=['avg_structural_isolation_score', 'avg_kossda_group_isolation_score'],
                           var_name='isolation_type', value_name='score')
    
    fig_iso = px.bar(df_iso, x='hongong_group', y='score', color='isolation_type', barmode='group',
                     title="구조적 고립 vs 기능적(그룹) 고립 점수",
                     labels={'avg_structural_isolation_score': '구조적 고립', 'avg_kossda_group_isolation_score': '기능적 고립'})
    fig_iso.update_layout(font_family=FONT_FAMILY)
    st.plotly_chart(fig_iso, use_container_width=True)
    
    st.markdown(f"""
    > **핵심 발견:** 기능적 고립(동반자 부재)은 혼공의 형태를 결정하지만, **구조적 고립점수({df_group.loc[df_group['hongong_group']=='동행자 부족 관람 포기층', 'avg_structural_isolation_score'].values[0]:.2f})**가 높은 층은 관람 가능성 자체가 차단될 수 있습니다.
    """)

# --- 섹션 4: STEP 3 ---
st.divider()
st.header("STEP 3. 통계 밖의 포기층")

c1, c2, c3, c4 = st.columns(4)
c1.metric("포기층 규모", "n=79")
c2.metric("사회건강취약", "18.99%")
c3.metric("정신건강취약", "15.19%")
c4.metric("구조적 고립점수", "1.08")

q3 = "SELECT item, value FROM add_kosis_culture_barrier_long WHERE class1='전체' AND class2='소계' AND year=2024 AND unit='%' ORDER BY value DESC"
df_barrier = load_data(db_path, q3)

if not df_barrier.empty:
    # 강조 색상 설정
    df_barrier['color'] = df_barrier['item'].apply(lambda x: COLORS['포기'] if '함께 관람할 사람 없음' in x else '#cccccc')
    
    fig_barr = px.bar(df_barrier, x='value', y='item', orientation='h', 
                      title="문화예술행사 직접 관람 걸림돌 (2024)",
                      text_auto='.1f')
    fig_barr.update_traces(marker_color=df_barrier['color'])
    fig_barr.update_layout(yaxis={'categoryorder':'total ascending'}, font_family=FONT_FAMILY)
    st.plotly_chart(fig_barr, use_container_width=True)
    st.write("**“동행자 부재는 실제 관람 장벽으로 나타납니다.”** 이들은 가고 싶은 의향이 있어도 혼공 대열에 합류하지 못한 채 통계 밖으로 밀려나 있습니다.")

# --- 섹션 5: Genre View ---
st.divider()
st.header("Genre View: 장르에 따라 다른 혼공의 양상")

q4 = "SELECT * FROM result_genre_solo_isolation"
df_genre = load_data(db_path, q4)

if not df_genre.empty:
    tab1, tab2 = st.tabs(["장르별 혼공률", "고립 점수와의 관계"])
    
    with tab1:
        fig_g1 = px.bar(df_genre.sort_values('solo_rate', ascending=True), 
                        x='solo_rate', y='genre_name', orientation='h',
                        title="장르별 혼공률 (%)", text_auto='.1f', color_discrete_sequence=[COLORS['자발']])
        st.plotly_chart(fig_g1, use_container_width=True)
        
    with tab2:
        fig_g2 = px.scatter(df_genre, x='solo_rate', y='avg_structural_isolation_score', 
                            size='viewed_n', text='genre_name',
                            title="장르별 혼공률과 구조적 고립점수 관계",
                            labels={'solo_rate': '혼공률 (%)', 'avg_structural_isolation_score': '평균 구조적 고립 점수'})
        fig_g2.update_traces(textposition='top center')
        st.plotly_chart(fig_g2, use_container_width=True)
    
    st.write("장르마다 혼공의 정도와 관람객의 특성이 다릅니다. 이는 혼공이 단일한 현상이 아님을 시사합니다.")

# --- 섹션 6: Conclusion ---
st.divider()
st.header("Conclusion: 요약 및 제언")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"### <span style='color:{COLORS['자발']}'>자발 혼공자</span>", unsafe_allow_html=True)
    st.write("- 관계망이 없어도 혼자 즐김\n- 1인가구 비율 높음\n- **자유로운 취향 소비자**")
with col_b:
    st.markdown(f"### <span style='color:{COLORS['비자발']}'>비자발 혼공자</span>", unsafe_allow_html=True)
    st.write("- 동반자가 없어서 혼자 감\n- 표본은 적으나 보완적 관람\n- **타협적 혼공**")
with col_c:
    st.markdown(f"### <span style='color:{COLORS['포기']}'>관람 포기층</span>", unsafe_allow_html=True)
    st.write("- 가고 싶어도 못 감\n- 구조적 고립 및 취약성 높음\n- **통계 밖의 고립**")

st.info("#### 📢 정책 제언\n1. **자발 혼공자**: 1인 좌석 확대 및 혼자 보기 편한 인프라 강화\n2. **비자발 혼공자**: 커뮤니티 기반 동반자 연결 매칭 프로그램\n3. **포기층**: 경제적 지원을 넘어선 사회적 관계망 및 접근성 지원")

st.markdown("---")
st.markdown("#### “혼공 증가는 가장 고독한 집단의 배제를 은폐할 수 있습니다.”")