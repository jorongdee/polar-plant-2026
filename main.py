# main.py — 극지식물 생육 차이 분석 대시보드 (Gowun Dodum 전체 통일 · 한 화면 열람)
import io, os as _os, re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ────────────────────────────────────────────────────
# 폰트: Gowun Dodum (배너 제목과 동일한 둥근 고딕 · 전체 통일)
# ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, [class*="css"],
div[data-testid="stInfo"],
div[data-testid="stWarning"],
div.stMetric,
section.sidebar .stMarkdown,
section.sidebar p,
section.sidebar li,
section.sidebar .stSelectbox,
section.sidebar .stMultiSelect,
section.sidebar .stFileUploader,
.stButton > button,
.stExpander {
   font-family: 'Gowun Dodum', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
   letter-spacing: 0.1px;
   word-break: keep-all;
}

.stApp {
   background: #ffffff !important;
}

/* 배너 — "극지식물 생육 차이 분석"에 쓰인 것과 동일 스타일 */
.banner-box {
   background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 50%, #c8e6c9 100%);
   border-radius: 0 0 24px 24px;
   border-bottom: 2px solid #a5d6a7;
   padding: 20px 36px 16px;
   display: flex;
   align-items: center;
   justify-content: center;
   gap: 18px;
   margin-bottom: 30px;
   box-shadow: 0 3px 14px rgba(0,0,0,0.04);
}

.banner-title {
   font-family: 'Gowun Dodum', sans-serif;
   font-size: 27px;
   font-weight: 400;
   color: #2e7d32;
   letter-spacing: 0.6px;
}

.banner-sub {
   font-family: 'Gowun Dodum', sans-serif;
   font-size: 14px;
   color: #558b2f;
   font-weight: 400;
   border-left: 1px solid #c8e6c9;
   padding-left: 12px;
}

