import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from corona_dashboard.forecast import process_data

APP = dash.Dash(__name__)

US_COUNTIES, FIPS_METADATA = process_data()

MAP = px.choropleth_mapbox(
    US_COUNTIES, geojson=FIPS_METADATA, locations='fips', color='hotspot_risk',
    color_continuous_scale='orrd', range_color=(0, 5),
    hover_name='location',
    hover_data=['hotspot_labels'],
    mapbox_style='carto-darkmatter', zoom=3.2, opacity=0.5,
    center={'lat': 39, 'lon': -96},
    labels={'hotspot_labels': 'risk level'}
)
MAP.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)

APP.layout = html.Div(
    [html.Div([
        dcc.Graph(
            id="map", figure=MAP,
            className="map"),
        dcc.Graph(id="line", className="cases")
    ])
])


@APP.callback(Output('line', 'figure'), [Input('map', 'clickData')])
def display_county_graph(clickData: dict) -> px.line:
    if not clickData:
        # Arlignton, Virigina has a FIPS code of 51013
        clicked_county = US_COUNTIES[US_COUNTIES.fips == '51013']
    else:
        clicked_county = US_COUNTIES[US_COUNTIES.fips ==
                                     clickData['points'][0]['location']]
    county_name = clicked_county['location'].iloc[-1]
    hotspot_labels = clicked_county['hotspot_labels'].iloc[-1]
    fig = px.line(clicked_county, x='date', y='cases',
                  title=f"{county_name} (Hotspot Risk: {hotspot_labels})")
    fig.update_layout(margin=dict(l=0, r=0, t=32, b=0))
    return fig


def main():
    print('Running the web server...')
    APP.title = 'Coronavirus Dashboard'
    APP.run_server(debug=True)
