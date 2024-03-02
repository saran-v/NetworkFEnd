import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table, ctx
import os
import flask
import csv
import plotly.express as px
from dash.exceptions import PreventUpdate
from datetime import datetime as date
import numpy as np
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache

from datetime import date, datetime
import dash_auth
from flask import request
import configparser
import subprocess
import time
import dash_table as dt

configDict = {}
parser = configparser.ConfigParser()
parser.read('config.ini')
for sect in parser.sections():
    print('Section:', sect)
    for k, v in parser.items(sect):
        print(' {} = {}'.format(k, v))
        configDict[k] = v
    print()

colors = {"graphBackground": "#F5F5F5", "background": "#ffffff", "text": "#000000"}
# wos_df = pd.DataFrame()
parameter_df = pd.read_csv('Parameters.csv')
df = pd.read_csv('Item_Master.csv')
summary_df = pd.DataFrame()
num_record = 0
# username = ''
NAVBAR_STYLE = {
    "height": "5rem",
    'background-color': '#6B9AC4',
    "display": "flex",
    "align-items": "center",
    "justify-content": "center",
    "textAlign": "center",
    "fontSize": 12,
    "font-family": "Helvetica",
    "color": "white",
    "fontWeight": "bold",
}
hover_style = {
    'selector': 'tr:hover td',
    'rule': '''
        background-color: #6B9AC4;
        color: white;
    '''
}
TAB_STYLE = {
    'backgroundColor': '#6B9AC4',
    'padding': '10px',
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'margin-bottom': '10px',
    'font-size': '16px',
    'color': 'white'
}
# Custom styles for the selected tab
SELECTED_TAB_STYLE = {
    'backgroundColor': '#e9e9e9',
    'padding': '10px',
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'margin-bottom': '10px',
    'font-size': '16px',
}

app = dash.Dash(__name__, suppress_callback_exceptions=True)
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) #ternal_stylesheets=external_stylesheets)
# Expose Flask instance
server = app.server

auth = dash_auth.BasicAuth(
    app,
    {'planner': 'planner',
     'ETHAN': 'bob2627',
     'unknown': 'unknown',
     'JENNIFER': 'bob2728',
     'STEPHANIE': 'bob2829',
     'VICKI': 'bob5633',
     'TANYAF': 'bob7427',
     'MICHELLE': 'bob9245',
     'TANYAK': 'bob6390',
     'TANYAC': 'bob7823',
     'KENDRA': 'bob9851',
     'TANAYF': 'bob3529',
     'admin': 'admin'}
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='dropdown-loaded', data=False, storage_type='session'),
    dcc.Store(id='username', storage_type='session'),
    html.Div(
        html.H1('NETWORK PLANNING SYSTEM (NPS)'),
        style=NAVBAR_STYLE,
    ),
    html.Div(
        style={'display': 'flex', 'height': '100%', 'font-family': 'Helvetica'},
        # Set the height of the container to 100% of the viewport height
        children=[
            html.Br(),
            html.Br(),
            html.Div(
                dcc.Tabs(
                    id='hor_tabs',
                    value="PO's Report",
                    children=[
                        dcc.Tab(label="Network Plan", value="PO's Report", style=TAB_STYLE,
                                selected_style=SELECTED_TAB_STYLE, ),
                        dcc.Tab(label='Demand Flow', value='View Demand', style=TAB_STYLE,
                                selected_style=SELECTED_TAB_STYLE, ),
                        dcc.Tab(label='Performance Report', value='View Exception', style=TAB_STYLE,
                                selected_style=SELECTED_TAB_STYLE, ),
                        # dcc.Tab(label='Create a PO', value='Create a PO', style=TAB_STYLE,
                        #         selected_style=SELECTED_TAB_STYLE, ),
                        # dcc.Tab(label='Performance Report', value='Performance Report', style=TAB_STYLE,
                        #         selected_style=SELECTED_TAB_STYLE, ),
                    ],
                    vertical=True,  # Set the Tabs component to vertical mode
                    style={'height': '100%'}
                ),
                style={'backgroundColor': '#f1f1f1', 'padding': '20px'},
            ),
            html.Div(
                children=[
                    html.Br(),
                    html.Div(
                        style={'display': 'grid', 'grid-template-columns': "40% 40% 20%", 'border': 'None',
                               'grid-gap': '10px', 'font-family': 'Helvetica', 'background': '#E8E8E8'},
                        children=[
                            html.Div([
                                dcc.Store(id='dropdown-clicked', data=0, storage_type='session'),
                                dcc.Dropdown(
                                    id='vendor-name-dropdown', className='dropdown-class',
                                    placeholder="Select a vendor", persistence=True, persistence_type='memory',
                                    style={'font-family': 'Helvetica', 'width': '90%', 'margin': '0 auto',
                                           'color': 'black', 'borderColor': '#6B9AC4'},
                                ),
                                # hidden_trigger_div
                            ]),

                            html.Div([
                                dcc.Dropdown(
                                    id='family-code-dropdown', className='dropdown-class', multi =True,
                                    placeholder="Select a family code", persistence=True, persistence_type='memory',
                                    style={'font-family': 'Helvetica', 'width': '90%', 'margin': '0 auto',
                                           'color': 'black', 'borderColor': '#6B9AC4'},
                                ),
                            ]),
                            html.Div([
                                dcc.Dropdown(
                                    id='site-fc-dropdown', className='dropdown-class',
                                    placeholder="Select a site", persistence=True, persistence_type='memory',
                                    style={'font-family': 'Helvetica', 'width': '90%', 'margin': '0 auto',
                                           'color': 'black', 'borderColor': '#6B9AC4'},
                                ),
                            ]),
                        ]),
                    html.Br(),
                    html.Div(id='tab-content'), ],
                style={'flex': '1', 'width': '100%', 'overflow': 'auto', 'background': '#E8E8E8'}
            )
        ]
    )
])


@app.callback(
    Output('dropdown-loaded', 'data'),
    Input('url', 'pathname')
)
def load_dropdown(pathname):
    return True


