# Candidate promotion-window comparison

One observation is a new-season launch and a relative week. At least one older season in the Top 10 gives 1; none gives 0. Multiple listed older seasons count once. The denominator is launches × observed weeks, not the number of older seasons.

| Format | Candidate window | Positive launch/weeks inside | Positive launch/weeks outside | Difference |
|---|---|---:|---:|---:|
| All-at-once, n=4 | −1 to +5 | 19/28 = 67.9% | 9/68 = 13.2% | +54.6 pp |
| Split release, n=6 | −1 to +10 | 47/72 = 65.3% | 8/72 = 11.1% | +54.2 pp |

All-at-once outside weeks are −12 to −2 and +6 to +11 (17 per launch); split outside weeks are −12 to −2 and +11 (12 per launch). Window selection and this comparison use the same data. This describes concentration rather than independently validating the cutoffs.

Eight of ten launches have higher within-window presence, Manifest S4 is tied and Ms. Rachel S2 is lower. The small, selected sample and repeated observations cannot establish format effectiveness, optimal timing or incremental viewing.

Run `python src/analyze.py` to export `candidate_window_summary.csv`, `candidate_window_by_launch.csv` and `candidate_window_event_weeks.csv`. The latter has 240 rows, while the sample remains 10 launches across 6 series. The experiment proposal uses weekly TV viewing hours per randomized user as its primary metric.
