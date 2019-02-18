import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime as dt
import pandas as pd
import psycopg2

app = dash.Dash(__name__, static_folder='assets')
app.scripts.config.serve_locally=True
app.css.config.serve_locally=True
app.config.suppress_callback_exceptions = True

# Settings for psycopg Timescale connector
user = 'postgres'
host = '0.0.0.0'
dbname = 'pages'
con = None
con = psycopg2.connect(database = dbname, user = user, password='password', host='localhost')


app.layout = html.Div([
    html.Div(dcc.Location(id='url', refresh=False)),
    html.Div(className='app-header'),
    html.Div(id='page-content'),
])


index_page = html.Div([
    html.H1("EditWindow by Keo Chan"),
    dcc.Link(html.Button('MOST EDITS IN 2018: InternetArchiveBot', className='button1'), href='/page-1'),
    dcc.Link(html.Button('MOST EDITS IN 2018 (non-bot): EP111', className='button1'), href='/page-2'),
    dcc.Link(html.Button('EDIT FREQUENCY BY USER', className='button1'), href='/page-3'),
    dcc.Link(html.Button('EDIT LENGTH BY USER', className='button1'), href='/page-4')
])


page_1_layout = html.Div([
    html.H1('Most Edits in 2018'),
    dcc.Link(html.Button('Go back to home'), href='/'), html.Br(),
    html.Div(id='page-1-content'), html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker-range-1',
        min_date_allowed=dt(2001, 1, 15),
        max_date_allowed=dt.today(),
	start_date=dt(2018, 1, 1),
        end_date=dt(2018, 12, 31),
    ),
    html.H5("(Press page up/down to switch month quickly)"), html.Br(),
    html.Div(id='output-container-date-picker-range-1'), html.Br()
])
@app.callback(
    dash.dependencies.Output('output-container-date-picker-range-1', 'children'),
    [dash.dependencies.Input('my-date-picker-range-1', 'start_date'),
     dash.dependencies.Input('my-date-picker-range-1', 'end_date')])
def page_1_output(start_date, end_date):
    sql_query = "SELECT username, count(*) as frequency FROM revs WHERE lower(username) IS NOT NULL AND time BETWEEN "
    if start_date is not None and end_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime("'%Y-%m-%d'")
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime("'%Y-%m-%d'")
        sql_query = sql_query + start_date_string + " AND " + end_date_string + " GROUP BY username ORDER BY count(*) DESC LIMIT 10;"
    query_results=pd.read_sql_query(sql_query,con)
    revs = []
    for i in range(0,query_results.shape[0]):
        revs.append(dict(username=query_results.iloc[i]['username'], frequency=query_results.iloc[i]['frequency']))
    if len(sql_query) == 0:
        return 'Select a date to see it displayed here'
    else:
        return dcc.Graph(
	       id='example',
	       figure={
	           'data': [{'x': query_results['username'], 'y': query_results['frequency'], 'type': 'bar', 'name': 'Users'}],
	           'layout': {
	               'title': 'Most Edits',
	               'height': 700, 'width': 1200}
	           }
	       )

page_2_layout = html.Div([
    html.H1('Most Edits in 2018 (without bots)'),
    dcc.Link(html.Button('Go back to home'), href='/'), html.Br(),
    html.Div(id='page-2-content'), html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker-range-2',
        min_date_allowed=dt(2001, 1, 15),
        max_date_allowed=dt.today(),
        start_date=dt(2018, 1, 1),
        end_date=dt(2018, 12, 31)
    ),
    html.H5("(Press page up/down to switch month quickly)"), html.Br(),
    html.Div(id='output-container-date-picker-range-2'), html.Br()

])
@app.callback(
    dash.dependencies.Output('output-container-date-picker-range-2', 'children'),
    [dash.dependencies.Input('my-date-picker-range-2', 'start_date'),
     dash.dependencies.Input('my-date-picker-range-2', 'end_date')])
def page_2_output(start_date, end_date):
    sql_query_2 = "SELECT username, count(*) as frequency FROM revs WHERE lower(username) NOT LIKE '%bot%' AND time BETWEEN "
    if start_date is not None and end_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime("'%Y-%m-%d'")
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime("'%Y-%m-%d'")
        sql_query_2 = sql_query_2 + start_date_string + " AND " + end_date_string + " GROUP BY username ORDER BY count(*) DESC LIMIT 10;"
    query_results_2=pd.read_sql_query(sql_query_2,con)
    revs_2 = []
    for i in range(0,query_results_2.shape[0]):
        revs_2.append(dict(username=query_results_2.iloc[i]['username'], frequency=query_results_2.iloc[i]['frequency']))
    if len(sql_query_2) == 0:
        return 'Select a date to see it displayed here'
    else:
        return [sql_query_2,
                dcc.Graph(
                id='example',
                figure={
                    'data': [{'x': query_results_2['username'], 'y': query_results_2['frequency'], 'type': 'bar', 'name': 'Users'}],
                    'layout': {
                        'title': 'Most Edits (non-bot)',
                        'height': 700, 'width': 1200}
                    }
                )
        ]

