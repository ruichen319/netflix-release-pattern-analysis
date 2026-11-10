# Previous versus earlier seasons

Use the same candidate windows as the timing analysis: all-at-once −1 to +5; split release −1 to +10. Previous = immediately preceding season; earlier = seasons before it.

For each season calculate listed weeks / candidate weeks. Average earlier seasons within each launch, then give launches equal weight. Include only launches that have both groups. This metric differs from the any-older-season indicator used for promotion timing.

| Format | Previous-season share | Earlier-season mean share | Launches |
|---|---:|---:|---:|
| All-at-once | 57.1% | 42.9% | 1 |
| Split release | 55.0% | 53.3% | 5 |

| Format | Launch | Previous | Earlier mean | Earlier-season count | Gap (pp) |
|---|---|---:|---:|---:|---:|
| All-at-once | Squid Game S3 | 57.1% | 42.9% | 1 | +14.3 |
| Split | Bridgerton S3 | 66.7% | 66.7% | 1 | +0.0 |
| Split | Bridgerton S4 | 25.0% | 16.7% | 2 | +8.3 |
| Split | Manifest S4 | 8.3% | 25.0% | 2 | −16.7 |
| Split | Stranger Things S4 | 91.7% | 83.3% | 2 | +8.3 |
| Split | Stranger Things S5 | 83.3% | 75.0% | 3 | +8.3 |

The split-release average gap is +1.7 pp, with 3 positive gaps, 1 tie and 1 negative gap. That small mean does not show equivalence or no effect. The all-at-once result is only Squid Game S3. These samples cannot establish a universal season-group priority; keep the promotion experiment's season selection exploratory.

Exports: `season_candidate_summary.csv`, `season_candidate_by_launch.csv`, `season_candidate_by_season.csv`, `season_candidate_paired.csv`. The existing `*_previous_vs_earlier.csv` paths are updated to the candidate-window metric; they no longer describe full-24-week comparisons.
