import json
import warnings
from time import time
from pathlib import Path
from urllib.request import urlretrieve
from tqdm import tqdm
import numpy as np
import pandas as pd
from sktime.forecasting.arima import AutoARIMA


OUTBREAK_LABELS = {1: 'Low', 2: 'Medium',
                  3: 'Medium-High', 4: 'High', 5: 'Very High'}

def get_data() -> (Path, Path):
    print('Getting data...')
    Path('data').mkdir(exist_ok=True)

    fips_path = Path('data', 'us-fips.json')
    counties_path = Path('data', 'us-counties.csv')
    fips_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
    counties_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

    # 86400 = how many seconds there are in a day
    counties_is_fresh = counties_path.exists() and (
        time() - counties_path.stat().st_ctime) < 86400

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
    us_counties = us_counties[us_counties.county != 'Unknown']
    us_counties['location'] = us_counties[[
        'county', 'state']].apply(', '.join, axis=1)

    growth_rates = {}
    horizon = 6

    for location in tqdm(
            us_counties['location'].unique(),
            unit=' counties'):
        y = us_counties[us_counties.location == location].reset_index()[
            'cases']
        if len(y) < horizon:
            continue
        model = AutoARIMA()
        fh = np.arange(1, horizon)
        with warnings.catch_warnings():
            # When there is no cases, it will throw a warning
            warnings.filterwarnings("ignore") 
            try: 
                model.fit(y) 
            # Value error very rarely with weird/broken time series data
            except ValueError: 
                continue
            forecast = model.predict(fh).to_numpy()
            last_forecast = forecast[len(forecast) - 1]
            todays_cases = y[len(y) - 1]
            # Places with very small amount of cases are hard to predict
            case_handicap = min(1.0, todays_cases / 60)
            growth = (last_forecast / todays_cases) * case_handicap
            growth_rates[location] = growth
            
    final_list = [i[0] for i in sorted(growth_rates.items(), key=lambda i: i[1], reverse=True)] 

    def rank_by_buckets(row) -> int:
        if row.location in final_list[:22]:
            return 5
        if row.location in final_list[22:72]:
            return 4
        if row.location in final_list[72:216]:
            return 3
        if row.location in final_list[216:720]:
            return 2
        return 1

    us_counties['outbreak_risk'] = us_counties.apply(rank_by_buckets, axis=1)
    us_counties['outbreak_labels'] = us_counties.apply(
        lambda row: OUTBREAK_LABELS[row.outbreak_risk], axis=1)

    return us_counties, fips_metadata