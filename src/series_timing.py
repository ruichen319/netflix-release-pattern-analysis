"""Series-level descriptive timing checks; no claims about unobserved viewing."""

import pandas as pd
from compare_windows import compare_candidate_windows


def summarize_series_timing(panels, chart_tv):
    _, by_launch, event_weeks = compare_candidate_windows(panels)
    event_weeks["week"] = event_weeks.launch_week + pd.to_timedelta(event_weeks.relative_week * 7, unit="D")
    keys = ["release_mode", "category", "show_title", "new_season_number", "launch_week"]
    listed = event_weeks[event_weeks.any_older_season_in_top10.eq(1)]
    spans = listed.groupby(keys, as_index=False).agg(
        listed_weeks=("week", "nunique"), first_listed_week=("week", "min"),
        last_listed_week=("week", "max"), first_listed_relative_week=("relative_week", "min"),
        last_listed_relative_week=("relative_week", "max"))
    timing = by_launch.merge(spans, on=keys, how="left", validate="one_to_one")
    timing["candidate_presence_higher"] = timing.difference_percentage_points.gt(0)

    dates = chart_tv.loc[chart_tv.show_title.eq("Ms. Rachel") & chart_tv.season_number.eq(1), "week"].drop_duplicates().sort_values()
    if dates.empty:
        raise ValueError("Ms. Rachel S1 must be present for the documented case check")
    span = int((dates.iloc[-1] - dates.iloc[0]).days // 7 + 1)
    gaps = (dates.diff().dt.days.div(7).sub(1)).dropna()
    case = pd.DataFrame([{"show_title": "Ms. Rachel", "old_season_number": 1,
        "first_listed_week": dates.iloc[0], "last_listed_week": dates.iloc[-1],
        "listed_weeks": len(dates), "first_to_last_calendar_weeks": span,
        "longest_unlisted_gap_weeks": int(gaps.max()) if len(gaps) else 0}])
    return timing, event_weeks, case
