"""
The WSGI (web app) entry point.
"""
from typing import Sequence
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from corona_dashboard.forecast import process_data

APP = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
US_COUNTIES, FIPS_METADATA, WORST_COUNTIES = process_data()

_MAP = px.choropleth_mapbox(
        US_COUNTIES, geojson=FIPS_METADATA, locations='fips', color='outbreak_risk',
        color_continuous_scale='orrd', range_color=(0, 6),
        hover_name='location',
        hover_data=['outbreak_labels'],
        mapbox_style='carto-darkmatter', zoom=3.2, opacity=0.5,
        center={'lat': 39, 'lon': -96},
        labels={'outbreak_labels': 'risk level'}
)
_MAP.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                   font=dict(color="white"))

APP.layout = html.Div(
            children=[
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="three columns div-user-controls",
                            children=[
                                html.Img(
                                    className="logo", src=APP.get_asset_url("logo.png")
                                ),
                                html.P("Our artificial intelligence model learns from growth trends to predict next week's outbreak risk on a per-county basis. These results are experimental."),
                                html.Br(),
                                html.H3("FUTURE OUTBREAKS")
                            ] + [html.P(i) for i in WORST_COUNTIES],
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
    hotspot_labels = clicked_county['outbreak_labels'].iloc[-1]
    fig = px.line(clicked_county, x='date', y='cases',
                title=f"{county_name} (Outbreak Risk: {hotspot_labels})")
    fig.update_layout(margin=dict(l=0, r=0, t=32, b=0), plot_bgcolor='#323130',
                    paper_bgcolor='#323130', font=dict(color="white"))
    return fig


def main(debug=False):
    APP.title = 'Coronavirus Dashboard'
    print('Running the web server...')
    APP.run_server(debug=debug)