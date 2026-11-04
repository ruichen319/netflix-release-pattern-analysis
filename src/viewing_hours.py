"""Content-group comparisons restored from the original project notebook."""

import pandas as pd

CATEGORIES = ['Films (English)', 'Films (Non-English)', 'TV (English)', 'TV (Non-English)']


def export_viewing_hours(data, output_directory):
    """Summarize listed hours, retaining full-year comparisons for 2022–2025."""
    source = data.copy()
    source['month'] = source['week'].dt.to_period('M')
    source['year'] = source['week'].dt.year
    results = {}
    for period in ['month', 'year']:
        selected = source if period == 'month' else source.loc[source['year'].between(2022, 2025)]
        hours = (selected.groupby([period, 'category'])['weekly_hours_viewed']
                 .sum(min_count=1).unstack('category').reindex(columns=CATEGORIES)
                 .div(1_000_000))
        hours['film_hours_millions'] = hours['Films (English)'] + hours['Films (Non-English)']
        hours['tv_hours_millions'] = hours['TV (English)'] + hours['TV (Non-English)']
        hours['total_hours_millions'] = hours[CATEGORIES].sum(axis=1)
        hours['tv_share_pct'] = 100 * hours['tv_hours_millions'] / hours['total_hours_millions']
        hours['non_english_share_of_tv_pct'] = 100 * hours['TV (Non-English)'] / hours['tv_hours_millions']
        filename = 'monthly_viewing_hours.csv' if period == 'month' else 'annual_viewing_hours.csv'
        hours.reset_index().to_csv(output_directory / filename, index=False)
        results[period] = hours
    return results['month'], results['year']
