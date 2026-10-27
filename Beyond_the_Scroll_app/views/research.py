"""Research dashboard: five focused charts, each followed by a clear insight.

All figures are calculated from the supplied research trial data. The interactive
mini-game is separate and never changes these figures.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import (
    GROUP_ORDER, PHASE_ORDER, accuracy_changes, group_accuracy,
    group_changes, participant_response_times, speed_accuracy,
)
from app import (
    GROUP_COLORS, GROUP_NAMES, INK, PHASE_COLORS, STRETCH, TASK_COLORS,
    chapter, fine_print, go_to_page, hero, mini_insight, render_chart,
    section, stat_card,
)


# Display the two cognitive tasks with the same vocabulary throughout the app.
def task_name(code):
    return "Prospective memory" if code == "PM" else "Lexical decision"


# Plot 1: compare the average PRE and POST prospective-memory correctness.
def plot_pm_before_after(df):
    section(
        "What happened to memory after the interruption?",
        "Prospective memory (PM): remembering to carry out an intended action.",
        "01 / THE MAIN QUESTION",
    )
    pm = group_accuracy(df).query("task == 'PM'").copy()
    pm["Group"] = pm["interruption_group"].map(GROUP_NAMES)
    pm["Phase"] = pm["phase"].map({"pre": "Before", "post": "After"})
    fig = px.line(
        pm, x="Phase", y="accuracy_pct", color="Group", markers=True,
        category_orders={"Phase": ["Before", "After"],
                         "Group": [GROUP_NAMES[g] for g in GROUP_ORDER]},
        color_discrete_map={GROUP_NAMES[g]: GROUP_COLORS[g] for g in GROUP_ORDER},
        labels={"accuracy_pct": "Average participant correctness (%)"},
        hover_data={"participants": True},
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    fig.update_yaxes(range=[0, 105])
    render_chart(fig, 420)
    mini_insight(
        "The TikTok group shows the clearest downward change in prospective-memory "
        "correctness. Rest and Twitter trend upward, while YouTube is nearly stable "
        "on average. These are descriptive results, not a significance test."
    )


# Plot 2: show that the changes differ greatly between task types.
def plot_change_by_task(df):
    chapter("How does that compare with the ongoing word task?")
    changes = group_changes(df).copy()
    changes["Group"] = changes["interruption_group"].map(GROUP_NAMES)
    changes["Task"] = changes["task"].map({"LD": "Lexical decision", "PM": "Prospective memory"})
    fig = px.bar(
        changes, x="Group", y="change_pp", color="Task", barmode="group",
        color_discrete_map={"LD": TASK_COLORS["LD"], "PM": TASK_COLORS["PM"],
                            "Lexical decision": TASK_COLORS["LD"],
                            "Prospective memory": TASK_COLORS["PM"]},
        category_orders={"Group": [GROUP_NAMES[g] for g in GROUP_ORDER]},
        labels={"change_pp": "Average change (percentage points)"},
        hover_data={"participants": True},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#C9D4E3", opacity=0.75)
    render_chart(fig, 395)
    mini_insight(
        "Lexical-decision correctness changes very little across conditions, "
        "whereas prospective-memory correctness changes much more. The difference "
        "reflects two tasks with different cognitive demands."
    )


# Plot 3: show the spread, not just the average, of individual PM changes.
def plot_individual_variation(df):
    section(
        "Did everyone respond the same way?",
        "Each point represents one participant's change in PM correctness.",
        "02 / INDIVIDUAL DIFFERENCES",
    )
    changes = accuracy_changes(df).query("task == 'PM'").copy()
    changes["Group"] = changes["interruption_group"].map(GROUP_NAMES)
    fig = px.box(
        changes, x="Group", y="change_pp", color="Group", points="all",
        color_discrete_map={GROUP_NAMES[g]: GROUP_COLORS[g] for g in GROUP_ORDER},
        category_orders={"Group": [GROUP_NAMES[g] for g in GROUP_ORDER]},
        hover_data=["participant_id", "pre", "post"],
        labels={"change_pp": "Participant PM accuracy change (pp)"},
    )
    fig.update_layout(showlegend=False)
    fig.add_hline(y=0, line_dash="dash", line_color="#C9D4E3", opacity=0.75)
    render_chart(fig, 450)
    mini_insight(
        "Participants do not respond identically. Some experience large decreases "
        "even in groups with little average change. These unusual values deserve "
        "inspection; they should not be removed automatically."
    )


# Plot 4: compare participant-level mean response times by task and phase.
def plot_response_speed(df):
    section(
        "Did participants answer faster after the break?",
        "Response-time averages are calculated per participant before combining them.",
        "03 / RESPONSE SPEED",
    )
    per_person = participant_response_times(df).dropna(subset=["response_time"])
    time_summary = (
        per_person.groupby(["task", "phase"], as_index=False)["response_time"].mean()
    )
    time_summary["Task"] = time_summary["task"].map({"LD": "Lexical decision", "PM": "Prospective memory"})
    time_summary["Phase"] = time_summary["phase"].map({"pre": "Before", "post": "After"})
    fig = px.bar(
        time_summary, x="Task", y="response_time", color="Phase", barmode="group",
        color_discrete_map={"Before": PHASE_COLORS["pre"], "After": PHASE_COLORS["post"]},
        category_orders={"Task": ["Lexical decision", "Prospective memory"],
                         "Phase": ["Before", "After"]},
        labels={"response_time": "Mean response time (seconds)"},
        text_auto=".2f",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(rangemode="tozero")
    render_chart(fig, 390)
    mini_insight(
        "Prospective-memory responses generally take longer than lexical decisions. "
        "Both tasks are slightly faster after the interruption on average, but "
        "faster responses do not necessarily mean better accuracy."
    )


# Plot 5: compare average response time with accuracy at participant level.
def plot_speed_accuracy(df):
    chapter("Does being faster mean being less accurate?")
    results = speed_accuracy(df).dropna(subset=["avg_response_time", "accuracy"]).copy()
    results["Correctness (%)"] = 100 * results["accuracy"]
    results["Task"] = results["task"].map({"LD": "Lexical decision", "PM": "Prospective memory"})
    results["Group"] = results["interruption_group"].map(GROUP_NAMES)
    fig = px.scatter(
        results, x="avg_response_time", y="Correctness (%)", color="Group",
        facet_col="Task", opacity=0.86,
        color_discrete_map={GROUP_NAMES[g]: GROUP_COLORS[g] for g in GROUP_ORDER},
        category_orders={"Task": ["Lexical decision", "Prospective memory"],
                         "Group": [GROUP_NAMES[g] for g in GROUP_ORDER]},
        hover_data=["participant_id"],
        labels={"avg_response_time": "Participant mean response time (seconds)"},
    )
    fig.update_yaxes(range=[0, 105])
    render_chart(fig, 440)
    mini_insight(
        "There is no consistent speed–accuracy trade-off across the two tasks. "
        "A few atypical participants can influence the apparent relationship, "
        "so the scatterplots are descriptive rather than evidence of a general rule."
    )


# Keep the interactive dashboard focused on the research questions.
def research_page(df: pd.DataFrame):
    hero(
        "THE RESEARCH · BEYOND THE SCROLL",
        "What changed <em>after the interruption?</em>",
        "Five focused visualizations connect the experiment to four research questions: "
        "performance change, interruption type, task differences, and response speed.",
        ["60 participants", "4 interruption groups", "PRE vs POST"],
    )
    pm = group_changes(df).query("task == 'PM'")
    worst = pm.loc[pm["change_pp"].idxmin()]
    stat1, stat2, stat3 = st.columns(3, gap="small")
    with stat1:
        stat_card(str(df["participant_id"].nunique()), "Participants", "Repeated measurements per person")
    with stat2:
        stat_card(f"{worst['change_pp']:+.1f} pp", "Largest average PM decline", GROUP_NAMES[worst["interruption_group"]])
    with stat3:
        stat_card("2", "Task types", "Ongoing decision + intended action")

    main_tab, variation_tab, speed_tab = st.tabs(
        ["Memory outcomes", "Individual differences", "Response speed"]
    )
    with main_tab:
        plot_pm_before_after(df)
        plot_change_by_task(df)
    with variation_tab:
        plot_individual_variation(df)
    with speed_tab:
        plot_response_speed(df)
        plot_speed_accuracy(df)

    st.divider()
    section(
        "What does the evidence suggest?",
        "Memory-cue performance changed more than the ongoing word task, particularly "
        "for the TikTok group. These results are specific to this experiment.",
        "TAKEAWAY",
    )
    fine_print(
        "These charts describe the researcher-provided trial correctness flag in rt.csv. "
        "They average participants equally and exclude practice trials for comparisons. "
        "They do not reproduce the article's official significance tests or its acc.csv analysis."
    )
    col1, col2, _ = st.columns([1, 1, 1])
    with col1:
        st.button("Read conclusions  →", on_click=go_to_page,
                  args=("About the study",), type="primary", **STRETCH)
    with col2:
        st.button("Explore raw records", on_click=go_to_page,
                  args=("Data explorer",), **STRETCH)