page_1_layout = html.Div([
    # html.Br(),
    dcc.Tabs(id='tabs', value='tab-1',
             style={
                 'font-family': 'Helvetica',
             },
             children=[
                 dcc.Tab(label='Summary', className='tab-style', selected_className='selected-tab-style', value='tab-1',
                         style={'font-family': 'Helvetica', 'border-style': "outset", 'border-color': 'white',
                                "margin": 'auto', 'color': 'white', 'background-color': '#6B9AC4'}, children=[
                         html.Br(),
                         html.Br(),
                         html.Div(
                             children=[
                                 html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                                     html.Br(),
                                     dash_table.DataTable(
                                         id='summary-table',
                                         columns=[
                                             {'name': 'Source', 'id': 'src'},
                                             {'name': 'Destination', 'id': 'dest'},
                                             {'name': 'Week Date', 'id': 'wdate'},
                                             {'name': 'Quantity', 'id': 'qty'},
                                             {'name': 'SKUs_Count', 'id': 'Sku_count'}
                                         ],
                                         filter_action='native',
                                         row_deletable=True,
                                         style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                                         style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold',
                                                       'color': 'white'},
                                         style_table={'overflowX': 'scroll'},
                                         sort_action='native',
                                         sort_mode='multi',
                                         # css=[hover_style],
                                         tooltip_header={
                                             'Source': 'Source DC Location',
                                             'Destination': 'Destination DC Location',
                                             'Quantity': 'Quantity Transferred',
                                             'SKUs_Count': 'Number of Items Transferred',
                                         },
                                         css=[hover_style, {
                                             'selector': '.dash-table-tooltip',
                                             'rule': 'background-color: grey; font-family: monospace; color: white',
                                         }],
                                         tooltip_delay=0,
                                         tooltip_duration=None
                                     ),
                                     html.Br(),
                                     dcc.Store(id='intermediate-value-sum', storage_type='session'),
                                     # html.Button('SAVE', id='save_changes1', n_clicks=0,
                                     #             style={'fontWeight': 'bold', 'display': 'inline-block',
                                     #                    'vertical-align': 'middle', "min-width": "150px",
                                     #                    'height': "25px", "margin-top": "0px",
                                     #                    "margin-left": "5px", 'backgroundColor': '#1f77b4',
                                     #                    'color': 'white', 'border': '0px', 'border-radius': '5px',
                                     #                    'cursor': 'pointer'}),
                                     html.Div(id='dateValue'),
                                     html.Br(),
                                     html.Button('Download', id='download-po-btn', n_clicks=0,
                                                 style={'fontWeight': 'bold', 'display': 'inline-block',
                                                        'vertical-align': 'middle', "min-width": "150px",
                                                        'height': "25px", "margin-top": "0px",
                                                        "margin-left": "5px", 'backgroundColor': '#1f77b4',
                                                        'color': 'white', 'border': '0px',
                                                        'border-radius': '5px', 'cursor': 'pointer'}),
                                     dcc.Download(id="download_po"),
                                     html.Br(),
                                     html.Br(),
                                     html.Br(),
                                     html.Br(),
                                     html.Div(style={'display': 'grid', 'grid-template-columns': "18% 10%", # "5% 13% 10%",
                                                     'border': 'None',
                                                     'grid-gap': '10px', 'font-family': 'Helvetica',
                                                     'background': '#E8E8E8'}, children=[
                                         # dcc.Input(id='numWeeks', type="number", placeholder="Number of weeks", min=0,
                                         #           # Set the minimum value to 0
                                         #           step=1, value=4, readOnly=False,
                                         #           style={'margin': '1 0 0 0px', 'width': '100px', 'height': "30px",
                                         #                  'border-radius': '5px', 'border': '#1f77b4',
                                         #                  'text-align': 'center', 'display': 'flex'}),
                                         dcc.Input(id="dload-date", type="text", placeholder="Date (MM/DD/YY)",
                                                   # Set the minimum value to 0
                                                   step=1, persistence=True, persistence_type='memory',
                                                   style={'margin': '0 auto', 'width': '180px', 'height': "30px",
                                                          'border-radius': '5px', 'border': '#1f77b4',
                                                          'text-align': 'center', 'display': 'flex',
                                                          'justifyContent': 'center',
                                                          'alignItems': 'center'}),
                                         # dcc.DatePickerSingle(
                                         #         id='date-picker-download',
                                         #         # min_date_allowed=date(2020, 8, 5),
                                         #         # max_date_allowed=date(2030, 9, 19),
                                         #         # initial_visible_month=date(2017, 8, 5),
                                         #         # date=date(2017, 8, 25)
                                         # ),
                                         html.Button('Generate SAP Files', id='sap-btn', n_clicks=0,
                                                     style={'fontWeight': 'bold', 'display': 'inline-block',
                                                            'margin': '3px 0 0 0',
                                                            'vertical-align': 'middle', "width": "200px",
                                                            'height': "25px",
                                                            'backgroundColor': '#1f77b4',
                                                            'color': 'white', 'border': '0px', 'border-radius': '5px',
                                                            'cursor': 'pointer'}), dcc.Download(id="download")]),
                                     html.Div(id='output1'),
                                     html.Br(),
                                     # html.Div(
                                     #     style={'border': 'none'},
                                     #     children=[
                                     #         html.Br(),
                                     #         html.Div(
                                     #             style={'display': 'grid', 'grid-template-columns': "25% 25% 25% 25%",
                                     #                    'border': 'None', 'grid-gap': '10px',
                                     #                    'font-family': 'Helvetica'},
                                     #             children=[
                                     #                 html.Div(style={'display': 'flex', 'flex-direction': 'column',
                                     #                                 'justify-content': 'center',
                                     #                                 'align-items': 'center'}, children=[
                                     #                     # html.H3('Choose Your Filter!'),
                                     #                     dcc.Dropdown(
                                     #                         placeholder="Select a Site", persistence=True,
                                     #                         persistence_type='memory',
                                     #                         id='site-dropdown', className='dropdown-class',
                                     #                         style={'width': '90%', 'font-family': 'Helvetica',
                                     #                                'borderColor': '#6B9AC4', 'margin': '0 auto'},
                                     #                         value='All'
                                     #                     )]),
                                     #                 html.Div(style={'display': 'flex', 'flex-direction': 'column',
                                     #                                 'justify-content': 'center',
                                     #                                 'align-items': 'center'}, children=[
                                     #                     dcc.Dropdown(
                                     #                         placeholder="Select a Family Code", persistence=True,
                                     #                         persistence_type='memory',
                                     #                         id='fc-dropdown', className='dropdown-class',
                                     #                         style={'width': '90%', 'font-family': 'Helvetica',
                                     #                                'borderColor': '#6B9AC4', 'margin': '0 auto'},
                                     #                         value='All'
                                     #                     )]),
                                     #                 html.Div(style={'display': 'flex', 'flex-direction': 'column',
                                     #                                 'justify-content': 'center',
                                     #                                 'align-items': 'center'}, children=[
                                     #                     dcc.Dropdown(
                                     #                         id='graph-type',
                                     #                         options=[
                                     #                             # {'label': 'Scatter Plot', 'value': 'Scatter Plot'},
                                     #                             {'label': 'Histogram', 'value': 'Histogram'},
                                     #                             {'label': 'Scatter', 'value': 'Scatter'},
                                     #                         ],
                                     #                         placeholder="Select the trace type",
                                     #                         style={'width': '90%', 'font-family': 'Helvetica',
                                     #                                'borderColor': '#6B9AC4', 'margin': '0 auto'},
                                     #                         value='Scatter',
                                     #                     )]),
                                     #             ]),
                                     #     ]),
                                     html.Br(),
                                     # html.Div([
                                     #     dcc.Graph(id='wos-graph'),
                                     # ]),
                                     html.Br(),
                                 ]),
                             ]),
                     ]),
                 dcc.Tab(label="Transfers", value='tab-2', className='tab-style',
                         selected_className='selected-tab-style',
                         style={'font-family': 'Helvetica', 'background-color': '#6B9AC4', 'border-style': "outset",
                                'border-color': 'white', "margin": 'auto', 'color': 'white'}, children=[
                         html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                             html.Br(),
                             html.Br(),
                             html.Br(),
                             html.Br(),
                             dash_table.DataTable(
                                 id='summary2-table',
                                 columns=[
                                     {'name': 'Item', 'id': 'item'},
                                     {'name': 'Source', 'id': 'src'},
                                     {'name': 'Destination', 'id': 'dest'},
                                     {'name': 'Quantity', 'id': 'qty'},
                                     {'name': 'Source-Before-WOS', 'id': 'src-b-wos'},
                                     {'name': 'Source-After-WOS', 'id': 'src-a-wos'},
                                     {'name': 'Dest-Before-WOS', 'id': 'dest-b-wos'},
                                     {'name': 'Dest-After-WOS', 'id': 'dest-a-wos'},
                                     {'name': 'Source-Target-WOS', 'id': 'src-wos'},
                                     {'name': 'Dest-Target-WOS', 'id': 'dest-wos'},
                                 ],
                                 filter_action='native',
                                 row_deletable=True,
                                 style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                                 style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                                 style_data_conditional=[
                                     {
                                         'if': {'column_id': 'PO_Week_Date'},
                                         # 'backgroundColor': 'red',
                                         'color': 'blue',
                                     }],
                                 style_table={'overflowX': 'scroll'},
                                 sort_action='native',
                                 sort_mode='multi',
                                 css=[hover_style],
                                 page_size=20
                             ),
                             html.Br(),
                             dcc.Store(id='intermediate-valueM', storage_type='session'),
                             dcc.Store(id='intermediate-value', storage_type='session'),
                             dcc.Store(id='intermediate-value-string', storage_type='session'),

                             # html.Button('SAVE', id='save_changes2', n_clicks=0,
                             #             style={'fontWeight': 'bold', 'display': 'inline-block',
                             #                    'vertical-align': 'middle', "min-width": "150px", 'height': "25px",
                             #                    "margin-top": "0px",
                             #                    "margin-left": "5px", 'backgroundColor': '#1f77b4', 'color': 'white',
                             #                    'border': '0px', 'border-radius': '5px', 'cursor': 'pointer'}),
                             html.Br(),
                             html.Div(id='output2'),
                             html.H2('WOS Performance', className='h1',
                                     style={'font-family': 'Helvetica', 'textAlign': 'center'}),
                             html.Div(
                                 style={'border': 'none'},
                                 children=[
                                     html.Br(),
                                     html.Div(style={'margin': '0 20px'}, children=[
                                         dcc.Dropdown(
                                             id='graph-type-po',
                                             options=[
                                                 {'label': 'Histogram', 'value': 'Histogram'},
                                                 {'label': 'Line Graph', 'value': 'Line Graph'},
                                             ],
                                             value='Line Graph', persistence=True, persistence_type='memory',
                                             placeholder="Select the trace type",
                                             style={'width': '50%', 'font-family': 'Helvetica',
                                                    'borderColor': '#6B9AC4'}
                                         ),
                                     ]),
                                     html.Br(),
                                     html.Div([
                                         dcc.Graph(id='wos-graph-po'),
                                     ]),
                                     html.Br(),
                                 ]
                             ),
                             html.Br(),
                             html.Br()
                         ])
                     ]),
                 # dcc.Tab(label="Forecasts", className='tab-style', value='tab-3', selected_className='selected-tab-style',
                 #         style={'font-family': 'Helvetica', 'background-color': '#6B9AC4', 'border-style': "outset",
                 #                'border-color': 'white', "margin": 'auto', 'color': 'white'}, children=[
                 #         html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                 #             html.Br(),
                 #             html.Br(),
                 #             dcc.Store(id='intermediate-value', storage_type='session'),
                 #             dcc.Store(id='intermediate-value-string', storage_type='session'),
                 #             html.Br(),
                 #             html.Br(),
                 #             dash_table.DataTable(
                 #                 id='details-table',
                 #                 columns=[
                 #                     {'name': 'Item', 'id': 'Item', 'editable': False},
                 #                     {'name': 'Site', 'id': 'Site', 'editable': False},
                 #                     {'name': 'Date', 'id': 'Date', 'editable': False},
                 #                     {'name': 'Demand', 'id': 'Demand', 'editable': False},
                 #                     {'name': 'UB', 'id': 'UB', 'editable': False},
                 #                     {'name': 'LB', 'id': 'LB', 'editable': False},
                 #                 ],
                 #                 filter_action='native',
                 #                 style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                 #                 style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                 #                 style_data_conditional=[
                 #                     {
                 #                         'if': {'column_id': 'POs'},
                 #                         # 'backgroundColor': 'red',
                 #                         'color': 'blue',
                 #                     }],
                 #                 style_table={'overflowX': 'scroll'},
                 #                 sort_action='native',
                 #                 sort_mode='multi',
                 #                 css=[hover_style],
                 #                 page_size=20
                 #             ),
                 #             dcc.Store(id='intermediate-value2', storage_type='session'),
                 #             html.Div(id='total-volume-output'),
                 #             html.Br(),
                 #             html.Button('SAVE', id='save_changes3', n_clicks=0,
                 #                         style={'fontWeight': 'bold', 'display': 'inline-block',
                 #                                'vertical-align': 'middle', "min-width": "150px", 'height': "25px",
                 #                                "margin-top": "0px",
                 #                                "margin-left": "5px", 'backgroundColor': '#1f77b4', 'color': 'white',
                 #                                'border': '0px', 'border-radius': '5px', 'cursor': 'pointer'}),
                 #             html.Br(),
                 #             html.Div(id='output3'),
                 #             html.Div(id='selected-cell-output'),  # Placeholder for displaying additional content
                 #             html.H2('Demand - Predictive Intervals Flow', className='h1',
                 #                     style={'font-family': 'Helvetica', 'textAlign': 'center'}),
                 #             html.Div(
                 #                 style={'border': 'none'},
                 #                 children=[
                 #                     html.Br(),
                 #                     html.Div(style={'margin': '0 20px'}, children=[
                 #                         dcc.Dropdown(
                 #                             id='graph-type-po',
                 #                             options=[
                 #                                 {'label': 'Histogram', 'value': 'Histogram'},
                 #                                 {'label': 'Line Graph', 'value': 'Line Graph'},
                 #                             ],
                 #                             value='Line Graph', persistence=True, persistence_type='memory',
                 #                             placeholder="Select the trace type",
                 #                             style={'width': '50%', 'font-family': 'Helvetica',
                 #                                    'borderColor': '#6B9AC4'}
                 #                         ),
                 #                     ]),
                 #                     html.Br(),
                 #                     html.Div([
                 #                         dcc.Graph(id='wos-graph-po'),
                 #                     ]),
                 #                     html.Br(),
                 #                 ]
                 #             ),
                 #             html.Br()
                 #         ])
                 #     ]),
             ])
],
    style={
        'minHeight': '100vh',
        'fontFamily': 'Helvetica',
        'background': '#E8E8E8',
        'maxWidth': '100%'
    }, id='hover-box')
