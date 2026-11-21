import io
import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------------------------------------
# 한글 폰트 CSS
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap');
html, body, [class*="css"] {
   font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CSV 인코딩 처리 (utf-8-sig -> cp949)
# --------------------------------------------------
@st.cache_data
def read_csv(file):
    """업로드된 파일을 utf-8-sig -> cp949 순서로 시도하여 읽기"""
    if file is None:
        return pd.DataFrame()
    data = file.getvalue()
    for enc in ("utf-8-sig", "cp949"):
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc)
        except Exception:
            pass
    return pd.DataFrame()

# --------------------------------------------------
# 열 이름 표준화 (KeyError 방지)
# --------------------------------------------------
def std_cols(df):
    """CSV 열 이름을 표준 이름으로 통일"""
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

    # 숫자 변환 (글자 열은 계산에서 제외)
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

    # 생중량 결측 시 지상부+지하부 질량 합산
    if "생중량" not in df.columns and {"지상부 질량", "지하부 질량"} <= set(df.columns):
        df["생중량"] = df["지상부 질량"] + df["지하부 질량"]

    # 시간 포맷 파싱
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

# --------------------------------------------------
# 학교명 추출 (파일명에서)
# --------------------------------------------------
def extract_school(filename):
    if not filename:
        return "우리 학교"
    base = os.path.splitext(filename)[0]
    m = re.match(r"[\s\S]*?(송천고|OO고|고등학교|고)[-_]", base)
    if m:
        return m.group(1).replace("_", "")
    parts = re.split(r"[-_]", base)
    for p in parts:
        if "고" in p and len(p) <= 10:
            return p
    return base[:12] if len(base) > 0 else "우리 학교"

# --------------------------------------------------
# Plotly 한글 폰트 적용 헬퍼
# --------------------------------------------------
def set_korean_font(fig):
    fig.update_layout(
        font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif")
    )

# --------------------------------------------------
# 사이드바
# --------------------------------------------------
st.set_page_config(page_title="극지식물 생육 분석", layout="wide")
st.title("🌱 우리 학교 극지식물 개체별 생육 차이 분석")

st.sidebar.header("📁 데이터 업로드")
env_file = st.sidebar.file_uploader("환경 CSV", type="csv")
growth_file = st.sidebar.file_uploader("생육 결과 CSV", type="csv")

with st.sidebar.expander("💡 사용 안내"):
    st.write("""
- 두 CSV를 업로드하면 자동으로 분석됩니다.
- 학교마다 열 이름이 달라도 앱이 알아서 맞춰 읽습니다.
- 인코딩(utf-8-sig/cp949) 오류와 한글 폰트 깨짐을 방지합니다.
""")

st.sidebar.markdown("---")
growth_items = st.sidebar.multiselect(
    "📊 생육 측정 항목 선택",
    ["잎 수", "지상부 길이", "지하부 길이", "생중량", "지상부 질량", "지하부 질량"],
    default=["잎 수", "지상부 길이", "생중량"],
)

# --------------------------------------------------
# 데이터 로딩 (한 번만)
# --------------------------------------------------
with st.spinner("데이터를 읽는 중..."):
    env_raw = read_csv(env_file)
    growth_raw = read_csv(growth_file)

env_df = std_cols(env_raw) if not env_raw.empty else pd.DataFrame()
growth_df = std_cols(growth_raw) if not growth_raw.empty else pd.DataFrame()

school_name = extract_school(env_file.name if env_file else "") or \
              extract_school(growth_file.name if growth_file else "") or \
              "우리 학교"

st.sidebar.info(f"🏫 분석 학교: **{school_name}**")

# --------------------------------------------------
# 탭
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📖 실험 개요", "🌡️ 환경 데이터", "📊 생육 결과"])

