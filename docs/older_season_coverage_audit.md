# Older-season coverage check

Counts are calculated separately for each new-season launch. The same older season can contribute again at another launch: Squid Game S1 around S2 and around S3 is counted twice.

| Release format | Launches | Older seasons identified | Included in analysis | Excluded | No Top 10 listings in 24 weeks, still included |
|---|---:|---:|---:|---:|---:|
| All-at-once | 4 | 5 | 5 | 0 | 0 |
| Split release | 6 | 16 | 16 | 0 | 1 |
| Total | 10 | 21 | 21 | 0 | 1 |

The 21 launch-specific observations cover **14 distinct older seasons**. Bridgerton S2 around S4 has zero listings across all 24 weeks and remains in the analysis. Absence inside a window is not itself an exclusion rule.

## What the check establishes

For the same 10 selected launches, enumerate lower-numbered seasons from `data/season_release_dates.json`, then compare them with the weekly tracking panels. Distinguish absence from the full chart snapshot, a matching omission, and a retained season with no listings in the particular launch window. The code reuses the existing Stranger Things name harmonization.

No exclusions were found against the available reference. All 24 seasons in that selected eight-series reference appear somewhere in the snapshot, and it has no lower-numbered gaps for the selected launches.

## What remains unknown

The reference is selected and is not an independent complete Netflix catalog. This cannot count never-charted seasons outside the available list, prove worldwide availability during every week, or observe viewing below the Top 10 threshold. A zero chart indicator does not mean zero viewing.

Internal CSV fields retain `event_season_pairs` and `metadata` names for explicit keys/reference provenance. A pair means one older season at one new-season launch, not a distinct season, source chart row or viewer.
