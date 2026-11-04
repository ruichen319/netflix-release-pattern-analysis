"""Portable version of the supplied 24-week Netflix analysis."""

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

from viewing_hours import export_viewing_hours

# Compare all four chart categories before focusing on launch-aligned TV data.
monthly_hours, annual_hours = export_viewing_hours(df, OUT)
display(annual_hours.round(2))

dates_path = ROOT / "data/season_release_dates.json"

release_dates = pd.read_json(dates_path)
release_dates["release_date"] = pd.to_datetime(
    release_dates["release_date"]
)

# 第二季及以后，且有明确上线日期
events = release_dates.loc[
    release_dates["season_number"].gt(1)
    & release_dates["release_date"].notna()
].copy()

# 对齐到上线所在报告周的周日
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

# 检查每个类别、每周的榜单是否完整
coverage = tv.groupby(["category", "week"])["weekly_rank"].agg(
    rows="size",
    ranks_ok=lambda x: set(x) == set(range(1, 11))
)
complete_weeks = set(
    coverage.index[coverage["rows"].eq(10) & coverage["ranks_ok"]]
)

# 为上线事件匹配榜单类别
show_categories = tv[["show_title", "category"]].drop_duplicates()

all_at_once_events = (
    events.loc[events["release_mode"].eq("all_at_once")]
    .merge(show_categories, on="show_title", validate="many_to_one")
)

# 从第−12周到第+11周，共24周
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

# 提取榜单中的季数；无法识别的季名保留为空
tv["season_number"] = pd.to_numeric(
    tv["season_title"].str.extract(
        r"(?:Season|Part)\s+(\d+)", expand=False
    ),
    errors="coerce"
).astype("Int64")

season_catalog = tv[[
    "category", "show_title", "season_title", "season_number"
]].drop_duplicates()

# 将每个上线事件与同剧、同类别的季匹配
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

# 每个“上线事件—旧季”组合展开为24周
relative_weeks = pd.DataFrame({"relative_week": range(-12, 12)})

weekly_panel = event_old_seasons.merge(relative_weeks, how="cross")
weekly_panel["week"] = (
    weekly_panel["launch_week"]
    + pd.to_timedelta(weekly_panel["relative_week"] * 7, unit="D")
)

# 原始榜单中实际出现的剧季及周
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

# 查看每个旧季在−12to+11周的上榜情况
weekly_matrix = weekly_panel.pivot(
    index=["show_title", "new_season_number", "old_season_title"],
    columns="relative_week",
    values="in_top10"
)

display(weekly_matrix)
print("Weekly panel rows:", len(weekly_panel))

# 按事件统计每周上榜旧季数
chart_data = weekly_panel.groupby(
    ["relative_week", "show_title", "new_season_number"]
)["in_top10"].sum().unstack(["show_title", "new_season_number"])

# 简化列名
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

# 在副本中统一 Stranger Things 第一季的季名
split_tv = tv.copy()

mask = split_tv["show_title"].eq("Stranger Things") & (
    split_tv["season_title"].isna()
    | split_tv["season_title"].eq("Stranger Things 1")
)
split_tv.loc[mask, "season_title"] = "Stranger Things: Season 1"

# 识别标准季名及 Stranger Things 的特殊季名格式
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

def label_old_seasons(panel):
    result = panel.copy()
    result["old_season_group"] = "earlier_seasons"

    is_previous = (
        result["old_season_number"]
        == result["new_season_number"] - 1
    )
    result.loc[is_previous, "old_season_group"] = "previous_season"
    return result

comparison_all = label_old_seasons(weekly_panel)
comparison_split = label_old_seasons(split_weekly_panel)

# 检查每个事件中，两组各有多少个旧季
for name, panel in [
    ("all_at_once", comparison_all),
    ("split_batches", comparison_split)
]:
    print(name)
    display(
        panel.groupby([
            "show_title", "new_season_number", "old_season_group"
        ])["old_season_number"]
        .nunique()
        .unstack(fill_value=0)
    )

def keep_comparable_events(panel):
    event_keys = ["show_title", "new_season_number"]

    group_counts = (
        panel.groupby(event_keys)["old_season_group"]
        .nunique()
        .reset_index(name="group_count")
    )

    eligible = group_counts.loc[
        group_counts["group_count"].eq(2), event_keys
    ]

    return panel.merge(
        eligible, on=event_keys, how="inner", validate="many_to_one"
    )

