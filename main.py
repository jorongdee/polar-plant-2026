# main.py — 극지식물 생육 분석 대시보드 (테마 디자인 적용 · 오류 수정)
import io
import os as _os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ────────────────────────────────────────────────────
# 테마 CSS  (극지·식물 컨셉: 깊은 숲 그린 + 새싹 포인트)
# ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
   font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}

/* 전체 배경: 깊은 숲 그라데이션 */
.stApp {
   background: linear-gradient(160deg, #0d2810 0%, #163d1a 55%, #1a4a25 100%) !important;
}

/* 메인 컨테이너 배경 투명 */
.css-18ni7ap, .main .block-container {
   background: transparent;
}

/* 카드 스타일 */
.green-card {
   background: linear-gradient(135deg, #1b4320 0%, #22552c 100%);
   border: 1px solid rgba(102, 187, 106, 0.25);
   border-radius: 14px;
   padding: 20px 24px;
   box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(102, 187, 106, 0.15);
   transition: all 0.25s ease;
}
.green-card:hover {
   box-shadow: 0 6px 28px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(102, 187, 106, 0.25);
   transform: translateY(-2px);
}

/* 탭 버튼 */
.stTabs [role="tab"] {
   background: transparent;
   color: #a5d6a7;
   font-weight: 500;
   border-bottom: 2px solid transparent;
   transition: all 0.2s ease;
}
.stTabs [role="tab"][aria-selected="true"] {
   background: rgba(102, 187, 106, 0.12);
   color: #66bb6a;
   border-bottom: 2px solid #66bb6a;
   font-weight: 600;
}

/* 버튼 */
.stButton > button {
   background: linear-gradient(135deg, #2e7d32, #388e3c);
   border: 1px solid #4caf50;
   border-radius: 8px;
   color: #e8f5e9;
   font-weight: 500;
   transition: all 0.25s ease;
}
.stButton > button:hover {
   background: linear-gradient(135deg, #1b5e20, #2e7d32);
   border-color: #66bb6a;
   color: #c8e6c9;
   box-shadow: 0 4px 12px rgba(102, 187, 106, 0.3);
}

/* metric 카드 배경 */
div.stMetric {
   background: rgba(27, 67, 32, 0.65);
   border: 1px solid rgba(102, 187, 106, 0.2);
   border-radius: 10px;
   padding: 8px 12px;
   backdrop-filter: blur(6px);
}

/* 사이드바 */
section.sidebar {
   background: linear-gradient(160deg, #0a1f0a 0%, #142e14 100%) !important;
   border-right: 1px solid rgba(102, 187, 106, 0.15);
}
section.sidebar .stMarkdown, section.sidebar p, section.sidebar li {
   color: #c8e6c9;
}
section.sidebar .stSelectbox, section.sidebar .stMultiSelect,
section.sidebar .stFileUploader {
   background: rgba(27, 67, 32, 0.6) !important;
   border: 1px solid rgba(102, 187, 106, 0.2);
   border-radius: 8px;
   color: #e8f5e9;
}

/* expander */
.stExpander {
   border: 1px solid rgba(102, 187, 106, 0.2);
   border-radius: 8px;
   background: rgba(27, 67, 32, 0.4);
}

/* info box */
div[data-testid="stInfo"] {
   background: rgba(33, 150, 122, 0.12);
   border-left: 4px solid #4db6ac;
   border-radius: 8px;
   color: #b2dfdb;
}

/* warning box */
div[data-testid="stWarning"] {
   background: rgba(239, 83, 80, 0.08);
   border-left: 4px solid #ef5350;
   border-radius: 8px;
   color: #ef9a9a;
}

/* metric 값 */
.stMetric .stMetricValue {
   color: #66bb6a;
   font-weight: 700;
}
.stMetric .stMetricLabel {
   color: #a5d6a7;
}

/* 스크롤바 */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(27, 67, 32, 0.3); }
::-webkit-scrollbar-thumb { background: #2e7d32; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #388e3c; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────
# 상단 헤더 배너
# ────────────────────────────────────────────────────
st.markdown("""
<div style="
   background: linear-gradient(90deg, #0a1f0a 0%, #1b4320 40%, #22552c 70%, #0a1f0a 100%);
   border-radius: 0 0 16px 16px;
   border-bottom: 2px solid rgba(102,187,106,0.3);
   padding: 18px 28px 14px;
   display: flex;
   align-items: center;
   justify-content: center;
   gap: 16px;
   margin-bottom: 28px;
">
   <span style="font-size:32px;">🌿</span>
   <span style="
      background: linear-gradient(90deg, #66bb6a, #a5d6a7);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.5px;
   ">극지식물 생육 차이 분석</span>
   <span style="
      background: linear-gradient(90deg, #81c784, #4db6ac);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-size: 14px;
      font-weight: 400;
      opacity: 0.85;
   ">— 어떤 지표가 생장을 가장 잘 보여줄까?</span>
   <span style="font-size:28px; opacity:0.7;">🌱</span>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────
# CSV 인코딩 처리 (utf-8-sig → cp949)
# ────────────────────────────────────────────────────
@st.cache_data
def read_csv(file):
    if file is None:
        return pd.DataFrame()
    data = file.getvalue()
    for enc in ("utf-8-sig", "cp949"):
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc)
        except Exception:
            pass
    return pd.DataFrame()

# ────────────────────────────────────────────────────
# 열 이름 표준화
# ────────────────────────────────────────────────────
def std_cols(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    rename = {}
    for c in df.columns:
        k = c.lower().replace(" ", "")
        if k in ("time", "categories", "시간", "날짜", "datetime", "date"):
            rename[c] = "time"
        elif k in ("temperature", "온도"):
            rename[c] = "temperature"
        elif k in ("humidity", "습도"):
            rename[c] = "humidity"
        elif k == "ph":
            rename[c] = "ph"
        elif k == "ec":
            rename[c] = "ec"
        elif "생중량" in k:
            rename[c] = "생중량"
        elif "잎" in k:
            rename[c] = "잎 수"
        elif "지상부" in k and "길이" in k:
            rename[c] = "지상부 길이"
        elif "지하부" in k and "길이" in k:
            rename[c] = "지하부 길이"
        elif "지상부" in k and ("질량" in k or "무게" in k):
            rename[c] = "지상부 질량"
        elif "지하부" in k and ("질량" in k or "무게" in k):
            rename[c] = "지하부 질량"
        elif "개체" in k:
            rename[c] = "개체번호"
    df = df.rename(columns=rename)

    for c in df.columns:
        if c in ("time", "개체번호"):
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            num = pd.to_numeric(
                df[c].astype(str).str.replace(",", "").
                str.extract(r"(-?\d+\.?\d*)")[0],
                errors="coerce"
            )
            if num.notna().mean() >= 0.5:
                df[c] = num

    if "생중량" not in df.columns and {"지상부 질량", "지하부 질량"} <= set(df.columns):
        df["생중량"] = df["지상부 질량"] + df["지하부 질량"]

    if "time" in df.columns:
        t = df["time"].astype(str).str.strip()
        parsed = pd.to_datetime(t, errors="coerce", format="mixed")
        bad = parsed.isna() & t.str.match(r"^\d{8}_\d{1,2}$")
        if bad.any():
            parts = t[bad].str.split("_", expand=True)
            parsed[bad] = (
                pd.to_datetime(parts[0], format="%Y%m%d") +
                pd.to_timedelta(parts[1].astype(int), unit="h")
            )
        df["time"] = parsed

    return df

# ────────────────────────────────────────────────────
# 학교명 추출
# ────────────────────────────────────────────────────
def extract_school(filename):
    if not filename:
        return "우리 학교"
    base = _os.path.splitext(filename)[0]
    m = re.match(r"[\s\S]*?(송천고|OO고|고등학교|고)[-_]", base)
    if m:
        return m.group(1).replace("_", "")
    parts = re.split(r"[-_]", base)
    for p in parts:
        if "고" in p and len(p) <= 10:
            return p
    return base[:12] if len(base) > 0 else "우리 학교"

# ────────────────────────────────────────────────────
# Plotly 한글 폰트 헬퍼 + 테마
# ────────────────────────────────────────────────────
def set_korean_font(fig):
    fig.update_layout(
        font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
    )

def apply_plot_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(13,40,16,0.85)",
        plot_bgcolor="rgba(13,40,16,0.85)",
        font=dict(
            family="Malgun Gothic, Apple SD Gothic Neo, sans-serif",
            color="#c8e6c9",
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(102,187,106,0.12)",
        zerolinecolor="rgba(102,187,106,0.2)",
        tickfont=dict(color="#a5d6a7"),
    )
    fig.update_yaxes(
        gridcolor="rgba(102,187,106,0.12)",
        zerolinecolor="rgba(102,187,106,0.2)",
        tickfont=dict(color="#a5d6a7"),
    )

# ────────────────────────────────────────────────────
# 사이드바
# ────────────────────────────────────────────────────
st.set_page_config(page_title="극지식물 생육 분석", layout="wide")

st.sidebar.header("🌱 데이터 업로드")

env_file = st.sidebar.file_uploader("환경 CSV", type="csv")
growth_file = st.sidebar.file_uploader("생육 결과 CSV", type="csv")

with st.sidebar.expander("💡 사용 안내", expanded=False):
    st.markdown("""
    - 두 CSV를 업로드하면 자동으로 분석됩니다.
    - 학교마다 열 이름이 달라도 앱이 알아서 맞춰 읽습니다.
    - 인코딩(utf-8-sig/cp949) 오류와 한글 깨짐을 방지합니다.
    - 생중량(g) 열이 없으면 지상부+지하부 질량이 자동 합산됩니다.
    """)

st.sidebar.markdown("---")
growth_items = st.sidebar.multiselect(
    "📊 생육 측정 항목 선택",
    ["잎 수", "지상부 길이", "지하부 길이", "생중량", "지상부 질량", "지하부 질량"],
    default=["잎 수", "지상부 길이", "생중량"],
)

# ────────────────────────────────────────────────────
# 데이터 로딩 (한 번만)
# ────────────────────────────────────────────────────
with st.spinner("🌿 데이터를 읽어오는 중..."):
    env_raw = read_csv(env_file)
    growth_raw = read_csv(growth_file)

env_df = std_cols(env_raw) if not env_raw.empty else pd.DataFrame()
growth_df = std_cols(growth_raw) if not growth_raw.empty else pd.DataFrame()

school_name = (
    extract_school(env_file.name if env_file else "") or
    extract_school(growth_file.name if growth_file else "") or
    "우리 학교"
)

st.sidebar.info(f"🏫 분석 학교: **{school_name}**")

# ────────────────────────────────────────────────────
# 탭
# ────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌿 탭1: 실험 소개",
    "📊 탭2: 생육 지표 표",
    "📈 탭3: 산점도 그래프",
])

# ══════════════════════════════════════════════════════
# Tab 1: 실험 소개
# ══════════════════════════════════════════════════════
with tab1:
    try:
        col_l, col_r = st.columns([1, 1])

        with col_l:
            with st.container():
                st.markdown('<div class="green-card">', unsafe_allow_html=True)
                st.subheader("🎯 실험 목적")
                st.markdown("""
                이 실험은 **극지식물 개체의 생육을 가장 잘 드러내는 지표가 무엇인지** 찾기 위해 진행되었습니다.

                같은 스마트팜 환경에서 자라는 식물이라도 개체마다 잎 수, 줄기 길이, 생중량 등에 차이가 나타납니다. 이 차이를 여러 지표로 비교하고, 어떤 지표가 생장 정도를 가장 잘 설명하는지 확인하는 것이 목적입니다.
                """.strip())
                st.markdown("---")
                st.markdown(
                    "*상관계수*: 두 값이 함께 증가하거나 감소하는 정도를 "
                    "**-1 ~ 1** 사이 숫자로 나타낸 값. "
                    "1에 가까울수록 함께 증가, -1에 가까울수록 함께 감소, "
                    "0에 가까울수록 관계 약함."
                )
                st.markdown(
                    "*생중량*: 식물을 수확해 마른 잎·줄기·뿌리의 무게를 "
                    "모두 합한 값. 식물의 전체 생장량을 나타내는 대표 지표."
                )
                st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            with st.container():
                st.markdown('<div class="green-card">', unsafe_allow_html=True)
                st.subheader("🔍 핵심 발견")
                st.markdown("""
                관찰된 주요 패턴 세 가지:
                """.strip())
                items = [
                    (
                        "🌿 강한 길이 상관관계",
                        "지상부 길이와 지하부 길이는 강한 상관관계를 보여, "
                        "줄기가 길어질수록 뿌리도 함께 길어지는 경향이 뚜렷합니다.",
                    ),
                    (
                        "🌱 큰 생중량 차이",
                        "같은 스마트팜 환경에서도 식물마다 생중량 차이가 크게 "
                        "나타납니다. 같은 조건에서 자란다는 것이 "
                        "같은 결과로 이어지지는 않습니다.",
                    ),
                    (
                        "🍃 잎 수가 가장 관련 깊음",
                        "생중량 차이는 길이 지표만으로 설명되지 않으며, "
                        "**잎 수**가 생중량과 가장 관련 깊은 지표로 확인됩니다.",
                    ),
                ]
                for title, desc in items:
                    st.markdown(f"**{title}**  {desc}")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📋 데이터 요약")

        if not env_df.empty and "time" in env_df.columns:
            env_time_min = env_df["time"].min()
            env_time_max = env_df["time"].max()
            env_days = env_df["time"].dt.date.nunique()
            env_period = (
                f"{env_time_min.strftime('%Y-%m-%d')} ~ "
                f"{env_time_max.strftime('%Y-%m-%d')} "
                f"({env_days}일)"
            )
        else:
            env_period = "—"

        if not growth_df.empty and "개체번호" in growth_df.columns:
            n_ind = growth_df["개체번호"].nunique()
        else:
            n_ind = 0

        env_cols_name = [
            c.replace("temperature", "온도")
             .replace("humidity", "습도")
             .replace("ph", "pH")
             .replace("ec", "EC")
            for c in ["temperature", "humidity", "ph", "ec"]
            if c in env_df.columns
        ]
        growth_cols_name = [
            c for c in ["잎 수", "지상부 길이", "지하부 길이", "생중량"]
            if c in growth_df.columns
        ]

        rows = []
        rows.append(["🏫 학교명", school_name])
        rows.append(["🌡️ 환경 측정 기간", env_period])
        rows.append(["📡 환경 측정 항목", ", ".join(env_cols_name) if env_cols_name else "—"])
        rows.append(["🌱 생육 개체 수", f"{n_ind}개체" if n_ind else "—"])
        rows.append(["📐 생육 측정 항목", ", ".join(growth_cols_name) if growth_cols_name else "—"])
        st.dataframe(pd.DataFrame(rows, columns=["항목", "내용"]), width="stretch")

    except Exception as e:
        st.warning(f"⚠️ 이 부분은 데이터 형식 때문에 표시하지 못했어요: {e}")

# ══════════════════════════════════════════════════════
# Tab 2: 생육 지표 표
# ══════════════════════════════════════════════════════
with tab2:
    try:
        if growth_df.empty or "개체번호" not in growth_df.columns:
            st.info("📁 생육 결과 CSV를 업로드하면 생육 지표 표가 표시됩니다.")
        else:
            gd = growth_df.dropna(subset=["개체번호"]).copy()
            if "개체번호" in gd.columns:
                gd["개체번호"] = gd["개체번호"].astype(str)

            bio_col = "생중량" if "생중량" in gd.columns else None

            st.header("📊 식물의 생장을 나타내는 여러 지표")

            # ── 개체별 요약표 ──
            st.subheader("📋 개체별 생육 지표 요약표")
            summary_cols_available = [
                c for c in [
                    "개체번호", "잎 수", "지상부 길이", "지하부 길이",
                    "생중량", "지상부 질량", "지하부 질량",
                ]
                if c in gd.columns
            ]
            if summary_cols_available:
                df_show = gd[summary_cols_available].copy()
                for c in df_show.columns:
                    if c != "개체번호" and pd.api.types.is_numeric_dtype(df_show[c]):
                        df_show[c] = df_show[c].round(2)
                st.dataframe(df_show, width="stretch")
            else:
                st.info("표시할 생육 지표 열이 없습니다.")

            st.markdown("---")

            # ── 통계 요약표 ──
            st.subheader("📈 생육 지표별 통계 요약")
            stat_cols = [
                c for c in [
                    "잎 수", "지상부 길이", "지하부 길이", "생중량",
                    "지상부 질량", "지하부 질량",
                ]
                if c in gd.columns
            ]
            if stat_cols:
                stat_rows = []
                for c in stat_cols:
                    vals = gd[c].dropna()
                    if len(vals) >= 2:
                        mean_v = vals.mean()
                        std_v = vals.std()
                        cv_v = (std_v / mean_v * 100) if mean_v != 0 else 0
                        stat_rows.append({
                            "측정 항목": c,
                            "개체 수": len(vals),
                            "평균": round(mean_v, 2),
                            "표준편차": round(std_v, 2),
                            "변동계수(CV)": f"{cv_v:.1f}%",
                        })
                    else:
                        stat_rows.append({
                            "측정 항목": c,
                            "개체 수": len(vals),
                            "평균": "—",
                            "표준편차": "—",
                            "변동계수(CV)": "—",
                        })
                stat_df = pd.DataFrame(stat_rows)
                st.dataframe(stat_df, width="stretch")
                st.info(
                    "*(평균: 전체 값을 더해 개체 수로 나눈 대표값 / "
                    "표준편차: 값들이 평균에서 얼마나 퍼져 있는지 나타내는 값 / "
                    "CV: 표준편차를 평균으로 나눈 상대적 퍼짐 지표 — "
                    "값이 클수록 개체 간 차이가 큼)*"
                )
            else:
                st.info("통계 계산에 사용할 생육 지표 열이 없습니다.")

            st.markdown("---")

            # ── 통계 지표 카드 (delta_info → delta 만 사용) ──
            if stat_cols:
                cols_card = st.columns(min(4, len(stat_cols)))
                for i, c in enumerate(stat_cols[:4]):
                    vals = gd[c].dropna()
                    with cols_card[i]:
                        if len(vals) >= 2:
                            mean_v = vals.mean()
                            std_v = vals.std()
                            cv_v = (std_v / mean_v * 100) if mean_v != 0 else 0
                            st.metric(
                                label=c,
                                value=f"{mean_v:.2f}",
                                delta=f"CV {cv_v:.1f}%",
                            )
                        else:
                            st.metric(label=c, value="—")

            # ── 생중량 분포 요약 ──
            if bio_col and gd[bio_col].notna().sum() >= 3:
                vals = gd[bio_col].dropna()
                q25 = vals.quantile(0.25)
                q75 = vals.quantile(0.75)
                st.subheader("📦 생중량 분포 요약")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("평균 생중량", f"{vals.mean():.2f}g")
                with c2:
                    st.metric("표준편차", f"{vals.std():.2f}g")
                with c3:
                    st.metric("하위 25% 경계", f"{q25:.2f}g")
                with c4:
                    st.metric("상위 25% 경계", f"{q75:.2f}g")

            # ── 원본 데이터 및 다운로드 ──
            st.markdown("---")
            with st.expander("📋 생육 데이터 원본 테이블 및 CSV 다운로드"):
                st.dataframe(gd, width="stretch")
                if not gd.empty:
                    csv_bytes = gd.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 생육 결과 CSV 다운로드 (utf-8-sig)",
                        data=csv_bytes,
                        file_name=f"{school_name}_생육결과데이터.csv",
                        mime="text/csv",
                    )

    except Exception as e:
        st.warning(f"⚠️ 이 부분은 데이터 형식 때문에 표시하지 못했어요: {e}")

# ══════════════════════════════════════════════════════
# Tab 3: 산점도 그래프
# ══════════════════════════════════════════════════════
with tab3:
    try:
        if growth_df.empty or "개체번호" not in growth_df.columns:
            st.info("📁 생육 결과 CSV를 업로드하면 산점도 그래프가 표시됩니다.")
        else:
            st.header("📈 산점도 그래프로 정리")

            gd = growth_df.dropna(subset=["개체번호"]).copy()
            if "개체번호" in gd.columns:
                gd["개체번호"] = gd["개체번호"].astype(str)

            bio_col = "생중량" if "생중량" in gd.columns else None
            st.subheader("🔗 생육 지표 vs 생중량  산점도")

            scatter_pairs = [
                ("잎 수", "잎 수"),
                ("지상부 길이", "지상부 길이"),
                ("지하부 길이", "지하부 길이"),
            ]
            avail_pairs = [
                (x_label, y_col)
                for x_label, y_col in scatter_pairs
                if y_col in gd.columns and bio_col in gd.columns
            ]

            if avail_pairs:
                for x_label, y_col in avail_pairs:
                    gd_corr = gd.dropna(subset=[x_label, bio_col]).copy()
                    if len(gd_corr) < 2:
                        st.info(
                            f"{x_label}과 생중량의 관계를 표시하기에 "
                            f"데이터 포인트가 부족합니다."
                        )
                        continue

                    x_vals = gd_corr[x_label].values.astype(float)
                    y_vals = gd_corr[bio_col].values.astype(float)

                    r = np.corrcoef(x_vals, y_vals)[0, 1]
                    abs_r = abs(r)
                    if abs_r >= 0.7:
                        strength = "강한"
                    elif abs_r >= 0.4:
                        strength = "중간"
                    else:
                        strength = "약한"
                    direction = "양의" if r > 0 else "음의"

                    color = "#66bb6a" if x_label == "잎 수" else "#4db6ac"

                    fig_s = go.Figure()
                    fig_s.add_trace(
                        go.Scatter(
                            x=x_vals, y=y_vals,
                            mode="markers",
                            marker=dict(
                                size=10,
                                color=color,
                                line=dict(width=1.5, color="rgba(255,255,255,0.7)"),
                                opacity=0.9,
                            ),
                            hovertemplate=(
                                f"<b>{x_label}</b>: %{{x:.1f}}<br>"
                                f"<b>생중량</b>: %{{y:.2f}}g<extra></extra>"
                            ),
                            name="개체",
                        )
                    )

                    # 추세선 (np.polyfit 직접 계산, trendline 인자 사용 금지)
                    slope, intercept = np.polyfit(x_vals, y_vals, 1)
                    x_line = np.array([x_vals.min(), x_vals.max()])
                    y_line = slope * x_line + intercept
                    fig_s.add_trace(
                        go.Scatter(
                            x=x_line, y=y_line,
                            mode="lines",
                            line=dict(color="#ef5350", width=2.5, dash="dash"),
                            name=f"추세선 (기울기 {slope:.3f})",
                        )
                    )

                    fig_s.update_layout(
                        title=(
                            f"{x_label} vs 생중량"
                            f"   |   상관계수 <b>r = {r:.3f}</b>"
                            f"   ({strength} {direction} 상관관계)"
                        ),
                        xaxis_title=x_label,
                        yaxis_title="생중량 (g)",
                        width=720,
                        height=440,
                    )
                    apply_plot_theme(fig_s)
                    st.plotly_chart(fig_s, width="stretch")

                    st.info(
                        f"*(상관계수 r = {r:.3f} → {direction} {strength} 상관관계. "
                        f"0에 가까울수록 관계가 약하고, "
                        f"1 또는 -1에 가까울수록 관계가 강합니다.)*"
                    )
                    st.markdown("---")

            else:
                if bio_col not in gd.columns:
                    st.info("생중량 열이 없어 산점도 그래프를 표시할 수 없습니다.")
                else:
                    st.info(
                        "비교할 생육 지표(잎 수·지상부 길이·지하부 길이) "
                        "열이 없어 산점도를 표시할 수 없습니다."
                    )

            st.markdown("---")

            # ── 개체별 생중량 분포 (colorbar titlefont 제거) ──
            if bio_col and gd[bio_col].notna().sum() >= 3:
                st.subheader("📊 개체별 생중량 분포")
                gd_b = gd.dropna(subset=[bio_col]).copy()
                gd_b = gd_b.sort_values(bio_col, ascending=True)

                fig_dist = go.Figure()
                fig_dist.add_trace(
                    go.Scatter(
                        x=gd_b["개체번호"],
                        y=gd_b[bio_col],
                        mode="markers+lines",
                        marker=dict(
                            size=9,
                            color=gd_b[bio_col],
                            colorscale=[
                                [0, "#1b5e20"],
                                [0.5, "#66bb6a"],
                                [1, "#ef5350"],
                            ],
                            line=dict(width=1.5, color="rgba(255,255,255,0.7)"),
                            showscale=True,
                            colorbar=dict(
                                title="생중량 (g)",
                                tickfont=dict(color="#a5d6a7"),
                            ),
                        ),
                        line=dict(color="rgba(102,187,106,0.4)", width=1.2),
                        hovertemplate=(
                            "<b>개체</b>: %{{x}}<br>"
                            "<b>생중량</b>: %{{y:.2f}}g<extra></extra>"
                        ),
                        name="개체별 생중량",
                    )
                )
                mean_bio = gd_b[bio_col].mean()
                fig_dist.add_hline(
                    y=mean_bio,
                    line_dash="dash",
                    line_color="#ef5350",
                    line_width=2,
                    annotation_text=f"평균 {mean_bio:.2f}g",
                    annotation_position="top right",
                )
                apply_plot_theme(fig_dist)
                fig_dist.update_layout(
                    title=(
                        f"개체별 생중량 분포 "
                        f"(붉은 점선: 평균 {mean_bio:.2f}g)"
                    ),
                    xaxis_title="개체번호",
                    yaxis_title="생중량 (g)",
                    width=740,
                    height=420,
                )
                st.plotly_chart(fig_dist, width="stretch")

                cv = (
                    (gd_b[bio_col].std() / gd_b[bio_col].mean() * 100)
                    if gd_b[bio_col].mean() != 0 else 0
                )
                st.info(
                    f"• 평균: **{gd_b[bio_col].mean():.2f}g**  |  "
                    f"표준편차: **{gd_b[bio_col].std():.2f}g**  |  "
                    f"CV: **{cv:.1f}%**  "
                    f"*(CV가 클수록 같은 환경에서 개체 간 생중량 차이가 큼)*"
                )

            st.markdown("---")

            # ── 지상부 vs 지하부 길이 (강한 상관관계) ──
            if {"지상부 길이", "지하부 길이"} <= set(gd.columns):
                gd_sub = gd.dropna(subset=["지상부 길이", "지하부 길이"])
                if len(gd_sub) >= 2:
                    st.subheader("🌿 지상부 길이 vs 지하부 길이  (강한 상관관계 확인)")
                    x_sub = gd_sub["지상부 길이"].values.astype(float)
                    y_sub = gd_sub["지하부 길이"].values.astype(float)
                    r_sub = np.corrcoef(x_sub, y_sub)[0, 1]
                    slope_s, intercept_s = np.polyfit(x_sub, y_sub, 1)
                    x_s_line = np.array([x_sub.min(), x_sub.max()])
                    y_s_line = slope_s * x_s_line + intercept_s

                    fig_sub = go.Figure()
                    fig_sub.add_trace(
                        go.Scatter(
                            x=x_sub, y=y_sub,
                            mode="markers",
                            marker=dict(
                                size=10,
                                color="#26a69a",
                                line=dict(width=1.5, color="rgba(255,255,255,0.7)"),
                                opacity=0.9,
                            ),
                            hovertemplate=(
                                "<b>지상부 길이</b>: %{{x:.1f}}mm<br>"
                                "<b>지하부 길이</b>: %{{y:.1f}}mm<extra></extra>"
                            ),
                            name="개체",
                        )
                    )
                    fig_sub.add_trace(
                        go.Scatter(
                            x=x_s_line, y=y_s_line,
                            mode="lines",
                            line=dict(color="#ef5350", width=2.5, dash="dash"),
                            name=f"추세선 (r = {r_sub:.3f})",
                        )
                    )
                    apply_plot_theme(fig_sub)
                    fig_sub.update_layout(
                        title=(
                            f"지상부 길이 vs 지하부 길이"
                            f"   |   상관계수 <b>r = {r_sub:.3f}</b>"
                            f"  (강한 양의 상관관계)"
                        ),
                        xaxis_title="지상부 길이 (mm)",
                        yaxis_title="지하부 길이 (mm)",
                        width=700,
                        height=430,
                    )
                    st.plotly_chart(fig_sub, width="stretch")
                    st.info(
                        f"*(r = {r_sub:.3f} → 지상부 길이가 길어질수록 "
                        f"지하부 길이도 함께 길어지는 강한 양의 상관관계를 보입니다.)*"
                    )
                else:
                    st.info(
                        "지상부 길이·지하부 길이 데이터가 부족하여 "
                        "산점도를 표시할 수 없습니다."
                    )

            st.markdown("---")

            # ── 원본 데이터 및 다운로드 ──
            with st.expander("📋 생육 데이터 원본 테이블 및 CSV 다운로드"):
                st.dataframe(gd, width="stretch")
                if not gd.empty:
                    csv_bytes = gd.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 생육 결과 CSV 다운로드 (utf-8-sig)",
                        data=csv_bytes,
                        file_name=f"{school_name}_생육결과데이터.csv",
                        mime="text/csv",
                    )

    except Exception as e:
        st.warning(f"⚠️ 이 부분은 데이터 형식 때문에 표시하지 못했어요: {e}")

# ────────────────────────────────────────────────────
# 푸터
# ────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🌱 극지식물 생육 차이 분석 대시보드  |  "
    "Streamlit + Plotly  |  데이터 기반 분석"
)
