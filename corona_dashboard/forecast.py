import json
import warnings
import pickle
from typing import Sequence
from time import time
from pathlib import Path
from urllib.request import urlretrieve
from tqdm import tqdm
import numpy as np
import pandas as pd
from sktime.forecasting.arima import AutoARIMA


OUTBREAK_LABELS = {1: 'Low', 2: 'Medium-Low', 3: 'Medium',
                   4: 'Medium-High', 5: 'High', 6: 'Very High'}

FIPS_URL = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
COUNTRIES_URL = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
FIPS_PATH = Path('data', 'us-fips.json')
FORECAST_PATH = Path('data', 'forecast.pickle')

def get_fips_data() -> dict:
    if not FIPS_PATH.exists():
        print('FIPS data missing, downloading...')
        urlretrieve(FIPS_URL, FIPS_PATH)
    
    with open(FIPS_PATH) as fd:
        fips_metadata = json.load(fd)
    
    return fips_metadata

def get_counties_data() -> pd.DataFrame:
    us_counties = pd.read_csv(COUNTRIES_URL, dtype={"fips": str})
    us_counties = us_counties[us_counties.county != 'Unknown']
    us_counties['location'] = us_counties[[
        'county', 'state']].apply(', '.join, axis=1)
    
    return us_counties


def forecast(us_counties: pd.DataFrame):
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
            predictions = model.predict(fh).to_numpy()
            last_forecast = predictions[len(predictions) - 1]
            todays_cases = y[len(y) - 1]
            # Places with very small amount of cases are hard to predict
            case_handicap = min(1.0, 0.5 + (todays_cases / 120))
            growth = (last_forecast / todays_cases) * case_handicap
            growth_rates[location] = growth

    final_list = [
        i[0]
        for i in sorted(
            growth_rates.items(),
            key=lambda i: i[1],
            reverse=True)]

    def rank_by_buckets(row) -> int:
        case_growth = growth_rates.get(row.location)
        if not case_growth:
            return 1
        return max(1,
                   min(6, round((case_growth ** 2) + ((case_growth - 1) * 8))))

    us_counties['outbreak_risk'] = us_counties.apply(rank_by_buckets, axis=1)
    us_counties['outbreak_labels'] = us_counties.apply(
        lambda row: OUTBREAK_LABELS[row.outbreak_risk], axis=1)

    return us_counties, growth_rates, final_list


def process_data() -> (pd.DataFrame, dict, Sequence):
    Path('data').mkdir(exist_ok=True)

    fips_metadata = get_fips_data()

    # 86400 = how many seconds there are in a day
    counties_is_fresh = FORECAST_PATH.exists() and (
        time() - FORECAST_PATH.stat().st_ctime) < 86400

    if counties_is_fresh and FORECAST_PATH.exists():
        with open(FORECAST_PATH, 'rb') as fd:
            us_counties, growth_rates, final_list = pickle.load(fd)
    else:
        print('US Counties data missing or stale. Creating new forecasts...')
        us_counties = get_counties_data()
        us_counties, growth_rates, final_list = forecast(us_counties)
        with open(FORECAST_PATH, 'wb') as fd:
            pickle.dump((us_counties, growth_rates, final_list), fd)

    return us_counties, fips_metadata, final_list[:15]
