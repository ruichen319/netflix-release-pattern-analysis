"""Reconcile frozen-snapshot results to the final presentation."""

import math


def validate_results(panels, windows, audit, seasons, paired, timing, case):
    assert sum(len(x) for x in panels.values()) == 504
    assert len(audit) == 21 and audit.included_in_panel.all()
    assert len(audit[["show_title", "old_season_number"]].drop_duplicates()) == 14
    zero = audit[audit.retained_zero_window]
    assert len(zero) == 1
    assert (zero.iloc[0].show_title, zero.iloc[0].new_season_number, zero.iloc[0].old_season_number) == ('Bridgerton',4,2)
    expected = {'all_at_once': (4,19,28,9,68), 'split_batches': (6,47,72,8,72)}
    fields=['launches','candidate_positive_event_weeks','candidate_total_event_weeks',
            'noncandidate_positive_event_weeks','noncandidate_total_event_weeks']
    for mode, values in expected.items():
        row=windows.set_index('release_mode').loc[mode]
        assert tuple(int(row[f]) for f in fields) == values
    for mode, previous, earlier in [('all_at_once',4/7,3/7),('split_batches',.55,8/15)]:
        part=seasons[seasons.release_mode.eq(mode)].set_index('old_season_group')
        assert math.isclose(part.loc['previous_season','mean_top10_share'],previous,abs_tol=1e-12)
        assert math.isclose(part.loc['earlier_seasons','mean_top10_share'],earlier,abs_tol=1e-12)
    split=paired[paired.release_mode.eq('split_batches')]
    gaps=split.difference_percentage_points
    assert (gaps.gt(1e-9).sum(),gaps.abs().le(1e-9).sum(),gaps.lt(-1e-9).sum()) == (3,1,1)
    assert math.isclose(gaps.mean(),5/3,abs_tol=1e-9)
    assert len(paired)==6 and timing.candidate_presence_higher.sum()==8
    assert timing.difference_percentage_points.abs().le(1e-9).sum()==1
    assert (int(case.iloc[0].listed_weeks),int(case.iloc[0].first_to_last_calendar_weeks),
            int(case.iloc[0].longest_unlisted_gap_weeks)) == (26,75,38)
    return {'checks':'passed','launches':10,'series':6,'older_season_observations':21,
            'distinct_older_seasons':14,'season_week_rows':504,'launch_week_rows':240,
            'omitted_observations':0,'retained_all_zero_observations':1}
