"""Page 1 - The experience: game logic first, then one function per screen.

Stages:  welcome -> pre -> middle -> post -> results
"""

import random
import statistics
import time
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from app import *


# GAME LOGIC (state, button callbacks, scoring) - no layout here
def init_game_state() :
    """Create the keys the game needs, once per browser session."""
    st.session_state.setdefault("game_stage", "welcome")
    st.session_state.setdefault("selected_interruption", FEED_MODES[0])
    st.session_state.setdefault("break_mode", FEED_MODES[0])


def select_interruption(mode: str) :
    """Welcome-page button: remember which interruption was clicked."""
    st.session_state.selected_interruption = mode


def start_game() :
    """Shuffle both rounds, clear records and begin the PRE test."""
    rng = random.Random()  # different order in each playthrough
    st.session_state.rounds = {
        "pre": rng.sample(PRE_ITEMS, len(PRE_ITEMS)),
        "post": rng.sample(POST_ITEMS, len(POST_ITEMS)),
    }
    st.session_state.game_records = []
    st.session_state.game_stage = "pre"
    st.session_state.game_idx = 0
    st.session_state.stimulus_started = None
    # Lock in the chosen interruption for the whole game.
    st.session_state.break_mode = st.session_state.selected_interruption


def reset_game() :
    """Back to the welcome screen (the last interruption stays selected)."""
    st.session_state.selected_interruption = st.session_state.break_mode
    st.session_state.game_stage = "welcome"


def start_second_round() :
    """Leave the MIDDLE interruption and begin the POST test."""
    st.session_state.game_stage = "post"
    st.session_state.game_idx = 0
    st.session_state.stimulus_started = None


def start_clock() :
    """Start timing the current item (once per rendered item)."""
    if st.session_state.stimulus_started is None:
        st.session_state.stimulus_started = time.perf_counter()


# Answering
def record_response(answer: str) :
    """Button callback: store the answer and advance to the next item."""
    stage = st.session_state.game_stage
    if stage not in ("pre", "post"):
        return
    trials = st.session_state.rounds[stage]
    index = st.session_state.game_idx
    if index >= len(trials):
        return

    word, target = trials[index]
    elapsed = None
    if st.session_state.stimulus_started is not None:
        elapsed = max(0.0, time.perf_counter() - st.session_state.stimulus_started)

    st.session_state.game_records.append(
        {
            "phase": stage,
            "stimulus": word,
            "task": "PM" if target == "cue" else "LD",
            "target": target,
            "answer": answer,
            "correct": answer == target,
            "approx_response_time": elapsed,
        }
    )
    st.session_state.game_idx += 1
    st.session_state.stimulus_started = None

    if st.session_state.game_idx >= len(trials):
        st.session_state.game_idx = 0
        # PRE -> MIDDLE, POST -> results.
        st.session_state.game_stage = "middle" if stage == "pre" else "results"


# Scoring

def percent_correct(records: list[dict]) :
    if not records:
        return 0
    return 100 * sum(r["correct"] for r in records) / len(records)


def compute_round_stats(records: list[dict], phase: str) :
    """Accuracy, cue accuracy, lexical-decision accuracy and median speed."""
    part = [r for r in records if r["phase"] == phase]
    cues = [r for r in part if r["task"] == "PM"]
    word_trials = [r for r in part if r["task"] == "LD"]
    observed = [r["approx_response_time"] for r in part if r["approx_response_time"] is not None]
    return {
        "total": len(part),
        "accuracy": percent_correct(part),
        "cue": percent_correct(cues),
        "ld": percent_correct(word_trials),
        "speed": statistics.median(observed) if observed else None,
    }


# Welcome
def render_interruption_buttons():
    """Four full-width buttons; the selected one is highlighted."""
    section("Which would you prefer the break to be?", kicker="THE BREAK")
    chosen = st.session_state.selected_interruption
    for column, mode in zip(st.columns(len(FEED_MODES), gap="small"), FEED_MODES):
        with column:
            st.button(
                mode,
                key=f"mode_{mode}",
                type="primary" if mode == chosen else "secondary",
                on_click=select_interruption,
                args=(mode,),
                **STRETCH,
            )