page_ex_layout = html.Div([
    # html.Br(),
    dcc.Tabs(id='tabs', value='tab-1',
             style={
                 'font-family': 'Helvetica',
             },
             children=[
                 dcc.Tab(label='Algorithm Parameters', className='tab-style', selected_className='selected-tab-style',
                         value='tab-1',
                         style={'font-family': 'Helvetica', 'border-style': "outset", 'border-color': 'white',
                                "margin": 'auto', 'color': 'white', 'background-color': '#6B9AC4'}, children=[
                         html.Br(),
                         html.Br(),
                         html.Div(style={'border': 'none', 'background': '#E8E8E8', 'minHeight': '100vh'}, children=[
                             # html.Br(),
                             # html.Br(),
                             html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                                 dash_table.DataTable(
                                     id='exception-table1',
                                     # columns=[{"name": i, "id": i} for i in wos_df.columns],
                                     style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                                     style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold+',
                                                   'color': 'white'},
                                     style_table={'overflowX': 'scroll'},
                                     filter_action='native',
                                     sort_action='native',
                                     sort_mode='multi',
                                     css=[hover_style],
                                     page_size=10
                                 ),
                                 html.Br(),
                                 html.Button('Download', id='Download-excep-btn', n_clicks=0,
                                             style={'fontWeight': 'bold', 'display': 'inline-block',
                                                    'vertical-align': 'middle', "min-width": "150px", 'height': "25px",
                                                    "margin-top": "0px",
                                                    "margin-left": "5px", 'backgroundColor': '#1f77b4',
                                                    'color': 'white',
                                                    'border': '0px', 'border-radius': '5px', 'cursor': 'pointer'}),
                                 dcc.Download(id="download_excep"),
                             ]),
                             html.Div(id='plot-data-out1'),
                             html.Br(),
                             # html.Div(
                             #     style={'border': 'none', 'margin': '0 20px'},
                             #     children=[
                             #         html.Br(),
                             #         html.Div(style={'margin': '0 20px'}, children=[
                             #             dcc.Dropdown(
                             #                 id='graph-type-e', persistence=True, persistence_type='memory',
                             #                 options=[
                             #                     {'label': 'Histogram', 'value': 'Histogram'},
                             #                     {'label': 'Line Graph', 'value': 'Line Graph'},
                             #                 ],
                             #                 value='Line Graph',
                             #                 placeholder="Select the trace type",
                             #                 style={'width': '50%', 'font-family': 'Helvetica',
                             #                        'borderColor': '#6B9AC4'}
                             #             ),
                             #         ]),
                             #         html.Br(),
                             #         html.Div([
                             #             dcc.Graph(id='wos-graph-e'),
                             #         ]),
                             #     ]),
                             html.Br()
                         ])
                     ]),
                 # dcc.Tab(label="Inventory Flow", value='tab-2', className='tab-style',
                 #         selected_className='selected-tab-style',
                 #         style={'font-family': 'Helvetica', 'background-color': '#6B9AC4', 'border-style': "outset",
                 #                'border-color': 'white', "margin": 'auto', 'color': 'white'}, children=[
                 #         html.Div(style={'border': 'none', 'background': '#E8E8E8', 'minHeight': '100vh'}, children=[
                 #             # html.Br(),
                 #             html.Br(),
                 #             html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                 #                 dash_table.DataTable(
                 #                     id='exception-table2',
                 #                     columns=[{"name": i, "id": i} for i in parameter_df.columns],
                 #                     style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                 #                     style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold+',
                 #                                   'color': 'white'},
                 #                     style_table={'overflowX': 'scroll'},
                 #                     filter_action='native',
                 #                     sort_action='native',
                 #                     sort_mode='multi',
                 #                     css=[hover_style],
                 #                     page_size=10
                 #                 ),
                 #             ]),
                 #             html.Div(id='plot-data-out'),
                 #             html.Br(),
                 #             html.Div(
                 #                 style={'border': 'none', 'margin': '0 20px'},
                 #                 children=[
                 #                     html.Br(),
                 #                     html.Div(style={'margin': '0 20px'}, children=[
                 #                         dcc.Dropdown(
                 #                             id='graph-type-e', persistence=True, persistence_type='memory',
                 #                             options=[
                 #                                 {'label': 'Histogram', 'value': 'Histogram'},
                 #                                 {'label': 'Line Graph', 'value': 'Line Graph'},
                 #                             ],
                 #                             value='Line Graph',
                 #                             placeholder="Select the trace type",
                 #                             style={'width': '50%', 'font-family': 'Helvetica',
                 #                                    'borderColor': '#6B9AC4'}
                 #                         ),
                 #                     ]),
                 #                     html.Br(),
                 #                     html.Div([
                 #                         dcc.Graph(id='wos-graph-e'),
                 #                     ]),
                 #                 ]),
                 #             html.Br()
                 #         ])
                 #     ]),
             ])
],
    style={
        'minHeight': '100vh',
        'fontFamily': 'Helvetica',
        'background': '#E8E8E8',
        'maxWidth': '100%'
        # E8E8E8
        # F5F5F5
    }, id='hover-box')


