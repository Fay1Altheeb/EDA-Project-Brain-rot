"""Beyond the Scroll: interactive memory experience + research dashboard.

Run from this folder:  python -m streamlit run app.py

The game is a playful illustration, not the 2023 study's actual protocol.

Project layout
--------------
app.py              settings, look (CSS + cards), data loading, sidebar, page routing
analysis.py         pandas helpers for the research charts
views/experience.py page 1 - the mini-game (logic + screens)
views/research.py   page 2 - research dashboard (EDA)
views/explorer.py   page 3 - data explorer
views/about.py      page 4 - about the study

The view files import their helpers from this file (from app import ...).
"""

from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import load_data

# 1. SETTINGS (paths, colours, game words, video links)
# --- Paths and navigation
DATA_PATH = Path(__file__).resolve().parent / "clean_data.csv"

PAGES = ["The experience", "Research dashboard", "Data explorer", "About the study"]


def stretch_kwargs() -> dict:
    """Full-width option; Streamlit renamed it in version 1.50."""
    major, minor = (int(part) for part in st.__version__.split(".")[:2])
    if (major, minor) >= (1, 50):
        return {"width": "stretch"}
    return {"use_container_width": True}


STRETCH = stretch_kwargs()

# Research colours and names
GROUP_NAMES = {"rest": "Rest", "tiktok": "TikTok", "youtube": "YouTube", "twitter": "Twitter"}
GROUP_COLORS = {"rest": "#67D8C4", "tiktok": "#B59CFF", "youtube": "#F7BB79", "twitter": "#8BAFFF"}
TASK_COLORS = {"LD": "#9C80E7", "PM": "#E8A3D8"}
TASK_NAMES = {"LD": "Lexical Decision", "PM": "Prospective Memory"}
PHASE_COLORS = {"pre": "#96A4BD", "post": "#B59CFF"}
INK = "#EDEBFF"

# Mini-game content
# For each round: 6 ordinary LD items + 2 BLUE intention cues.
# The content and timings are not those of the published experiment.
PRE_ITEMS = [
    ("CLOUD", "word"), ("TRANE", "nonword"), ("BLUE", "cue"), ("HOUSE", "word"),
    ("SLINT", "nonword"), ("GARDEN", "word"), ("BLUE", "cue"), ("PLAVE", "nonword"),
]
POST_ITEMS = [
    ("RIVER", "word"), ("DREMP", "nonword"), ("BLUE", "cue"), ("MUSIC", "word"),
    ("FLONE", "nonword"), ("PLANET", "word"), ("BLUE", "cue"), ("GREST", "nonword"),
]

# The four interruption choices (educational examples, not the study's exact stimuli).
FEED_MODES = ["TikTok", "YouTube", "Twitter", "Rest"]

# Middle-stage media (replace with your own links)
YOUTUBE_VIDEO_URL = "https://youtu.be/m34ZKJNyxac"

# The short link opens the video; the embedded player needs the numeric video ID.
TIKTOK_SHORT_URL = "https://vt.tiktok.com/ZSgXu1t7n/"
TIKTOK_VIDEO_ID = "7661198271196482837"
TIKTOK_PLAYER_URL = f"https://www.tiktok.com/player/v1/{TIKTOK_VIDEO_ID}"

# X/Twitter does not allow its ordinary scrolling feed inside an iframe.
TWITTER_FEED_URL = "https://x.com/explore"


