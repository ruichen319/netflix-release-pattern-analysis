"""Reproducible portfolio charts, styled to match the final presentation."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.ticker import PercentFormatter
import numpy as np
from analysis_config import CANDIDATE_WINDOWS, FORMAT_LABELS

RED, DARK, GRAY, LIGHT, RULE = "#C90000", "#171B22", "#9CA5B1", "#F3F4F6", "#E2E5E9"


def _style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 14, "axes.titleweight": "bold", "text.color": DARK,
        "axes.labelcolor": DARK, "xtick.color": "#626975", "ytick.color": "#626975",
        "axes.spines.top": False, "axes.spines.right": False,
        "svg.fonttype": "none", "figure.facecolor": "white", "axes.facecolor": "white"})


def _save(fig, directory, name):
    for suffix in ["svg", "png"]:
        fig.savefig(directory / f"{name}.{suffix}", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_figures(directory, panels, window_summary, season_summary, timing_weeks, paired):
    directory.mkdir(parents=True, exist_ok=True)
    _style()
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.4), sharex=True)
    for ax, (mode, panel) in zip(axes, panels.items()):
        counts = panel.groupby("relative_week").in_top10.sum().reindex(range(-12, 12))
        start, end = CANDIDATE_WINDOWS[mode]
        ax.axvspan(start-.5, end+.5, color="#FFF1F1", zorder=0)
        ax.bar(counts.index, counts, width=.64,
               color=[RED if start <= w <= end else GRAY for w in counts.index], zorder=3)
        ax.axvline(0, color="#697587", linewidth=.8)
        eligible = panel[["show_title", "new_season_number", "old_season_number"]].drop_duplicates()
        n = len(panel[["show_title", "new_season_number"]].drop_duplicates())
        ax.set_title(f"{FORMAT_LABELS[mode]}: {n} launches; candidate weeks {start} to +{end}", loc="left", pad=12)
        ax.set_ylabel("Listed older-season observations")
        ax.set_ylim(0, len(eligible)); ax.set_axisbelow(True)
        ax.set_yticks(range(0,6) if len(eligible)==5 else [0,4,8,12,16])
        ax.yaxis.grid(True, color=RULE, linewidth=.7)
        ax.spines["left"].set_visible(False); ax.spines["bottom"].set_color(RULE)
        ax.tick_params(axis="both", length=0)
    axes[-1].set_xticks(range(-12, 12))
    axes[-1].set_xlabel("Weeks relative to first release (Week 0)")
    fig.suptitle("Older-season chart activity around new-season launches", x=.08, ha="left", fontsize=17, fontweight="bold")
    fig.text(.08,.015,"Separate count scales: formats contain different numbers of older-season observations. Shading marks candidate windows.",fontsize=9,color="#626975")
    fig.tight_layout(rect=[0,.045,1,.95],h_pad=2.3)
    _save(fig,directory,"weekly_chart_patterns")

    fig, ax = plt.subplots(figsize=(10.5,4.7))
    rows = window_summary.set_index("release_mode").loc[list(panels)]
    for i, (mode, row) in enumerate(rows.iterrows()):
        y = 1-i
        for offset, field, color in [(.13,"candidate_rate",RED),(-.13,"noncandidate_rate",GRAY)]:
            value = row[field]
            ax.barh(y+offset,value,height=.20,color=color)
            ax.text(value+.014,y+offset,f"{value:.1%}",va="center",fontweight="bold",color=color)
        ax.text(.92,y,f"+{row.difference_percentage_points:.1f} pp",va="center",ha="center",color=RED,fontsize=17)
    ax.set_yticks([1,0],["All-at-once (4 launches)","Split release (6 launches)"])
    ax.set_xlim(0,1.05);ax.set_xticks([0,.5,1]);ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("Share of launch–weeks with any older season in the Top 10")
    ax.set_title("Candidate windows show >50 pp higher older-season chart presence",loc="left",pad=32)
    ax.plot([],[],color=RED,lw=7,label="Candidate window")
    ax.plot([],[],color=GRAY,lw=7,label="Other observation weeks")
    ax.legend(loc="lower left",bbox_to_anchor=(0,1.01),ncol=2,frameon=False)
    for side in ["left","bottom"]:ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    fig.text(.04,.015,"Windows selected from the same sample; descriptive concentration, not independent validation or promotion lift.",fontsize=9,color="#626975")
    fig.tight_layout(rect=[0,.055,1,1])
    _save(fig,directory,"candidate_window_comparison")

    fig, axes = plt.subplots(1,2,figsize=(10.5,4.7),sharex=True)
    for ax, mode in zip(axes, panels):
        part = season_summary[season_summary.release_mode.eq(mode)].set_index("old_season_group")
        vals=[part.loc[g,"mean_top10_share"] for g in ["previous_season","earlier_seasons"]]
        ax.barh([1,0],vals,height=.32,color=["#697587","#BCC4CE"])
        for y,value in zip([1,0],vals):ax.text(value+.02,y,f"{value:.1%}",va="center",fontweight="bold")
        ax.set_yticks([1,0],["Previous season","Earlier seasons"])
        ax.set_xlim(0,1);ax.set_xticks([0,.25,.5,.75,1]);ax.xaxis.set_major_formatter(PercentFormatter(1))
        n=int(part.launches.iloc[0]);start,end=CANDIDATE_WINDOWS[mode]
        ax.set_title(f"{FORMAT_LABELS[mode]}: n = {n}\nWeeks {start} to +{end}",loc="left")
        for side in ["left","bottom"]:ax.spines[side].set_visible(False)
        ax.tick_params(length=0)
    fig.suptitle("Current evidence cannot prioritize one season group",x=.04,ha="left",fontsize=17,fontweight="bold")
    fig.text(.04,.02,"Per-season chart shares; average earlier seasons within each launch, then weight launches equally. No equivalence or causal claim.",fontsize=9,color="#626975")
    fig.tight_layout(rect=[0,.06,1,.9],w_pad=2)
    _save(fig,directory,"previous_vs_earlier")

    cases=[("Ms. Rachel",2),("Bridgerton",2),("Squid Game",2),("Squid Game",3)]
    fig, ax = plt.subplots(figsize=(11,4.8))
    matrix=[];labels=[]
    for show,season in cases:
        event=timing_weeks[timing_weeks.release_mode.eq("all_at_once") & timing_weeks.show_title.eq(show) & timing_weeks.new_season_number.eq(season)]
        matrix.append(event.set_index("relative_week").any_older_season_in_top10.reindex(range(-12,12)).to_numpy())
        labels.append(f"{show} S{season}")
    ax.pcolormesh(np.arange(-12.5,12),np.arange(-.5,4),np.asarray(matrix),cmap=ListedColormap(["#EDF0F3",RED]),vmin=0,vmax=1,edgecolors="white",linewidth=1)
    ax.invert_yaxis();ax.set_yticks(range(4),labels)
    ax.set_xticks([-12,-8,-4,0,4,8,11]);ax.set_xlabel("Relative report week (0 contains release)")
    ax.axvline(0,color="#697587",lw=.8);ax.set_title("Ms. Rachel suggests a different promotion-timing hypothesis",loc="left",pad=22)
    for spine in ax.spines.values():spine.set_visible(False)
    ax.tick_params(length=0)
    fig.text(.04,.02,"Red = at least one older season listed. Within-window timelines do not establish stable year-round viewing.",fontsize=9,color="#626975")
    fig.tight_layout(rect=[0,.06,1,1])
    _save(fig,directory,"series_timing_patterns")

    part=paired[paired.release_mode.eq("split_batches")].copy()
    fig,ax=plt.subplots(figsize=(10.5,4.8))
    y=np.arange(len(part))
    ax.barh(y,part.difference_percentage_points,height=.5,color="#697587")
    for yy,value in zip(y,part.difference_percentage_points):
        ax.text(value+(1 if value>=0 else -1),yy,f"{value:+.1f} pp",ha="left" if value>=0 else "right",va="center")
    ax.set_yticks(y,[f"{r.show_title} S{r.new_season_number}" for r in part.itertuples()]);ax.invert_yaxis()
    ax.set_xlim(-23,16);ax.axvline(0,color=GRAY,lw=.8)
    ax.set_xlabel("Previous-season share − earlier-season mean share (percentage points)")
    ax.set_title("Split-release gaps vary by launch, averaging +1.7 pp",loc="left",pad=18)
    for side in ["left","bottom"]:ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    fig.text(.04,.02,"3 positive gaps, 1 tie and 1 negative; 5 launches across 3 series. The mean does not establish equivalence.",fontsize=9,color="#626975")
    fig.tight_layout(rect=[0,.06,1,1])
    _save(fig,directory,"paired_season_differences")
