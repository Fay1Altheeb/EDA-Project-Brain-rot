
# Beyond the Scroll: Short Videos and Memory

**An exploratory data analysis (EDA) project and interactive Streamlit app exploring memory performance before and after social-media interruptions.**

Can a short break change what we remember to do?

*Beyond the Scroll* investigates this question using experimental data from 60 participants assigned to one of four conditions: **TikTok, YouTube, Twitter/X, or Rest**.

The project combines a research dashboard, data visualizations, insights, and an interactive memory challenge to make the findings accessible.

## Research Questions

1. How does task performance change from before to after an interruption?
2. Do the changes differ between TikTok, Twitter, YouTube, and Rest?
3. Do Lexical Decision (LD) and Prospective Memory (PM) tasks show different patterns?
4. Are faster responses associated with lower accuracy?

## Key Findings

- **Prospective Memory changes more than Lexical Decision.** Accuracy on the ongoing word task remains relatively stable, while remembering an intended action shows greater variation.
- **TikTok shows the largest average decline in Prospective Memory accuracy.** The Rest and Twitter groups show improvements on average, while YouTube remains comparatively stable.
- **Individual performance varies.** Some participants experience large declines in their scores even when the group's average changes little.
- **Faster responses do not necessarily mean lower accuracy.** Prospective Memory responses generally take longer, but no consistent speed–accuracy trade-off is observed.

These findings describe patterns in the experiment and do not establish that TikTok causes lasting memory problems.

## Streamlit App Features

### 1. Interactive Memory Experience
Try a mini memory challenge inspired by the experiment:

- Complete a memory test before an interruption.
- Choose TikTok, YouTube, Twitter, or Rest.
- Complete a second memory test.
- Compare your accuracy before and after.

The mini-game is an educational illustration, not a recreation of the original experiment.

### 2. Research Dashboard
Explore interactive visualizations covering:

- Memory accuracy before and after interruptions.
- Differences between interruption groups and task types.
- Individual differences in accuracy changes.
- Response times before and after interruptions.
- The relationship between response speed and accuracy.

Each chart includes a short insight explaining its main finding.

### 3. Data Explorer
- Filter data by interruption group, task, and experimental phase.
- Preview experimental records.
- Examine missing values and summary statistics.
- Download filtered data as CSV.

### 4. About the Study
Learn about the original experiment and explore the project's research-question answers, key findings, outliers, limitations, and final conclusion.

## Dataset

The dataset comes from the research study *Short-Form Videos Degrade Our Capacity to Retain Intentions* by Chiossi et al. (2023).

The experiment involved **60 participants** divided into four interruption conditions.

Two task types were examined:

- **Lexical Decision (LD):** Identifying whether a sequence of letters represents a real word or a nonword.
- **Prospective Memory (PM):** Remembering to perform an intended action when a specific cue appears.

The dataset includes participant identifiers, interruption conditions, task types, experimental phases, correctness, response times, and presented stimuli.

## Data Analysis Process

1. **Data Understanding:** Examined dataset structure, data types, and descriptive statistics.
2. **Data Cleaning:** Investigated missing values and duplicates, improved column names, and corrected data types.
3. **Feature Engineering:** Created stimulus length and participant-level accuracy-change features.
4. **Univariate Analysis:** Explored distributions of response times, stimulus lengths, task types, and accuracy changes.
5. **Bivariate Analysis:** Compared memory performance, interruption groups, response times, and relationships between variables.
6. **Insights and Conclusion:** Answered the research questions and summarized the main findings and limitations.

## Technologies Used

- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Plotly
- Streamlit
- Google Colab / Jupyter Notebook

## How to Run the App

**Requirements:** Python 3.10 or later.

1. Clone or download the repository.
2. Open a terminal inside the project folder.
3. Install the required libraries:

```bash
python -m pip install -r requirements.txt
```

4. Run the Streamlit application:

```bash
python -m streamlit run app.py
```

5. Open the local URL displayed in your terminal.

On Windows, you can also run the included `run_app.bat` file.

## Project Structure

```text
beyond-the-scroll/
├── app.py
├── analysis.py
├── clean_data.csv
├── requirements.txt
├── run_app.bat
├── README.md
└── views/
    ├── __init__.py
    ├── experience.py
    ├── research.py
    ├── explorer.py
    └── about.py
```

## Conclusion

This project explores how different social-media interruptions relate to memory performance and response speed.

The findings suggest that **Prospective Memory shows greater changes after interruptions than Lexical Decision**, particularly in the TikTok group.

However, individual performance varies, and the results are limited to this experimental dataset. Exploratory analysis alone cannot establish long-term effects or prove that a particular platform causes memory loss.

## References

- **Research Paper:** [Short-Form Videos Degrade Our Capacity to Retain Intentions](https://doi.org/10.1145/3544548.3580778)
- **Original Dataset:** [DaRUS Research Repository](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-3327)
- **Original Research Code:** [GitHub Repository](https://github.com/mimuc/media-prospective-memory)

The original research and dataset belong to their respective authors. This project is an independent educational analysis.

---

**Developed by Fay Altheeb**

*Exploratory Data Analysis | Data Science | Interactive Visualization*
