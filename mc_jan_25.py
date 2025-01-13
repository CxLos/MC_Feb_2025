# =================================== IMPORTS ================================= #
import csv, sqlite3
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.figure_factory as ff
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from folium.plugins import MousePosition
import plotly.express as px
import datetime
import folium
import os
import sys
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.development.base_component import Component
# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)
# -------------------------------------- DATA ------------------------------------------- #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = 'data/MarCom_Responses.xlsx'
file_path = os.path.join(script_dir, data_path)
data = pd.read_excel(file_path)
df = data.copy()

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Define a discrete color sequence
color_sequence = px.colors.qualitative.Plotly

# Filtered df where 'Date of Activity:' is in December
df = df[df['Date of Activity:'].dt.month == 1]

# print(df_m.head())
# print('Total Marketing Events: ', len(df))
# print('Column Names: \n', df.columns)
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())

# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns ================================= #

# Column Names: 
#  Index([
#        'Timestamp',
#        'Which MarCom activity category are you submitting an entry for?',
#        'Person completing this form:', 
#        'Activity duration:',
#        'Purpose of the activity (please only list one):',
#        'Please select the type of product(s):',
#        'Please provide public information:', 
#        'Please explain event-oriented:',
#        'Date of Activity:', 
#        'Brief activity description:', 
#        'Activity Status'],
#  dtype='object')

# =============================== Missing Values ============================ #

# missing = df.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 0])

#  Please provide public information:    137
# Please explain event-oriented:        13

# ============================== Data Preprocessing ========================== #

# Check for duplicate columns
# duplicate_columns = df.columns[df.columns.duplicated()].tolist()
# print(f"Duplicate columns found: {duplicate_columns}")
# if duplicate_columns:
#     print(f"Duplicate columns found: {duplicate_columns}")

# Rename columns
df.rename(columns={"Which MarCom activity category are you submitting an entry for?": "MarCom Activity"}, inplace=True)

# Rename Purpose of the activity (please only list one): to Purpose
df.rename(columns={"Purpose of the activity (please only list one):": "Purpose"}, inplace=True)

# Rename 'Please select the type of product(s):' to 'Product Type'
df.rename(columns={"Please select the type of product(s):": "Product Type"}, inplace=True)

# Rename 'Please select the type of product(s):' to 'Product Type'
df.rename(columns={"Activity duration (hours):": "Activity duration"}, inplace=True)

# Fill Missing Values
df['Please provide public information:'] = df['Please provide public information:'].fillna('N/A')
df['Please explain event-oriented:'] = df['Please explain event-oriented:'].fillna('N/A')

# print(df.dtypes)

# ========================= Filtered DataFrames ========================== #

marcom_events = len(df)

# Group by "Which MarCom activity category are you submitting an entry for?"
df_activities = df.groupby('MarCom Activity').size().reset_index(name='Count')
# print('Activities:\n', df_activities)

# Purpose dataframe:
df_purpose = df.groupby('Purpose').size().reset_index(name='Count')

# Product Type dataframe:
df_product_type = df.groupby('Product Type').size().reset_index(name='Count')

# "Activity Duration" dataframe:
# Remove the word 'hours' from the 'Activity duration:' column
df['Activity duration'] = df['Activity duration'].str.replace(' hours', '')
df['Activity duration'] = df['Activity duration'].str.replace(' hour', '')
df['Activity duration'] = pd.to_numeric(df['Activity duration'], errors='coerce')

marcom_hours = df.groupby('Activity duration').size().reset_index(name='Count')
marcom_hours = df['Activity duration'].sum()
# print('Total Activity Duration:', sum_activity_duration, 'hours')

# "Person completing this form:" dataframe:
df['Person completing this form:'] = df['Person completing this form:'].str.strip()
df['Person completing this form:'] = df['Person completing this form:'].replace('Felicia Chanlder', 'Felicia Chandler')
df_person = df.groupby('Person completing this form:').size().reset_index(name='Count')
# print(df_person.value_counts())

# "Activity Status" dataframe:
df_activity_status = df.groupby('Activity Status').size().reset_index(name='Count')

# # ========================== DataFrame Table ========================== #

# MarCom Table
marcom_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

marcom_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=400,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# Products Table
products_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_product_type.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df_product_type[col] for col in df_product_type.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

products_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=400,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# Purpose Table
purpose_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_purpose.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df_purpose[col] for col in df_purpose.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

purpose_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=400,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ============================== Dash Application ========================== #

app = dash.Dash(__name__)
server= app.server

app.layout = html.Div(
    children=[ 
    html.Div(
        className='divv', 
        children=[ 
        html.H1(
            'MarCom Report January 2025', 
            className='title'),

                    html.Div(
            className='btn-box', 
            children=[
                html.A(
                'Repo',
                href='https://github.com/CxLos/MC_Jan_2025',
                className='btn'),
            ]),
    ]),    

# Data Table
# html.Div(
#     className='row0',
#     children=[
#         html.Div(
#             className='table',
#             children=[
#                 html.H1(
#                     className='table-title',
#                     children='Data Table'
#                 )
#             ]
#         ),
#         html.Div(
#             className='table2', 
#             children=[
#                 dcc.Graph(
#                     className='data',
#                     figure=marcom_table
#                 )
#             ]
#         )
#     ]
# ),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph11',
            children=[
            html.Div(
                className='high1',
                children=['MarCom Events:']
            ),
            html.Div(
                className='circle',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high2',
                            children=[marcom_events]
                    ),
                        ]
                    )
 
                ],
            ),
            ]
        ),
        html.Div(
            className='graph22',
            children=[
            html.Div(
                className='high1',
                children=['MarCom Hours:']
            ),
            html.Div(
                className='circle',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high2',
                            children=[marcom_hours]
                    ),
                        ]
                    )
 
                ],
            ),
            ]
        ),
    ]
),

