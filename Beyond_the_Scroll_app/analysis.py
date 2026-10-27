"""Data loading and summary helpers used by app.py.

Everything here is plain pandas, so it can be tested without Streamlit.
Accuracy is always computed per participant first, so every person counts
equally no matter how many trials they have.
"""

from pathlib import Path
import pandas as pd

GROUP_ORDER = ["rest", "tiktok", "youtube", "twitter"]
TASK_ORDER = ["LD", "PM"]
PHASE_ORDER = ["pre", "post"]

PARTICIPANT_KEYS = ["participant_id", "interruption_group", "task"]


def load_data(path: Path) :
    """Read the cleaned CSV and add the engineered stimulus length."""
    df = pd.read_csv(path)
    df["stimulus_length"] = df["stimulus"].astype(str).str.len()
    return df


def experimental_trials(df: pd.DataFrame) :
    """Keep only the pre and post trials (drops practice trials)."""
    return df.loc[df["phase"].isin(PHASE_ORDER)]


def coverage(df: pd.DataFrame) :
    """Number of recorded trials per group, task and phase."""
    return df.groupby(["interruption_group", "task", "phase"], as_index=False).size().rename(columns={"size": "trials"})


def participant_accuracy(df: pd.DataFrame) :
    """Share of correct trials for each participant, task and phase."""
    trials = experimental_trials(df).assign(correct=lambda x: x["correct"].astype(float))
    out = trials.groupby([*PARTICIPANT_KEYS, "phase"], as_index=False).agg(
        accuracy=("correct", "mean"), trials=("correct", "size")
    )
    out["accuracy_pct"] = out["accuracy"] * 100
    return out


def group_accuracy(df: pd.DataFrame) :
    """Average participant accuracy (%) per group, task and phase."""
    per_person = participant_accuracy(df)
    return per_person.groupby(["interruption_group", "task", "phase"], as_index=False).agg(
        accuracy_pct=("accuracy_pct", "mean"), participants=("participant_id", "nunique")
    )


def accuracy_changes(df: pd.DataFrame) :
    """Post minus pre accuracy, in percentage points, per participant and task."""
    per_person = participant_accuracy(df)
    wide = per_person.pivot_table(index=PARTICIPANT_KEYS, columns="phase", values="accuracy_pct").reset_index()
    if not set(PHASE_ORDER) <= set(wide.columns):
        return pd.DataFrame(columns=[*PARTICIPANT_KEYS, "pre", "post", "change_pp"])
    wide["change_pp"] = wide["post"] - wide["pre"]
    return wide.dropna(subset=["change_pp"])


def group_changes(df: pd.DataFrame) :
    """Mean accuracy change (percentage points) per group and task."""
    changes = accuracy_changes(df)
    if changes.empty:
        return changes
    return changes.groupby(["interruption_group", "task"], as_index=False).agg(
        change_pp=("change_pp", "mean"), participants=("participant_id", "nunique")
    )


def participant_response_times(df: pd.DataFrame) :
    """Mean response time for each participant, task and phase."""
    trials = experimental_trials(df)
    return trials.groupby([*PARTICIPANT_KEYS, "phase"], as_index=False)["response_time"].mean()


def speed_accuracy(df: pd.DataFrame) :
    """Mean response time and accuracy for each participant and task."""
    trials = experimental_trials(df).assign(correct=lambda x: x["correct"].astype(float))
    return trials.groupby(PARTICIPANT_KEYS, as_index=False).agg(
        avg_response_time=("response_time", "mean"), accuracy=("correct", "mean")
    )