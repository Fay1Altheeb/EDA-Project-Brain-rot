"""Study description, answers to the research questions, and EDA conclusions."""

import pandas as pd
import streamlit as st

from analysis import accuracy_changes, group_changes
from app import (
    STRETCH, fine_print, flow_card, go_to_page, hero,
    insight_card, mini_insight, section,
)


# Answer the project's original research questions with concise conclusions.
def about_page(df: pd.DataFrame):
    hero(
        "ABOUT THE STUDY · INSIGHTS & CONCLUSION",
        "What did we <em>actually learn?</em>",
        "The project examines the relationship between TikTok, YouTube, Twitter, "
        "and Rest interruptions and performance on two different memory tasks.",
        ["Research questions", "Patterns and outliers", "Limitations"],
    )

    section("How was the experiment organized?", kicker="THE DESIGN")
    steps = [
        ("01", "Before", "Participants completed an initial ongoing word task and memory-cue trials."),
        ("02", "Interruption", "Participants were assigned to TikTok, YouTube, Twitter, or Rest."),
        ("03", "After", "The tasks were repeated to examine changes in correctness and speed."),
    ]
    for column, (number, title, detail) in zip(st.columns(3, gap="medium"), steps):
        with column:
            flow_card(number, title, detail)

    st.write("")
    left, right = st.columns(2, gap="large")
    with left:
        section("Lexical decision (LD)",
                "The ongoing task: decide whether a letter sequence is a real word.",
                "THE FIRST TASK")
    with right:
        section("Prospective memory (PM)",
                "Remember to perform a planned action when a target cue appears.",
                "THE SECOND TASK")

    section("Answers to our four research questions", kicker="EDA FINDINGS")
    questions = [
        (
            "01", "How does performance change before and after the interruption?",
            "LD correctness is relatively stable, while PM correctness changes more markedly. "
            "Participants also tend to respond a little faster afterward on average."
        ),
        (
            "02", "Do the results differ between the four interruption conditions?",
            "Yes. The TikTok group shows the largest average PM decline. Rest and Twitter "
            "show average improvements, while YouTube is broadly stable on average."
        ),
        (
            "03", "Do the two tasks show different patterns?",
            "Yes. LD is the more frequent, ongoing task and remains comparatively consistent. "
            "PM is less frequent and exhibits much greater variation in before/after correctness."
        ),
        (
            "04", "Are faster responses associated with lower accuracy?",
            "Not consistently. The relationship is weak or mixed across tasks, so these "
            "plots do not demonstrate a general speed–accuracy trade-off."
        ),
    ]
    for number, title, answer in questions:
        insight_card(number, title, answer)

    # Summarize patterns and unusual observations without overclaiming.
    section("Patterns, relationships and unusual cases", kicker="INSIGHTS SUMMARY")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        insight_card(
            "Pattern", "Memory cues are more variable",
            "The ongoing word task is comparatively steady. The biggest descriptive "
            "difference appears in memory-cue performance after TikTok interruption."
        )
        insight_card(
            "Relationship", "Speed does not tell the full story",
            "PM responses are usually slower than LD responses, but slight changes "
            "in speed do not correspond consistently to changes in correctness."
        )
    with col2:
        pm_changes = accuracy_changes(df).query("task == 'PM'")
        low_count = (pm_changes["change_pp"] <= -50).sum()
        insight_card(
            "Outliers", "Participants differ substantially",
            f"Several participants experienced sharp decreases in PM correctness "
            f"({low_count} had drops of at least 50 percentage points). "
            "Such results need review rather than automatic deletion."
        )
        insight_card(
            "Takeaway", "Compare tasks, not only platforms",
            "Changes in remembering an intended action are more noticeable than "
            "changes in simple word classification within this dataset."
        )

    section("Final conclusion", kicker="WHAT THE EDA SUPPORTS")
    mini_insight(
        "This experiment suggests that interruption conditions are associated with "
        "different patterns of prospective-memory performance, especially in the "
        "TikTok group. However, the exploratory analysis does not prove a lasting "
        "effect on memory or establish how ordinary social-media use affects everyone."
    )

    section("Limitations and interpretation", kicker="READ THE FINDINGS CAREFULLY")
    st.markdown(
        "The study includes only **60 participants**, with repeated trials for each "
        "person. The dashboard averages each participant's correctness before "
        "averaging groups; individual trials are not independent participants. "
        "The results reflect the supplied **`correct`** flag in `rt.csv`, not the "
        "paper's full analysis. One participant has unusually low LD correctness, "
        "which is kept in the data rather than silently excluded. "
        "Statistical significance and long-term effects were not established by this EDA."
    )
    st.markdown(
        "The mini-game uses original English examples and optional media embeds. "
        "It is an **educational demonstration**, not the published experiment; "
        "its player results are separate from the research dataset."
    )

    section("Sources and attribution", kicker="REFERENCES")
    st.markdown(
        "**Paper:** Chiossi et al. (2023), "
        "[Short-Form Videos Degrade Our Capacity to Retain Intentions]"
        "(https://doi.org/10.1145/3544548.3580778).  "
        "**Dataset:** [DaRUS repository]"
        "(https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-3327).  "
        "**Research code:** [GitHub]"
        "(https://github.com/mimuc/media-prospective-memory)."
    )
    fine_print("Conclusions are descriptive, based on the attached cleaned trial data.")
    st.button("Return to research charts  →", on_click=go_to_page,
              args=("Research dashboard",), **STRETCH)