page_d_layout = html.Div([
    # html.Br(),
    dcc.Tabs(id='tabs', value='tab-1',
             style={
                 'font-family': 'Helvetica',
             },
             children=[
                 dcc.Tab(label='Demand-Inventory Flow', className='tab-style', selected_className='selected-tab-style', value='tab-1',
                         style={'font-family': 'Helvetica', 'border-style': "outset", 'border-color': 'white',
                                "margin": 'auto', 'color': 'white', 'background-color': '#6B9AC4'}, children=[
                         html.Br(),
                         html.Br(),
                         html.Div(
                             children=[
                                 html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                                     html.Br(),
                                     dash_table.DataTable(
                                         id='po-table',
                                         columns=[
                                             {'name': 'Item', 'id': 'item'},
                                             {'name': 'Site', 'id': 'site'},
                                             {'name': 'Demand', 'id': 'demand'},
                                             {'name': 'Inventory', 'id': 'inv'},
                                             {'name': 'Transfer_In', 'id': 'tin'},
                                             {'name': 'Transfer_Out', 'id': 'tout'},
                                             {'name': 'SS_Weeks', 'id': 'sw'},
                                             {'name': 'WOS', 'id': 'wos'},
                                             {'name': 'Sim_Inv', 'id': 'sinv'},
                                             {'name': 'Sim_WOS', 'id': 'swos'},
                                         ],
                                         filter_action='native',
                                         row_deletable=True,
                                         style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                                         style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold',
                                                       'color': 'white'},
                                         style_table={'overflowX': 'scroll'},
                                         sort_action='native',
                                         sort_mode='multi',
                                         # css=[hover_style],
                                         tooltip_header={
                                             'Source': 'Source DC Location',
                                             'Destination': 'Destination DC Location',
                                             'Quantity': 'Quantity Transferred',
                                             'SKUs_Count': 'Number of Items Transferred',
                                         },
                                         css=[hover_style, {
                                             'selector': '.dash-table-tooltip',
                                             'rule': 'background-color: grey; font-family: monospace; color: white',
                                         }],
                                         tooltip_delay=0,
                                         tooltip_duration=None
                                     ),
                                     html.Br(),
                                     html.Br(),
                                     html.Br(),
                                     html.Br(),
                                     html.Div(id='output-1'),
                                     html.Br(),
                                     html.Br(),
                                 ]),
                             ]),
                     ]),
                 # dcc.Tab(label="Forecasts", className='tab-style', value='tab-3', selected_className='selected-tab-style',
                 #         style={'font-family': 'Helvetica', 'background-color': '#6B9AC4', 'border-style': "outset",
                 #                'border-color': 'white', "margin": 'auto', 'color': 'white'}, children=[
                 #         html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                 #             html.Br(),
                 #             html.Br(),
                 #             dcc.Store(id='intermediate-value', storage_type='session'),
                 #             dcc.Store(id='intermediate-value-string', storage_type='session'),
                 #             html.Br(),
                 #             html.Br(),
                 #             dash_table.DataTable(
                 #                 id='details-table',
                 #                 columns=[
                 #                     {'name': 'Item', 'id': 'Item', 'editable': False},
                 #                     {'name': 'Site', 'id': 'Site', 'editable': False},
                 #                     {'name': 'Date', 'id': 'Date', 'editable': False},
                 #                     {'name': 'Demand', 'id': 'Demand', 'editable': False},
                 #                     {'name': 'UB', 'id': 'UB', 'editable': False},
                 #                     {'name': 'LB', 'id': 'LB', 'editable': False},
                 #                 ],
                 #                 filter_action='native',
                 #                 style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                 #                 style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                 #                 style_data_conditional=[
                 #                     {
                 #                         'if': {'column_id': 'POs'},
                 #                         # 'backgroundColor': 'red',
                 #                         'color': 'blue',
                 #                     }],
                 #                 style_table={'overflowX': 'scroll'},
                 #                 sort_action='native',
                 #                 sort_mode='multi',
                 #                 css=[hover_style],
                 #                 page_size=20
                 #             ),
                 #             dcc.Store(id='intermediate-value2', storage_type='session'),
                 #             html.Div(id='total-volume-output'),
                 #             html.Br(),
                 #             html.Button('SAVE', id='save_changes3', n_clicks=0,
                 #                         style={'fontWeight': 'bold', 'display': 'inline-block',
                 #                                'vertical-align': 'middle', "min-width": "150px", 'height': "25px",
                 #                                "margin-top": "0px",
                 #                                "margin-left": "5px", 'backgroundColor': '#1f77b4', 'color': 'white',
                 #                                'border': '0px', 'border-radius': '5px', 'cursor': 'pointer'}),
                 #             html.Br(),
                 #             html.Div(id='output3'),
                 #             html.Div(id='selected-cell-output'),  # Placeholder for displaying additional content
                 #             html.H2('Demand - Predictive Intervals Flow', className='h1',
                 #                     style={'font-family': 'Helvetica', 'textAlign': 'center'}),
                 #             html.Div(
                 #                 style={'border': 'none'},
                 #                 children=[
                 #                     html.Br(),
                 #                     html.Div(style={'margin': '0 20px'}, children=[
                 #                         dcc.Dropdown(
                 #                             id='graph-type-po',
                 #                             options=[
                 #                                 {'label': 'Histogram', 'value': 'Histogram'},
                 #                                 {'label': 'Line Graph', 'value': 'Line Graph'},
                 #                             ],
                 #                             value='Line Graph', persistence=True, persistence_type='memory',
                 #                             placeholder="Select the trace type",
                 #                             style={'width': '50%', 'font-family': 'Helvetica',
                 #                                    'borderColor': '#6B9AC4'}
                 #                         ),
                 #                     ]),
                 #                     html.Br(),
                 #                     html.Div([
                 #                         dcc.Graph(id='wos-graph-po'),
                 #                     ]),
                 #                     html.Br(),
                 #                 ]
                 #             ),
                 #             html.Br()
                 #         ])
                 #     ]),
             ])
],
    style={
        'minHeight': '100vh',
        'fontFamily': 'Helvetica',
        'background': '#E8E8E8',
        'maxWidth': '100%'
    }, id='hover-box')

@app.callback(
    Output('family-code-dropdown', 'options'),
    Input('vendor-name-dropdown', 'value'), Input('username', 'data'))
def update_family_code_dropdown(vendor_name, data):
    df = pd.read_csv('PO_STO_Transfer_Out.csv')

    if data != 'admin':
        df = df.loc[df['Planner'] == data]

    df = df.loc[df['Vendor_Name'] == vendor_name]
    options = [{'label': i, 'value': i} for i in df['Family_Code'].unique()]
    return options


@app.callback(
    Output('site-fc-dropdown', 'options'),
    Input('family-code-dropdown', 'value'),Input('username', 'data'))
def update_sitedropdown(family_code, username):
    df = pd.read_csv('PO_STO_Transfer_Out.csv')

    print('FC-VALUES:', family_code, type(family_code))

    if username != 'admin':
        df = df.loc[df['Planner'] == username]

    if family_code != None: # first time loading
        df = df.loc[df['Family_Code'].isin(family_code)]

    options = [{'label': i, 'value': i} for i in pd.concat([df['Loc-Source'], df['Loc-Destination']]).unique()]
    options.insert(0, {'label': 'All', 'value': 'All'})
    return options


# Callback function for grouping vendor values corresponding to the selected planner value
@app.callback(
    Output('vendor-name-dropdown', 'options'),
    Output('username', 'data'),
    Input('dropdown-loaded', 'data'))
def update_vendor_name_dropdown(data):
    # global username
    username = request.authorization['username']
    if data or auth.is_authorized():
        with open('removed_data_{}.csv'.format(username), 'w') as file:
            print(' ')
        file.close()
        with open('edited_data_{}.csv'.format(username), 'w') as file:
            print(' ')
        file.close()
        with open('edited_sum_data_{}.csv'.format(username), 'w') as file:
            print(' ')
        file.close()

        df = pd.read_csv('PO_STO_Transfer_Out.csv')

        if username != 'admin':
            df = df.loc[df['Planner'] == username]

        options = [{'label': i, 'value': i} for i in df['Vendor_Name'].unique()]
        print("Options=", options)
        return options, username
    else:
        return [],''

class poBean:
    vendor = ""
    dc = ""
    date = ""
    wkAfLT = 0

    def __init__(self, v, dc, da, wk):
        self.vendor = v
        self.dc = dc
        self.date = da
        self.wkAfLT = wk