paired_all = keep_comparable_events(comparison_all)
paired_split = keep_comparable_events(comparison_split)

for name, panel in [
    ("all_at_once", paired_all),
    ("split_batches", paired_split)
]:
    print(name)
    display(
        panel[["show_title", "new_season_number"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

def calculate_group_rates(panel):
    return (
        panel.groupby([
            "show_title", "new_season_number",
            "relative_week", "old_season_group"
        ], as_index=False)
        .agg(
            old_seasons=("old_season_number", "nunique"),
            seasons_in_top10=("in_top10", "sum"),
            top10_rate=("in_top10", "mean")
        )
    )

rates_all = calculate_group_rates(paired_all)
rates_split = calculate_group_rates(paired_split)

display(rates_all.head(8))
display(rates_split.head(8))

def count_top10_weeks(panel):
    return (
        panel.groupby([
            "show_title", "new_season_number",
            "old_season_group", "old_season_number"
        ], as_index=False)
        .agg(top10_weeks=("in_top10", "sum"))
    )

weeks_all = count_top10_weeks(paired_all)
weeks_split = count_top10_weeks(paired_split)

def summarize_weeks(season_weeks):
    # 先在每个事件内，计算两组平均每季上榜周数
    event_weeks = (
        season_weeks.groupby([
            "show_title", "new_season_number", "old_season_group"
        ])["top10_weeks"].mean()
    )

    # 再对事件等权平均
    return (
        event_weeks.groupby("old_season_group")
        .mean()
        .reindex(["previous_season", "earlier_seasons"])
        .rename("mean_top10_weeks")
        .reset_index()
    )

weeks_summary_all = summarize_weeks(weeks_all)
weeks_summary_split = summarize_weeks(weeks_split)

print("all_at_once")
display(weeks_summary_all)

print("split_batches")
display(weeks_summary_split)

# Export the selected sample, weekly panel, and normalized supplementary comparison.
import sys
sys.path.insert(0, str(ROOT / 'src'))
from plot_svg import line_panels, bars, COLORS

event_rows = []
for mode, panel in [('all_at_once',weekly_panel),('split_batches',split_weekly_panel)]:
    for (show,season), part in panel.groupby(['show_title','new_season_number']):
        event_rows.append({'release_mode':mode,'show_title':show,'new_season_number':int(season),'older_seasons':part.old_season_number.nunique()})
event_sample=pd.DataFrame(event_rows)
event_sample.to_csv(OUT/'event_sample.csv',index=False)
for name,table in [('all_at_once_panel',weekly_panel),('split_batches_panel',split_weekly_panel),
                   ('all_at_once_previous_vs_earlier',weeks_summary_all),('split_batches_previous_vs_earlier',weeks_summary_split)]:
    table.to_csv(OUT/f'{name}.csv',index=False)

for expected_name,table in [('all_at_once_24week_total',total_weekly),('split_batches_24week_total',split_total_weekly)]:
    assert table.relative_week.tolist()==list(range(-12,12))
    assert table.total_old_seasons_in_top10.ge(0).all()

line_panels(FIGURES/'weekly_chart_patterns.svg',{
    f'All at once: {len(selected_events)} launches, {len(event_old_seasons)} event-season pairs':list(total_weekly.itertuples(index=False,name=None)),
    f'Split batches: {len(selected_split_events)} launches, {len(split_old_seasons)} event-season pairs':list(split_total_weekly.itertuples(index=False,name=None)),
},'Older-season chart appearances around a new-season launch','24 report weeks; counts are descriptive and depend on the selected sample')

rows=[]
for i,(mode,table) in enumerate([('All at once',weeks_summary_all),('Split batches',weeks_summary_split)]):
    for r in table.itertuples(index=False):
        rows.append((f"{mode} | {r.old_season_group.replace('_',' ')}",r.mean_top10_weeks,COLORS[i]))
bars(FIGURES/'previous_vs_earlier.svg',rows,'Previous seasons do not consistently lead earlier seasons',
     'Equal event weighting; 1 eligible all-at-once event and 5 split-batch events','Mean chart weeks per season within a 24-week window')
print('Selected sample:',len(event_sample),'launches across',event_sample.show_title.nunique(),'series')
display(event_sample)

