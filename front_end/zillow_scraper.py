import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


# meggans imports
import json
import requests
import zipcodes
import http.client
import matplotlib.pyplot as plt
from collections import defaultdict
import quandl
import plotly.graph_objects as go

# CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
html.Button('Submit', id='button'),
dcc.Input(
    id='my-zip',
    type='number',
    value='78721',
    debounce = True
),
dcc.Graph(id = 'my-graph')
])

@app.callback(
    Output('my-graph', 'figure'),
    [Input('button', 'n_clicks')],
    [State('my-zip', 'value')])
def predict(n_clicks, zipinput):
    year, month, day = 2020, 10, 20
    key = ['MYKEY']
    zipinput = int(zipinput)
    conn = http.client.HTTPSConnection("api.gateway.attomdata.com")
    headers = {
        'accept': "application/json",
        'apikey': key
        }
    conn.request("GET",f"/propertyapi/v1.0.0/assessment/detail?geoid=ZI{zipinput}&startcalendardate={year-1}-{month}-{day}&endcalendardate={year}-{month}-{day}&page=1&pagesize=10000", headers=headers)

    res = conn.getresponse()
    data = res.read()

    dict1 = json.loads(data.decode("utf-8"))


    df_property = pd.DataFrame({
        'property_type': [dict1['property'][num]['summary']['proptype'] for num in range((len(dict1['property'])))],
        'calculated_improved_value': [dict1['property'][num]['assessment']['calculations']['calcimprvalue'] for num in range((len(dict1['property'])))],
        'calculated_land_value': [dict1['property'][num]['assessment']['calculations']['calclandvalue'] for num in range((len(dict1['property'])))],
        'calculated_total_value': [dict1['property'][num]['assessment']['calculations']['calcttlvalue'] for num in range((len(dict1['property'])))],
    })

    def get_custom_describe(value_col, df_group=df_property.groupby(['property_type'])):
        return pd.DataFrame({
                            'Count of Properties': df_group[value_col].count(),
                            'Mean Property Value': df_group[value_col].mean().map('${:,.2f}'.format),
                            'Standard Deviation': df_group[value_col].std().map('${:,.2f}'.format),
                            'Median Property Value': df_group[value_col].median().map('${:,.2f}'.format),
                            'Minimum Property Value': df_group[value_col].min().map('${:,.2f}'.format),
    #                         '25_percentile': df_group[value_col].quantile(.25).map('${:,.2f}'.format),
    #                         '75_percentile': df_group[value_col].quantile(.75).map('${:,.2f}'.format),
                            'Maximum Property Value': df_group[value_col].max().map('${:,.2f}'.format),
                            'TOTAL PROPERTIES VALUE': df_group[value_col].sum().map('${:,.2f}'.format)

        })

    # -----------------------------------
    ## Summary of Current Property Values
    df = get_custom_describe(df_group=df_property, value_col=['calculated_land_value', 'calculated_improved_value',
                                                          'calculated_total_value']).T
    df.drop(['Count of Properties', 'Standard Deviation'], inplace=True)
    df.rename(columns={
        'calculated_land_value': 'Land Value',
        'calculated_improved_value': 'Improved Value of the Land',
        'calculated_total_value': 'Total Property Value'
    })

    fig = go.Figure(data=[go.Table(
        header=dict(values=[zipinput]+list(df.columns),
                    line_color='darkslategray',
                    fill_color='royalblue',
                    align=['center',],
                    font=dict(color='white', size=12),
                    height=40
    ),
        cells=dict(values=[df.index]+list(df.values.T),
                   line_color='darkslategray',
                   fill=dict(color=['paleturquoise', 'white']),
                   align=['left', 'right'],
                   font_size=12,
                   height=30))
    ])
    return fig






if __name__ == '__main__':
    app.run_server(debug=True, port = 5000)