def render_welcome_screen() :
    hero(
        "INTERACTIVE EXPERIENCE · 2–3 MINUTES",
        "How much can your <em>mind hold?</em>",
        "Try a short word-and-memory challenge, pass through a short interruption, and see how your performance changes. Then explore the real research behind the idea.",
    )
    steps = [
        ("01", "Remember one rule", "When BLUE appears, choose Remember cue, even though it is a real word."),
        ("02", "Decide quickly", "For other stimuli, choose Real word or Made-up word."),
        ("03", "Compare rounds", "Pick an interruption and see your before/after scores."),
    ]
    for column, (number, title, description) in zip(st.columns(3, gap="medium"), steps):
        with column:
            flow_card(number, title, description)

    render_interruption_buttons()

    st.write("")
    left, right, _ = st.columns([1, 1, 1], gap="small")
    with left:
        st.button("Start the memory lab  →", type="primary", on_click=start_game, **STRETCH)
    with right:
        st.button("Explore real research instead", on_click=go_to_page, args=("Research dashboard",), **STRETCH)


# PRE and POST test
def render_trial_screen(stage: str) :
    label = "ROUND 01 · BEFORE" if stage == "pre" else "ROUND 02 · AFTER"
    section("The word + memory challenge", kicker=label)

    index = st.session_state.game_idx
    trials = st.session_state.rounds[stage]
    word, _target = trials[index]
    when = "Before" if stage == "pre" else "After"
    st.progress(index / len(trials), text=f"Question {index + 1} of {len(trials)} · {when} interruption")
    render_html(
        '<div class="game-stage"><div class="micro">LOOK CLOSELY · MAKE YOUR CHOICE</div>'
        f'<div class="main-word">{escape(word)}</div></div>'
    )

    start_clock()
    spacer()  # keeps the three buttons a little below the card

    col_word, col_nonword, col_cue = st.columns(3, gap="small")
    with col_word:
        st.button("✓  Real word", key=f"w_{stage}_{index}", on_click=record_response, args=("word",), **STRETCH)
    with col_nonword:
        st.button("◌  Made-up word", key=f"n_{stage}_{index}", on_click=record_response, args=("nonword",), **STRETCH)
    with col_cue:
        st.button(
            "Remember cue",
            key=f"c_{stage}_{index}",
            type="primary",
            on_click=record_response,
            args=("cue",),
            **STRETCH,
        )


# MIDDLE: show only the interruption the player selected before PRE.
def render_middle_media(mode):
    if mode == "YouTube":
        st.video(YOUTUBE_VIDEO_URL)
    elif mode == "TikTok":
        components.iframe(TIKTOK_PLAYER_URL, height=610, scrolling=False)
        st.link_button("Open TikTok in your browser", TIKTOK_SHORT_URL)
    elif mode == "Twitter":
        feed_card("TEXT FEED", "💬", "Browse posts on X / Twitter",
                  "Open the feed in another tab, then return to complete the POST round.")
        st.link_button("Open X / Twitter", TWITTER_FEED_URL)
    else:
        feed_card("QUIET PAUSE", "🌙", "Time to rest",
                  "Take a short break without social media. Continue when you are ready.")


# After the PRE round, show media or a rest activity before the POST round.
def render_middle_screen():
    mode = st.session_state.break_mode
    section(f"{mode} interruption", "Complete your interruption before the POST test.", "MIDDLE STAGE")
    render_middle_media(mode)

    st.write("")
    col_continue, _, _ = st.columns([1, 1, 1], gap="small")
    with col_continue:
        st.button("Continue to POST test  →", type="primary",
                  on_click=start_second_round, **STRETCH)
    hint(
        "This is an educational illustration with example media and no enforced "
        "viewing duration. It does not recreate the original controlled exposure."
    )


