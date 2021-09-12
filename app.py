import dash
from dash.dependencies import Output,Input,State
from dash import dcc
from dash import html
from datetime import date
import yfinance as yf
import pandas as pd
import plotly.express as px

from model import prediction


external_stylesheets=["/assets/styles.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

app.layout = html.Div([
    html.Div(
        [
            html.P("Welcome to the Stock Dash App!",className="start"),
            html.Div([    
                # stock code input
                html.P("Input stock code:",id="stockText"),
                html.Div([
                    dcc.Input(
                    placeholder= "Stock Code",
                    type = "text",
                    id ="stockcode"
                ),
                html.Button("Submit",id="submit")
                ],className="form")
            ],className="stockCode"),
            
            html.Div([
                # Date Range picker input
                dcc.DatePickerRange(id="date-picker",
                    min_date_allowed=date(1995,1, 1),
                    max_date_allowed=date.today(),
                    initial_visible_month=date.today(),
                    end_date=date.today(),
                )
            ],className="datepicker"),
            html.Div([
                # Stock price button
                html.Button("Stock Price",className="stockbutton",id="stock-button"),
                # Indicators button
                html.Button("Indicators",className="indicatorbutton",id="indicators-button"),
                # Number of days of forecast
                dcc.Input(
                    placeholder="number of days",
                    type="text",
                    id="input-Forcast"
                ),
                # Forecast button
                html.Button("Forcast",className="forcastbutton",id="forcast-button")
            ],className="buttons"),
        ],
        className="nav"
    ),

    html.Div(
        [
            html.Div(
                [ #Logo
                    html.Img(id="logo"),
                  # Company Name
                    html.P(id="name"),    
                ],
                className="header"),
                html.Div( #Description
                    id="description",className="description_ticker"),
                html.Div([
                    # Stock Price plot
                ], id="graph-content"),
                html.Div([
                    # Indicator plot
                ], id="main-content"),
                html.Div([
                    # Forcast plot
                ],id="forcast-content")
        ],
        className="content")
],className="container")

@app.callback([
    Output("description", "children"),
    Output("logo","src"),
    Output("name","children"),
    Output("stock-button","n_clicks"),
    Output("indicators-button","n_clicks"),
    Output("forcast-button","n_clicks")
    ],
    [
    Input("submit","n_clicks")
    ],
    [
    State("stockcode", "value")
    ])
def update_data(name,code):  # input parameter(s)
    # your function here
    if code == None:
        return "This is a single-page web application using Dash (a python framework) which will show company information (logo, registered name and description) and stock plots based on the stock code given by the user. Also it contains an ML model will enable the user to get predicted stock prices for the date inputted by the user.","https://www.aegonlife.com/insurance-investment-knowledge/wp-content/uploads/2019/08/shutterstock_601834022.jpg","Stock Prediction",None,None,None
    ticker = yf.Ticker(code)
    inf = ticker.info
    df = pd.DataFrame().from_dict(inf, orient="index").T
    return df["longBusinessSummary"].values[0], df["logo_url"].values[0], df["shortName"].values[0],None,None,None

@app.callback([
    Output("graph-content","children")
    ],
    [
    Input("stock-button","n_clicks"),
    Input("date-picker","start_date"),
    Input("date-picker","end_date"),
    ],
    [State("stockcode","value")]
    )

def graph_plot(n,startdate,enddate,code):
    if n==None:
        return[""]
    if code == None:
        return [""]
    else:
        if startdate != None:
            df = yf.download(code, str(startdate), str(enddate))
        else:
            df = yf.download(code)
    df.reset_index(inplace=True)
    fig=get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]

def get_stock_price_fig(df):
    fig=px.line(df,x="Date",y=["Close","Open"],title="Closing and Opening Price vs Date")
    return fig

@app.callback([
    Output("main-content","children")
    ],
    [
    Input("indicators-button","n_clicks"),
    Input("date-picker","start_date"),
    Input("date-picker","end_date")
    ],
    [
    State("stockcode","value")
    ]
)

def ind_plot(n,startdate,enddate,code):
    if n== None:
        return[""]
    if code == None:
        return [""]
    if startdate != None:
        df = yf.download(code, str(startdate), str(enddate))
    else:
        df = yf.download(code)
    df.reset_index(inplace=True)
    fig=get_mode(df)
    return [dcc.Graph(figure=fig)]

def get_mode(df):
    df["EWA_20"]=df['Close'].ewm(span=20,adjust=False).mean()
    fig=px.scatter(df,
        x="Date",
        y="EWA_20",
        title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback([Output("forcast-content", "children")],
              [Input("forcast-button", "n_clicks")],
              [State("input-Forcast", "value"),
               State("stockcode", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        return [""]
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)