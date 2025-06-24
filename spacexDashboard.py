import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os
csv_filename = "spacex_launch_dash.csv"
if not  os.path.exists(csv_filename):
    raise FileNotFoundError(f"The file '{csv_filename}' was not found. Please download it and place it in the same directory as this script.")

spacex_df = pd.read_csv(csv_filename)

app = dash.Dash(__name__)


launch_sites = spacex_df['Launch Site'].unique()

dropdown_options = [{'label': 'All Sites', 'value': 'All'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()


app.layout = html.Div(children=[html.H1("SpaceX Launch Records Dashboard", style= {'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
                                html.Div([html.Label("Selects Launch Site"),
                                         dcc.Dropdown( id= 'site-dropdown',
                                                       options= dropdown_options,
                                                       placeholder= "Launch Site",
                                                       value = 'All',
                                                       style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'},
                                                       searchable= True)], style={'textAlign': 'center'}),
                                                       html.Br(),
                                                       html.Div([
                                                           dcc.Graph(id = 'success-pie-chart')
                                                       ]),
                                                       html.Br(),


                                                       html.Div([
                                                           html.Label("Select Payload Mass Range (kg)"),
                                                           dcc.RangeSlider(
                                                               id= 'payload-slider',
                                                               min = 0,
                                                               max = 10000,
                                                               step = 1000,
                                                               value = [min_payload,max_payload]
                                                           )
                                                       ],style={'padding': '40px'}
                                                       ),
                                                       html.Br(),
                                                       dcc.Graph(id = 'success-payload-scatter-chart')])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property= 'value'))
def update_pie_chart(selected_site):
    if selected_site == 'All':
        fig = px.pie(spacex_df[spacex_df['class'] == 1],
                     names = 'Launch Site',
                     title = 'Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_count = filtered_df['class'].value_counts().reset_index()
        site_count.columns = ['class', 'count']
        fig = px.pie(
            site_count,
            names='class',
            values='count',
            title=f'Success vs. Failure for site {selected_site}',
            labels={0: 'Failure', 1: 'Success'}
        ) 
    return fig       

@app.callback(
    Output(component_id= 'success-payload-scatter-chart', component_property= 'figure'),
    [Input(component_id = 'site-dropdown',  component_property =  'value'),
     Input(component_id = 'payload-slider', component_property= 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range

    payload_filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'All':
        fig = px.scatter(
            payload_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Launch Outcome for All Sites'
        )
    else:
        filtered_df = payload_filtered_df[payload_filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Launch Outcome for site {selected_site}'
        )
    return fig    
if __name__ == '__main__':
    app.run(debug=True, port= 8060)