class poDataBean:
    po = 0
    vendor = ""
    dc = ""
    item = ""
    date = ""
    qty = 0

    def __init__(self, p, v, dcen, da, t, q):
        self.po = p
        self.vendor = v
        self.dc = dcen
        self.date = da
        self.item = t
        self.qty = q

    def as_dict(self):
        return {'PO': self.po, 'Vendor': self.vendor, 'DC': self.dc, 'Date': self.date, 'Article': self.item, 'Qty': self.qty, 'Header Text':''}


# Callback function for downloading SAP csv file
@app.callback(
    Output('download', 'data'),
    Input('sap-btn', 'n_clicks'), Input('vendor-name-dropdown', 'value'),
    Input('family-code-dropdown', 'value'),
    Input('site-fc-dropdown', 'value'), Input('dload-date', 'value'), Input('username', 'data'))
def download_sap_data(n_clicks, vendor_name, family_code, site_select, date_value, username):
    # if n_clicks > 0:
    if "sap-btn" == ctx.triggered_id:
        df = pd.read_csv('PO_STO_Transfer_Out.csv')
        df = df.loc[df['Vendor_Name'] == vendor_name]
        df = df.loc[df['Family_Code'].isin(family_code)]

        if site_select != 'All':
            df = df.loc[df['Loc-Destination'] == site_select]

        poBeanObjects = dict()
        poBeanItemObjects = dict()

        for index, row in df.iterrows():
            if row.PO_Index not in poBeanObjects:
                poBeanObjects[row.PO_Index] = poBean(row.Vendor_Id, row.Site, row.PO_Week_Date, row.WK_AFTER_LT)

            if row.PO_Index not in poBeanItemObjects:
                poBeanItemObjects[row.PO_Index] = {}
            poBeanItemObjects[row.PO_Index][str(row.Item)] = int(row.POs)

        family_codeStr = '.'.join(str(x) for x in family_code)
        fileName = "PO_STO_Transfer_" + vendor_name + "_" + family_codeStr + "_" + str(site_select) + ".csv";
        df.to_csv(fileName, index=False)
        return dcc.send_file(fileName)



# Callback function to display the table in vendor selection tab corresponding to the selected vendor value
@app.callback(
    Output('summary-table', 'data'),
    Output('dateValue', 'children'),
    # Output('site-dropdown', 'options'),
    # Output('fc-dropdown', 'options'),
    Input('vendor-name-dropdown', 'value'), Input('family-code-dropdown', 'value'), Input('site-fc-dropdown', 'value'))