/* 카드 */
.paper-card {
   background: #ffffff;
   border: 1px solid #e0e0e0;
   border-radius: 18px;
   padding: 18px 22px;
   box-shadow: 0 2px 10px rgba(0,0,0,0.04);
   transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.paper-card:hover {
   box-shadow: 0 5px 18px rgba(0,0,0,0.07);
   transform: translateY(-1px);
}

/* 탭 */
.stTabs [role="tab"] {
   background: transparent;
   color: #78909c;
   font-family: 'Gowun Dodum', sans-serif;
   font-weight: 400;
   border-bottom: 2px solid transparent;
   transition: all 0.2s ease;
   padding: 10px 6px;
   letter-spacing: 0.2px;
}
.stTabs [role="tab"][aria-selected="true"] {
   background: #f1f8e9;
   color: #2e7d32;
   border-bottom: 2px solid #81c784;
   font-weight: 400;
}

/* 사이드바 */
section.sidebar {
   background: #f9fbe7 !important;
   border-right: 1px solid #e0e0e0;
}

/* metric */
div.stMetric {
   background: #f1f8e9;
   border: 1px solid #c8e6c9;
   border-radius: 14px;
   padding: 8px 16px 6px;
   transition: box-shadow 0.2s ease;
}
div.stMetric:hover {
   box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stMetric .stMetricValue {
   color: #2e7d32;
   font-weight: 500;
}
.stMetric .stMetricLabel {
   color: #607d8b;
}

/* expander */
.stExpander {
   border: 1px solid #e0e0e0;
   border-radius: 12px;
   background: #fafafa;
}

/* 안내 박스 */
div[data-testid="stInfo"] {
   background: #f1f8e9;
   border-left: 4px solid #81c784;
   border-radius: 10px;
   color: #455a64;
}
div[data-testid="stWarning"] {
   background: #fff8e1;
   border-left: 4px solid #ffb74d;
   border-radius: 10px;
   color: #5d4037;
}

/* 버튼 */
.stButton > button {
   background: #e8f5e9;
   border: 1px solid #a5d6a7;
   border-radius: 10px;
   color: #2e7d32;
   font-weight: 400;
   transition: all 0.25s ease;
}
.stButton > button:hover {
   background: #c8e6c9;
   border-color: #81c784;
   color: #1b5e20;
   box-shadow: 0 2px 8px rgba(46,125,50,0.15);
}

/* 파일 업로드 영역 */
.stFileUploader {
   border: 2px dashed #c8e6c9 !important;
   border-radius: 12px !important;
   background: #fafafa !important;
}

/* dataframe */
div[data-testid="stDataFrame"] {
   border-radius: 8px !important;
   border: 1px solid #e0e0e0 !important;
}

/* 스크롤바 */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f1f8e9; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: #a5d6a7; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #81c784; }

hr {
   border-color: #c8e6c9 !important;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────
# 배너 — "극지식물 생육 차이 분석" (폰트 동일)
# ────────────────────────────────────────────────────
st.markdown("""
<div class="banner-box">
   <span style="font-size:36px;">🌱</span>
   <span class="banner-title">극지식물 생육 차이 분석</span>
   <span class="banner-sub">어떤 지표가 생장을 가장 잘 보여줄까?</span>
   <span style="font-size:30px; opacity:0.7;">🌿</span>
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
# 열 이름 표준화 (KeyError 방지)
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
# Plotly 테마 — Gowun Dodum 폰트 + 흰 배경
# ────────────────────────────────────────────────────
def apply_plot_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.96)",
        plot_bgcolor="rgba(255,255,255,0.96)",
        font=dict(
            family="Gowun Dodum, Noto Sans KR, Malgun Gothic, sans-serif",
            color="#546e7a",
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(165,214,167,0.28)",
        zerolinecolor="rgba(165,214,167,0.4)",
        tickfont=dict(color="#78909c", family="Gowun Dodum, sans-serif"),
        linecolor="rgba(165,214,167,0.5)",
        linewidth=1,
    )
    fig.update_yaxes(
        gridcolor="rgba(165,214,167,0.28)",
        zerolinecolor="rgba(165,214,167,0.4)",
        tickfont=dict(color="#78909c", family="Gowun Dodum, sans-serif"),
        linecolor="rgba(165,214,167,0.5)",
        linewidth=1,
    )
    fig.update_layout(margin=dict(l=50, r=20, t=55, b=50))

# ────────────────────────────────────────────────────
# 사이드바
# ────────────────────────────────────────────────────
st.set_page_config(page_title="극지식물 생육 분석", layout="wide")

st.sidebar.header("🌱 데이터 업로드")

env_file = st.sidebar.file_uploader(
    "환경 CSV (.csv)",
    type="csv",
    help="시간·온도·습도·pH·EC가 담긴 파일",
)
growth_file = st.sidebar.file_uploader(
    "생육 결과 CSV (.csv)",
    type="csv",
    help="개체별 잎 수·길이·질량 데이터",
)

with st.sidebar.expander("💡 사용 안내", expanded=False):
    st.markdown("""
    - 두 CSV를 업로드하면 자동으로 분석돼요.
    - 학교마다 열 이름이 달라도 앱이 알아서 맞춰 읽어요.
    - 인코딩(utf-8-sig / cp949) 오류와 한글 깨짐을 방지해요.
    - 생중량(g) 열이 없으면 지상부 + 지하부 질량이 자동 합산돼요.
    - 한 파일만 올려도 해당 탭은 정상 동작해요.
    """)

st.sidebar.markdown("---")
growth_items = st.sidebar.multiselect(
    "📊 생육 측정 항목 선택",
    [
        "잎 수",
        "지상부 길이",
        "지하부 길이",
        "생중량",
        "지상부 질량",
        "지하부 질량",
    ],
    default=["잎 수", "지상부 길이", "생중량"],
)

# ────────────────────────────────────────────────────
# 데이터 로딩 (맨 위에서 딱 한 번)
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

# ────────────────────────────────────────────────────
# 탭
# ────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌿 탭1: 실험 소개",
    "📊 탭2: 생육 지표 표",
    "📈 탭3: 산점도 그래프",
])

# ══════════════════════════════════════════════════════
# Tab 1: 실험 소개 (단일 컬럼 — 글 한 화면에 표시)
# ══════════════════════════════════════════════════════
with tab1:
    try:
        st.markdown('<div class="paper-card">', unsafe_allow_html=True)
        st.subheader("🎯 실험 목적")
        st.markdown("""
        이 실험은 **극지식물 개체의 생육을 가장 잘 드러내는 지표가 무엇인지** 찾기 위해 진행했어요.

        같은 스마트팜 환경에서 자라는 식물이라도 개체마다 잎 수, 줄기 길이, 생중량 등에 차이가 나타나요.  
        이 차이를 여러 지표로 비교하고, 어떤 지표가 생장 정도를 가장 잘 설명하는지 알아보는 것이 목적이에요.
        """.strip())
        st.markdown("---")
        st.markdown(
            "📌 *상관계수*: 두 값이 함께 증가하거나 감소하는 정도를 "
            "**-1 ~ 1** 사이 숫자로 나타낸 값이에요. "
            "1에 가까울수록 함께 증가, -1에 가까울수록 함께 감소, "
            "0에 가까울수록 관계가 약해요."
        )
        st.markdown(
            "📌 *생중량*: 식물을 수확해 마른 잎·줄기·뿌리의 무게를 "
            "모두 합한 값이에요. 식물의 전체 생장량을 나타내는 대표 지표예요."
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        with st.container():
            st.markdown('<div class="paper-card">', unsafe_allow_html=True)
            st.subheader("🔍 핵심 발견")
            st.markdown("""
            관찰된 주요 패턴 세 가지를 미리 살펴볼게요.
            """.strip())
            items = [
                (
                    "🌿 강한 길이 상관관계",
                    "지상부 길이와 지하부 길이는 강한 상관관계를 보여, "
                    "줄기가 길어질수록 뿌리도 함께 길어지는 경향이 뚜렷해요.",
                ),
                (
                    "🌱 큰 생중량 차이",
                    "같은 스마트팜 환경에서도 식물마다 생중량 차이가 크게 "
                    "나타나요. 같은 조건에서 자란다고 해서 "
                    "같은 결과로 이어지지는 않네요.",
                ),
                (
                    "🍃 잎 수가 가장 관련 깊음",
                    "생중량 차이는 길이 지표만으로 설명되지 않으며, "
                    "**잎 수**가 생중량과 가장 관련 깊은 지표로 확인됐어요.",
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
                st.info("표시할 생육 지표 열이 없어요.")

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
                    "📌 평균: 전체 값을 더해 개체 수로 나눈 대표값 / "
                    "표준편차: 값들이 평균에서 얼마나 퍼져 있는지 나타내는 값 / "
                    "CV(변동계수): 표준편차를 평균으로 나눈 상대적 퍼짐 지표 — "
                    "값이 클수록 개체 간 차이가 커요."
                )
            else:
                st.info("통계 계산에 사용할 생육 지표 열이 없어요.")

            st.markdown("---")

            # ── 통계 지표 카드 ──
            if stat_cols:
                n_card = min(4, len(stat_cols))
                cols_card = st.columns(n_card)
                for i in range(n_card):
                    c = stat_cols[i]
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

            st.markdown("---")

            with st.expander("📋 생육 데이터 원본 테이블 및 CSV 다운로드"):
                st.dataframe(gd, width="stretch")
                if not gd.empty:
                    csv_bytes = gd.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 생육 결과 CSV 다운로드",
                        data=csv_bytes,
                        file_name=f"{school_name}_생육결과데이터.csv",
                        mime="text/csv",
                        key="download_growth_tab2",
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

            palette = {
                "잎 수": "#66bb6a",
                "지상부 길이": "#43a047",
                "지하부 길이": "#26a69a",
            }

            if avail_pairs:
                for x_label, y_col in avail_pairs:
                    gd_corr = gd.dropna(subset=[x_label, bio_col]).copy()
                    if len(gd_corr) < 2:
                        st.info(
                            f"{x_label}과 생중량의 관계를 표시하기에 "
                            f"데이터 포인트가 부족해요."
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
                    color = palette.get(x_label, "#2e7d32")

                    fig_s = go.Figure()
                    fig_s.add_trace(
                        go.Scatter(
                            x=x_vals, y=y_vals,
                            mode="markers",
                            marker=dict(
                                size=11,
                                color=color,
                                line=dict(width=1.5, color="rgba(255,255,255,0.85)"),
                                opacity=0.92,
                            ),
                            hovertemplate=(
                                f"<b>{x_label}</b>: %{{x:.1f}}<br>"
                                f"<b>생중량</b>: %{{y:.2f}}g<extra></extra>"
                            ),
                            name="개체",
                        )
                    )

                    slope, intercept = np.polyfit(x_vals, y_vals, 1)
                    x_line = np.array([x_vals.min(), x_vals.max()])
                    y_line = slope * x_line + intercept
                    fig_s.add_trace(
                        go.Scatter(
                            x=x_line, y=y_line,
                            mode="lines",
                            line=dict(color="#e57373", width=2.5, dash="dash"),
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
                        height=450,
                    )
                    apply_plot_theme(fig_s)
                    st.plotly_chart(fig_s, width="stretch")

                    st.info(
                        f"📌 상관계수 r = {r:.3f} → {direction} {strength} 상관관계. "
                        f"0에 가까울수록 관계가 약하고, "
                        f"1 또는 -1에 가까울수록 관계가 강해요."
                    )
                    st.markdown("---")

            else:
                if bio_col not in gd.columns:
                    st.info("생중량 열이 없어 산점도 그래프를 표시할 수 없어요.")
                else:
                    st.info(
                        "비교할 생육 지표(잎 수·지상부 길이·지하부 길이) "
                        "열이 없어 산점도를 표시할 수 없어요."
                    )

            st.markdown("---")

            # ── 개체별 생중량 분포 ──
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
                            size=10,
                            color=gd_b[bio_col],
                            colorscale=[
                                [0, "#81c784"],
                                [0.5, "#43a047"],
                                [1, "#e57373"],
                            ],
                            line=dict(width=1.5, color="rgba(255,255,255,0.85)"),
                            showscale=True,
                            colorbar=dict(
                                title="생중량 (g)",
                                tickfont=dict(color="#78909c", family="Gowun Dodum, sans-serif"),
                            ),
                        ),
                        line=dict(color="rgba(165,214,167,0.5)", width=1.2),
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
                    line_color="#e57373",
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
                    height=430,
                )
                st.plotly_chart(fig_dist, width="stretch")

                cv = (
                    (gd_b[bio_col].std() / gd_b[bio_col].mean() * 100)
                    if gd_b[bio_col].mean() != 0 else 0
                )
                st.info(
                    f"📌 평균: **{gd_b[bio_col].mean():.2f}g**  |  "
                    f"표준편차: **{gd_b[bio_col].std():.2f}g**  |  "
                    f"CV: **{cv:.1f}%**  "
                    f"*(CV가 클수록 같은 환경에서 개체 간 생중량 차이가 커요)*"
                )

            st.markdown("---")

            # ── 지상부 vs 지하부 길이 ──
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
                                size=11,
                                color="#43a047",
                                line=dict(width=1.5, color="rgba(255,255,255,0.85)"),
                                opacity=0.92,
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
                            line=dict(color="#e57373", width=2.5, dash="dash"),
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
                        height=440,
                    )
                    st.plotly_chart(fig_sub, width="stretch")
                    st.info(
                        f"📌 r = {r_sub:.3f} → 지상부 길이가 길어질수록 "
                        f"지하부 길이도 함께 길어지는 강한 양의 상관관계를 보여요."
                    )
                else:
                    st.info(
                        "지상부 길이·지하부 길이 데이터가 부족하여 "
                        "산점도를 표시할 수 없어요."
                    )

            st.markdown("---")

            with st.expander("📋 생육 데이터 원본 테이블 및 CSV 다운로드"):
                st.dataframe(gd, width="stretch")
                if not gd.empty:
                    csv_bytes = gd.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 생육 결과 CSV 다운로드",
                        data=csv_bytes,
                        file_name=f"{school_name}_생육결과데이터.csv",
                        mime="text/csv",
                        key="download_growth_tab3",
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
