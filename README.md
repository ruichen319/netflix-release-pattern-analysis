# Netflix Release Patterns and Older-Season Chart Presence

Analyzed Netflix's Global Weekly Top 10 data to compare viewing-hour opportunities across content groups and examine older-season chart patterns around new-season launches.

[Presentation PDF](presentation/netflix-promotion-analysis.pdf) · [Python analysis](src/analyze.py) · [Analysis notebook](notebooks/netflix_analysis.ipynb) · [Chart patterns](outputs/figures/weekly_chart_patterns.svg) · [Data and methodology](docs/data_and_methodology.md)

## Business question

**Which promotion opportunities should Netflix prioritize testing to increase total weekly viewing hours?**

Using Netflix's Global Weekly Top 10 data, this analysis compares viewing-hour patterns across content groups and examines older-season chart presence around new-season launches to identify promotion hypotheses. The dataset covers chart-listed titles rather than Netflix's full viewing activity.

## Analytical approach

Python and pandas combine weekly chart records with curated release metadata to construct launch-aligned panels.

1. Compare TV and film viewing hours, then English and non-English TV, within the Top 10 data to identify areas for further investigation.
2. Filter to TV, standardize season names, and match release dates.
3. Align each first-batch release to its Sunday-ending report week; define that week as Week 0.
4. Retain launches with complete category charts across Weeks −12 through +11, requiring ten entries and ranks 1–10.
5. Match each launch to lower-numbered seasons from the same series and construct weekly Top 10 indicators.
6. Separate release formats. For previous-versus-earlier comparisons, require both groups, average chart weeks within each event, then give events equal weight.

Techniques include validated joins, regular expressions, cross joins, datetime alignment, aggregation, reshaping, and event-weighted comparisons.

## Data and analytical unit

Netflix's **Global Weekly Top 10** file reports worldwide weekly rankings, rather than individual-country charts. This snapshot contains **10,960 records across 274 weeks**, from **4 July 2021 to 27 September 2026**.

Each week contains 40 entries: ten each for Films (English), Films (Non-English), TV (English), and TV (Non-English). Each source row represents a film or TV season in one category and report week; the same title can recur.

The nine fields record week, category, rank, show title, season title, weekly hours viewed, runtime, weekly views, and cumulative Top 10 weeks. **Views = hours viewed ÷ runtime**, not unique viewers. Views and runtime are populated from the week ending 18 June 2023; earlier records retain hours viewed. See [Netflix's ranking-methodology update](https://about.netflix.com/en/news/top-10-things-about-netflix-top-10).

This project uses **5,480 TV records** and follows **10 sampled launches across six series**: four all-at-once and six split-batch. An analysis row is a launch–older-season–report-week combination. Totals count listed event–season pairs, not viewers. Field definitions and coverage are in the [data guide](docs/data_and_methodology.md).

## Findings

TV contributes about 67–71% of listed viewing hours in 2022–2025. Within TV, non-English content's share rises from 33.04% to 43.20%, supporting further investigation of TV promotion opportunities.

In the all-at-once sample, aggregate older-season appearances peak in the launch week and the following two report weeks, then fall to zero from Week 6 onward. In the split-batch sample, appearances peak in Week 1 and continue through Week 10. The samples contain five and sixteen event–older-season pairs respectively, so raw count magnitudes do not establish a release-format advantage.

**Previous-season targeting remains inconclusive.** Only one all-at-once launch and five split-batch launches included both previous and earlier seasons. Mean chart weeks were 4.0 versus 3.0 for all-at-once releases and 7.0 versus 7.37 for split releases. This small exploratory sample is insufficient to justify consistently prioritizing the immediately previous season.

## Proposed next steps

- **Test timing by release format:** use the observed weekly patterns to develop separate promotion hypotheses and account for later batches in split releases.
- **Investigate launch concentration:** measure chart presence in Weeks −1 through +5 while retaining later split-release activity. This candidate interval is not an established optimal window.
- **Expand season comparisons:** add more series with Season 3 or later launches before choosing between previous- and earlier-season promotion.

These are proposed analyses and tests. No campaign experiment or incremental viewing effect has been established.

## Repository structure

```text
netflix-release-pattern-analysis/
├── README.md
├── presentation/         # Business presentation PDF
├── src/                  # Runnable analysis and SVG chart helper
├── notebooks/            # Executed analysis notebook
├── data/                 # Frozen chart snapshot and release references
├── outputs/
│   ├── tables/           # Weekly panels, selected events and comparisons
│   └── figures/          # Weekly patterns and season comparisons
├── docs/                 # Data definitions and methodology
├── requirements.txt
└── requirements-notebook.txt
```

## How to run

1. Download the repository and open its root directory. Python 3.10 or later is recommended.
2. Install the analysis dependency and run:

   ```bash
   python -m pip install -r requirements.txt
   python src/analyze.py
   ```

3. Review regenerated tables and figures under `outputs/`. For interactive use, install `requirements-notebook.txt` and open the notebook in Jupyter.

The snapshot supports offline reproduction. The analysis was executed end to end; its three launch-pattern CSV exports match the original results.

## Limitations

- The selected sample is small; repeated series contribute multiple launches.
- Later release batches and other contemporaneous events may influence chart activity.
- Top 10 absence means below the observed chart threshold, not zero viewing. The older-season catalog includes only seasons observed somewhere in the dataset.
- Netflix changed ranking from hours viewed to views in June 2023; historical chart thresholds therefore reflect different ranking metrics.
- Release references were retained from the project, not reverified during packaging. Global availability can vary by market.
- Findings are descriptive and do not establish causality, retention, campaign lift, or ROI.