def update_summary_table(vendor_name, family_code, site_select):

    print('vendor_name:', vendor_name)
    print('family_code:', family_code)
    print('site_select:', site_select)


    if vendor_name is None or family_code is None or not family_code or site_select is None:
        return [], ''

    # global df
    df = pd.read_csv('PO_STO_Transfer_Out.csv')
    if site_select != 'All':
        df = df.loc[df['Item-Destination'] == site_select]

    df = df.loc[df['Vendor_Name'] == vendor_name]
    df = df.loc[df['Family_Code'].isin(family_code)]

    print('df', df)

    dateValue = df.iloc[0][0]
    df['Item-Source'] = df['Item-Source'].astype(str)
    date_time_obj = str(dateValue).partition('.')[0]

    # date_time_obj = datetime.strptime(str(date_time_obj), '%Y-%m-%d %H:%M:%S')
    date_time_obj = datetime.strptime(str(date_time_obj), '%m/%d/%Y %H:%M')
    # options_site = [{'label': i, 'value': i} for i in df['Site'].unique()]
    # options_site.insert(0, {'label': 'All', 'value': 'All'})
    options_fc = [{'label': i, 'value': i} for i in df['Family_Code'].unique()]
    options_fc.insert(0, {'label': 'All', 'value': 'All'})
    method = html.Div([
        html.H3('Latest RunDate : {}'.format(date_time_obj.strftime('%m/%d/%Y')),
                style={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'})])
    summary_df = df.groupby(['Loc-Source','Loc-Destination', 'Week_Date']).agg({'Qty': ['sum'], 'Item-Source': 'nunique'}).reset_index()
    print('summary_df', summary_df)
    summary_df.columns = summary_df.columns.droplevel(0)
    summary_df.columns = ['src', 'dest', 'wdate', 'qty', 'Sku_count']
    summary_df = summary_df.reset_index().rename(columns={"index": "id"})

    return summary_df.round(2).to_dict('records'), method

@app.callback(
    Output('po-table', 'data'),
    # Output('dateValue-po', 'children'),
    # Output('site-dropdown', 'options'),
    # Output('fc-dropdown', 'options'),
    Input('vendor-name-dropdown', 'value'), Input('family-code-dropdown', 'value'), Input('site-fc-dropdown', 'value'))
def update_po_table(vendor_name, family_code, site_select):

    # print('vendor_name:', vendor_name)
    print('family_code:', family_code)
    print('site_select:', site_select)

    if vendor_name is None or family_code is None or not family_code or site_select is None:
        return [], ''

    # global df
    df = pd.read_csv('Plot_Data_out.csv')
    if site_select != 'All':
        df = df.loc[df['Site'] == site_select]

    # df = df.loc[df['Vendor_Name'] == vendor_name]
    df = df.loc[df['Family_Code'].isin(family_code)]
    print('df', df)

    df['Item'] = df['Item'].astype(str)

    # options_site = [{'label': i, 'value': i} for i in df['Site'].unique()]
    # options_site.insert(0, {'label': 'All', 'value': 'All'})
    options_fc = [{'label': i, 'value': i} for i in df['Family_Code'].unique()]
    options_fc.insert(0, {'label': 'All', 'value': 'All'})

    df = df[['Item', 'Site', 'Demand', 'Inventory', 'Transfer_In', 'Transfer_Out', 'SS_Weeks', 'WOS','Sim_Inv', 'Sim_WOS']]

    print('summary_df', df)
    # df.columns = df.columns.droplevel(0)
    df.columns = ['item', 'site', 'demand', 'inv', 'tin', 'tout', 'sw', 'wos','sinv','swos']
    df = df.reset_index().rename(columns={"index": "id"})

    return df.round(2).to_dict('records')

@app.callback(
    Output('wos-graph-po', 'figure'),
    Input('graph-type-po', 'value'),
    Input('summary2-table', 'active_cell'),
    State('summary2-table', 'data')
)
def update_graph(graph_type, active_cell, table_data):
    if active_cell:
        fig = go.Figure()
        fig.update_layout(
            plot_bgcolor='#ADD8E6',  # Set the plot background color
            paper_bgcolor='rgb(240, 240, 240)',  # Set the paper background color
            # margin=dict(l=50, r=40, t=40, b=40),  # Adjust margins as needed
            xaxis_title='Week', yaxis_title='WOS Values',
            xaxis=dict(showline=True, linewidth=2, linecolor='#6B9AC4'),  # X-axis border
            yaxis=dict(showline=True, linewidth=2, linecolor='#6B9AC4')
        )
        selected_row = table_data[active_cell['row']]
        item = selected_row['item']
        # location = selected_row['src']

        locList = []
        locList.append(str(selected_row['src']))
        locList.append(str(selected_row['dest']))

        df_2 = pd.read_csv('Plot_Data_out.csv')

        df_2['Item'] = df_2['Item'].astype(str)
        df_2['Site'] = df_2['Site'].astype(str)
        df_2 = df_2[df_2['Item'].str.contains(str(item))]
        # df_2 = df_2.loc[df_2['Site'].isin(locList)]

        print('loclist:',locList)
        print('item:',item)
        print('df_2:',df_2)

        df_2['Week_Date'] = pd.to_datetime(df_2['Week_Date'], format='%m/%d/%Y')

        df_2.sort_values('Week_Date', inplace=True)
        for location in locList:
            df_3 = df_2[df_2['Site'].str.contains(str(location))]
            print('df_3:', df_3)
            for column in ['SS_Weeks', 'WOS', 'Sim_WOS']:
                y_vals = df_3.groupby('Week_Date')[column].mean()
                if graph_type == 'Line Graph':
                    x_axis = str(item) + '_' + str(location) + '_' + column
                    fig.add_trace(go.Scatter(x=y_vals.index, y=y_vals, name=x_axis))  # mode='lines'
                elif graph_type == 'Histogram':
                    fig.add_trace(go.Histogram(x=y_vals.index, y=y_vals, name=column))

        return fig
    else:
        fig = go.Figure()
        fig.update_layout(
            plot_bgcolor='#ADD8E6',  # Set the plot background color
            paper_bgcolor='rgb(240, 240, 240)',  # Set the paper background color
            # margin=dict(l=50, r=40, t=40, b=40),  # Adjust margins as needed
            xaxis_title='Week', yaxis_title='Demand',
            xaxis=dict(showline=True, linewidth=2, linecolor='#6B9AC4'),  # X-axis border
            yaxis=dict(showline=True, linewidth=2, linecolor='#6B9AC4')
        )
        return fig


# add an intermediate data with save button, the intermediate data gets
# Callback function for displaying the table in PO Aggregate tab according to the selected cell in the vendor selection tab
@app.callback(
    Output('summary2-table', 'data'),
    Output('intermediate-value-sum', 'data'),
    Input('summary-table', 'active_cell'),
    State('summary-table', 'data'),
    Input('summary-table', 'data_timestamp'),
    State('summary-table', 'data_previous'),
    Input('intermediate-value-sum', 'data')
)
def update_summary2_table(active_cell, summary_table_data, time, previous, df_sum_deleted):
    df = pd.read_csv('PO_STO_Transfer_Out.csv', index_col=False)

    if (time is not None) & (summary_table_data is not None) & (previous is not None) & (df_sum_deleted is not None):
        if df_sum_deleted is None:
            df_sum_deleted = []
        for row in previous:
            if row not in summary_table_data:
                # selected_item_group = row['ItemGroup']
                Location = row['Site']
                # FamilyCode = row['Family_Code']
                details_data = df[(df['Site'] == Location)] # & (df['Family_Code'] == FamilyCode)
                details_data = details_data['Item'].unique().tolist()
                df_sum_deleted = df_sum_deleted + details_data
        if active_cell is not None:
            Date = summary_table_data[active_cell['row_id']]['Site']
            print('Date:', Date)
            Location = summary_table_data[active_cell['row_id']]['Site']
            filtered_df = df[(df['Site'] == Location)]
            summary2_df = filtered_df[['Item', 'Site', 'Family_Code', 'Article_Desc', 'LT_Weeks', 'LT_error', 'Rank', 'Error']]
            # summary2_df.columns = summary2_df.columns.droplevel(0)
            summary2_df.columns = ['Item', 'Site', 'Family_Code', 'Article_Desc', 'LT_Weeks', 'LT_error', 'Rank',
                                   'Error']
            print('summary2_df:',summary2_df)
            return summary2_df.round(2).to_dict('records'), df_sum_deleted
        return summary_table_data, df_sum_deleted
    if active_cell is not None:
        if df_sum_deleted is None:
            df_sum_deleted = []

        src = summary_table_data[active_cell['row_id']]['src']
        dest = summary_table_data[active_cell['row_id']]['dest']
        wDate = summary_table_data[active_cell['row_id']]['wdate']

        print('src:', src)
        print('dest:', dest)
        print('wDate:', wDate)

        # summary_df.columns = ['src', 'dest', 'wdate', 'qty', 'Sku_count']


        filtered_df = df[(df['Loc-Source'] == src) & (df['Loc-Destination'] == dest) & (df['Week_Date'] == wDate)]
        print('filtered_df:', filtered_df)

        summary2_df = filtered_df[['Item-Source', 'Loc-Source','Loc-Destination',
                                   'Qty', 'Item-Source-Before-WOS', 'Item-Source-After-WOS', 'Item-Destination-Before-WOS', 'Item-Destination-After-WOS', 'Item-Source-WOS','Item-Destination-WOS']]
        # summary2_df.columns = summary2_df.columns.droplevel(0)
        summary2_df.columns = ['item', 'src', 'dest', 'qty', 'src-b-wos', 'src-a-wos', 'dest-b-wos', 'dest-a-wos','src-wos','dest-wos']
        summary2_df = summary2_df.reset_index().rename(columns={"index": "id"})
        print('summary2_df111:', summary2_df)
        return summary2_df.round(2).to_dict('records'), df_sum_deleted
    else:
        return [], []


@app.callback(
    Output('details-table', 'data'),
    Input('summary2-table', 'active_cell'),
    Input('summary2-table', 'data'),
    Input('details-table', 'data_timestamp'),
    Input('details-table', 'data'),
    Input('intermediate-value2', 'data'),
    Input('intermediate-value-string', 'data'),
    State('details-table', 'data_previous')
)
def update_details_table(active_cell, summary_table_data, time, data, df_edited, key_string, data_previous):
    key_new_value = ''
    if (active_cell is not None):

        Item = summary_table_data[active_cell['row']]['Item']
        Location = summary_table_data[active_cell['row']]['Site']

        print('comes in-2:',Item,'Loc:', Location)

        data = pd.read_csv('DemandData.csv')

        data['Item'] = data['Item'].astype(str)
        data['Site'] = data['Site'].astype(str)
        data = data[data['Item'].str.contains(str(Item))]
        data = data[data['Site'].str.contains(str(Location))]

        data.columns = ['Item', 'Site', 'Date','Demand', 'UB', 'LB']
        print('summary2_df:', data)
        return data.round(2).to_dict('records')
        # return data.to_dict('records')
    else:
        return []

# Callback function for getting the deleted rows from PO Aggregate tab
@app.callback(
    Output('intermediate-value', 'data'),
    Output('intermediate-valueM', 'data'),
    Input('summary2-table', 'data_timestamp'),
    State('summary2-table', 'data'),
    State('summary2-table', 'data_previous'),
    Input('intermediate-value', 'data'),
    Input('intermediate-valueM', 'data'))
def show_removed_rows(time, current, previous, df_deleted, df_sum_edit):
    print('show_remov-time:', time)
    print('show_remov-current:', current)
    print('show_remov-previous:', previous)
    print('show_remov-df-del:', df_deleted)
    if (time is not None) & (current is not None) & (previous is not None) & (df_deleted is not None):
        if df_deleted is None:
            df_deleted = []
        for row in previous:
            print('row-previous:', row)
            rowPresent = False
            for row1 in current:
                print('row-previous:', row['PO_Index'], row1['PO_Index'], row['PO_Week_Date'], ' row1-value:',
                      row1['PO_Week_Date'])
                if row['PO_Index'] == row1['PO_Index'] and row['PO_Week_Date'] != row1['PO_Week_Date']:  # date modified
                    print('Gets in:')
                    current_data = pd.DataFrame(current)
                    previous_data = pd.DataFrame(previous)
                    diff_poss = current_data['PO_Week_Date'] != previous_data['PO_Week_Date']
                    edited_data = current_data[diff_poss]
                    edited_data = edited_data.round(2).to_dict('records')
                    df_sum_edit = df_sum_edit + edited_data
                    print('diff_pos:', diff_poss)
                    print('edited_data:', edited_data)
                    print('show_df_summ_edit:', df_sum_edit)
                    rowPresent = True
                    break
                elif row['PO_Index'] == row1['PO_Index']:
                    rowPresent = True
                    break
            if not rowPresent:  # row['PO_Index'] not in current[]['PO_Index']:
                print('NOT IN CURRENT:')
                Date = row['PO_Week_Date']
                Location = row['Site']
                PO_index = row['PO_Index']
                print('Date, Loc, PO_Index:', Date, Location, PO_index)
                details_data = df[
                    (df['PO_Week_Date'] == Date) & (df['Site'] == Location) & (df['PO_Index'] == PO_index)]
                details_data = details_data.round(2).to_dict('records')
                print('details_data:', details_data)
                df_deleted = df_deleted + details_data
                print('show_remov-4-df-del:', df_deleted)
        return df_deleted, df_sum_edit
    else:
        return [], []

@app.callback(
    Output('selected-cell-output', 'children'),
    Input('details-table', 'active_cell'),
    State('details-table', 'data')
)
def display_selected_cell(active_cell, table_data):
    if active_cell:
        selected_row = table_data[active_cell['row']]
        item = selected_row['Item']
        location = selected_row['Site']

        data = pd.read_csv('RawSummary.csv')
        # data = data.loc[data['Item'] == item]
        # data = data.loc[data['Site'] == location]
        data['Item'] = data['Item'].astype(str)
        data['Site'] = data['Site'].astype(str)
        data = data[data['Item'].str.contains(str(item))]
        data = data[data['Site'].str.contains(str(location))]

        data['MAE'] = data['MAE'].astype('float').round(2)
        data['RMSE'] = data['RMSE'].astype('float').round(2)
        data['MAPE'] = data['MAPE'].astype('float').round(2)
        data['R2'] = data['R2'].astype('float').round(2)

        method = html.Div(children=[
            html.Br(),
            html.H2('Forecast Methods Performance', className='h1', style={'font-family': 'Helvetica', 'textAlign': 'center'}),
            dash_table.DataTable(
                columns=[
                    {'name': 'Item', 'id': 'Item'},
                    {'name': 'Site', 'id': 'Site'},
                    {'name': 'Method', 'id': 'Method'},
                    {'name': 'MAE', 'id': 'MAE'},
                    {'name': 'RMSE', 'id': 'RMSE'},
                    {'name': 'MAPE', 'id': 'MAPE'},
                    {'name': 'R2', 'id': 'R2'}
                ],
                data=data.to_dict('records'),
                style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                style_table={'overflowX': 'scroll', 'overflowX': 'scroll'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                row_selectable=False,
                css=[hover_style],
                page_size=10
            )
        ])
        return method
    else:
        return []


@app.callback(
    Output('download_excep', 'data'),
    Input('Download-excep-btn', 'n_clicks'), Input('vendor-name-dropdown', 'value'),
    Input('family-code-dropdown', 'value'), Input('site-fc-dropdown', 'value'))
def download_excep_data(n_clicks, vendor_name, family_code, site_select):
    if "Download-excep-btn" == ctx.triggered_id:
        return dcc.send_file('Parameters.csv')

@app.callback(
    Output('download_po', 'data'),
    Input('download-po-btn', 'n_clicks'), Input('vendor-name-dropdown', 'value'),
    Input('family-code-dropdown', 'value'), Input('site-fc-dropdown', 'value'))
def download_po_data(n_clicks, vendor_name, family_code, site_select):
    # if n_clicks > 0:
    if "download-po-btn" == ctx.triggered_id:
        df = pd.read_csv('PO_STO_Transfer_Out.csv')
        df = df.loc[df['Vendor_Name'] == vendor_name]
        df = df.loc[df['Family_Code'].isin(family_code)]

        if site_select != 'All':
            df = df.loc[df['Loc-Source'] == site_select]

        family_codeStr = '.'.join(str(x) for x in family_code)
        fileName = "PO_STO_Transfer_" + vendor_name + "_" + family_codeStr + "_" + str(site_select) + ".csv";
        df.to_csv(fileName, index=False)
        return dcc.send_file(fileName)

# Callback function for comparing the changes made with parent data file and creating an updated csv file
@app.callback(
    Output('save_changes3', 'n_clicks'),
    Input('save_changes3', 'n_clicks'),
    Input('intermediate-value', 'data'),
    Input('intermediate-value2', 'data'),
    Input('intermediate-valueM', 'data'),
    Input('intermediate-value-sum', 'data'), Input('username', 'data'))
def save_changes(n_clicks3, df_deleted, df_edited, df_edit_summ, df_sum_deleted, username):

    # if (n_clicks1 == 1):
    # if (n_clicks1 == 1):
    # if (n_clicks2 == 1):
    return 0

page_2_layout = html.Div(
    style={
        'backgroundColor': '#1f1f1f',
        'color': 'white',
        'height': '100vh',
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'textAlign': 'center',
        'fontFamily': 'Helvetica',
    },
    children=[
        html.H2("The application has ended!")
    ]
)


@app.callback(
    Output('plot-data-out1', 'children'),
    Input('exception-table1', 'active_cell'),
    State('exception-table1', 'data')
)
def display_selected_cell(active_cell, table_data):
    if active_cell:

        strVals  = active_cell["row_id"].split('_')

        item = str(strVals[0])
        location = str(strVals[1])

        data = pd.read_csv('Plot_Data_out_stage.csv')
        data['Item'] = data['Item'].astype(str)
        data['Site'] = data['Site'].astype(str)
        data = data[data['Item'].str.contains(str(item))]
        data = data[data['Site'].str.contains(str(location))]

        method = html.Div(children=[
            html.Br(),
            html.H2('Item Supply Details', className='h1', style={'font-family': 'Helvetica', 'textAlign': 'center'}),
            dash_table.DataTable(
                columns=[
                    {'name': 'Item', 'id': 'Item'},
                    {'name': 'Site', 'id': 'Site'},
                    {'name': 'Week_Year', 'id': 'Week_Year'},
                    {'name': 'Week_Date', 'id': 'Week_Date'},
                    {'name': 'Demand', 'id': 'Demand'},
                    {'name': 'POs', 'id': 'POs'},
                    {'name': 'Receipts', 'id': 'Receipts'},
                    {'name': 'Inventory', 'id': 'Inventory'},
                    {'name': 'WOS', 'id': 'WOS'}
                ],
                data=data.to_dict('records'),
                style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                style_table={'overflowX': 'scroll', 'overflowX': 'scroll'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                row_selectable=False,
                css=[hover_style],
                page_size=10
            )
        ])
        return method
    else:
        return []


@app.callback(
    Output('plot-data-out', 'children'),
    Input('exception-table2', 'active_cell'),
    State('exception-table2', 'data')
)
def display_selected_cell(active_cell, table_data):
    if active_cell:

        # selected_row = table_data[active_cell['row']]
        # item = selected_row['Item']
        # location = selected_row['Site']

        strVals  = active_cell["row_id"].split('_')
        item = str(strVals[0])
        location = str(strVals[1])

        data = pd.read_csv('Plot_Data_out_stage.csv')

        data['Item'] = data['Item'].astype(str)
        data['Site'] = data['Site'].astype(str)
        data = data[data['Item'].str.contains(str(item))]
        data = data[data['Site'].str.contains(str(location))]

        method = html.Div(children=[
            html.Br(),
            html.H2('Item Supply Details', className='h1', style={'font-family': 'Helvetica', 'textAlign': 'center'}),
            dash_table.DataTable(
                columns=[
                    {'name': 'Item', 'id': 'Item'},
                    {'name': 'Site', 'id': 'Site'},
                    {'name': 'Week_Year', 'id': 'Week_Year'},
                    {'name': 'Week_Date', 'id': 'Week_Date'},
                    {'name': 'Demand', 'id': 'Demand'},
                    {'name': 'POs', 'id': 'POs'},
                    {'name': 'Receipts', 'id': 'Receipts'},
                    {'name': 'Inventory', 'id': 'Inventory'},
                    {'name': 'WOS', 'id': 'WOS'}
                ],
                data=data.to_dict('records'),
                style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                style_table={'overflowX': 'scroll', 'overflowX': 'scroll'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                row_selectable=False,
                css=[hover_style],
                page_size=10
            )
        ])
        return method
    else:
        return []



@app.callback(Output('exception-table1', 'data'), Output('exception-table1', 'columns'),
              Input('vendor-name-dropdown', 'value'),
              Input('family-code-dropdown', 'value'),
              Input('site-fc-dropdown', 'value'))
def loadExceptionTable(vendorName, family_code, site_select):

    if vendorName is None or family_code is None or site_select is None:
        return [], []

    data = pd.read_csv('Parameters.csv')
    columnNames = [{'name': i, 'id': i} for i in data.columns]

    return data.to_dict("records"), columnNames


@app.callback(
    Output('wos-graph-e', 'figure'),
    Input('graph-type-e', 'value'),
    Input('exception-table2', 'active_cell'),
    State('exception-table2', 'data')
)
def update_graph(graph_type, active_cell, table_data):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='#ADD8E6',  # Set the plot background color
        paper_bgcolor='rgb(240, 240, 240)',  # Set the paper background color
        # margin=dict(l=50, r=40, t=40, b=40),  # Adjust margins as needed
        xaxis_title='Week', yaxis_title='Quantity',
        xaxis=dict(showline=True, linewidth=2, linecolor='#6B9AC4'),  # X-axis border
        yaxis=dict(showline=True, linewidth=2, linecolor='#6B9AC4')
    )
    if active_cell:
        selected_row = table_data[active_cell['row']]
        item = selected_row['Item']
        loc = selected_row['Site']
        # conn3 = pyodbc.connect(
        #     'Driver={SQL Server};' + 'Server=' + configDict['server'] + ';' + 'Database=' + configDict['db'] + ';'
        #     + 'Trusted_Connection=yes;')
        # query = "SELECT * FROM " + configDict['plot_data'] + " WHERE Item = ? AND Site = ?"
        # data = pd.read_sql(query, conn3, params=[item, loc])

        data = pd.read_csv('Plot_Data_out_stage.csv')

        data['Item'] = data['Item'].astype(str)
        data['Site'] = data['Site'].astype(str)
        data = data[data['Item'].str.contains(str(item))]
        data = data[data['Site'].str.contains(str(loc))]

        for column in ['Demand', 'POs', 'Inventory', 'Receipts']:
            y_vals = data.groupby('Week')[column].mean()
            if graph_type == 'Line Graph':
                fig.add_trace(go.Scatter(x=y_vals.index, y=y_vals, mode='lines', name=column))
            elif graph_type == 'Histogram':
                fig.add_trace(go.Histogram(x=y_vals.index, y=y_vals, name=column))
    return fig

@app.callback(
    Output("input-table", "data"),
    Output('valid-site', 'children'),
    Input("input-table", "data_previous"),
    Input('vendor-name-dropdown', "value"),
    Input("site-val", "value"),
    Input("input-table", "data"),
    Input("generate-fields-button", "n_clicks"),
    [State("num-records-input", "value")]
)
def update_po_volume(previous_data, vendor_val, site, current_data, n_clicks, num_records):
    if n_clicks > 0 and site is None:
        return [], html.Div("Encountered invalid site value. Please choose a valid value", style={"margin": "20px"})
    if n_clicks > 0 and num_records is not None and num_records > 0 and not current_data:
        # Generate empty rows based on the number of records
        empty_rows = [{"Item": None, "PO Value": None}] * num_records
        return empty_rows, ""
    if current_data is not None:
        for row_idx in range(len(current_data)):
            # Get the current values of 'Item' and 'PO Value' for the row
            item = current_data[row_idx]['Item']
            po_value = current_data[row_idx]['PO Value']

            # sql_select = "SELECT [Volume] FROM " + configDict[
            #     'item_master'] + " WHERE site=? AND item_desc=? AND Vendor_Name=?"

            if item is not None and po_value is not None:
                # data = (site, item, vendor_val)

                data = pd.read_csv('Item_Master.csv')
                data = data.loc[data['Site'] == site]
                data = data.loc[data['item_desc'] == item]
                data = data.loc[data['Vendor_Name'] == vendor_val]

                # po_volume = cursor.execute(sql_select, data).fetchall()[0][0]
                po_volume = data['Volume'].iloc[0]
                # print(po_volume)
                # Update the 'PO Volume' column in the current data
                current_data[row_idx]['PO Volume'] = po_volume * po_value
        return current_data, ""
    else:
        return [], ""


tab_4_layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1',
             style={
                 'font-family': 'Helvetica',
             },
             children=[
                 dcc.Tab(label="Summary", value='tab-1', className='tab-style',
                         selected_className='selected-tab-style',
                         style={'font-family': 'Helvetica', 'background-color': '#6B9AC4', 'border-style': "outset",
                                'border-color': 'white', "margin": 'auto', 'color': 'white'}, children=[
                         html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                             html.Br(),
                             html.Br(),
                             html.Br(),
                             dash_table.DataTable(
                                 id='summary1-table-po',
                                 columns=[
                                     {'name': 'Family_Code', 'id': 'Family_Code'},
                                     {'name': 'Avg_Inv', 'id': 'Avg_Inv'},
                                     {'name': 'SO', 'id': 'SO'},
                                     {'name': 'PO', 'id': 'PO'},
                                     {'name': 'Receipt', 'id': 'Receipt'},
                                     {'name': 'Inv($)', 'id': 'Inv$'},
                                     {'name': 'SO($)', 'id': 'SO$'},
                                     {'name': 'PO($)', 'id': 'PO$'},
                                     {'name': 'Receipt($)', 'id': 'Receipt$'},
                                 ],
                                 # VendorId,Family_Code,Family,Location,Week,Year,Date,Inv,SO,PO,Receipt,Inv$,SO$,PO$,Receipt$,LeadTime,Demand
                                 filter_action='native',
                                 style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                                 style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold', 'color': 'white'},
                                 style_table={'overflowX': 'scroll'},
                                 sort_action='native',
                                 sort_mode='multi',
                                 css=[hover_style],
                                 page_size=20
                             ),
                             html.Br(),
                             html.Br()
                         ])
                     ]),
                 dcc.Tab(label="Details", value='tab-2', className='tab-style',
                         selected_className='selected-tab-style',
                         style={'font-family': 'Helvetica', 'background-color': '#6B9AC4', 'border-style': "outset",
                                'border-color': 'white', "margin": 'auto', 'color': 'white'}, children=[
                         html.Div(style={'border': 'none', 'margin': '0 20px'}, children=[
                             html.Br(),
                             html.Br(),
                             html.Br(),
                             dash_table.DataTable(
                                 id='summary2-table-po',
                                 columns=[
                                     {'name': 'Family_Code', 'id': 'Family_Code'},
                                     {'name': 'Family', 'id': 'Family'},
                                     {'name': 'Location', 'id': 'Location'},
                                     {'name': 'Date', 'id': 'Date'},
                                     {'name': 'Inv', 'id': 'Inv'},
                                     {'name': 'SO', 'id': 'SO'},
                                     {'name': 'PO', 'id': 'PO'},
                                     {'name': 'Receipt', 'id': 'Receipt'},
                                     {'name': 'Inv($)', 'id': 'Inv$'},
                                     {'name': 'PO($)', 'id': 'PO$'},
                                     {'name': 'SO($)', 'id': 'SO$'},
                                     {'name': 'Receipt($)', 'id': 'Receipt$'},
                                     {'name': 'LeadTime', 'id': 'LeadTime'},
                                     {'name': 'Demand', 'id': 'Demand'},
                                 ],
                                 style_cell={'textAlign': 'center', 'fontSize': 14, 'font-family': 'Helvetica'},
                                 style_header={'backgroundColor': '#1f77b4', 'fontWeight': 'bold+', 'color': 'white'},
                                 style_table={'overflowX': 'scroll'},
                                 filter_action='native',
                                 sort_action='native',
                                 sort_mode='multi',
                                 css=[hover_style],
                                 page_size=10
                             ),
                             html.Br(),
                             html.Br()
                         ])
                     ]),
             ]),
])


@app.callback(
    Output('summary1-table-po', 'data'),
    Input('vendor-name-dropdown', 'value'), Input('username', 'data')
)
def update_summary_table_po(vendor_name, username):
    if vendor_name is not None:
        data = pd.read_csv('Po_Performance_out_stage.csv')
        data = data.loc[data['Vendor_Id'] == configDict[vendor_name.lower()]]

        summary_df = data.groupby(['Family_Code', 'Location']).agg(
            {'Inv': 'sum', 'SO': 'sum', 'PO': 'sum', 'Receipt': 'sum', 'Inv$': 'sum', 'SO$': 'sum', 'PO$': 'sum',
             'Receipt$': 'sum'}).reset_index()
        summary_df.rename(columns={'Inv': 'Avg_Inv'}, inplace=True)
        return summary_df.to_dict('records')
    else:
        return []


@app.callback(
    Output('summary2-table-po', 'data'),
    Input('summary1-table-po', 'active_cell'),
    State('summary1-table-po', 'data')
)
def update_summary2_table(active_cell, summary_table_data):
    # VendorId,Family_Code,Family,Location,Week,Year,Date,Inv,SO,PO,Receipt,Inv$,SO$,PO$,Receipt$,LeadTime,Demand
    if active_cell is not None:
        selected_item_group = summary_table_data[active_cell['row']]['Family_Code']
        Location = summary_table_data[active_cell['row']]['Location']

        data = pd.read_csv('Po_Performance_out_stage.csv')
        filtered_df = data[
            (data['Family_Code'] == selected_item_group) & (data['Location'] == Location)]
        summary_df = filtered_df.groupby(['Family_Code', 'Family', 'Location', 'Week', 'Year', 'Date']).agg(
            {'Inv': 'mean', 'SO': 'sum', 'PO': 'sum', 'Receipt': 'sum', 'Inv$': 'sum', 'SO$': 'sum', 'PO$': 'sum',
             'Receipt$': 'sum', 'LeadTime': 'sum', 'Demand': 'sum'}).reset_index()
        print(summary_df)
        return summary_df.to_dict('records')
    else:
        return []


@app.callback(
    Output('pr-table', 'data'),
    Input('pr-table', 'active_cell'),
    Input('vendor-name-dropdown', 'value'), Input('username', 'data')
)
def display_perform_report(active_cell, vendor_name, username):
    if vendor_name is not None:
        data = pd.read_csv('Po_Performance_out_stage.csv')

        if username != 'admin':
            data = data.loc[data['Planner'] == username]

        data = data.loc[data['Vendor_Name'] == vendor_name]

        return data.to_dict('records')
    else:
        return []


@app.callback(Output('tab-content', 'children'), [Input('hor_tabs', 'value'),
                                                  Input('url', 'pathname')])
def render_content(tab, pathname):
    if tab == "PO's Report":
        if pathname == '/page-2':
            return page_2_layout  # Call a function from tab1_content.py to get the content for Tab 1
        else:
            return page_1_layout
    elif tab == 'View Demand':
        return page_d_layout  # tab_2_layout
    # elif tab == 'Create a PO':
    #     return tab_3_layout
    elif tab == 'Performance Report':
        return tab_4_layout
    else:
        return []


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    # app.run_server(debug=True, threaded=True, port=8040)
    app.run(debug=False, port=server_port, host='0.0.0.0')
