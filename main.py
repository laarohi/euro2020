import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly
from dash.dependencies import Input, Output
from euro_prediction import Tournament

#------------------------------ LOAD DATA ------------------------------- #

tournament = Tournament('./', 'https://www.livescores.com/soccer/euro-2020/')

# ----------------------------- DASH ---------------------------------- #


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app  = dash.Dash(__name__ , external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True


# -------------------------- PROJECT DASHBOARD ---------------------------- #

app.layout = html.Div(
    html.Div([
        html.H1('CxF Euro 2020 Pools',
                style={
                    "width": "100%",
                    "text-align": "center",
                    "padding-top": "2%",
                    },
                ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Standings",
                    children=[
                        html.H2(
                            "Standings",
                            style={
                                "width": "100%",
                                "text-align": "center",
                                "padding-top": "3%",
                            },
                        ),
						dash_table.DataTable(
							id='scoring-table',
						),
					]
				),
                dcc.Tab(
                    label="Upcoming Predictions",
                    children=[
                        html.H2(
                            "Upcoming Predictions",
                            style={
                                "width": "100%",
                                "text-align": "center",
                                "padding-top": "3%",
                            },
                        ),
						dash_table.DataTable(
							id='pred-table',
							),
                        ]
                    ),
                ]
            ),
					
				
        dcc.Interval(
            id='scoring-interval-component',
            interval=1*60*1*1000, # in milliseconds
            n_intervals=0
        ),
        dcc.Interval(
            id='pred-interval-component',
            interval=24*60*60*1*1000, # in milliseconds
            n_intervals=0
        ),

    ])
    )


# Multiple components can update everytime interval gets fired.
@app.callback([
              Output('scoring-table', 'data'),
              Output('scoring-table', 'columns'),
              ],
              Input('scoring-interval-component', 'n_intervals'))
def update_scoring_live(n):
    tournament.reload()
    df = tournament.standings
    df.index.name = 'Name'
    df = df.loc[:, (df.sum() > 0)]
    df = df.reset_index(col_fill=None)
    df.columns = df.columns.droplevel(0)
    df['Total'] = df.sum(axis=1)
    df = df.sort_index().sort_values('Total', ascending=False)
    df['Ranking'] = df.Total.rank(method='min', ascending=False)
    df = df[['Ranking'] + list(df.columns)[:-1]]
    data = df.to_dict('records')
    columns=[{'name': x, 'id': x} for x in df.columns]
    return data, columns


# Multiple components can update everytime interval gets fired.
@app.callback([
              Output('pred-table', 'data'),
              Output('pred-table', 'columns'),
              ],
              Input('pred-interval-component', 'n_intervals'))
def update_pred_live(n):
    df = tournament.predicted_scores
    df.index.name = 'Name'
    df = df.reset_index()
    data = df.to_dict('records')
    columns=[{'name': x, 'id': x} for x in df.columns]
    return data, columns

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