# ======== Tab 1: 실험 개요 ========
with tab1:
    try:
        st.header("📖 실험 개요")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.subheader("연구 배경")
            st.write(f"""
**{school_name}**에서는 극지식물(Polar plant)을 직접 재배하며 개체별로 생육 차이를 관찰하는 실험을 진행했습니다.
극지식물은 낮은 온도, 건조한 환경 등 가혹한 조건에서도 살아남는 식물로,
같은 조건에서 자라더라도 개체마다 잎 수, 줄기 길이, 질량 등에 차이가 나타납니다.

이 대시보드는 각 개체의 생육 결과를 비교하고, 환경 조건(온도·습도·pH·EC 등)과의 관계를
확인하여 어떤 개체가 잘 자랐는지, 어떤 환경이 생육에 도움이 되었는지 살펴보기 위해 만들었습니다.
""")
        with col_b2:
            st.subheader("연구 목적")
            st.write("""
- 개체별 생중량 분포와 차이를 평균·표준편차·변동계수(CV)로 파악한다.
  *(평균: 전체 값을 더해 개수로 나눈 대표값, 표준편차: 값들이 평균에서 얼마나 퍼져 있는지 나타내는 값, CV: 표준편차를 평균으로 나눈 상대적 퍼짐 지표)*
- 잎 수·지상부 길이와 생중량의 관계(상관계수·산점도)를 확인한다.
  *(상관계수: -1~1 사이 값으로, 두 값이 함께 증가/감소하는 정도를 나타냄. 1에 가까울수록 함께 증가)*
- 생중량 상위 25% 개체와 하위 25% 개체의 차이를 비교한다.
""")

        st.markdown("---")
        st.subheader("📋 데이터 요약")

        # 환경 요약
        if not env_df.empty and "time" in env_df.columns:
            env_time_min = env_df["time"].min()
            env_time_max = env_df["time"].max()
            env_day_count = env_df["time"].dt.date.nunique()
            env_period_str = f"{env_time_min.strftime('%Y-%m-%d')} ~ {env_time_max.strftime('%Y-%m-%d')}"
        else:
            env_period_str = "—"
            env_day_count = 0

        # 생육 요약
        if not growth_df.empty and "개체번호" in growth_df.columns:
            growth_count = growth_df["개체번호"].nunique()
        else:
            growth_count = 0

        # 측정 항목 구성
        env_cols_avail = [c for c in ["temperature", "humidity", "ph", "ec"] if c in env_df.columns]
        growth_cols_avail = [c for c in ["잎 수", "지상부 길이", "지하부 길이", "생중량"] if c in growth_df.columns]

        summary_data = [
            ["학교명", school_name],
            ["환경 데이터 측정 기간", env_period_str],
            ["환경 데이터 측정 일수", f"{env_day_count}일" if env_day_count else "—"],
            ["환경 측정 항목", ", ".join(c.replace("temperature","온도").replace("humidity","습도")
                                        .replace("ph","pH").replace("ec","EC") for c in env_cols_avail) or "—"],
            ["생육 데이터 개체 수", f"{growth_count}개체" if growth_count else "—"],
            ["생육 측정 항목", ", ".join(growth_cols_avail) or "—"],
        ]
        st.dataframe(pd.DataFrame(summary_data, columns=["항목", "내용"]), width="stretch")

        st.markdown("---")
        st.subheader("📊 주요 지표 카드")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("총 개체수", f"{growth_count}개체" if growth_count else "—")
        with c2:
            if "temperature" in env_df.columns and env_df["temperature"].notna().sum() >= 2:
                avg_temp = env_df["temperature"].dropna().mean()
                st.metric("평균 온도", f"{avg_temp:.1f}°C")
            else:
                st.metric("평균 온도", "—")
        with c3:
            if "humidity" in env_df.columns and env_df["humidity"].notna().sum() >= 2:
                avg_hum = env_df["humidity"].dropna().mean()
                st.metric("평균 습도", f"{avg_hum:.1f}%")
            else:
                st.metric("평균 습도", "—")
        with c4:
            if "생중량" in growth_df.columns and growth_df["생중량"].notna().sum() >= 2:
                avg_bio = growth_df["생중량"].dropna().mean()
                st.metric("평균 생중량", f"{avg_bio:.2f}g")
            else:
                st.metric("평균 생중량", "—")
    except Exception as e:
        st.warning(f"⚠️ 이 부분은 데이터 형식 때문에 표시하지 못했어요: {e}")

