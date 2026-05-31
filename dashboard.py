import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
from scipy.stats.contingency import association

st.set_page_config(
    page_title="Biodiversity in National Parks",
    page_icon="🌿",
    layout="wide",
)

# ── Data loading & cleaning ────────────────────────────────────────────────────

@st.cache_data
def load_data():
    species = pd.read_csv("species_info.csv")
    observations = pd.read_csv("observations.csv")

    species["conservation_status"] = species["conservation_status"].fillna("No Concern")

    severity_map = {
        "No Concern": 0,
        "Species of Concern": 1,
        "In Recovery": 2,
        "Threatened": 3,
        "Endangered": 4,
    }
    species["_sev"] = species["conservation_status"].map(severity_map)
    species = (
        species.sort_values("_sev", ascending=False)
        .drop_duplicates(subset="scientific_name", keep="first")
        .drop(columns="_sev")
        .reset_index(drop=True)
    )
    species["at_risk"] = species["conservation_status"] != "No Concern"

    merged = observations.merge(
        species[["scientific_name", "category", "conservation_status", "at_risk"]],
        on="scientific_name",
        how="left",
    )

    return species, observations, merged


species, observations, merged = load_data()

STATUS_ORDER = ["Species of Concern", "In Recovery", "Threatened", "Endangered"]
STATUS_COLOURS = {
    "Species of Concern": "#4878d0",
    "In Recovery": "#6acc65",
    "Threatened": "#ee854a",
    "Endangered": "#d65f5f",
}
PARK_SHORT = {
    "Great Smoky Mountains National Park": "Great Smoky Mtns",
    "Yellowstone National Park": "Yellowstone",
    "Yosemite National Park": "Yosemite",
    "Bryce National Park": "Bryce",
}

# ── Sidebar navigation ─────────────────────────────────────────────────────────

st.sidebar.title("🌿 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Risk by Category",
        "Park Explorer",
        "Endangered Species",
        "Chi-Square Deep Dive",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: NPS species records & observation counts · "
    "Analysis: chi-square + Cramér's V"
)

# ── Overview ───────────────────────────────────────────────────────────────────

