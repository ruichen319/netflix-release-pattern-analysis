"""Behavior checks for chart absence, endpoints and aggregation weights."""

from pathlib import Path
import sys
import unittest
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from compare_windows import compare_candidate_windows
from season_comparison import compare_season_groups


def panel(show, new_season, seasons):
    rows=[]
    launch=pd.Timestamp('2025-01-05')
    for old, listed in seasons.items():
        for week in range(-12,12):
            rows.append({'category':'TV (English)','show_title':show,'new_season_number':new_season,
                'launch_week':launch,'old_season_number':old,'relative_week':week,
                'in_top10':int(week in listed)})
    return pd.DataFrame(rows)


class WindowTests(unittest.TestCase):
    def test_multiple_seasons_count_once_and_all_zero_launch_is_retained(self):
        both=panel('A',3,{1:{-1},2:{-1}})
        zero=panel('B',2,{1:set()})
        summary,by_launch,weeks=compare_candidate_windows({'all_at_once':pd.concat([both,zero])})
        self.assertEqual(len(weeks),48)
        self.assertEqual(int(summary.iloc[0].candidate_positive_event_weeks),1)
        self.assertEqual(int(summary.iloc[0].candidate_total_event_weeks),14)
        self.assertEqual(by_launch.set_index('show_title').loc['B','candidate_rate'],0)

    def test_split_window_includes_week_ten_but_not_week_eleven(self):
        data=panel('A',2,{1:{10,11}})
        summary,_,_=compare_candidate_windows({'split_batches':data})
        row=summary.iloc[0]
        self.assertEqual(int(row.candidate_total_event_weeks),12)
        self.assertEqual(int(row.candidate_positive_event_weeks),1)
        self.assertEqual(int(row.noncandidate_positive_event_weeks),1)

    def test_missing_and_duplicate_observations_are_rejected(self):
        data=panel('A',2,{1:set()})
        with self.assertRaisesRegex(ValueError,'all 24 weeks'):
            compare_candidate_windows({'all_at_once':data.iloc[1:]})
        with self.assertRaisesRegex(ValueError,'duplicate'):
            compare_candidate_windows({'all_at_once':pd.concat([data,data.iloc[:1]])})

    def test_season_groups_average_within_launch_then_weight_launches_equally(self):
        window=set(range(-1,6))
        # A has two earlier seasons (one listed, one unlisted); B has one earlier season.
        a=panel('A',4,{1:window,2:set(),3:window})
        b=panel('B',3,{1:window,2:set()})
        summary,_,_,paired=compare_season_groups({'all_at_once':pd.concat([a,b])})
        means=summary.set_index('old_season_group').mean_top10_share
        self.assertAlmostEqual(means['previous_season'],.5)
        self.assertAlmostEqual(means['earlier_seasons'],.75)
        self.assertEqual(len(paired),2)


if __name__=='__main__':
    unittest.main()