# ROW 3
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
            # 'Which MarCom activity category are you submitting an entry for?' bar chart
            dcc.Graph(
                figure=px.bar(
                    df_activities,
                    x='MarCom Activity',
                    y='Count',
                    color='MarCom Activity',
                    text='Count'
                ).update_layout(
                    title='MarCom Activity Categories',
                    xaxis_title='Activity',
                    yaxis_title='Count',
                    title_x=0.5,
                    font=dict(
                        family='Calibri',
                        size=17,
                        color='black'
                    )
                ).update_traces(
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br><b>Count</b>: %{y}<extra></extra>'
                )
            )
            ],
        ),
        html.Div(
            className='graph4',
            children=[                
                # Person completing this form: bar chart
                dcc.Graph(
                    figure=px.bar(
                        df_person,
                        x='Person completing this form:',
                        y='Count',
                        color='Person completing this form:',
                        text='Count'
                    ).update_layout(
                        title='Person Completing Form',
                        xaxis_title='Person',
                        yaxis_title='Count',
                        title_x=0.5,
                        font=dict(
                            family='Calibri',
                            size=17,
                            color='black'
                        )
                    ).update_traces(
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br><b>Count</b>: %{y}<extra></extra>'
                    )
                )
            ]
        )
    ]
),

# ROW 2
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                html.Div(
                    className='table',
                    children=[
                        html.H1(
                            className='table-title',
                            children='Products Table'
                        )
                    ]
                ),
                html.Div(
                    className='table2', 
                    children=[
                        dcc.Graph(
                            className='data',
                            figure=products_table
                        )
                    ]
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[                
              html.Div(
                    className='table',
                    children=[
                        html.H1(
                            className='table-title',
                            children='Purpose Table'
                        )
                    ]
                ),
                html.Div(
                    className='table2', 
                    children=[
                        dcc.Graph(
                            className='data',
                            figure=purpose_table
                        )
                    ]
                )
   
            ]
        )
    ]
),

# ROW 4
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph1',
            children=[
                # 'Activity Status' pie chart
                dcc.Graph(
                    figure=px.pie(
                        df_activity_status,
                        values='Count',
                        names='Activity Status',
                        color='Activity Status',
                    ).update_layout(
                        title='Activity Status',
                        title_x=0.5,
                        font=dict(
                            family='Calibri',
                            size=17,
                            color='black'
                        )
                    ).update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hoverinfo='label+percent',
                        hole=0.3
                    )
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[                
                # Person completing this form: bar chart
                dcc.Graph(

                )
            ]
        )
    ]
),
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=True)
                #    False)
# =================================== Updated Database ================================= #

# updated_path = 'data/bmhc_q4_2024_cleaned.xlsx'
# data_path = os.path.join(script_dir, updated_path)
# df.to_excel(data_path, index=False)
# print(f"DataFrame saved to {data_path}")

# updated_path1 = 'data/service_tracker_q4_2024_cleaned.csv'
# data_path1 = os.path.join(script_dir, updated_path1)
# df.to_csv(data_path1, index=False)
# print(f"DataFrame saved to {data_path1}")

# -------------------------------------------- KILL PORT ---------------------------------------------------

# netstat -ano | findstr :8050
# taskkill /PID 24772 /F
# npx kill-port 8050

# ---------------------------------------------- Host Application -------------------------------------------

# 1. pip freeze > requirements.txt
# 2. add this to procfile: 'web: gunicorn impact_11_2024:server'
# 3. heroku login
# 4. heroku create
# 5. git push heroku main

# Create venv 
# virtualenv venv 
# source venv/bin/activate # uses the virtualenv

# Update PIP Setup Tools:
# pip install --upgrade pip setuptools

# Install all dependencies in the requirements file:
# pip install -r requirements.txt

# Check dependency tree:
# pipdeptree
# pip show package-name

# Remove
# pypiwin32
# pywin32
# jupytercore

# ----------------------------------------------------

# Name must start with a letter, end with a letter or digit and can only contain lowercase letters, digits, and dashes.

# Heroku Setup:
# heroku login
# heroku create mc-impact-11-2024
# heroku git:remote -a mc-impact-11-2024
# git push heroku main

# Clear Heroku Cache:
# heroku plugins:install heroku-repo
# heroku repo:purge_cache -a mc-impact-11-2024

# Set buildpack for heroku
# heroku buildpacks:set heroku/python

# Heatmap Colorscale colors -----------------------------------------------------------------------------

#   ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            #  'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            #  'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            #  'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            #  'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            #  'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            #  'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            #  'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            #  'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            #  'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            #  'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            #  'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            #  'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            #  'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            #  'ylorrd'].

# rm -rf ~$bmhc_data_2024_cleaned.xlsx
# rm -rf ~$bmhc_data_2024.xlsx
# rm -rf ~$bmhc_q4_2024_cleaned2.xlsx