# 2. LOOK: CSS and building blocks
STYLESHEET = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {--ink:#F5F2FF;--muted:#A8B1CC;--border:#303751;--violet:#B59CFF;--teal:#67D8C4;}
html,body,[class*="css"] {font-family:'DM Sans',system-ui,sans-serif;}
[data-testid="stAppViewContainer"] {background:radial-gradient(circle at 75% -9%,#27204C 0%,transparent 34%),radial-gradient(circle at 0% 55%,#111F30 0%,transparent 45%),#090D19;color:var(--ink);}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {background:#101524 !important;border-right:1px solid #283047;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#B6BED5;}
[data-testid="stMainBlockContainer"] {padding-top:2rem;padding-bottom:5rem;max-width:1320px;}
@media(max-width:760px){
  [data-testid="stMainBlockContainer"] {padding:1.2rem .8rem 3rem;}
  .hero-title {font-size:2.55rem!important;}
  .main-word {font-size:3.6rem!important;letter-spacing:.02em!important;}
}
h1,h2,h3,h4 {font-family:'Space Grotesk',system-ui,sans-serif;letter-spacing:-.035em;}
h1 {color:#FFF!important;}
h2,h3 {color:#F0EEFF!important;}
a {color:#B6A0FF!important;}
.brand {font-family:'Space Grotesk',sans-serif;font-size:1.38rem;letter-spacing:-.055em;font-weight:700;line-height:1.05;color:#FBF9FF;}
.brand mark {background:none;color:#B89FFF;}
.sidebar-note {color:#9EABC8;font-size:.78rem;line-height:1.7;padding:.65rem 0;}
.eyebrow {font-weight:800;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:#91DACA;margin:0 0 .7rem;}
.hero {position:relative;overflow:hidden;border-radius:27px;padding:3rem 3.05rem 2.6rem;border:1px solid #3F4066;background:linear-gradient(125deg,rgba(32,27,57,.98),rgba(20,25,47,.93) 57%,rgba(19,47,54,.83));margin-bottom:1.4rem;}
.hero:after {content:"";position:absolute;width:330px;height:330px;right:-95px;top:-135px;border:42px solid rgba(176,156,255,.1);border-radius:50%;box-shadow:0 0 0 48px rgba(126,220,208,.035),0 0 0 95px rgba(175,150,255,.025);pointer-events:none;}
.hero-title {font-family:'Space Grotesk',sans-serif;font-size:clamp(2.7rem,5vw,5rem);font-weight:700;letter-spacing:-.067em;line-height:1.03;max-width:850px;position:relative;z-index:1;color:#FFF;}
.hero-title em {font-style:normal;color:#B79CFF;}
.hero-desc {font-size:1.04rem;line-height:1.7;color:#CED3EA;max-width:690px;margin:1.25rem 0 0;position:relative;z-index:1;}
.small-tag {display:inline-block;padding:.4rem .7rem;border:1px solid #4C5272;border-radius:100px;background:#252A46;color:#E7E6FD;font-weight:700;font-size:.73rem;margin-right:.36rem;margin-top:.7rem;}
.section-overline {font-size:.72rem;letter-spacing:.15em;color:#8EADC4;text-transform:uppercase;font-weight:800;margin:1.6rem 0 .5rem;}
.section-head {font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.9rem;letter-spacing:-.047em;margin:.1rem 0 .65rem;color:#F8F5FF;}
.section-sub {color:#A9B4CE;line-height:1.65;max-width:880px;font-size:.95rem;}
.stat-card {min-height:122px;border-radius:18px;border:1px solid #323A55;background:linear-gradient(140deg,#1C2338,#171D30);padding:1.35rem 1.3rem;margin-bottom:.45rem;}
.stat-number {font-family:'Space Grotesk',sans-serif;font-size:2.15rem;letter-spacing:-.06em;font-weight:700;color:#F7F3FF;line-height:1.15;}
.stat-label {color:#9CAAC9;font-size:.82rem;margin-top:.38rem;}
.stat-meta {color:#C7D3E8;font-size:.76rem;margin-top:.43rem;}
.insight-card {border:1px solid #313B56;border-radius:20px;padding:1.25rem 1.3rem;min-height:165px;background:#182033;margin-bottom:.8rem;}
.insight-num {font-family:'Space Grotesk',sans-serif;color:#C0ABFF;font-size:1.45rem;font-weight:700;letter-spacing:-.03em;margin-bottom:.45rem;}
.insight-title {color:#FAF8FF;font-weight:750;font-size:.96rem;margin-bottom:.45rem;}
.insight-copy {color:#ACBAD3;font-size:.87rem;line-height:1.62;}
.chapter {font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.4rem;letter-spacing:-.04em;color:#F9F5FF;margin:1.35rem 0 .38rem;}
.hint {border-left:3px solid #8F7ADC;border-radius:3px;background:#171C2D;padding:.7rem 1rem;color:#BFC8DF;font-size:.85rem;line-height:1.6;margin:.6rem 0 1.2rem;}
.game-stage {position:relative;text-align:center;padding:2rem 1.35rem 1.8rem;border:1px solid #46456C;border-radius:28px;background:radial-gradient(circle at 50% 5%,#322B58,transparent 72%),linear-gradient(155deg,#1E2339,#141B2C);margin:1rem auto .5rem;max-width:920px;min-height:290px;display:flex;align-items:center;justify-content:center;flex-direction:column;}
.game-stage .main-word {font-family:'Space Grotesk',sans-serif;font-size:clamp(3.6rem,8vw,6.7rem);letter-spacing:.065em;font-weight:700;color:white;text-shadow:0 8px 58px #7E5CBA55;line-height:1.2;max-width:100%;overflow-wrap:anywhere;}
.game-stage .micro {text-transform:uppercase;letter-spacing:.19em;font-weight:800;font-size:.67rem;color:#B0ACD4;margin-bottom:1.3rem;}
.game-gap {height:1.6rem;}
.mini-insight {border:1px solid #3F3C66;border-radius:14px;background:linear-gradient(120deg,#1E1B38,#17213A);padding:.85rem 1.15rem;color:#D6D9EE;font-size:.9rem;line-height:1.65;margin:.5rem 0 1.5rem;}
.mini-insight b {color:#C8B6FF;letter-spacing:.15em;font-size:.66rem;margin-right:.7rem;}
.flow-card {border:1px solid #34415B;border-radius:18px;background:#192035;padding:1.4rem;min-height:135px;}
.flow-num {font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;color:#B5A0FF;}
.flow-title {font-weight:750;color:#FFF;margin:.35rem 0;}
.flow-desc {color:#AEBAD5;font-size:.86rem;line-height:1.55;}
.feed-card {border-radius:24px;border:1px solid #4C4971;background:linear-gradient(135deg,#2A2650 0%,#292C4B 55%,#193F48 100%);min-height:280px;padding:3rem 2.3rem;display:flex;flex-direction:column;justify-content:space-between;margin:1.1rem 0;}
.feed-card .feed-icon {font-size:2.4rem;margin-bottom:1.3rem;}
.feed-card .feed-heading {font-family:'Space Grotesk',sans-serif;font-size:2rem;line-height:1.18;font-weight:700;color:#FCFAFF;}
.feed-card .feed-copy {font-size:1rem;line-height:1.6;color:#C7D6E6;max-width:650px;margin-top:1rem;}
.feed-card .feed-label {font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:#D0C2FF;font-weight:700;}
.fine-print {color:#98A6C4;font-size:.81rem;line-height:1.65;margin:.55rem 0;}
.accent {color:#C8B6FF;font-weight:700;}
.divider {height:1px;background:linear-gradient(90deg,#343951,transparent);margin:1.7rem 0;}
[data-testid="stMetric"] {background:#171E31;border:1px solid #303B55;border-radius:16px;padding:1rem 1.1rem;}
[data-testid="stMetricLabel"] {color:#C4CCE0;}
[data-testid="stMetricValue"] {color:#F6F3FF;}
div.stButton>button {border-radius:12px!important;min-height:50px;padding:.5rem 1.15rem!important;font-family:'DM Sans',sans-serif;font-weight:800!important;letter-spacing:.007em;border:1px solid #505879;transition:transform .16s ease,border-color .16s ease,background .16s ease;}
div.stButton>button[kind="primary"] {background:linear-gradient(105deg,#A68CF1,#9A79E8)!important;color:#121024!important;border:1px solid #C6B1FF!important;}
div.stButton>button[kind="secondary"] {background:#202743!important;color:#F4F1FF!important;}
div.stButton>button:hover {transform:translateY(-1px);border-color:#B79AFF!important;}
[data-testid="stSidebar"] div.stButton>button {justify-content:flex-start;text-align:left;min-height:52px;margin-bottom:-.35rem;}
[data-testid="stMultiSelect"] label,[data-testid="stSelectbox"] label,[data-testid="stSlider"] label {color:#D7DEF0!important;}
[data-baseweb="tab-list"] {gap:.45rem;flex-wrap:wrap;}
button[data-baseweb="tab"] {color:#B7C0DA;padding:.65rem .85rem;border-radius:9px;}
[aria-selected="true"][data-baseweb="tab"] {background:#262845;color:#E9DDFF;}
[data-testid="stDataFrame"] {border:1px solid #313D55;border-radius:14px;}
footer {visibility:hidden;}
</style>
"""


def apply_styles() -> None:
    st.markdown(STYLESHEET, unsafe_allow_html=True)


# Building blocks
def render_html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def section(title: str, subtitle: str = "", kicker: str = "THE RESEARCH") -> None:
    """Small label, big heading and an optional sentence under it."""
    sub = f'<div class="section-sub">{escape(subtitle)}</div>' if subtitle else ""
    render_html(
        f'<div class="section-overline">{escape(kicker)}</div>'
        f'<div class="section-head">{escape(title)}</div>{sub}'
    )


def chapter(title: str) -> None:
    render_html(f'<div class="chapter">{title}</div>')


def hint(text: str) -> None:
    render_html(f'<div class="hint">{text}</div>')


def mini_insight(text: str) -> None:
    """Short takeaway shown right under a chart."""
    render_html(f'<div class="mini-insight"><b>INSIGHT</b>{escape(text)}</div>')


def fine_print(text: str) -> None:
    render_html(f'<div class="fine-print">{text}</div>')


def spacer(css_class: str = "game-gap") -> None:
    render_html(f'<div class="{css_class}"></div>')


def hero(kicker: str, title: str, desc: str, tags: list[str] | None = None) -> None:
    """Large page header; tags are optional."""
    tag_markup = "".join(f'<span class="small-tag">{escape(tag)}</span>' for tag in (tags or []))
    tag_block = f"<div>{tag_markup}</div>" if tag_markup else ""
    render_html(
        f'<div class="hero"><div class="eyebrow">{escape(kicker)}</div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-desc">{escape(desc)}</div>{tag_block}</div>'
    )


def stat_card(number: str, label: str, meta: str = "") -> None:
    render_html(
        f'<div class="stat-card"><div class="stat-number">{escape(number)}</div>'
        f'<div class="stat-label">{escape(label)}</div>'
        f'<div class="stat-meta">{escape(meta)}</div></div>'
    )


def insight_card(number: str, title: str, body: str) -> None:
    render_html(
        f'<div class="insight-card"><div class="insight-num">{escape(number)}</div>'
        f'<div class="insight-title">{escape(title)}</div>'
        f'<div class="insight-copy">{escape(body)}</div></div>'
    )


def flow_card(number: str, title: str, description: str) -> None:
    render_html(
        f'<div class="flow-card"><div class="flow-num">{number}</div>'
        f'<div class="flow-title">{escape(title)}</div>'
        f'<div class="flow-desc">{escape(description)}</div></div>'
    )


def feed_card(label: str, icon: str, heading: str, copy: str) -> None:
    """Large gradient card, used for the Twitter and Rest interruptions."""
    render_html(
        f'<div class="feed-card"><div><div class="feed-label">{escape(label)}</div>'
        f'<div class="feed-icon">{icon}</div>'
        f'<div class="feed-heading">{escape(heading)}</div>'
        f'<div class="feed-copy">{escape(copy)}</div></div></div>'
    )


def render_chart(fig: go.Figure, height: int = 390) -> None:
    """Apply the shared dark chart theme and draw the figure."""
    fig.update_layout(
        height=height,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, Arial", color=INK, size=12),
        margin=dict(l=16, r=18, t=52, b=45),
        legend=dict(title_text="", orientation="h", x=0, y=1.16, bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        hoverlabel=dict(bgcolor="#242A42", font=dict(color="#FFFFFF")),
        bargap=0.24,
    )
    axis_style = dict(
        showline=False,
        zeroline=False,
        gridcolor="#283149",
        tickfont=dict(color="#B8C1D7"),
        title_font=dict(color="#CBD2E5"),
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    fig.for_each_annotation(lambda a: a.update(text=a.text.replace("task=", "")))
    st.plotly_chart(fig, config={"displayModeBar": False, "responsive": True}, **STRETCH)


def go_to_page(page: str) -> None:
    """Button callback: switch the visible page."""
    st.session_state.nav = page


# 3. DATA
@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    return load_data(DATA_PATH)


def load_data_or_stop() -> pd.DataFrame:
    """Return the dataset, or show a friendly error and stop the app."""
    if not DATA_PATH.exists():
        st.error("Missing clean_data.csv. Keep it in the same folder as app.py.")
        st.stop()
    try:
        return get_data()
    except Exception as exc:
        st.error(f"Unable to load the research data: {exc}")
        st.stop()


# Sidebar navigation: one full-width button per page
def render_sidebar_navigation() -> None:
    with st.sidebar:
        render_html(
            '<div style="padding:.35rem .25rem 1.35rem">'
            '<div class="eyebrow">A DIGITAL COGNITION EXPERIENCE</div>'
            '<div class="brand">BEYOND<br>THE <mark>SCROLL.</mark></div>'
            '<div class="sidebar-note">A memory lab you can experience, then investigate.</div>'
            "</div>"
        )
        for page in PAGES:
            st.button(
                page,
                key=f"nav_{page}",
                type="primary" if page == st.session_state.nav else "secondary",
                on_click=go_to_page,
                args=(page,),
                **STRETCH,
            )
        render_html(
            '<div class="divider"></div><div class="eyebrow">AT A GLANCE</div>'
            '<div class="sidebar-note"><strong style="color:#EEE7FF">60</strong> participants &nbsp; · &nbsp; '
            '<strong style="color:#EEE7FF">4</strong> groups<br>'
            '<strong style="color:#EEE7FF">2</strong> cognitive tasks &nbsp; · &nbsp; '
            '<strong style="color:#EEE7FF">2023</strong> research</div>'
            '<div class="divider"></div>'
            '<div class="sidebar-note">Designed for exploratory learning. '
            "The interactive mini-test is for fun and is separate from the actual research data.</div>"
        )


# Main: page setup, state, sidebar, then the selected page
def main() -> None:
    # Page setup must run before anything is drawn.
    st.set_page_config(
        page_title="Beyond the Scroll | The Memory Lab",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={"About": "A playful memory demo and an EDA dashboard using published research data."},
    )
    # The pages are imported here (not at the top) because they import helpers from this file.
    from views.about import about_page
    from views.experience import experience_page
    from views.explorer import data_page
    from views.research import research_page

    apply_styles()
    df = load_data_or_stop()
    st.session_state.setdefault("nav", PAGES[0])
    render_sidebar_navigation()

    route = st.session_state.nav
    if route == "The experience":
        experience_page()
    elif route == "Research dashboard":
        research_page(df)
    elif route == "Data explorer":
        data_page(df)
    else:
        about_page(df)

if __name__ == "__main__":
    main()