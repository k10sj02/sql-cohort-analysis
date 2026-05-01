from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import joblib

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cohort Retention Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .block-container { padding-top: 2rem; }
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid #313244;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #cdd6f4; }
    .metric-label { font-size: 0.8rem; color: #6c7086; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-delta { font-size: 0.85rem; margin-top: 0.2rem; }
    h1, h2, h3 { color: #cdd6f4 !important; }
    .stMarkdown p { color: #a6adc8; }
    div[data-testid="stSidebar"] { background: #181825; }
    .insight-box {
        background: #1e1e2e;
        border-left: 3px solid #89b4fa;
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #cdd6f4;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ─── Data loading — reads pre-built joblib cache only ───────────────────────
CACHE_DIR = Path(__file__).parent / "data" / "processed"


@st.cache_resource(show_spinner="Loading cached data…")
def load_all():
    missing = [
        f
        for f in ["df", "cohort_pivot", "retention", "cohort_size"]
        if not (CACHE_DIR / f"{f}.joblib").exists()
    ]
    if missing:
        st.error(
            f"Cache files missing: {missing}. Run `uv run python preprocess.py` first.",
            icon="🚨",
        )
        st.stop()
    return (
        joblib.load(CACHE_DIR / "df.joblib"),
        joblib.load(CACHE_DIR / "cohort_pivot.joblib"),
        joblib.load(CACHE_DIR / "retention.joblib"),
        joblib.load(CACHE_DIR / "cohort_size.joblib"),
    )


def compute_kpis(df: pd.DataFrame, cohort_size: pd.Series):
    total_customers = df["CustomerID"].nunique()
    total_revenue = (df["Quantity"] * df["UnitPrice"]).sum()
    avg_order_value = (
        (df["Quantity"] * df["UnitPrice"]).groupby(df["InvoiceNo"]).sum().mean()
    )
    avg_retention_m2 = cohort_size  # placeholder
    cohort_sizes = cohort_size.values
    return {
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "num_cohorts": len(cohort_size),
        "largest_cohort": int(cohort_sizes.max()),
        "smallest_cohort": int(cohort_sizes.min()),
    }


# ─── Heatmap builder ────────────────────────────────────────────────────────
def make_heatmap(matrix: pd.DataFrame, title: str, is_pct: bool, colorscale: str):
    z = matrix.values.tolist()
    x = [str(c) for c in matrix.columns]
    y = [str(p) for p in matrix.index]

    text = []
    for row in matrix.values:
        text_row = []
        for val in row:
            if pd.isna(val):
                text_row.append("")
            elif is_pct:
                text_row.append(f"{val:.0f}%")
            else:
                text_row.append(f"{int(val):,}")
        text.append(text_row)

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=x,
            y=y,
            text=text,
            texttemplate="%{text}",
            textfont={"size": 11},
            colorscale=colorscale,
            showscale=True,
            hoverongaps=False,
            xgap=2,
            ygap=2,
            zmin=0,
            zmax=100 if is_pct else None,
            colorbar=dict(
                thickness=12,
                tickfont=dict(color="#a6adc8"),
                ticksuffix="%" if is_pct else "",
            ),
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#cdd6f4")),
        xaxis=dict(
            title="Cohort Index (months since first purchase)",
            tickfont=dict(color="#a6adc8"),
            title_font=dict(color="#6c7086"),
        ),
        yaxis=dict(
            title="Cohort Period",
            tickfont=dict(color="#a6adc8"),
            title_font=dict(color="#6c7086"),
            autorange="reversed",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6f4"),
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
    )
    return fig


def make_retention_lines(retention: pd.DataFrame, selected_cohorts):
    fig = go.Figure()
    colors = px.colors.qualitative.Pastel
    subset = retention.loc[[c for c in selected_cohorts if c in retention.index]]

    for i, (cohort, row) in enumerate(subset.iterrows()):
        row_clean = row.dropna()
        fig.add_trace(
            go.Scatter(
                x=row_clean.index.tolist(),
                y=row_clean.values.tolist(),
                mode="lines+markers",
                name=str(cohort),
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        title=dict(
            text="Retention Curves by Cohort", font=dict(size=16, color="#cdd6f4")
        ),
        xaxis=dict(
            title="Cohort Index",
            tickfont=dict(color="#a6adc8"),
            title_font=dict(color="#6c7086"),
        ),
        yaxis=dict(
            title="Retention %",
            tickfont=dict(color="#a6adc8"),
            title_font=dict(color="#6c7086"),
            ticksuffix="%",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,30,46,0.6)",
        font=dict(color="#cdd6f4"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a6adc8")),
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
    )
    return fig


def make_cohort_size_bar(cohort_size: pd.Series):
    fig = go.Figure(
        go.Bar(
            x=[str(c) for c in cohort_size.index],
            y=cohort_size.values,
            marker_color="#89b4fa",
            marker_line_width=0,
        )
    )
    fig.update_layout(
        title=dict(
            text="New Customers per Cohort", font=dict(size=16, color="#cdd6f4")
        ),
        xaxis=dict(tickfont=dict(color="#a6adc8"), title_font=dict(color="#6c7086")),
        yaxis=dict(tickfont=dict(color="#a6adc8"), title_font=dict(color="#6c7086")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,30,46,0.6)",
        font=dict(color="#cdd6f4"),
        margin=dict(l=20, r=20, t=60, b=20),
        height=320,
    )
    return fig


def make_avg_retention_bar(retention: pd.DataFrame):
    avg = retention.mean(skipna=True)
    fig = go.Figure(
        go.Bar(
            x=[str(c) for c in avg.index],
            y=avg.values,
            marker_color=avg.values,
            marker_colorscale="RdYlGn",
            marker_cmin=0,
            marker_cmax=100,
            marker_line_width=0,
            text=[f"{v:.1f}%" for v in avg.values],
            textposition="outside",
            textfont=dict(color="#a6adc8", size=10),
        )
    )
    fig.update_layout(
        title=dict(
            text="Average Retention Rate by Cohort Index",
            font=dict(size=16, color="#cdd6f4"),
        ),
        xaxis=dict(
            title="Cohort Index",
            tickfont=dict(color="#a6adc8"),
            title_font=dict(color="#6c7086"),
        ),
        yaxis=dict(
            title="Avg Retention %",
            tickfont=dict(color="#a6adc8"),
            title_font=dict(color="#6c7086"),
            ticksuffix="%",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,30,46,0.6)",
        font=dict(color="#cdd6f4"),
        margin=dict(l=20, r=20, t=60, b=40),
        height=360,
    )
    return fig


# ─── Excel export ────────────────────────────────────────────────────────────
def to_excel(abs_df: pd.DataFrame, pct_df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        abs_df.to_excel(writer, sheet_name="Absolute Counts")
        pct_df.round(1).to_excel(writer, sheet_name="Retention %")
    return buf.getvalue()


# ─── Layout ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")
    max_index = st.slider("Max Cohort Index shown", min_value=3, max_value=13, value=13)
    colorscale = st.selectbox(
        "Heatmap colour scale", ["RdYlGn", "Blues", "Viridis", "Plasma"], index=0
    )
    st.markdown("---")
    st.markdown("### 📖 How to read this")
    st.markdown("""
**Horizontally →** Track a single cohort's retention over time.

**Vertically ↓** Compare cohorts at the same age.

**Diagonally ↘** Spot calendar-driven spikes (e.g. holiday season).

*Index 1 = month of first purchase (always 100%).*
    """)
    st.markdown("---")
    st.caption("Data: UCI Online Retail Dataset")

# ── Load & process ────────────────────────────────────────────────────────────
df, cohort_pivot, retention, cohort_size = load_all()
kpis = compute_kpis(df, cohort_size)

# Trim to selected max index
cols_to_show = [c for c in cohort_pivot.columns if c <= max_index]
pivot_trimmed = cohort_pivot[cols_to_show]
retention_trimmed = retention[cols_to_show]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Customer Cohort Retention Analysis")
st.markdown("*Online Retail Dataset · Dec 2010 – Dec 2011*")
st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Unique Customers</div>
        <div class="metric-value">{kpis['total_customers']:,}</div>
    </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">£{kpis['total_revenue']:,.0f}</div>
    </div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Avg Order Value</div>
        <div class="metric-value">£{kpis['avg_order_value']:,.2f}</div>
    </div>""",
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Total Cohorts</div>
        <div class="metric-value">{kpis['num_cohorts']}</div>
    </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Heatmaps ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["🔥 Retention Heatmaps", "📈 Retention Curves", "📦 Cohort Sizing"]
)

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(
            make_heatmap(
                retention_trimmed,
                "Retention Rate (%)",
                is_pct=True,
                colorscale=colorscale,
            ),
            use_container_width=True,
        )
    with col_b:
        st.plotly_chart(
            make_heatmap(
                pivot_trimmed,
                "Absolute Customer Counts",
                is_pct=False,
                colorscale="Blues",
            ),
            use_container_width=True,
        )

    st.markdown("#### 💡 Key Insights")
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        m2_avg = retention_trimmed[2].mean() if 2 in retention_trimmed.columns else 0
        st.markdown(
            f"""<div class="insight-box">
            <strong>Month 2 Drop-off</strong><br>
            Average retention at index 2 is <strong>{m2_avg:.0f}%</strong> — the steepest single-month decline.
            A loyalty nudge in this window could significantly move the needle.
        </div>""",
            unsafe_allow_html=True,
        )
    with col_i2:
        nov_col = 12 if 12 in retention_trimmed.columns else None
        if nov_col:
            nov_avg = retention_trimmed[nov_col].mean()
            st.markdown(
                f"""<div class="insight-box">
                <strong>November Surge (Index 12)</strong><br>
                Index 12 averages <strong>{nov_avg:.0f}%</strong> — higher than surrounding months,
                consistent with holiday/Thanksgiving lift.
            </div>""",
                unsafe_allow_html=True,
            )
    with col_i3:
        first_cohort_size = cohort_size.iloc[0]
        last_cohort_size = cohort_size.iloc[-1]
        delta = (last_cohort_size - first_cohort_size) / first_cohort_size * 100
        st.markdown(
            f"""<div class="insight-box">
            <strong>Acquisition Trend</strong><br>
            New customer acquisition shifted from <strong>{first_cohort_size:,}</strong>
            (Dec '10) to <strong>{last_cohort_size:,}</strong> (Dec '11) — a
            <strong>{delta:+.0f}%</strong> change worth investigating.
        </div>""",
            unsafe_allow_html=True,
        )

with tab2:
    all_cohorts = retention_trimmed.index.tolist()
    default_sel = all_cohorts[:5]
    selected = st.multiselect(
        "Select cohorts to display",
        options=[str(c) for c in all_cohorts],
        default=[str(c) for c in default_sel],
    )
    selected_periods = [c for c in all_cohorts if str(c) in selected]

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.plotly_chart(
            make_retention_lines(retention_trimmed, selected_periods),
            use_container_width=True,
        )
    with col_right:
        st.plotly_chart(
            make_avg_retention_bar(retention_trimmed), use_container_width=True
        )

with tab3:
    col_x, col_y = st.columns([3, 2])
    with col_x:
        st.plotly_chart(make_cohort_size_bar(cohort_size), use_container_width=True)
    with col_y:
        st.markdown("#### Cohort Size Summary")
        size_df = cohort_size.rename("New Customers").reset_index()
        size_df.columns = ["Cohort Period", "New Customers"]
        size_df["% of Total"] = (
            size_df["New Customers"] / size_df["New Customers"].sum() * 100
        ).round(1)
        st.dataframe(
            size_df.set_index("Cohort Period"), use_container_width=True, height=320
        )

# ── Raw data & export ─────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🗂  Raw Cohort Tables"):
    t1, t2 = st.tabs(["Retention %", "Absolute Counts"])
    with t1:
        st.dataframe(
            retention_trimmed.round(1).style.background_gradient(
                cmap="RdYlGn", vmin=0, vmax=100
            ),
            use_container_width=True,
        )
    with t2:
        st.dataframe(pivot_trimmed.fillna("").astype(str), use_container_width=True)

excel_bytes = to_excel(pivot_trimmed, retention_trimmed)
st.download_button(
    label="⬇️  Download cohort tables (.xlsx)",
    data=excel_bytes,
    file_name="cohort_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Built by Stann-Omar Jones")
