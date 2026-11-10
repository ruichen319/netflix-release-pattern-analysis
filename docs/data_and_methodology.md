# Data and methodology

## Frozen inputs

- `data/all-weeks-global.tsv`: worldwide weekly Top 10 rankings, with 10,960 rows and 274 weeks (2021-07-04 to 2026-09-27). Each week contains ten rows for each of four film/TV and English/non-English categories. The launch analysis uses the 5,480 TV rows; the film rows remain in the original input for traceability.
- `data/season_release_dates.json`: 24 season-reference rows for 8 selected series, including first and later-batch dates and source URLs. References are retained from the original project and are not newly reverified. The list is not an independent complete Netflix catalog.
- Original source entry point: [Netflix Global Top 10](https://www.netflix.com/tudum/top10).

## Source fields

| Field | Meaning |
|---|---|
| `week` | Sunday ending a Monday–Sunday report week |
| `category` | Global format/language chart, not production country |
| `weekly_rank` | Position 1–10 in the category/week |
| `show_title` | Series or film name |
| `season_title` | Season/part label, sometimes missing |
| `weekly_hours_viewed` | Reported hours for a listed title/season |
| `runtime` | Runtime used to normalize hours |
| `weekly_views` | Hours divided by runtime, not distinct viewers |
| `cumulative_weeks_in_top_10` | Accumulated chart weeks, including returns |

The main outcome is published chart presence. The historical file spans Netflix's hours-to-views ranking change; views and runtime are not available throughout the full period. No user exposure, cost or individual viewing history is included.

## Cleaning and selection

1. Parse report and release dates; filter to the two TV categories.
2. Map first release/batch dates to Sunday-ending report weeks. That week is Week 0.
3. Keep launches with complete category charts in every week from −12 through +11: ten entries with ranks 1–10. Unknown-date and weekly-release cases are outside the comparison.
4. Parse season numbers and reuse the original specific Stranger Things label corrections. Other unrecognized labels are not assigned automatically to Season 1.
5. Match lower-numbered seasons in the chart-derived catalog, expand every launch/older-season combination to 24 weeks, and left-join chart membership with validated keys.
6. Fill absent listings with `in_top10 = 0` after verifying chart completeness. This means below the observed chart threshold, not no viewing.
7. Audit against the available lower-season reference. Report any exclusions separately from retained observations that never list in the 24-week window.

## Selected launches

All-at-once: Bridgerton S2, Ms. Rachel S2, Squid Game S2 and S3.

Split release: Bridgerton S3 and S4, Manifest S4, Stranger Things S4 and S5, Wednesday S2.

There are 10 launches across 6 distinct series. Bridgerton appears in both formats. Complete charts do not prove availability in every market; availability of some earlier seasons can differ by region.

## Three deliberately different units

| Analysis | Observation/aggregation | Meaning |
|---|---|---|
| Weekly activity | Sum listed older seasons across launches | A repeated old season is counted separately at each release; 5 vs. 16 eligible observations |
| Candidate timing | One launch × one week; maximum chart indicator across its older seasons | Any older-season listing counts once, even if several seasons list |
| Season targeting | Share of candidate weeks listed per season; average within group/launch, then across launches | Controls for different numbers of earlier seasons and gives each eligible launch equal weight |

The complete tracking dataset has 504 rows: 21 older-season observations × 24 weeks. These cover 14 distinct older seasons. Collapsing to any-season presence yields 240 launch/week rows. Neither is the number of independent launches; repeated series also create dependence.

## Candidate periods

The shared `src/analysis_config.py` defines all-at-once −1 to +5 (7 weeks) and split release −1 to +10 (12 weeks). Outside weeks are the other 17 and 12 weeks respectively within the same 24-week observation. These cutoffs follow observed chart activity; no optimization, significance test or independent validation is claimed.

## Previous versus earlier seasons

Previous = immediately preceding numbered season. Earlier = lower-numbered seasons excluding the previous season. Include only launches containing both groups: 1 all-at-once and 5 split releases. For each season divide listed weeks by candidate weeks; average earlier seasons within a launch, then average launches equally. The reported gap is previous minus earlier, in percentage points.

## Series timing

Use the same all-at-once 24-week timelines for the Ms. Rachel comparison. Dates are report-week ends; first-to-last spans can include unlisted gaps. The full-snapshot check separately reports listed weeks, elapsed weeks and the longest interior unlisted gap. It does not infer unseen viewing.

## Reproducibility

`python src/analyze.py` and the notebook regenerate the same tables and figures from unchanged frozen inputs. Missing observation rows and duplicate launch/season/week keys are rejected rather than silently counted as zero. Tests verify window boundaries, any-season aggregation, all-zero retention and equal-launch weighting. `src/validate_results.py` reconciles the final slide values.
