"""Equal-launch-weighted, per-season chart shares within candidate windows."""

import pandas as pd
from analysis_config import CANDIDATE_WINDOWS
from compare_windows import compare_candidate_windows


def compare_season_groups(panels):
    # Reuse the complete-panel/duplicate/indicator checks before any aggregation.
    compare_candidate_windows(panels)
    season_parts, launch_parts, summaries, paired_parts = [], [], [], []
    keys = ["category", "show_title", "new_season_number", "launch_week"]
    for mode, panel in panels.items():
        start, end = CANDIDATE_WINDOWS[mode]
        data = panel.copy()
        data["old_season_group"] = "earlier_seasons"
        previous = data.old_season_number.eq(data.new_season_number - 1)
        data.loc[previous, "old_season_group"] = "previous_season"
        counts = data.groupby(keys).old_season_group.nunique()
        eligible = counts[counts.eq(2)].reset_index()[keys]
        data = data.merge(eligible, on=keys, validate="many_to_one")
        data = data[data.relative_week.between(start, end)]
        seasons = data.groupby(keys + ["old_season_group", "old_season_number"], as_index=False).agg(
            top10_weeks=("in_top10", "sum"), candidate_weeks=("relative_week", "size"))
        if seasons.empty:
            raise ValueError(f"{mode}: no launches contain both season groups")
        assert seasons.candidate_weeks.eq(end - start + 1).all()
        seasons["top10_share"] = seasons.top10_weeks / seasons.candidate_weeks
        launches = seasons.groupby(keys + ["old_season_group"], as_index=False).agg(
            mean_top10_weeks=("top10_weeks", "mean"),
            mean_top10_share=("top10_share", "mean"),
            season_count=("old_season_number", "nunique"))
        summary = launches.groupby("old_season_group", as_index=False).agg(
            mean_top10_weeks=("mean_top10_weeks", "mean"),
            mean_top10_share=("mean_top10_share", "mean"),
            launches=("show_title", "size"))
        summary["candidate_weeks"] = end - start + 1
        paired = launches.pivot(index=keys, columns="old_season_group", values="mean_top10_share").reset_index()
        paired.columns.name = None
        earlier_counts = launches[launches.old_season_group.eq("earlier_seasons")][keys + ["season_count"]]
        paired = paired.merge(earlier_counts, on=keys, validate="one_to_one").rename(
            columns={"season_count": "earlier_season_count"})
        paired["difference_percentage_points"] = 100 * (paired.previous_season - paired.earlier_seasons)
        for frame in [seasons, launches, summary, paired]:
            frame.insert(0, "release_mode", mode)
            frame["candidate_start_week"], frame["candidate_end_week"] = start, end
        season_parts.append(seasons); launch_parts.append(launches)
        summaries.append(summary); paired_parts.append(paired)
    return tuple(pd.concat(parts, ignore_index=True) for parts in
                 [summaries, launch_parts, season_parts, paired_parts])