# ======== Tab 2: 환경 데이터 ========
with tab2:
    try:
        if env_df.empty or "time" not in env_df.columns:
            st.info("📁 환경 CSV를 업로드하면 환경 데이터 분석이 표시됩니다.")
        else:
            st.header("🌡️ 환경 데이터")

            # 환경 요약 표
            env_num_cols = [c for c in ["temperature", "humidity", "ph", "ec"] if c in env_df.columns]
            if env_num_cols:
                env_summary = env_df[env_num_cols].dropna()
                if not env_summary.empty:
                    summ = pd.DataFrame({
                        "측정 항목": [
                            c.replace("temperature","온도")
                             .replace("humidity","습도")
                             .replace("ph","pH")
                             .replace("ec","EC")
                            for c in env_num_cols
                        ],
                        "평균": [round(env_summary[c].mean(), 2) for c in env_num_cols],
                        "최소": [round(env_summary[c].min(), 2) for c in env_num_cols],
                        "최대": [round(env_summary[c].max(), 2) for c in env_num_cols],
                    })
                    st.subheader("환경 요약 (평균·최소·최대)")
                    st.dataframe(summ, width="stretch")
                else:
                    st.info("환경 데이터의 수치 값이 충분하지 않아 요약을 표시할 수 없습니다.")
            else:
                st.info("환경 데이터에 온도·습도·pH·EC 열이 없어 요약을 표시할 수 없습니다.")

            st.markdown("---")
            st.subheader("📈 날짜별 환경 변화 (일별 평균)")

            env_time_df = env_df.dropna(subset=["time"]).copy()
            if not env_time_df.empty:
                env_time_df["date"] = env_time_df["time"].dt.date

                date_agg = env_time_df.groupby("date").mean(numeric_only=True).reset_index()

                # 온도
                if "temperature" in date_agg.columns:
                    fig_t = px.line(date_agg, x="date", y="temperature",
                                    title="📅 일별 평균 온도 변화",
                                    labels={"date":"날짜", "temperature":"온도 (°C)"})
                    fig_t.update_traces(line=dict(color="#e74c3c", width=2))
                    set_korean_font(fig_t)
                    fig_t.update_layout(xaxis_title="날짜", yaxis_title="온도 (°C)")
                    st.plotly_chart(fig_t, width="stretch")

                # 습도
                if "humidity" in date_agg.columns:
                    fig_h = px.line(date_agg, x="date", y="humidity",
                                    title="📅 일별 평균 습도 변화",
                                    labels={"date":"날짜", "humidity":"습도 (%)"})
                    fig_h.update_traces(line=dict(color="#3498db", width=2))
                    set_korean_font(fig_h)
                    fig_h.update_layout(xaxis_title="날짜", yaxis_title="습도 (%)")
                    st.plotly_chart(fig_h, width="stretch")

                # pH·EC
                ph_ec_avail = [c for c in ["ph", "ec"] if c in date_agg.columns]
                if ph_ec_avail:
                    fig_pe = make_subplots(
                        rows=1, cols=len(ph_ec_avail),
                        subplot_titles=["pH 변화", "EC 변화"],
                        horizontal_spacing=0.15,
                    )
                    colors_pe = {"ph": "#2ecc71", "ec": "#f39c12"}
                    for i, c in enumerate(ph_ec_avail):
                        trace = go.Scatter(
                            x=date_agg["date"], y=date_agg[c],
                            mode="lines", name=c.upper(),
                            line=dict(color=colors_pe.get(c, "#333"), width=2),
                            hovertemplate=f"{c}: %{{y:.2f}}<extra></extra>",
                        )
                        fig_pe.add_trace(trace, row=1, col=i+1)
                    set_korean_font(fig_pe)
                    fig_pe.update_layout(
                        title="📅 일별 pH · EC 변화",
                        xaxis_title="날짜",
                        height=350,
                    )
                    if "ph" in date_agg.columns:
                        fig_pe.update_yaxes(title_text="pH", row=1, col=1)
                    if "ec" in date_agg.columns:
                        fig_pe.update_yaxes(title_text="EC (mS/cm)", row=1, col=2)
                    st.plotly_chart(fig_pe, width="stretch")
                else:
                    st.info("pH·EC 열이 없어 해당 그래프는 건너뛰었습니다.")

            st.markdown("---")
            with st.expander("📋 환경 데이터 원본 테이블 및 CSV 다운로드"):
                st.dataframe(env_df, width="stretch")
                if not env_df.empty:
                    csv_bytes = env_df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 환경 데이터 CSV 다운로드",
                        data=csv_bytes,
                        file_name=f"{school_name}_환경데이터.csv",
                        mime="text/csv",
                    )
    except Exception as e:
        st.warning(f"⚠️ 이 부분은 데이터 형식 때문에 표시하지 못했어요: {e}")