page_3_layout = html.Div([
    html.H1('Frequency of edits by user'),
    dcc.Link(html.Button('Go back to home'), href='/'), html.Br(),
    html.Div(id='page-3-content'), html.Br(),
    dcc.Input(id='name-picker-3', type='text',value='cluebot ng'), html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker-range-3',
        min_date_allowed=dt(2001, 1, 15),
        max_date_allowed=dt.today(),
        start_date=dt(2008, 1, 1),
        end_date=dt(2018, 12, 31)
    ),
    html.Div(id='output-container-3'), html.Br(),
])
@app.callback(
    dash.dependencies.Output('output-container-3', 'children'),
    [dash.dependencies.Input('name-picker-3', 'value'),
     dash.dependencies.Input('my-date-picker-range-3', 'start_date'),
     dash.dependencies.Input('my-date-picker-range-3', 'end_date')])
def page_3_output(value, start_date, end_date):
    sql_query_3 = "SELECT CAST(time AS DATE), count(*) as frequency FROM revs WHERE lower(username) = lower('"
    if value is not None and start_date is not None and end_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime("'%Y-%m-%d'")
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime("'%Y-%m-%d'")
        sql_query_3 = sql_query_3 + str(value) + "') AND time BETWEEN " + start_date_string + " AND " + end_date_string + " GROUP BY CAST(time as DATE);"
    query_results_3=pd.read_sql_query(sql_query_3,con)
    revs_3 = []
    for i in range(0,query_results_3.shape[0]):
        revs_3.append(dict(username=query_results_3.iloc[i]['time'], frequency=query_results_3.iloc[i]['frequency']))
    if len(sql_query_3) == 0:
        return 'Select a date to see it displayed here'
    else:
        return [sql_query_3,
                dcc.Graph(
	            id='example3',
	    	    figure={
	                'data': [{'x': query_results_3['time'], 'y': query_results_3['frequency'], 'type': 'line', 'name': 'Users'}],
	                'layout': {
	                    'title': 'Frequency of edits by ' + str(value) + ' by date',
	                    'xaxis': {
	                       'type': 'date',
	                       'tickformat': '%Y-%m-%d',
	                       'tickmode': 'linear',
	                       'dtick': 86400000.0*29.5 #one day * x
	                    },
	                    'height': 700, 'width': 1200
			}
	            }
	        )
        ]


page_4_layout = html.Div([
    html.H1('Length of pages edited by user'),
    dcc.Link(html.Button('Go back to home'), href='/'), html.Br(),
    html.Div(id='page-4-content'), html.Br(),
    dcc.Input(id='name-picker-4', type='text',value='cluebot ng'), html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker-range-4',
        min_date_allowed=dt(2001, 1, 15),
        max_date_allowed=dt.today(),
        start_date=dt(2018, 1, 1),
        end_date=dt(2018, 12, 31)
    ),
    html.Div(id='output-container-4'), html.Br(),
])
@app.callback(
    dash.dependencies.Output('output-container-4', 'children'),
    [dash.dependencies.Input('name-picker-4', 'value'),
     dash.dependencies.Input('my-date-picker-range-4', 'start_date'),
     dash.dependencies.Input('my-date-picker-range-4', 'end_date')])
def page_4_output(value, start_date, end_date):
    sql_query_4 = "SELECT LENGTH(text) as length, count(*) as frequency FROM revs WHERE lower(username) = lower('"
    if value is not None and start_date is not None and end_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime("'%Y-%m-%d'")
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime("'%Y-%m-%d'")
        sql_query_4 = sql_query_4 + str(value) + "') AND time BETWEEN " + start_date_string + " AND " + end_date_string + " GROUP BY LENGTH(text);"
    query_results_4=pd.read_sql_query(sql_query_4,con)
    revs_4 = []
    for i in range(0,query_results_4.shape[0]):
        revs_4.append(dict(username=query_results_4.iloc[i]['length'], frequency=query_results_4.iloc[i]['frequency']))
    if len(sql_query_4) == 0:
        return 'Select a date to see it displayed here'
    else:
        return [sql_query_4,
                dcc.Graph(
                    id='example4',
                    figure={
                        'data': [{'x': query_results_4['length'], 'y': query_results_4['frequency'], 'type': 'line', 'name': 'Users'}],
                        'layout': {
                            'title': 'Length of edits by ' + str(value),
                            'xaxis': {'title': 'Number of characters in article'},
			    'yaxis': {'title': 'Number of edits'},
                            'height': 700, 'width': 1200
                        }
                    }
                )
        ]



# Pagenav callback
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    elif pathname == '/page-4':
        return page_4_layout
    else:
        return index_page


# Run with sudo python app2.py for port 80
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=80)