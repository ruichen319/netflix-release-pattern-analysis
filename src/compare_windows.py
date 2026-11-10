"""Descriptive candidate-window comparison using launch-event/week observations."""

import pandas as pd
from analysis_config import CANDIDATE_WINDOWS


def compare_candidate_windows(panels, windows=None):
    """Return format summaries, per-launch counts, and one row per event/week.

    A positive observation means at least one cataloged older season appears in
    the chart. Multiple older seasons in the same event/week count once. Repeated
    observations are not independent launches. Windows describe the same data
    used to select them; this function does not perform a significance test.
    """
    if windows is None:
        windows = CANDIDATE_WINDOWS
    event_keys = ["category", "show_title", "new_season_number", "launch_week"]
    needed = set(event_keys + ["old_season_number", "relative_week", "in_top10"])
    weekly_parts, launch_rows = [], []

    for mode, panel in panels.items():
        if mode not in windows:
            raise ValueError(f"No candidate window specified for {mode}")
        if not needed.issubset(panel.columns) or panel.empty:
            raise ValueError(f"{mode}: a nonempty complete panel is required")
        if panel[list(needed)].isna().any().any():
            raise ValueError(f"{mode}: missing identifiers or chart indicators")
        if not panel.in_top10.isin([0, 1]).all():
            raise ValueError(f"{mode}: chart indicators must be 0 or 1")
        if panel.duplicated(event_keys + ["old_season_number", "relative_week"]).any():
            raise ValueError(f"{mode}: duplicate event/older-season/week rows")
        # Missing observation weeks must not be silently treated as off-chart.
        for _, season in panel.groupby(event_keys + ["old_season_number"]):
            if set(season.relative_week) != set(range(-12, 12)) or len(season) != 24:
                raise ValueError(f"{mode}: every included older season needs all 24 weeks")

        start, end = windows[mode]
        if not (-12 <= start <= end <= 11) or end - start + 1 == 24:
            raise ValueError(f"{mode}: window must leave at least one non-window week")

        weekly = panel.groupby(event_keys + ["relative_week"], as_index=False).agg(
            any_older_season_in_top10=("in_top10", "max")
        )
        weekly.insert(0, "release_mode", mode)
        weekly["in_candidate_window"] = weekly.relative_week.between(start, end)
        weekly_parts.append(weekly)

        for event, weeks in weekly.groupby(event_keys):
            inside = weeks.loc[weeks.in_candidate_window, "any_older_season_in_top10"]
            outside = weeks.loc[~weeks.in_candidate_window, "any_older_season_in_top10"]
            row = dict(zip(event_keys, event))
            row.update(
                release_mode=mode,
                candidate_start_week=start,
                candidate_end_week=end,
                candidate_observed_weeks=len(inside),
                candidate_positive_weeks=int(inside.sum()),
                noncandidate_observed_weeks=len(outside),
                noncandidate_positive_weeks=int(outside.sum()),
                candidate_rate=float(inside.mean()),
                noncandidate_rate=float(outside.mean()),
                difference_percentage_points=100 * float(inside.mean() - outside.mean()),
            )
            launch_rows.append(row)

    by_launch = pd.DataFrame(launch_rows)
    summaries = []
    for mode, launches in by_launch.groupby("release_mode"):
        start, end = windows[mode]
        inside_n = int(launches.candidate_observed_weeks.sum())
        outside_n = int(launches.noncandidate_observed_weeks.sum())
        inside_positive = int(launches.candidate_positive_weeks.sum())
        outside_positive = int(launches.noncandidate_positive_weeks.sum())
        summaries.append({
            "release_mode": mode,
            "launches": len(launches),
            "candidate_start_week": start,
            "candidate_end_week": end,
            "candidate_weeks_per_launch": end - start + 1,
            "noncandidate_weeks_per_launch": 24 - (end - start + 1),
            "candidate_positive_event_weeks": inside_positive,
            "candidate_total_event_weeks": inside_n,
            "candidate_rate": inside_positive / inside_n,
            "noncandidate_positive_event_weeks": outside_positive,
            "noncandidate_total_event_weeks": outside_n,
            "noncandidate_rate": outside_positive / outside_n,
            "difference_percentage_points": 100 * (
                inside_positive / inside_n - outside_positive / outside_n
            ),
            "events_with_candidate_chart_activity": int(launches.candidate_positive_weeks.gt(0).sum()),
            "events_with_noncandidate_chart_activity": int(launches.noncandidate_positive_weeks.gt(0).sum()),
        })

    return pd.DataFrame(summaries), by_launch, pd.concat(weekly_parts, ignore_index=True)