# ======== Tab 3: 생육 결과 ========
with tab3:
    try:
        if growth_df.empty or "개체번호" not in growth_df.columns:
            st.info("📁 생육 결과 CSV를 업로드하면 생육 분석이 표시됩니다.")
        else:
            st.header("📊 생육 결과")

            # 살아있는 데이터만 사용
            gd = growth_df.dropna(subset=["개체번호"]).copy()
            if "개체번호" in gd.columns:
                gd["개체번호"] = gd["개체번호"].astype(str)

            # --- 핵심 카드 ---
            st.subheader("🥇 핵심 결과")

            bio_col = "생중량" if "생중량" in gd.columns else None
            card_col1, card_col2, card_col3 = st.columns(3)

            with card_col1:
                if bio_col and gd[bio_col].notna().sum() >= 2:
                    avg_bio = gd[bio_col].dropna().mean()
                    st.metric("평균 생중량", f"{avg_bio:.2f}g",
                              delta=None,
                              help="모든 개체의 생중량을 더해 개체 수로 나눈 값")
                else:
                    st.metric("평균 생중량", "—")
            with card_col2:
                if bio_col and gd[bio_col].notna().sum() >= 2:
                    max_idx = gd[bio_col].dropna().idxmax()
                    max_val = gd.loc[max_idx, bio_col]
                    max_id = gd.loc[max_idx, "개체번호"]
                    st.metric("최대 생중량 개체", f"{max_id}",
                              delta=f"{max_val:.2f}g",
                              help=f"생중량이 가장 큰 개체 (개체번호 {max_id})")
                else:
                    st.metric("최대 생중량 개체", "—")
            with card_col3:
                if bio_col and gd[bio_col].notna().sum() >= 2:
                    min_idx = gd[bio_col].dropna().idxmin()
                    min_val = gd.loc[min_idx, bio_col]
                    min_id = gd.loc[min_idx, "개체번호"]
                    st.metric("최소 생중량 개체", f"{min_id}",
                              delta=f"{min_val:.2f}g",
                              help=f"생중량이 가장 작은 개체 (개체번호 {min_id})")
                else:
                    st.metric("최소 생중량 개체", "—")

            st.markdown("---")

            # --- 개체별 생육 비교 (막대 그래프) ---
            st.subheader("📊 개체별 생육 비교")

            plot_cols_map = {
                "잎 수": "잎 수",
                "지상부 길이": "지상부 길이",
                "지하부 길이": "지하부 길이",
                "생중량": "생중량",
            }
            plot_cols_avail = [
                c for name, c in plot_cols_map.items()
                if c in gd.columns and name in growth_items
            ]

            if plot_cols_avail:
                fig_bar = make_subplots(
                    rows=len(plot_cols_avail),
                    cols=1,
                    subplot_titles=[
                        f"평균 {c.replace('지상부 길이','지상부 길이').replace('지하부 길이','지하부 길이')}"
                        for c in plot_cols_avail
                    ],
                    vertical_spacing=0.12,
                )

                colors_bar = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

                for i, c in enumerate(plot_cols_avail):
                    gd_c = gd.dropna(subset=[c]).copy()
                    if gd_c.empty or len(gd_c) < 2:
                        continue
                    gd_sorted = gd_c.sort_values(c, ascending=True)

                    bars = go.Bar(
                        x=gd_sorted["개체번호"],
                        y=gd_sorted[c],
                        name=c,
                        marker=dict(color=colors_bar[i % len(colors_bar)]),
                        hovertemplate=f"<b>{c}</b><br>개체: %{{x}}<br>{c}: %{{y:.2f}}<extra></extra>",
                    )
                    fig_bar.add_trace(bars, row=i+1, col=1)

                    y_mean = gd_sorted[c].mean()
                    fig_bar.add_hline(
                        y=y_mean,
                        line_dash="dash",
                        line_color="gray",
                        row=i+1, col=1,
                        annotation_text=f"평균 {y_mean:.1f}",
                        annotation_position="top right",
                    )

                for i, c in enumerate(plot_cols_avail):
                    fig_bar.update_yaxes(title_text=c, row=i+1, col=1)

                set_korean_font(fig_bar)
                fig_bar.update_layout(
                    title="🌿 개체별 생육 지표 비교 (점선은 평균)",
                    height=280 * len(plot_cols_avail),
                    xaxis_title="개체번호",
                )
                st.plotly_chart(fig_bar, width="stretch")
            else:
                st.info("선택한 생육 측정 항목 열이 없어 그래프를 표시할 수 없습니다.")

            st.markdown("---")

            # --- 생중량 분포 (박스플롯) ---
            if bio_col and gd[bio_col].notna().sum() >= 3:
                st.subheader("📦 생중량 분포 (박스플롯)")
                fig_box = px.box(
                    gd.dropna(subset=[bio_col]),
                    y=bio_col,
                    title="생중량 분포",
                    labels={bio_col: "생중량 (g)"},
                )
                fig_box.update_traces(fillcolor="#3498db", boxmean=True)
                set_korean_font(fig_box)
                fig_box.update_layout(yaxis_title="생중량 (g)")
                st.plotly_chart(fig_box, width="stretch")

                # CV 표시
                vals = gd[bio_col].dropna()
                cv = (vals.std() / vals.mean()) * 100 if vals.mean() != 0 else 0
                st.info(
                    f"• 평균 생중량: **{vals.mean():.2f}g**  |  "
                    f"표준편차: **{vals.std():.2f}g**  |  "
                    f"변동계수(CV): **{cv:.1f}%**  "
                    f"*(CV: 표준편차를 평균으로 나눈 값으로, 개체 간 차이가 상대적으로 얼마나 큰지 나타냅니다)*"
                )
            else:
                st.info("생중량 데이터가 충분하지 않아 분포 그래프를 표시할 수 없습니다.")

            st.markdown("---")

            # --- 상관관계 분석 (산점도 + 추세선) ---
            st.subheader("🔗 상관관계 분석 (산점도 + 추세선)")

            scatter_pairs = [
                ("잎 수", "잎 수"),
                ("지상부 길이", "지상부 길이"),
            ]
            pair_avail = [
                (x_label, y_col)
                for x_label, y_col in scatter_pairs
                if y_col in gd.columns and bio_col in gd.columns
            ]

            for x_label, y_col in pair_avail:
                gd_corr = gd.dropna(subset=[x_label, bio_col]).copy()
                if len(gd_corr) < 2:
                    st.info(f"{x_label}과 생중량의 관계를 표시하기에 데이터 포인트가 부족합니다.")
                    continue

                x_vals = gd_corr[x_label].values.astype(float)
                y_vals = gd_corr[bio_col].values.astype(float)

                # 상관계수
                r = np.corrcoef(x_vals, y_vals)[0, 1]
                abs_r = abs(r)
                if abs_r >= 0.7:
                    strength = "강한"
                elif abs_r >= 0.4:
                    strength = "중간"
                else:
                    strength = "약한"
                direction = "양의" if r > 0 else "음의"

                fig_s = go.Figure()
                fig_s.add_trace(
                    go.Scatter(
                        x=x_vals, y=y_vals,
                        mode="markers",
                        marker=dict(
                            size=9,
                            color="#3498db",
                            line=dict(width=1, color="white"),
                        ),
                        hovertemplate=f"<b>{x_label}</b>: %{{x:.1f}}<br><b>생중량</b>: %{{y:.2f}}g<extra></extra>",
                        name="개체",
                    )
                )

                # 추세선 (np.polyfit 직접 계산)
                if len(x_vals) >= 2:
                    slope, intercept = np.polyfit(x_vals, y_vals, 1)
                    x_line = np.array([x_vals.min(), x_vals.max()])
                    y_line = slope * x_line + intercept
                    fig_s.add_trace(
                        go.Scatter(
                            x=x_line, y=y_line,
                            mode="lines",
                            line=dict(color="#e74c3c", width=2, dash="dash"),
                            name=f"추세선 (기울기 {slope:.3f})",
                        )
                    )

                fig_s.update_layout(
                    title=f"{x_label} vs 생중량  |  상관계수 r = {r:.3f} ({strength} {direction} 상관관계)",
                    xaxis_title=x_label,
                    yaxis_title="생중량 (g)",
                    width=650,
                    height=380,
                )
                set_korean_font(fig_s)
                st.plotly_chart(fig_s, width="stretch")

                st.write(
                    f"*상관계수 r = {r:.3f} → {direction} {strength} 상관관계. "
                    f"0에 가까울수록 관계가 약하고, 1 또는 -1에 가까울수록 관계가 강합니다.*"
                )

            # 선택된 생육 항목이 없을 때 안내
            if not pair_avail and bio_col not in gd.columns:
                st.info("생중량 열과 비교할 생육 측정 항목 열이 없어 상관관계 산점도를 표시할 수 없습니다.")

            st.markdown("---")

            # --- 상위·하위 25% 개체 비교 ---
            if bio_col and gd[bio_col].notna().sum() >= 4:
                st.subheader("🏆 생중량 상위 25% vs 하위 25% 개체")

                gd_b = gd.dropna(subset=[bio_col]).copy()
                q75 = gd_b[bio_col].quantile(0.75)
                q25 = gd_b[bio_col].quantile(0.25)

                top = gd_b[gd_b[bio_col] >= q75].sort_values(bio_col, ascending=False)
                bottom = gd_b[gd_b[bio_col] <= q25].sort_values(bio_col, ascending=True)

                c_top, c_mid, c_bot = st.columns(3)
                with c_top:
                    st.markdown(f"### 🔺 상위 25% (생중량 ≥ {q75:.2f}g)")
                    if not top.empty:
                        df_top_show = top[["개체번호", bio_col]].copy()
                        df_top_show[bio_col] = df_top_show[bio_col].round(2)
                        st.dataframe(df_top_show, width="stretch", hide_index=True)
                    else:
                        st.info("상위 25% 개체가 없습니다.")
                with c_mid:
                    st.markdown("### 📊 전체 분포")
                    fig_mid = px.histogram(
                        gd_b, x=bio_col,
                        nbins=12,
                        title=f"생중량 분포 (상위 ≥ {q75:.2f}g / 하위 ≤ {q25:.2f}g)",
                        labels={bio_col: "생중량 (g)"},
                        color_discrete_sequence=["#3498db"],
                    )
                    fig_mid.add_vline(x=q75, line_dash="dash", line_color="red",
                                     annotation_text="상위 25% 경계")
                    fig_mid.add_vline(x=q25, line_dash="dash", line_color="orange",
                                     annotation_text="하위 25% 경계")
                    set_korean_font(fig_mid)
                    fig_mid.update_layout(xaxis_title="생중량 (g)", yaxis_title="개체 수")
                    st.plotly_chart(fig_mid, width="stretch")
                with c_bot:
                    st.markdown(f"### 🔻 하위 25% (생중량 ≤ {q25:.2f}g)")
                    if not bottom.empty:
                        df_bot_show = bottom[["개체번호", bio_col]].copy()
                        df_bot_show[bio_col] = df_bot_show[bio_col].round(2)
                        st.dataframe(df_bot_show, width="stretch", hide_index=True)
                    else:
                        st.info("하위 25% 개체가 없습니다.")

                # 비교 요약
                if not top.empty and not bottom.empty:
                    top_mean = top[bio_col].mean()
                    bot_mean = bottom[bio_col].mean()
                    st.success(
                        f"상위 25% 평균: **{top_mean:.2f}g**  |  "
                        f"하위 25% 평균: **{bot_mean:.2f}g**  |  "
                        f"차이: **{top_mean - bot_mean:.2f}g**"
                    )

            st.markdown("---")

            # --- 원본 데이터 및 다운로드 ---
            with st.expander("📋 생육 데이터 원본 테이블 및 CSV 다운로드"):
                st.dataframe(gd, width="stretch")
                if not gd.empty:
                    csv_bytes = gd.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇ 생육 결과 CSV 다운로드",
                        data=csv_bytes,
                        file_name=f"{school_name}_생육결과데이터.csv",
                        mime="text/csv",
                    )

    except Exception as e:
        st.warning(f"⚠️ 이 부분은 데이터 형식 때문에 표시하지 못했어요: {e}")

# ========
# 푸터
# ========
st.markdown("---")
st.caption("🌱 극지식물 생육 분석 대시보드  |  Streamlit + Plotly  |  데이터 기반 분석")
