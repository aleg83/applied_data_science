# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        placeholder = 'Select a launch site',
                                        searchable = True,
                                        options=[
                                            {'label': 'All Sites', 'value': 'All Sites'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                        ],
                                        value='All Sites'
                                    ),
                                html.Br(),
                                
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                
                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={
                                        0: '0 kg',
                                        2500: '2500 kg',
                                        5000: '5000 kg',
                                        7500: '7500 kg',
                                        10000: '10000 kg'
                                    },
                                    value=[min_payload,max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(input_site):
    if input_site=='All Sites':
        data = spacex_df[['Launch Site','class']].groupby(['Launch Site']).sum() # here we have the number of successful launches per orbit
        data['Success rate'] = 100*data['class']/spacex_df['Launch Site'].value_counts() # get the success rate per orbit
        data['Launch Site'] = data.index
        fig = px.pie(data, names='Launch Site', values ='class')
    else:
        data = spacex_df[spacex_df['Launch Site']==input_site]
        counts = data['class'].value_counts().to_frame('success')
        counts['Class'] = counts.index
        counts.success = 100 * counts.success / (sum(counts.success))
        fig = px.pie(counts, names='Class', values =100 * counts.success / (sum(counts.success)))

    return fig

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])

def get_scatter_plot(input_site, payload_slider):
    if input_site=='All Sites':
        mask = np.logical_and(payload_slider[0] <= spacex_df['Payload Mass (kg)'], spacex_df['Payload Mass (kg)'] <= payload_slider[1])
        data = spacex_df[mask]
        fig_scatter = px.scatter(data, x='Payload Mass (kg)', y = 'class', color = 'Booster Version Category',
                                title = 'Correlation between payload mass and success for '+input_site)
    else:
        data = spacex_df[spacex_df['Launch Site']==input_site]
        mask = np.logical_and(payload_slider[0] <= data['Payload Mass (kg)'], data['Payload Mass (kg)'] <= payload_slider[1])
        data = data[mask]
        fig_scatter = px.scatter(data, x='Payload Mass (kg)', y = 'class', color = 'Booster Version Category',
                                title = 'Correlation between payload mass and success for '+input_site)
    return fig_scatter

# Run the app
if __name__ == '__main__':
    app.run_server()