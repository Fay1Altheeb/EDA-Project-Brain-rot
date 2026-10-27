# Beyond the Scroll — EDA Insights Dashboard

This Streamlit app uses a research dataset from the 2023 study *Short-Form Videos Degrade Our Capacity to Retain Intentions*. The mini-game is a separate educational demonstration and does not contribute to the study results.

## Run locally

On Windows, double-click `run_app.bat` or run the following commands from the project folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Keep `app.py`, `analysis.py`, `clean_data.csv`, and the entire `views` folder together. Start Streamlit from the directory containing `app.py`.

## What's new

The **Research dashboard** contains only five central plots grouped into three tabs:

1. **Memory outcomes** — prospective-memory correctness before and after interruption, plus LD-versus-PM accuracy changes across conditions.
2. **Individual differences** — participant-level distribution of prospective-memory accuracy changes, including unusual observations.
3. **Response speed** — mean response time by task and phase, plus participant-level speed versus correctness.

A short **INSIGHT** appears immediately underneath every chart. The **About the study** page answers all four research questions and includes a patterns/relationships/outliers section, final conclusion, methods caveats, and references.

The Data Explorer is preserved. The **PRE → MIDDLE → POST → RESULTS** mini-game is preserved, and a prior `MODE_BLURBS` NameError and duplicate middle-screen definition have been fixed. Media links are illustrative; availability and embedding depend on each platform.

## Research interpretation

- The charts use the supplied cleaned trial data and its `correct` flag, not the separate `acc.csv` file from the publication.
- PRE/POST analyses exclude practice trials and average participant outcomes equally before comparing groups.
- Individual observations are repeated trials, not independent people.
- The EDA is descriptive and does not establish statistical significance, long-term effects, or a general causal claim about social media.

## Main files

- `app.py`: layout, CSS, page navigation, shared display helpers, and game constants.
- `analysis.py`: pandas calculations for the research plots.
- `views/research.py`: selected plots and mini-insights.
- `views/about.py`: study overview, conclusions, insights, and four research answers.
- `views/experience.py`: educational game with real-media options or Rest.
- `views/explorer.py`: browse and download selected dataset rows.
- `clean_data.csv`: supplied cleaned research dataset.
