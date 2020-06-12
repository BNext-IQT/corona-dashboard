import json
from time import time
from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import pandas as pd

HOTSPOT_LABELS = {1: 'Low', 2: 'Medium',
                  3: 'Medium-High', 4: 'High', 5: 'Very High'}

def get_data() -> (Path, Path):
    print('Getting data...')
    Path('data').mkdir(exist_ok=True)

    fips_path = Path('data', 'us-fips.json')
    counties_path = Path('data', 'us-counties.csv')
    fips_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
    counties_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

    # 86400 = how many seconds there are in a day
    counties_is_fresh = counties_path.exists() and (time() - counties_path.stat().st_ctime) < 86400

    if not fips_path.exists():
        print('FIPS data missing, downloading...')
        urlretrieve(fips_url, fips_path)
    if not counties_is_fresh:
        print('US Counties data missing or stale, downloading...')
        urlretrieve(counties_url, counties_path)

    return fips_path, counties_path


def process_data() -> (pd.DataFrame, dict):
    fips_path, counties_path = get_data()
    with open(fips_path) as fd:
        fips_metadata = json.load(fd)
    print('Processing data...')

    us_counties = pd.read_csv(counties_path, dtype={"fips": str})

    us_counties['location'] = us_counties[['county', 'state']].apply(', '.join, axis=1)
    us_counties['pct_change'] = us_counties.groupby('location')['cases'].pct_change(
        periods=5).replace([np.inf, -np.inf], np.nan).dropna()
    final_list = us_counties.sort_values('pct_change', ascending=False)[
        'location'].unique()

    def rank_by_buckets(row) -> int:
        if row.location in final_list[:18]:
            return 5
        if row.location in final_list[18:72]:
            return 4
        if row.location in final_list[72:216]:
            return 3
        if row.location in final_list[216:720]:
            return 2
        return 1

    us_counties['hotspot_risk'] = us_counties.apply(rank_by_buckets, axis=1)
    us_counties['hotspot_labels'] = us_counties.apply(
        lambda row: HOTSPOT_LABELS[row.hotspot_risk], axis=1)

    return us_counties, fips_metadata