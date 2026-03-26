import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Market Trends 2026",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2e3450;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #7c83fd;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-top: 4px;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e2e8f0;
        border-left: 4px solid #7c83fd;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }
    [data-testid="stSidebar"] { background-color: #141620; }
    .stSelectbox label, .stMultiSelect label { color: #9ca3af; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("AI_Job_Market_Trends_2026.csv")
    skill_cols = ["skills_python", "skills_sql", "skills_ml", "skills_deep_learning", "skills_cloud"]
    df["total_skills"] = df[skill_cols].sum(axis=1)
    df["skill_list"] = df.apply(
        lambda r: ", ".join(
            [s.replace("skills_", "").replace("_", " ").title()
             for s in skill_cols if r[s] == 1]
        ) or "None", axis=1
    )
    return df

df = load_data()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Filters")
st.sidebar.markdown("---")

selected_countries = st.sidebar.multiselect(
    "🌍 Country",
    options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique()),
)
selected_roles = st.sidebar.multiselect(
    "💼 Job Title",
    options=sorted(df["job_title"].unique()),
    default=sorted(df["job_title"].unique()),
)
selected_exp = st.sidebar.multiselect(
    "📊 Experience Level",
    options=["Entry", "Mid", "Senior"],
    default=["Entry", "Mid", "Senior"],
)
selected_remote = st.sidebar.multiselect(
    "🏠 Remote Type",
    options=sorted(df["remote_type"].unique()),
    default=sorted(df["remote_type"].unique()),
)
salary_range = st.sidebar.slider(
    "💰 Salary Range (USD)",
    min_value=int(df["salary"].min()),
    max_value=int(df["salary"].max()),
    value=(int(df["salary"].min()), int(df["salary"].max())),
    step=1000,
    format="$%d",
)

# Apply filters
mask = (
    df["country"].isin(selected_countries) &
    df["job_title"].isin(selected_roles) &
    df["experience_level"].isin(selected_exp) &
    df["remote_type"].isin(selected_remote) &
    df["salary"].between(*salary_range)
)
fdf = df[mask].copy()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 24px 0 8px 0;'>
    <h1 style='color:#e2e8f0; font-size:2.2rem; margin:0;'>🤖 AI Job Market Trends 2026</h1>
    <p style='color:#9ca3af; margin-top:6px;'>Interactive dashboard — 10,345 job postings across 7 countries</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

if fdf.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar.")
    st.stop()

# ── KPI Row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, value, label):
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{value}</div>
        <div class='metric-label'>{label}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, f"{len(fdf):,}", "Total Listings")
kpi(k2, f"${fdf['salary'].mean():,.0f}", "Avg Salary")
kpi(k3, f"${fdf['salary'].median():,.0f}", "Median Salary")
kpi(k4, f"{fdf['job_openings'].sum():,}", "Total Openings")
kpi(k5, f"{fdf['years_experience'].mean():.1f} yrs", "Avg Experience")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Salary Analysis",
    "🌍 Geography",
    "💼 Roles & Skills",
    "🏢 Market Landscape",
    "📋 Raw Data",
])

