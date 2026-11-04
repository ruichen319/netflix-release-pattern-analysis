# Data and methodology

## Inputs

- `data/all-weeks-global.tsv`: Netflix Global Weekly Top 10 viewership data, a worldwide chart rather than a collection of country-level charts. The frozen snapshot contains 10,960 records across 274 reporting weeks, from 2021-07-04 to 2026-09-27. Each week has 40 rows: ten films or TV seasons in each of four categories.
- `data/season_release_dates.json`: 24 season-reference rows for 8 selected series. `source_url` stores the source used for each release. These references were retained from the original project and were not reverified during portfolio packaging.
- Source entry point: [Netflix Global Top 10](https://www.netflix.com/tudum/top10).

`release_date` is the first-batch date; `later_batch_dates` records additional batches of the same season. Releases with unknown dates and weekly release schedules are excluded from the main comparison. A release with no complete 24-week chart coverage is also excluded.

## Source dataset coverage

| Global chart category | Weekly entries | Snapshot records |
|---|---:|---:|
| Films (English) | 10 | 2,740 |
| Films (Non-English) | 10 | 2,740 |
| TV (English) | 10 | 2,740 |
| TV (Non-English) | 10 | 2,740 |
| Total | 40 | 10,960 |

A source row is one film or one TV season, in one chart category, during one reporting week. The same title or season can appear in multiple weeks. Different seasons of the same series are separate chart entries. Language categories are not production-country labels. The film rows remain in the input for traceability; the launch analysis filters to the 5,480 TV rows.

## Source field dictionary

| Field | Meaning and unit |
|---|---|
| `week` | Sunday ending the Monday–Sunday reporting week; a week label, not a release date |
| `category` | One of the four global format/language chart categories above |
| `weekly_rank` | Published position 1–10 within that category and reporting week |
| `show_title` | Film or series title |
| `season_title` | TV season or part label when supplied; missing values are not automatically Season 1 |
| `weekly_hours_viewed` | Total reported viewing hours for the listed film or season during that week |
| `runtime` | Reported film/season runtime in hours; used to normalize viewing hours |
| `weekly_views` | Reported views, defined as viewing hours divided by runtime; not unique people, accounts, or confirmed full completions |
| `cumulative_weeks_in_top_10` | Accumulated chart weeks, including returns to the chart; not necessarily a consecutive run |

### Metric availability and ranking change

`weekly_hours_viewed` is populated in all 10,960 records. `weekly_views` and `runtime` are populated in 6,880 records, beginning with the week ending 2023-06-18; both are missing in the preceding 4,080 records. These earlier missing values are retained, not interpreted as zero viewing.

Netflix's [20 June 2023 methodology update](https://about.netflix.com/en/news/top-10-things-about-netflix-top-10) announced a change from ranking by hours viewed to ranking by views. Its definition of views is total hours viewed divided by total runtime. Consequently, the full historical chart-presence series spans two ranking regimes. This project uses published chart membership and does not treat views as available throughout the entire period.

### Snapshot checks

- All 1,096 category–week groups contain exactly ten rows and ranks 1–10.
- There are no duplicate combinations of week, category, show title, and season title.
- TV rows include 175 missing season labels; only the specific Stranger Things name correction documented below is applied.
- The file contains 170 zero runtimes. Non-null runtime does not therefore guarantee a valid divisor. This project does not recompute views or use runtime as its main outcome.

## Derived observation and metric definitions

| Field | Definition |
|---|---|
| `category` | English or non-English TV chart; not production country |
| `launch_week` | Sunday ending the report week containing the first release batch |
| `relative_week` | Integer from −12 through +11; 0 contains the first release batch |
| `in_top10` | 1 if the older season is listed in that category and report week; 0 if absent from a complete chart |
| `total_old_seasons_in_top10` | Number of listed event–older-season pairs in a relative week, not unique viewers or titles |
| `previous_season` | Season numbered immediately before the new season |
| `earlier_seasons` | Lower-numbered seasons excluding the immediately previous season |
| `mean_top10_weeks` | Chart weeks averaged across seasons within an event, then averaged equally across eligible events |

The source notebook standardizes missing or nonstandard Stranger Things season names in the split-batch comparison. Other unrecognized season labels remain unmatched instead of being automatically assigned to Season 1. The older-season catalog is limited to seasons observed somewhere in the chart dataset, so it is not a complete catalog of all seasons available on the platform.

## Content-group comparisons

Before constructing launch panels, the analysis sums listed viewing hours across TV and film, then English and non-English TV. Monthly summaries retain the full observed period. Annual comparisons use only the complete years 2022–2025; partial 2021 and 2026 totals are not treated as comparable full years.

`outputs/tables/monthly_viewing_hours.csv` and `annual_viewing_hours.csv` report hours in millions. TV share divides the two TV categories by all four categories; non-English TV share divides non-English TV by the two TV categories. These are shares of chart-listed hours, not shares of all viewing on Netflix. Monthly assignment follows the Sunday reporting-week label.

These comparisons restore the earlier steps in the original project notebook. They provide context for further investigation, not evidence that promoting one content group will generate higher incremental viewing.

## Selected launch sample

All-at-once: Bridgerton S2, Ms. Rachel S2, Squid Game S2 and S3.

Split batches: Bridgerton S3 and S4, Manifest S4, Stranger Things S4 and S5, Wednesday S2.

Bridgerton appears in both groups. Ms. Rachel is an educational compilation rather than a conventional scripted series. Chart coverage confirms complete category lists, but it does not independently establish global availability in every market. Manifest earlier-season availability varies by region.

## Reading the results

Raw weekly counts describe each group's own selected sample. There are unequal numbers of events and eligible older seasons. They cannot establish that one release format creates more viewing. Similarly, later chart activity in the split-batch group may coincide with later batches and other events.

The previous-versus-earlier comparison uses only events containing both groups. It retains one all-at-once event and five split-batch events; its scope is narrower than the 10-launch weekly pattern analysis.

No user-level viewing, campaign exposure, cost, conversion, or experimental data are included. Recommendations are proposed tests. No experiment was run in this project.