# Results
def render_results_chart(pre: dict, post: dict) :
    results = pd.DataFrame(
        {
            "Round": ["Before", "After"],
            "Cue accuracy (%)": [pre["cue"], post["cue"]],
            "Lexical decision accuracy (%)": [pre["ld"], post["ld"]],
        }
    )
    melted = results.melt("Round", var_name="Type", value_name="Accuracy (%)")
    fig = px.bar(
        melted,
        x="Round",
        y="Accuracy (%)",
        color="Type",
        barmode="group",
        color_discrete_map={"Cue accuracy (%)": "#B69DFF", "Lexical decision accuracy (%)": "#69D9C6"},
        text_auto=".0f",
        category_orders={"Round": ["Before", "After"]},
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(range=[0, 110])
    render_chart(fig, 360)


def render_results_reflection(pre: dict, post: dict, delta: float) :
    if delta > 0:
        summary = "Your accuracy increased in the second round."
    elif delta < 0:
        summary = "Your accuracy decreased in the second round."
    else:
        summary = "Your overall accuracy was unchanged."

    render_html(
        f'<div class="insight-card"><div class="insight-title">{summary}</div>'
        f'<div class="insight-copy">This mini-game has only 8 trials per round and '
        f"2 memory cues per round. A difference of one answer can noticeably "
        f"change the percentage. It cannot establish that the interruption "
        f"caused the change.</div></div>"
    )
    if pre["speed"] is not None and post["speed"] is not None:
        st.metric("Approximate median click interval · Before", f"{pre['speed']:.2f} s")
        st.metric("Approximate median click interval · After", f"{post['speed']:.2f} s")
        fine_print(
            "These intervals include network and app-processing delay, "
            "so they should not be compared with research-grade reaction times."
        )


def render_results_screen() :
    records = st.session_state.game_records
    pre = compute_round_stats(records, "pre")
    post = compute_round_stats(records, "post")
    delta = post["accuracy"] - pre["accuracy"]

    hero(
        "YOUR PERSONAL PLAYTHROUGH · COMPLETE",
        "You remembered. <em>Or did you?</em>",
        "Here is your mini-test result. It reflects two very short rounds, not a scientific measurement of memory or an estimate of social media effects.",
    )
    col_a, col_b, col_c = st.columns(3, gap="small")
    with col_a:
        stat_card(f"{pre['accuracy']:.0f}%", "Round 1 accuracy", "Before the interruption")
    with col_b:
        stat_card(f"{post['accuracy']:.0f}%", "Round 2 accuracy", "After the interruption")
    with col_c:
        stat_card(f"{delta:+.0f} pp", "Accuracy change", "Round 2 minus Round 1")

    st.write("")
    left, right = st.columns(2, gap="large")
    with left:
        section("Remembering the cue", "In this mini-game, BLUE was the prospective-memory cue.", "YOUR RESULTS")
        render_results_chart(pre, post)
    with right:
        section("Your reflection", kicker="HOW TO READ THIS")
        render_results_reflection(pre, post, delta)

    st.divider()
    section(
        "Now compare with the real experiment",
        "The study includes thousands of task attempts from 60 participants. Its findings cannot be inferred from a single playthrough.",
        "GO BEYOND THE GAME",
    )
    col_a, col_b, col_c = st.columns(3, gap="small")
    with col_a:
        st.button(
            "See all research charts  →", type="primary", on_click=go_to_page, args=("Research dashboard",), **STRETCH
        )
    with col_b:
        st.button("Try again", on_click=reset_game, **STRETCH)
    with col_c:
        st.button("How the research works", on_click=go_to_page, args=("About the study",), **STRETCH)


# Entry point of the page
def experience_page() :
    """Show the screen that matches the current game stage."""
    init_game_state()
    stage = st.session_state.game_stage
    if stage == "welcome":
        render_welcome_screen()
    elif stage in ("pre", "post"):
        render_trial_screen(stage)
    elif stage == "middle":
        render_middle_screen()
    else:
        render_results_screen()
