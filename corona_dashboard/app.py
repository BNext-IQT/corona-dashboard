"""
The WSGI (web app) entry point.
"""
from datetime import datetime
from pathlib import Path
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from corona_dashboard.forecast import process_data, FORECAST_PATH

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
        color_continuous_scale='orrd', range_color=(0, 60),
        hover_name='location',
        hover_data=['outbreak_risk'],
        mapbox_style='carto-darkmatter', zoom=3.2, opacity=0.5,
        center={'lat': 39, 'lon': -96},
        labels={'outbreak_risk': 'growth percentage'}
)
_MAP.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                   font=dict(color="white"))

if (Path(APP.config.assets_folder) / "brand.png").exists():
    _LOGO = APP.get_asset_url("brand.png")
else:
    _LOGO = APP.get_asset_url("logo.png")

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
                                html.P("Our artificial intelligence model learns from growth trends to predict next week's outbreak risk on a per-county basis. These results are experimental."),
                                html.Br(),
                                html.B("Total Cases:"),
                                html.P(f"{US_CASES:,d}"),
                                html.B("Total Deaths:"),
                                html.P(f"{US_DEATHS:,d}"),
                                html.B("Forecast Generated:"),
                                html.P(FORECAST_TIMESTAMP),
                                html.B("Predictive Error (SMAPE):"),
                                html.P(METRICS),
                                html.Br(),
                                html.H3("TOP OUTBREAKS")
                            ] + [html.P(i) for i in WORST_COUNTIES]
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

@APP.callback(Output('line', 'figure'), [Input('map', 'clickData')])
def display_county_graph(clickData: dict) -> px.line:
    if not clickData:
        # Arlignton, Virigina has a FIPS code of 51013
        clicked_county = US_COUNTIES[US_COUNTIES.fips == '51013']
    else:
        clicked_county = US_COUNTIES[US_COUNTIES.fips ==
                                    clickData['points'][0]['location']]
    county_name = clicked_county['location'].iloc[-1]
    hotspot_risk = clicked_county['outbreak_risk'].iloc[-1]
    if hotspot_risk == 0:
        hotspot_risk = 'N/A [Not Enough Data]'
    fig = px.line(clicked_county, x='date', y='cases',
                title=f"{county_name} (Predicted Weekly Growth: {hotspot_risk}%)")
    fig.update_layout(margin=dict(l=0, r=0, t=32, b=0), plot_bgcolor='#323130',
                    paper_bgcolor='#323130', font=dict(color="white"))
    return fig


def main(debug=False):
    print('Running the web server...')
    APP.run_server(debug=debug)