"""Page 3 - Data explorer: filters, table, download, quality checks, dictionary."""


import pandas as pd
import streamlit as st

from analysis import GROUP_ORDER


# Table that explains what each column of clean_data.csv means.
DATA_DICTIONARY = pd.DataFrame(
    [
        ("participant_id", "Anonymous participant identifier; use as a category, not a numeric variable."),
        ("task", "LD = lexical decision; PM = prospective memory cue trial."),
        ("interruption_group", "Between-participant condition: rest, TikTok, YouTube or Twitter."),
        ("phase", "train = practice; pre = before; post = after the interruption."),
        ("stimulus", "Word or letter sequence presented on a trial (German stimuli in original study)."),
        ("success", "Researcher-supplied success flag; not interchangeable with correctness."),
        ("correct", "Researcher-supplied Boolean correctness flag for the trial."),
        ("response_time", "Recorded reaction time in seconds; some attempts have no recorded time."),
        ("stimulus_length", "Engineered feature: number of characters in stimulus."),
    ],
    columns=["Column", "Meaning"],
)
from app import (GROUP_NAMES,STRETCH,hero,section,stat_card,)


#Three dropdowns (group, task, phase)
def render_data_filters(df: pd.DataFrame) :
    section("Choose which trials to inspect", "Filters apply to the preview and exported CSV.", "FILTER THE DATA")
    col_a, col_b, col_c = st.columns(3, gap="small")
    with col_a:
        groups = st.multiselect(
            "Interruption group", GROUP_ORDER, default=GROUP_ORDER, format_func=lambda x: GROUP_NAMES[x]
        )
    with col_b:
        tasks = st.multiselect("Task type", ["LD", "PM"], default=["LD", "PM"])
    with col_c:
        phases = st.multiselect("Experimental phase", ["train", "pre", "post"], default=["pre", "post"])
    return df.loc[df.interruption_group.isin(groups) & df.task.isin(tasks) & df.phase.isin(phases)]

# Left: how many values are missing in each column.
# Right: summary statistics (mean, min, max...) for the numeric columns.
def render_data_quality(selected: pd.DataFrame) :
    left, right = st.columns(2, gap="large")
    with left:
        section("Data quality", "The missing response times are deliberately preserved.", "QUALITY CHECK")
        missing = selected.isna().sum().sort_values(ascending=False)
        quality = pd.DataFrame(
            {
                "Feature": missing.index,
                "Missing values": missing.values,
                "Missing %": (100 * missing / len(selected)).round(2).values,
            }
        )
        st.dataframe(quality, hide_index=True, height=330, **STRETCH)
    with right:
        section("Summary statistics", "Numeric values include the derived character length.", "STATISTICS")
        st.dataframe(selected[["response_time", "stimulus_length"]].describe().round(2), height=330, **STRETCH)

# Puts everything together from top to bottom.
def data_page(df: pd.DataFrame) :
    hero(
        "DATA EXPLORER · TRANSPARENT ANALYSIS",
        "Look closer at <em>every row.</em>",
        "Browse the supplied cleaned dataset, inspect its structure, identify missing values, and download a filtered subset.",
        ["Downloadable CSV", "Interactive table", "Data dictionary"],
    )
    # Three big numbers about the whole file
    col_a, col_b, col_c = st.columns(3, gap="small")
    with col_a:
        stat_card(f"{len(df):,}", "Rows in provided clean file")
    with col_b:
        stat_card(f"{df.shape[1] - 1}", "Original study columns", "+1 engineered stimulus length")
    with col_c:
        stat_card(f"{df.participant_id.nunique()}", "Unique participants")

    #  Filters
    selected = render_data_filters(df)
    if selected.empty:
        st.warning("No rows match these filters. Choose at least one value in each filter.")
        return

     # Three small numbers about the filtered rows
    col_a, col_b, col_c = st.columns(3, gap="small")
    with col_a:
        st.metric("Visible rows", f"{len(selected):,}")
    with col_b:
        st.metric("Missing response times", f"{selected.response_time.isna().sum():,}")
    with col_c:
        st.metric("Duplicate rows", f"{selected.duplicated().sum():,}")

    # Table preview + CSV download
    section("The first rows", "Each row represents one experimental trial, not one person.", "EXPLORE")
    st.dataframe(selected.head(500), hide_index=True, height=365, **STRETCH)
    st.download_button(
        "Download filtered CSV  ↓",
        data=selected.to_csv(index=False).encode("utf-8"),
        file_name="beyond_the_scroll_filtered.csv",
        mime="text/csv",
        type="primary",
    )

    st.write("")
    render_data_quality(selected)
    section("Data dictionary", "Names match the cleaned version of the uploaded rt.csv.", "MEANING OF EACH COLUMN")
    st.dataframe(DATA_DICTIONARY, hide_index=True, **STRETCH)