COLOR_SEQ = px.colors.qualitative.Vivid
TEMPLATE = "plotly_dark"

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Salary Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Salary Distribution</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(
            fdf, x="salary", nbins=50,
            color_discrete_sequence=["#7c83fd"],
            title="Salary Distribution",
            template=TEMPLATE,
            labels={"salary": "Annual Salary (USD)"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.box(
            fdf, x="experience_level", y="salary",
            color="experience_level",
            category_orders={"experience_level": ["Entry", "Mid", "Senior"]},
            color_discrete_sequence=COLOR_SEQ,
            title="Salary by Experience Level",
            template=TEMPLATE,
            labels={"salary": "Salary (USD)", "experience_level": "Level"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Salary Comparisons</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        avg_sal = fdf.groupby("job_title")["salary"].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(
            avg_sal, x="salary", y="job_title",
            orientation="h",
            color="salary",
            color_continuous_scale="Viridis",
            title="Average Salary by Job Title",
            template=TEMPLATE,
            labels={"salary": "Avg Salary (USD)", "job_title": ""},
        )
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        avg_sal2 = fdf.groupby(["job_title", "experience_level"])["salary"].mean().reset_index()
        fig = px.bar(
            avg_sal2, x="job_title", y="salary",
            color="experience_level",
            barmode="group",
            category_orders={"experience_level": ["Entry", "Mid", "Senior"]},
            color_discrete_sequence=COLOR_SEQ,
            title="Salary by Role & Experience",
            template=TEMPLATE,
            labels={"salary": "Avg Salary (USD)", "job_title": "", "experience_level": "Level"},
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Salary vs Experience</div>", unsafe_allow_html=True)
    fig = px.scatter(
        fdf.sample(min(2000, len(fdf)), random_state=42),
        x="years_experience", y="salary",
        color="job_title",
        size="job_openings",
        hover_data=["country", "remote_type", "education_level"],
        color_discrete_sequence=COLOR_SEQ,
        title="Salary vs Years of Experience (sample of 2,000)",
        template=TEMPLATE,
        labels={"years_experience": "Years of Experience", "salary": "Salary (USD)", "job_title": "Role"},
        opacity=0.7,
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Geography
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>Job Listings by Country</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        country_counts = fdf["country"].value_counts().reset_index()
        country_counts.columns = ["country", "count"]
        fig = px.pie(
            country_counts, names="country", values="count",
            color_discrete_sequence=COLOR_SEQ,
            title="Job Listings Share by Country",
            template=TEMPLATE,
            hole=0.4,
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        avg_sal_country = fdf.groupby("country")["salary"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(
            avg_sal_country, x="country", y="salary",
            color="salary",
            color_continuous_scale="Blues",
            title="Average Salary by Country",
            template=TEMPLATE,
            labels={"salary": "Avg Salary (USD)", "country": "Country"},
        )
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Roles per Country</div>", unsafe_allow_html=True)
    role_country = fdf.groupby(["country", "job_title"]).size().reset_index(name="count")
    fig = px.bar(
        role_country, x="country", y="count", color="job_title",
        barmode="stack",
        color_discrete_sequence=COLOR_SEQ,
        title="Job Title Distribution by Country",
        template=TEMPLATE,
        labels={"count": "Listings", "job_title": "Role"},
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Remote Work by Country</div>", unsafe_allow_html=True)
    remote_country = fdf.groupby(["country", "remote_type"]).size().reset_index(name="count")
    fig = px.bar(
        remote_country, x="country", y="count", color="remote_type",
        barmode="group",
        color_discrete_sequence=["#7c83fd", "#f59e0b", "#10b981"],
        title="Work Arrangement by Country",
        template=TEMPLATE,
        labels={"count": "Listings", "remote_type": "Work Type"},
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Roles & Skills
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>Job Title Breakdown</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        role_counts = fdf["job_title"].value_counts().reset_index()
        role_counts.columns = ["job_title", "count"]
        fig = px.bar(
            role_counts, x="count", y="job_title",
            orientation="h",
            color="count",
            color_continuous_scale="Purples",
            title="Listings per Job Title",
            template=TEMPLATE,
            labels={"count": "Listings", "job_title": ""},
        )
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        skill_cols = ["skills_python", "skills_sql", "skills_ml", "skills_deep_learning", "skills_cloud"]
        skill_labels = ["Python", "SQL", "ML", "Deep Learning", "Cloud"]
        skill_demand = fdf[skill_cols].sum().values
        fig = go.Figure(go.Bar(
            x=skill_labels, y=skill_demand,
            marker_color=COLOR_SEQ[:5],
            text=skill_demand,
            textposition="outside",
        ))
        fig.update_layout(
            title="Overall Skill Demand",
            template=TEMPLATE,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_title="# Listings Requiring Skill",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Skills by Role</div>", unsafe_allow_html=True)
    skill_by_role = fdf.groupby("job_title")[skill_cols].mean().reset_index()
    skill_by_role.columns = ["job_title"] + skill_labels
    skill_melted = skill_by_role.melt(id_vars="job_title", var_name="Skill", value_name="Demand Rate")

    fig = px.bar(
        skill_melted, x="job_title", y="Demand Rate", color="Skill",
        barmode="group",
        color_discrete_sequence=COLOR_SEQ,
        title="Skill Demand Rate by Job Title",
        template=TEMPLATE,
        labels={"Demand Rate": "Proportion of Listings", "job_title": ""},
    )
    fig.update_layout(yaxis_tickformat=".0%", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Skills & Salary Correlation</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        skill_salary = []
        for col, label in zip(skill_cols, skill_labels):
            avg = fdf[fdf[col] == 1]["salary"].mean()
            no_avg = fdf[fdf[col] == 0]["salary"].mean()
            skill_salary.append({"Skill": label, "With Skill": avg, "Without Skill": no_avg})
        ss_df = pd.DataFrame(skill_salary).melt(id_vars="Skill", var_name="Has Skill", value_name="Avg Salary")
        fig = px.bar(
            ss_df, x="Skill", y="Avg Salary", color="Has Skill",
            barmode="group",
            color_discrete_sequence=["#7c83fd", "#f59e0b"],
            title="Avg Salary: With vs Without Each Skill",
            template=TEMPLATE,
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        total_skill_salary = fdf.groupby("total_skills")["salary"].mean().reset_index()
        fig = px.line(
            total_skill_salary, x="total_skills", y="salary",
            markers=True,
            color_discrete_sequence=["#7c83fd"],
            title="Avg Salary by Number of Skills Required",
            template=TEMPLATE,
            labels={"total_skills": "Number of Skills Required", "salary": "Avg Salary (USD)"},
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Education Level Analysis</div>", unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    with c5:
        edu_count = fdf["education_level"].value_counts().reset_index()
        edu_count.columns = ["education_level", "count"]
        fig = px.pie(
            edu_count, names="education_level", values="count",
            hole=0.4,
            color_discrete_sequence=COLOR_SEQ,
            title="Listings by Education Level",
            template=TEMPLATE,
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c6:
        edu_sal = fdf.groupby("education_level")["salary"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(
            edu_sal, x="education_level", y="salary",
            color="education_level",
            color_discrete_sequence=COLOR_SEQ,
            title="Avg Salary by Education Level",
            template=TEMPLATE,
            labels={"salary": "Avg Salary (USD)", "education_level": "Education"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Market Landscape
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>Company & Hiring Trends</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        comp_counts = fdf["company_size"].value_counts().reset_index()
        comp_counts.columns = ["company_size", "count"]
        fig = px.pie(
            comp_counts, names="company_size", values="count",
            hole=0.4,
            color_discrete_sequence=COLOR_SEQ,
            title="Listings by Company Size",
            template=TEMPLATE,
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        urgency_counts = fdf["hiring_urgency"].value_counts().reset_index()
        urgency_counts.columns = ["hiring_urgency", "count"]
        fig = px.bar(
            urgency_counts, x="hiring_urgency", y="count",
            color="hiring_urgency",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
            title="Listings by Hiring Urgency",
            template=TEMPLATE,
            labels={"count": "Listings", "hiring_urgency": "Urgency"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Industry Analysis</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        ind_counts = fdf["company_industry"].value_counts().reset_index()
        ind_counts.columns = ["company_industry", "count"]
        fig = px.bar(
            ind_counts, x="count", y="company_industry",
            orientation="h",
            color="count",
            color_continuous_scale="Teal",
            title="Listings by Industry",
            template=TEMPLATE,
            labels={"count": "Listings", "company_industry": ""},
        )
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        ind_sal = fdf.groupby("company_industry")["salary"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(
            ind_sal, x="company_industry", y="salary",
            color="salary",
            color_continuous_scale="Oranges",
            title="Avg Salary by Industry",
            template=TEMPLATE,
            labels={"salary": "Avg Salary (USD)", "company_industry": "Industry"},
        )
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Postings Over Time</div>", unsafe_allow_html=True)
    monthly = fdf.groupby(["job_posting_year", "job_posting_month"]).size().reset_index(name="count")
    monthly["date"] = pd.to_datetime(monthly[["job_posting_year", "job_posting_month"]].assign(day=1).rename(
        columns={"job_posting_year": "year", "job_posting_month": "month"}
    ))
    fig = px.line(
        monthly.sort_values("date"), x="date", y="count",
        color_discrete_sequence=["#7c83fd"],
        title="Monthly Job Postings Over Time",
        template=TEMPLATE,
        markers=True,
        labels={"date": "Month", "count": "Listings"},
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Company Size vs Salary Heatmap</div>", unsafe_allow_html=True)
    heat_data = fdf.groupby(["company_size", "experience_level"])["salary"].mean().reset_index()
    heat_pivot = heat_data.pivot(index="company_size", columns="experience_level", values="salary")
    heat_pivot = heat_pivot[["Entry", "Mid", "Senior"]]
    fig = px.imshow(
        heat_pivot,
        color_continuous_scale="Purples",
        title="Avg Salary Heatmap: Company Size × Experience Level",
        template=TEMPLATE,
        text_auto=".0f",
        aspect="auto",
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Raw Data
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("<div class='section-header'>Filtered Dataset</div>", unsafe_allow_html=True)
    st.markdown(f"Showing **{len(fdf):,}** rows matching current filters.")

    col_order = [
        "job_title", "country", "company_size", "company_industry",
        "experience_level", "years_experience", "education_level",
        "remote_type", "salary", "hiring_urgency", "job_openings",
        "job_posting_year", "job_posting_month", "skill_list",
    ]
    display_df = fdf[col_order].rename(columns={
        "job_title": "Title",
        "country": "Country",
        "company_size": "Company Size",
        "company_industry": "Industry",
        "experience_level": "Experience",
        "years_experience": "Yrs Exp",
        "education_level": "Education",
        "remote_type": "Work Type",
        "salary": "Salary (USD)",
        "hiring_urgency": "Urgency",
        "job_openings": "Openings",
        "job_posting_year": "Year",
        "job_posting_month": "Month",
        "skill_list": "Skills Required",
    })

    st.dataframe(
        display_df.reset_index(drop=True),
        use_container_width=True,
        height=500,
    )

    csv_bytes = fdf.to_csv(index=False).encode()
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="ai_job_market_filtered.csv",
        mime="text/csv",
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#4b5563; font-size:0.8rem;'>"
    "AI Job Market Trends 2026 · Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True,
)
