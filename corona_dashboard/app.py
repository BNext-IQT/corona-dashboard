"""
The WSGI (web app) entry point.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Sequence, Generator
import plotly.express as px
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from corona_dashboard.forecast import process_data, FORECAST_PATH, HYPERPARAMETERS

APP = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
APP.title = 'Coronavirus Dashboard'
SERVER = APP.server

US_COUNTIES, FIPS_METADATA, WORST_COUNTIES, METRICS, US_CASES, US_DEATHS = process_data()

if len(METRICS) == 0:
    METRICS = "Not Measured"
else:
    METRICS = str(round(sum(METRICS.values()) / len(METRICS), 4))
FORECAST_TIMESTAMP = datetime.fromtimestamp(FORECAST_PATH.stat().st_ctime).strftime("%A, %d %b %Y %H:%M:%S %p")

_MAP = px.choropleth_mapbox(
        US_COUNTIES, geojson=FIPS_METADATA, locations='fips', color='outbreak_risk',
        color_continuous_scale='orrd', range_color=(0, 40),
        hover_name='location',
        hover_data=['outbreak_risk'],
        mapbox_style='carto-darkmatter', zoom=3.2, opacity=0.5,
        center={'lat': 39, 'lon': -96},
        labels={'outbreak_risk': 'growth (%)'}
)
_MAP.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                   font=dict(color="white"))

if os.environ.get('DASHBOARD_BRAND'):
    _LOGO = os.environ['DASHBOARD_BRAND']
else:
    _LOGO = APP.get_asset_url("logo.png")

def _create_outbreak_links(worst_counties: Sequence[str]) -> (Sequence, Sequence):
    html_eles = []
    inputs = []
    for county in worst_counties:
        html_eles.append(html.A(county, id=county, href="#"))
        html_eles.append(html.Br())
        inputs.append(Input(county, 'n_clicks_timestamp'))
    return html_eles, inputs

OUTBREAK_LINKS, OUTBREAK_INPUTS = _create_outbreak_links(WORST_COUNTIES)

APP.layout = html.Div(
            children=[
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="three columns div-user-controls",
                            children=[
                                html.Img(
                                    className="logo", src=_LOGO
                                ),
                                html.P("Our artificial intelligence learns from growth trends to predict next week's outbreak risk on a per-county basis. These results are experimental."),
                                html.Br(),
                                html.B("Total Cases / Deaths:"),
                                html.P(f"{US_CASES:,d} / {US_DEATHS:,d}"),
                                html.B("Forecast Generated:"),
                                html.P(f"{FORECAST_TIMESTAMP}"),
                                html.B(f"Predictive Error (SMAPE):"), 
                                html.P(METRICS),
                                html.Br(),
                                html.H3("TOP OUTBREAKS")
                            ] + OUTBREAK_LINKS
                        ),
                        html.Div(
                            className="nine columns div-for-charts bg-grey",
                            children=[
                                dcc.Graph(id="map", figure=_MAP),
                                dcc.Graph(id="line")
                            ],
                        ),
                    ],
                )
            ]
        )

def _create_line_graph(clicked_county: pd.DataFrame) -> px.line:
    county_name = clicked_county['location'].iloc[-1]
    hotspot_risk = clicked_county['outbreak_risk'].iloc[-1]
    deaths = clicked_county['deaths'].iloc[-1]
    if hotspot_risk == 0:
        hotspot_risk = 'N/A [Not Enough Data]'
    fig = px.line(clicked_county, x='date', y='cases',
                title=f"{county_name} [Predicted Weekly Growth: {hotspot_risk}%] [Deaths: {deaths}]")
    fig.update_layout(margin=dict(l=0, r=0, t=32, b=0), plot_bgcolor='#323130',
                    paper_bgcolor='#323130', font=dict(color="white"))
    return fig

def display_county_graph_from_map(fips: str) -> px.line:
    clicked_county = US_COUNTIES[US_COUNTIES.fips == fips]
    return _create_line_graph(clicked_county)

def display_county_graph_from_outbreaks(clicked_now: str) -> px.line:
    clicked_county = US_COUNTIES[US_COUNTIES.location == clicked_now]
    return _create_line_graph(clicked_county)

@APP.callback(Output('line', 'figure'), [Input('map', 'clickData')] + OUTBREAK_INPUTS)
def display_county_graph(*args):
    ctx = dash.callback_context
    if ctx.triggered:
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger == 'map':
            return display_county_graph_from_map(args[0]['points'][0]['location'])
        else:
            return display_county_graph_from_outbreaks(trigger)
    else: 
        # Arlignton, Virigina has a FIPS code of 51013
        return display_county_graph_from_map('51013')

def main(debug=False):
    print('Running the web server...')
    APP.run_server(debug=debug)