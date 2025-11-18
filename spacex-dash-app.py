# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site}
            for site in spacex_df['Launch Site'].unique()
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'fontSize': 20,
               'textAlign': 'center', 'margin': 'auto'}
    ),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            int(min_payload): f'{int(min_payload)}',
            int(max_payload): f'{int(max_payload)}'
        }
    ),

    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Total successful launches by site
        df_all = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df_all,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs Failure for a specific site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        df_counts = df_site['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']
        fig = px.pie(
            df_counts,
            names='class',
            values='count',
            title=f'Success vs Failure for site {selected_site}',
            labels={'class': 'Launch Outcome'}
        )
        # Optional: make labels clearer (0/1 → Failure/Success)
        fig.update_traces(
            textinfo='percent+label',
            hovertemplate='Outcome=%{label}<br>Count=%{value}'
        )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Further filter by site if needed
    if selected_site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == selected_site]

    fig = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success'
              + ('' if selected_site == 'ALL' else f' for {selected_site}'),
        labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()