if page == "Overview":
    st.title("Biodiversity in US National Parks")
    st.markdown(
        "Exploratory analysis of conservation risk across species categories and parks "
        "using chi-square inference and observation data from four US national parks."
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Species", f"{len(species):,}")
    col2.metric("At-Risk Species", f"{species['at_risk'].sum():,}")
    col3.metric("Endangered", f"{(species['conservation_status'] == 'Endangered').sum()}")
    col4.metric("Parks", f"{merged['park_name'].nunique()}")
    col5.metric("Total Observations", f"{merged['observations'].sum():,.0f}")

    st.markdown("---")

    # Chi-square result banner
    contingency = pd.crosstab(species["category"], species["at_risk"])
    chi2_stat, p_val, dof, _ = chi2_contingency(contingency)
    cramers_v = association(contingency, method="cramer")

    st.subheader("Key Finding")
    b1, b2, b3 = st.columns(3)
    b1.metric("Chi-square statistic", f"{chi2_stat:.2f}")
    b2.metric("p-value", "< 0.0001")
    b3.metric("Cramér's V (effect size)", f"{cramers_v:.3f}")

    st.info(
        "Conservation risk is **not randomly distributed** across species categories. "
        "Mammals (17%) and Birds (15.4%) are disproportionately at risk. "
        "Effect size is weak (V=0.28) — significant but not dominant. "
        "All four parks sit within a narrow 2.6–2.8% at-risk band: risk is systemic, not geographic."
    )

    st.markdown("---")
    st.subheader("At-Risk Rate by Category")

    category_summary = (
        species.groupby("category")
        .agg(total=("scientific_name", "count"), at_risk_count=("at_risk", "sum"))
        .assign(at_risk_pct=lambda df: (df["at_risk_count"] / df["total"] * 100).round(1))
        .sort_values("at_risk_pct", ascending=True)
        .reset_index()
    )

    fig = px.bar(
        category_summary,
        x="at_risk_pct",
        y="category",
        orientation="h",
        text="at_risk_pct",
        color="at_risk_pct",
        color_continuous_scale="Reds",
        labels={"at_risk_pct": "% at risk", "category": ""},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=380, margin=dict(l=0, r=40))
    st.plotly_chart(fig, width="stretch")

# ── Risk by Category ───────────────────────────────────────────────────────────

elif page == "Risk by Category":
    st.title("Conservation Risk by Category")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("At-Risk Rate")
        category_summary = (
            species.groupby("category")
            .agg(total=("scientific_name", "count"), at_risk_count=("at_risk", "sum"))
            .assign(at_risk_pct=lambda df: (df["at_risk_count"] / df["total"] * 100).round(1))
            .sort_values("at_risk_pct", ascending=True)
            .reset_index()
        )
        fig = px.bar(
            category_summary,
            x="at_risk_pct",
            y="category",
            orientation="h",
            text="at_risk_pct",
            color="at_risk_pct",
            color_continuous_scale="Reds",
            labels={"at_risk_pct": "% at risk", "category": ""},
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(coloraxis_showscale=False, height=380, margin=dict(l=0, r=40))
        st.plotly_chart(fig, width="stretch")

    with col_right:
        st.subheader("Species Count by Category")
        fig2 = px.bar(
            category_summary.sort_values("total", ascending=True),
            x="total",
            y="category",
            orientation="h",
            text="total",
            color="total",
            color_continuous_scale="Blues",
            labels={"total": "Total species", "category": ""},
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(coloraxis_showscale=False, height=380, margin=dict(l=0, r=40))
        st.plotly_chart(fig2, width="stretch")

    st.markdown("---")
    st.subheader("Severity Breakdown (At-Risk Species Only)")
    st.caption("Binary at-risk flag masks how severe. Endangered = existential risk; Species of Concern = monitoring flag.")

    at_risk_species = species[species["at_risk"]].copy()
    severity_breakdown = (
        at_risk_species.groupby(["category", "conservation_status"])
        .size()
        .reset_index(name="count")
    )
    severity_breakdown["conservation_status"] = pd.Categorical(
        severity_breakdown["conservation_status"], categories=STATUS_ORDER, ordered=True
    )
    severity_breakdown = severity_breakdown.sort_values("conservation_status")

    # Order categories by total at-risk count
    cat_order = (
        at_risk_species.groupby("category").size().sort_values(ascending=True).index.tolist()
    )

    fig3 = px.bar(
        severity_breakdown,
        x="count",
        y="category",
        color="conservation_status",
        orientation="h",
        category_orders={"category": cat_order, "conservation_status": STATUS_ORDER},
        color_discrete_map=STATUS_COLOURS,
        labels={"count": "Number of species", "category": "", "conservation_status": "Status"},
        height=400,
    )
    fig3.update_layout(margin=dict(l=0))
    st.plotly_chart(fig3, width="stretch")

    st.markdown("**Key insight:** Birds have breadth (68 Species of Concern, 4 Endangered). "
                "Mammals have depth (6 Endangered — highest of any category). "
                "Fish: 7 of 11 at-risk fish are Threatened or Endangered (64% severity rate).")

# ── Park Explorer ──────────────────────────────────────────────────────────────

elif page == "Park Explorer":
    st.title("At-Risk Observations by Park")

    park_summary = (
        merged.groupby(["park_name", "at_risk"])["observations"]
        .sum()
        .unstack()
        .rename(columns={False: "not_at_risk", True: "at_risk"})
    )
    park_summary["total"] = park_summary["not_at_risk"] + park_summary["at_risk"]
    park_summary["at_risk_pct"] = (
        park_summary["at_risk"] / park_summary["total"] * 100
    ).round(2)
    park_summary = park_summary.sort_values("at_risk_pct", ascending=False).reset_index()
    park_summary["park_short"] = park_summary["park_name"].map(PARK_SHORT)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("At-Risk Observation Share")
        fig = px.bar(
            park_summary,
            x="at_risk_pct",
            y="park_short",
            orientation="h",
            text="at_risk_pct",
            color="at_risk_pct",
            color_continuous_scale="Reds",
            range_x=[0, 5],
            labels={"at_risk_pct": "% of observations", "park_short": ""},
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(coloraxis_showscale=False, height=320, margin=dict(l=0, r=40))
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Total Observations by Park")
        fig2 = px.bar(
            park_summary.sort_values("total", ascending=True),
            x="total",
            y="park_short",
            orientation="h",
            text="total",
            color="total",
            color_continuous_scale="Blues",
            labels={"total": "Total observations", "park_short": ""},
        )
        fig2.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig2.update_layout(coloraxis_showscale=False, height=320, margin=dict(l=0, r=60))
        st.plotly_chart(fig2, width="stretch")

    st.info("All four parks sit in a narrow 2.6–2.8% band. Risk is systemic at the species level — not driven by geography.")

    st.markdown("---")
    st.subheader("At-Risk Observation % by Category × Park")
    st.caption("Does the park-level similarity hold within each category?")

    cat_park = (
        merged.groupby(["park_name", "category", "at_risk"])["observations"]
        .sum()
        .unstack("at_risk")
        .rename(columns={False: "not_at_risk", True: "at_risk"})
        .fillna(0)
    )
    cat_park["at_risk_pct"] = (
        cat_park["at_risk"] / (cat_park["at_risk"] + cat_park["not_at_risk"]) * 100
    ).round(1)
    pivot = cat_park["at_risk_pct"].unstack("park_name")
    pivot.columns = [PARK_SHORT.get(c, c) for c in pivot.columns]

    fig3 = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="YlOrRd",
            text=pivot.values.round(1),
            texttemplate="%{text}%",
            showscale=True,
            colorbar=dict(title="% at-risk"),
        )
    )
    fig3.update_layout(height=400, margin=dict(l=0))
    st.plotly_chart(fig3, width="stretch")

    st.markdown("**Key insight:** Mammals ~14%, Birds ~13%, Fish ~6%, Plants ~1% — consistent across every park. "
                "Risk tracks species identity, not location.")

# ── Endangered Species ─────────────────────────────────────────────────────────

elif page == "Endangered Species":
    st.title("The 15 Endangered Species")
    st.markdown("Only 15 species hold Endangered status across all four parks.")

    endangered = species[species["conservation_status"] == "Endangered"][
        ["category", "scientific_name", "common_names"]
    ].sort_values(["category", "scientific_name"]).reset_index(drop=True)

    st.dataframe(
        endangered.rename(columns={
            "category": "Category",
            "scientific_name": "Scientific Name",
            "common_names": "Common Name(s)",
        }),
        width="stretch",
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("Observations of Endangered Species by Park")

    endangered_obs = (
        merged[merged["conservation_status"] == "Endangered"]
        .groupby(["park_name", "scientific_name"])["observations"]
        .sum()
        .unstack(fill_value=0)
    )
    endangered_obs.index = [PARK_SHORT.get(p, p) for p in endangered_obs.index]

    totals = endangered_obs.sum(axis=1).sort_values(ascending=False)
    for park, total in totals.items():
        st.metric(f"{park}", f"{total:,} endangered observations")

    st.markdown("")
    fig = go.Figure(
        data=go.Heatmap(
            z=endangered_obs.values,
            x=endangered_obs.columns.tolist(),
            y=endangered_obs.index.tolist(),
            colorscale="YlOrRd",
            text=endangered_obs.values,
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Observations"),
        )
    )
    fig.update_layout(
        height=280,
        margin=dict(l=0, b=120),
        xaxis=dict(tickangle=-40, tickfont=dict(size=10)),
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("**Key insight:** Yellowstone records 1,228 endangered observations — nearly 4× Great Smoky Mountains (334). "
                "Driven by Gray Wolf, Red Wolf, and Indiana Bat populations.")

# ── Chi-Square Deep Dive ───────────────────────────────────────────────────────

elif page == "Chi-Square Deep Dive":
    st.title("Chi-Square Test Deep Dive")
    st.markdown(
        "Chi-square test of independence: is conservation risk randomly distributed across species categories, "
        "or are certain categories systematically more at risk?"
    )

    contingency = pd.crosstab(species["category"], species["at_risk"])
    contingency.columns = ["Not at risk", "At risk"]

    chi2_stat, p_val, dof, expected_vals = chi2_contingency(contingency)
    cramers_v = association(contingency, method="cramer")

    c1, c2, c3 = st.columns(3)
    c1.metric("χ² statistic", f"{chi2_stat:.2f}")
    c2.metric("Degrees of freedom", dof)
    c3.metric("Cramér's V", f"{cramers_v:.3f} (weak effect)")

    st.markdown(
        "**Interpretation:** p < 0.0001 — the association is real. "
        "V = 0.277 means statistically significant but not a dominant relationship. "
        "The signal is driven by Mammals and Birds being far more at-risk than the expected rate."
    )

    st.markdown("---")
    st.subheader("Standardised Residuals")
    st.caption(
        "Residual > +2: more at-risk than expected. Residual < −2: less at-risk than expected. "
        "These show *which cells* drive the chi-square signal."
    )

    std_residuals = (contingency.values - expected_vals) / np.sqrt(expected_vals)
    residuals_df = pd.DataFrame(
        std_residuals,
        index=contingency.index,
        columns=["Not at risk", "At risk"],
    ).round(2)

    fig = go.Figure(
        data=go.Heatmap(
            z=residuals_df.values,
            x=residuals_df.columns.tolist(),
            y=residuals_df.index.tolist(),
            colorscale="RdBu_r",
            zmid=0,
            text=residuals_df.values,
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Std. residual"),
        )
    )
    fig.update_layout(height=380, margin=dict(l=0))
    st.plotly_chart(fig, width="stretch")

    st.markdown(
        "**Birds (+14.92) and Mammals (+10.20)** are the primary drivers — far more at-risk than the random baseline. "
        "**Vascular Plants (−7.81)** are strongly under-represented: fewer at-risk listings than their species count would predict. "
        "Reptiles (+1.56) fall below the ±2 threshold — their apparent risk rate is not statistically notable."
    )

    st.markdown("---")
    st.subheader("Contingency Table")
    st.dataframe(contingency, use_container_width=False)
    
