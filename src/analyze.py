"""Reproduce the focused Netflix promotion analysis from the frozen inputs."""


def main():
    # load-data
    from pathlib import Path
    try:
        ROOT = Path(__file__).resolve().parents[1]
    except NameError:
        ROOT = Path.cwd().resolve()
        if not (ROOT / 'data').exists():
            ROOT = ROOT.parent
    if not (ROOT / 'data').exists():
        raise FileNotFoundError('Run from the repository root or notebooks directory.')
    OUT = ROOT / 'outputs' / 'tables'
    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES = ROOT / 'outputs' / 'figures'
    FIGURES.mkdir(parents=True, exist_ok=True)
    if 'display' not in globals():
        try:
            from IPython.display import display
        except ImportError:
            def display(value):
                if hasattr(value, 'data'):
                    value = value.data
                if hasattr(value, 'to_string'):
                    print(value.to_string(index=False))
                else:
                    print(value)

    import pandas as pd

    data_path = ROOT / "data/all-weeks-global.tsv"
    df = pd.read_csv(data_path, sep="\t")

    df["week"] = pd.to_datetime(df["week"])

    tv = df[
        df["category"].isin(["TV (English)", "TV (Non-English)"])
    ].copy()

    print("Chart coverage:", tv["week"].min(), "to", tv["week"].max())
    print("TV records:", len(tv))

    display(tv.head())
    display(tv.columns.to_list())

    import sys
    sys.path.insert(0, str(ROOT / "src"))

    # release-alignment
    dates_path = ROOT / "data/season_release_dates.json"

    release_dates = pd.read_json(dates_path)
    release_dates["release_date"] = pd.to_datetime(
        release_dates["release_date"]
    )

    events = release_dates.loc[
        release_dates["season_number"].gt(1)
        & release_dates["release_date"].notna()
    ].copy()

    events["launch_week"] = (
        events["release_date"]
        .dt.to_period("W-SUN")
        .dt.end_time
        .dt.normalize()
    )

    events = events.sort_values(["show_title", "season_number"])

    display(events[[
        "show_title", "season_number",
        "release_date", "launch_week", "release_mode"
    ]])

    # select-all-at-once
    coverage = tv.groupby(["category", "week"])["weekly_rank"].agg(
        rows="size",
        ranks_ok=lambda x: set(x) == set(range(1, 11))
    )
    complete_weeks = set(
        coverage.index[coverage["rows"].eq(10) & coverage["ranks_ok"]]
    )

    show_categories = tv[["show_title", "category"]].drop_duplicates()

    all_at_once_events = (
        events.loc[events["release_mode"].eq("all_at_once")]
        .merge(show_categories, on="show_title", validate="many_to_one")
    )

    all_at_once_events["full_24_weeks"] = all_at_once_events.apply(
        lambda e: all(
            (e["category"], e["launch_week"] + pd.Timedelta(weeks=r))
            in complete_weeks
            for r in range(-12, 12)
        ),
        axis=1
    )

    display(all_at_once_events[[
        "show_title", "season_number", "launch_week", "full_24_weeks"
    ]])

    selected_events = all_at_once_events.loc[
        all_at_once_events["full_24_weeks"]
    ].copy()

    print("Eligible events:", len(selected_events))

    # older-season-catalog
    tv["season_number"] = pd.to_numeric(
        tv["season_title"].str.extract(
            r"(?:Season|Part)\s+(\d+)", expand=False
        ),
        errors="coerce"
    ).astype("Int64")

    season_catalog = tv[[
        "category", "show_title", "season_title", "season_number"
    ]].drop_duplicates()

    event_old_seasons = selected_events[[
        "category", "show_title", "season_number", "launch_week"
    ]].rename(columns={"season_number": "new_season_number"}).merge(
        season_catalog.rename(columns={
            "season_title": "old_season_title",
            "season_number": "old_season_number"
        }),
        on=["category", "show_title"],
        how="inner"
    )

    event_old_seasons = event_old_seasons.loc[
        event_old_seasons["old_season_number"]
        < event_old_seasons["new_season_number"]
    ].sort_values(["show_title", "new_season_number", "old_season_number"])

    display(event_old_seasons[[
        "show_title", "new_season_number",
        "old_season_title", "old_season_number", "launch_week"
    ]])

    # all-at-once-panel
    relative_weeks = pd.DataFrame({"relative_week": range(-12, 12)})

    weekly_panel = event_old_seasons.merge(relative_weeks, how="cross")
    weekly_panel["week"] = (
        weekly_panel["launch_week"]
        + pd.to_timedelta(weekly_panel["relative_week"] * 7, unit="D")
    )

    chart_keys = ["category", "show_title", "old_season_title", "week"]

    observed = (
        tv[["category", "show_title", "season_title", "week"]]
        .rename(columns={"season_title": "old_season_title"})
        .drop_duplicates()
        .assign(in_top10=1)
    )

    weekly_panel = weekly_panel.merge(
        observed, on=chart_keys, how="left", validate="many_to_one"
    )
    weekly_panel["in_top10"] = (
        weekly_panel["in_top10"].fillna(0).astype(int)
    )

    weekly_matrix = weekly_panel.pivot(
        index=["show_title", "new_season_number", "old_season_title"],
        columns="relative_week",
        values="in_top10"
    )

    display(weekly_matrix)
    print("Weekly panel rows:", len(weekly_panel))

    # select-split
    split_events = (
        events.loc[events["release_mode"].eq("split_batches")]
        .merge(show_categories, on="show_title", validate="many_to_one")
    )

    split_events["full_24_weeks"] = split_events.apply(
        lambda e: all(
            (e["category"], e["launch_week"] + pd.Timedelta(weeks=r))
            in complete_weeks
            for r in range(-12, 12)
        ),
        axis=1
    )

    display(split_events[[
        "show_title", "season_number", "launch_week", "full_24_weeks"
    ]])

    selected_split_events = split_events.loc[
        split_events["full_24_weeks"]
    ].copy()

    print("Eligible events:", len(selected_split_events))

    # split-season-labels
    split_tv = tv.copy()

    mask = split_tv["show_title"].eq("Stranger Things") & (
        split_tv["season_title"].isna()
        | split_tv["season_title"].eq("Stranger Things 1")
    )
    split_tv.loc[mask, "season_title"] = "Stranger Things: Season 1"

    season_num = split_tv["season_title"].str.extract(
        r"(?:Season|Part)\s+(\d+)", expand=False
    )
    special_num = split_tv["season_title"].str.extract(
        r"^Stranger Things\s+(\d+)$", expand=False
    )
    split_tv["season_number"] = pd.to_numeric(
        season_num.fillna(special_num), errors="coerce"
    ).astype("Int64")

    split_catalog = split_tv[[
        "category", "show_title", "season_title", "season_number"
    ]].drop_duplicates()

    split_old_seasons = selected_split_events[[
        "category", "show_title", "season_number", "launch_week"
    ]].rename(columns={"season_number": "new_season_number"}).merge(
        split_catalog.rename(columns={
            "season_title": "old_season_title",
            "season_number": "old_season_number"
        }),
        on=["category", "show_title"],
        how="inner"
    )

    split_old_seasons = split_old_seasons.loc[
        split_old_seasons["old_season_number"]
        < split_old_seasons["new_season_number"]
    ].sort_values(["show_title", "new_season_number", "old_season_number"])

    display(split_old_seasons[[
        "show_title", "new_season_number",
        "old_season_title", "old_season_number"
    ]])

    # split-weekly-panel
    split_weekly_panel = split_old_seasons.merge(
        pd.DataFrame({"relative_week": range(-12, 12)}),
        how="cross"
    )

    split_weekly_panel["week"] = (
        split_weekly_panel["launch_week"]
        + pd.to_timedelta(split_weekly_panel["relative_week"] * 7, unit="D")
    )

    split_observed = (
        split_tv[["category", "show_title", "season_title", "week"]]
        .rename(columns={"season_title": "old_season_title"})
        .drop_duplicates()
        .assign(in_top10=1)
    )

    split_weekly_panel = split_weekly_panel.merge(
        split_observed,
        on=["category", "show_title", "old_season_title", "week"],
        how="left",
        validate="many_to_one"
    )

    split_weekly_panel["in_top10"] = (
        split_weekly_panel["in_top10"].fillna(0).astype(int)
    )

    split_weekly_matrix = split_weekly_panel.pivot(
        index=["show_title", "new_season_number", "old_season_title"],
        columns="relative_week",
        values="in_top10"
    )

    display(split_weekly_matrix)
    print("Weekly panel rows:", len(split_weekly_panel))

    # weekly-counts-exports
    chart_data = weekly_panel.groupby(
        ["relative_week", "show_title", "new_season_number"]
    )["in_top10"].sum().unstack(["show_title", "new_season_number"])

    chart_data.columns = [
        f"{title} S{season}" for title, season in chart_data.columns
    ]
    chart_data = chart_data.reindex(range(-12, 12))
    chart_data.index.name = "relative_week"
    chart_data = chart_data.reset_index()

    display(chart_data)

    chart_data.to_csv(
        OUT / "all_at_once_24week_chart_data.csv",
        index=False,
        encoding="utf-8-sig"
    )

    total_weekly = (
        weekly_panel.groupby("relative_week", as_index=False)
        .agg(total_old_seasons_in_top10=("in_top10", "sum"))
        .sort_values("relative_week")
    )

    display(total_weekly)

    total_weekly.to_csv(
        OUT / "all_at_once_24week_total.csv",
        index=False,
        encoding="utf-8-sig"
    )

    split_total_weekly = (
        split_weekly_panel.groupby("relative_week", as_index=False)
        .agg(total_old_seasons_in_top10=("in_top10", "sum"))
        .sort_values("relative_week")
    )

    display(split_total_weekly)

    split_total_weekly.to_csv(
        OUT / "split_batches_24week_total.csv",
        index=False,
        encoding="utf-8-sig"
    )


    panels = {"all_at_once": weekly_panel, "split_batches": split_weekly_panel}
    event_rows = []
    for mode, panel in panels.items():
        for (show, season), part in panel.groupby(["show_title", "new_season_number"]):
            event_rows.append({"release_mode": mode, "show_title": show,
                "new_season_number": int(season), "older_seasons": part.old_season_number.nunique()})
        panel.to_csv(OUT / f"{mode}_panel.csv", index=False)
    event_sample = pd.DataFrame(event_rows)
    event_sample.to_csv(OUT / "event_sample.csv", index=False)
    display(event_sample)

    # coverage-audit-code
    # Audit only: this section does not alter the original samples or chart indicators.
    audit_event_keys = [
        "release_mode", "category", "show_title", "new_season_number", "launch_week"
    ]
    audit_pair_keys = audit_event_keys + ["old_season_number"]

    audit_events = pd.concat([
        selected_events.assign(release_mode="all_at_once"),
        selected_split_events.assign(release_mode="split_batches"),
    ], ignore_index=True).rename(columns={"season_number": "new_season_number"})
    audit_events = audit_events[audit_event_keys].drop_duplicates()

    # Use the existing release metadata as the reference, not the chart-derived catalog.
    audit_known_seasons = release_dates[["show_title", "season_number"]].rename(
        columns={"season_number": "old_season_number"}
    ).drop_duplicates()
    assert not audit_known_seasons.duplicated(["show_title", "old_season_number"]).any()

    audit_expected = audit_events.merge(
        audit_known_seasons, on="show_title", how="left", validate="many_to_many"
    )
    audit_expected = audit_expected.loc[
        audit_expected.old_season_number.lt(audit_expected.new_season_number)
    ].copy()

    # Check that the reference itself contains every lower-numbered season.
    # Gaps are reported separately; they are not assumed to be real, available seasons.
    audit_metadata_gaps = []
    for event in audit_events.itertuples(index=False):
        known_numbers = set(audit_known_seasons.loc[
            audit_known_seasons.show_title.eq(event.show_title), "old_season_number"
        ].astype(int))
        for number in sorted(set(range(1, int(event.new_season_number))) - known_numbers):
            audit_metadata_gaps.append({
                "release_mode": event.release_mode,
                "show_title": event.show_title,
                "new_season_number": int(event.new_season_number),
                "missing_metadata_season_number": number,
            })
    audit_metadata_gaps = pd.DataFrame(audit_metadata_gaps, columns=[
        "release_mode", "show_title", "new_season_number", "missing_metadata_season_number"
    ])

    # split_tv already applies the Notebook's Stranger Things season-name harmonization.
    # A season's presence anywhere in the frozen snapshot is different from its
    # presence inside the 24-week launch window.
    audit_snapshot_counts = (
        split_tv.dropna(subset=["season_number"])
        .groupby(["category", "show_title", "season_number"], as_index=False)
        .agg(snapshot_chart_weeks=("week", "nunique"))
        .rename(columns={"season_number": "old_season_number"})
    )
    audit_expected = audit_expected.merge(
        audit_snapshot_counts,
        on=["category", "show_title", "old_season_number"],
        how="left", validate="many_to_one",
    )
    audit_expected["snapshot_chart_weeks"] = (
        audit_expected.snapshot_chart_weeks.fillna(0).astype(int)
    )

    audit_existing_panel = pd.concat([
        weekly_panel.assign(release_mode="all_at_once"),
        split_weekly_panel.assign(release_mode="split_batches"),
    ], ignore_index=True)
    assert not audit_existing_panel.duplicated(audit_pair_keys + ["relative_week"]).any()
    audit_actual = audit_existing_panel.groupby(audit_pair_keys, as_index=False).agg(
        panel_rows=("relative_week", "size"),
        observed_panel_weeks=("relative_week", "nunique"),
        window_top10_weeks=("in_top10", "sum"),
    )
    audit_pairs = audit_expected.merge(
        audit_actual, on=audit_pair_keys, how="outer", validate="one_to_one",
        indicator="reference_panel_match",
    )
    assert not audit_pairs.reference_panel_match.eq("right_only").any(), (
        "The panel contains seasons missing from the existing release metadata."
    )
    audit_pairs["included_in_panel"] = audit_pairs.reference_panel_match.eq("both")
    audit_pairs["not_observed_in_snapshot"] = audit_pairs.snapshot_chart_weeks.eq(0)
    audit_pairs["omitted_not_observed_in_snapshot"] = (
        ~audit_pairs.included_in_panel & audit_pairs.not_observed_in_snapshot
    )
    audit_pairs["omitted_despite_snapshot_presence"] = (
        ~audit_pairs.included_in_panel & ~audit_pairs.not_observed_in_snapshot
    )
    audit_pairs["retained_zero_window"] = (
        audit_pairs.included_in_panel & audit_pairs.window_top10_weeks.eq(0)
    )
    audit_pairs["status"] = "retained_with_window_chart_presence"
    audit_pairs.loc[audit_pairs.retained_zero_window, "status"] = "retained_zero_window"
    audit_pairs.loc[audit_pairs.omitted_not_observed_in_snapshot, "status"] = (
        "omitted_not_observed_in_snapshot"
    )
    audit_pairs.loc[audit_pairs.omitted_despite_snapshot_presence, "status"] = (
        "omitted_despite_snapshot_presence"
    )
    for name in ["panel_rows", "observed_panel_weeks", "window_top10_weeks"]:
        audit_pairs[name] = audit_pairs[name].astype("Int64")
    assert audit_pairs.loc[audit_pairs.included_in_panel, "panel_rows"].eq(24).all()
    assert audit_pairs.loc[audit_pairs.included_in_panel, "observed_panel_weeks"].eq(24).all()
    audit_pairs = audit_pairs.sort_values(audit_pair_keys).reset_index(drop=True)

    audit_summary = audit_pairs.groupby("release_mode", as_index=False).agg(
        expected_event_season_pairs=("old_season_number", "size"),
        included_event_season_pairs=("included_in_panel", "sum"),
        omitted_not_observed_in_snapshot=("omitted_not_observed_in_snapshot", "sum"),
        omitted_despite_snapshot_presence=("omitted_despite_snapshot_presence", "sum"),
        retained_zero_window_pairs=("retained_zero_window", "sum"),
    )
    audit_summary = audit_events.groupby("release_mode").size().rename("launches").reset_index().merge(
        audit_summary, on="release_mode", validate="one_to_one"
    )
    audit_unique_seasons = audit_pairs[[
        "show_title", "old_season_number", "snapshot_chart_weeks"
    ]].drop_duplicates()

    # Also show the limits of the reference: it is a selected list, not a complete
    # Netflix catalog. An observed list cannot enumerate other never-charted series.
    audit_metadata_coverage = audit_known_seasons.merge(
        audit_snapshot_counts.groupby(["show_title", "old_season_number"], as_index=False)
        .agg(snapshot_chart_weeks=("snapshot_chart_weeks", "sum")),
        on=["show_title", "old_season_number"], how="left", validate="one_to_one",
    )
    audit_metadata_coverage["snapshot_chart_weeks"] = (
        audit_metadata_coverage.snapshot_chart_weeks.fillna(0).astype(int)
    )
    audit_metadata_coverage["observed_in_snapshot"] = audit_metadata_coverage.snapshot_chart_weeks.gt(0)

    display(audit_summary)
    display(audit_pairs[[
        "release_mode", "show_title", "new_season_number", "old_season_number",
        "snapshot_chart_weeks", "window_top10_weeks", "included_in_panel", "status"
    ]])
    print("Distinct metadata-listed older seasons for selected launches:", len(audit_unique_seasons))
    print("Missing lower-season entries in the existing metadata:", len(audit_metadata_gaps))
    print("Metadata seasons absent from the entire frozen chart snapshot:",
          int((~audit_metadata_coverage.observed_in_snapshot).sum()),
          "of", len(audit_metadata_coverage))
    print("Reference scope: existing release metadata only; not a full Netflix catalog.")

    for name, table in [
        ("older_season_coverage_summary", audit_summary),
        ("older_season_coverage_pairs", audit_pairs),
        ("older_season_metadata_coverage", audit_metadata_coverage),
        ("older_season_metadata_gaps", audit_metadata_gaps),
    ]:
        table.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")

    # candidate-window-code
    from compare_windows import compare_candidate_windows

    window_summary, window_by_launch, window_event_weeks = compare_candidate_windows({
        "all_at_once": weekly_panel,
        "split_batches": split_weekly_panel,
    })

    # Keep exported values numeric; format only the displayed summary.
    window_display = window_summary[["release_mode", "launches"]].copy()
    window_display["candidate_window"] = window_summary.apply(
        lambda r: f"{int(r.candidate_start_week):+d} to {int(r.candidate_end_week):+d}", axis=1
    )
    window_display["inside_window"] = window_summary.apply(
        lambda r: f"{r.candidate_positive_event_weeks}/{r.candidate_total_event_weeks} = {r.candidate_rate:.1%}", axis=1
    )
    window_display["remaining_weeks"] = window_summary.apply(
        lambda r: f"{r.noncandidate_positive_event_weeks}/{r.noncandidate_total_event_weeks} = {r.noncandidate_rate:.1%}", axis=1
    )
    window_display["difference_pp"] = window_summary.difference_percentage_points.round(1)
    display(window_display)
    display(window_by_launch[[
        "release_mode", "show_title", "new_season_number",
        "candidate_positive_weeks", "candidate_observed_weeks",
        "noncandidate_positive_weeks", "noncandidate_observed_weeks",
        "candidate_rate", "noncandidate_rate",
    ]])

    for name, table in [
        ("candidate_window_summary", window_summary),
        ("candidate_window_by_launch", window_by_launch),
        ("candidate_window_event_weeks", window_event_weeks),
    ]:
        table.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")

    # series-timing-code
    from series_timing import summarize_series_timing

    series_timing, series_event_weeks, ms_rachel_snapshot = summarize_series_timing(panels, split_tv)
    display(series_timing[["release_mode", "show_title", "new_season_number", "listed_weeks",
        "first_listed_week", "last_listed_week", "difference_percentage_points"]])
    display(ms_rachel_snapshot)
    for name, table in [("series_timing_by_launch", series_timing),
        ("series_timing_event_weeks", series_event_weeks), ("ms_rachel_snapshot", ms_rachel_snapshot)]:
        table.to_csv(OUT / f"{name}.csv", index=False)

    # season-comparison-code
    from season_comparison import compare_season_groups

    season_summary, season_by_launch, season_by_season, paired_seasons = compare_season_groups(panels)
    display(season_summary)
    display(paired_seasons[["release_mode", "show_title", "new_season_number", "previous_season",
        "earlier_seasons", "earlier_season_count", "difference_percentage_points"]])
    for name, table in [("season_candidate_summary", season_summary),
        ("season_candidate_by_launch", season_by_launch), ("season_candidate_by_season", season_by_season),
        ("season_candidate_paired", paired_seasons)]:
        table.to_csv(OUT / f"{name}.csv", index=False)
    for mode in panels:
        season_summary[season_summary.release_mode.eq(mode)].drop(columns="release_mode").to_csv(
            OUT / f"{mode}_previous_vs_earlier.csv", index=False)

    # figures-code
    from plot_results import create_figures

    create_figures(FIGURES, panels, window_summary, season_summary, series_event_weeks, paired_seasons)
    try:
        from IPython.display import SVG
        for name in ["weekly_chart_patterns", "candidate_window_comparison", "series_timing_patterns",
                     "previous_vs_earlier", "paired_season_differences"]:
            display(SVG(filename=str(FIGURES / f"{name}.svg")))
    except ImportError:
        print("Charts saved under outputs/figures.")

    # validation-code
    from validate_results import validate_results

    validation = validate_results(panels, window_summary, audit_pairs, season_summary,
        paired_seasons, series_timing, ms_rachel_snapshot)
    display(validation)


if __name__ == "__main__":
    main()
