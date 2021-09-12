def prediction(code, noDays):
    import dash
    from dash.dependencies import Output,Input,State
    import dash_core_components as dcc
    import dash_html_components as html
    from datetime import date,timedelta
    from datetime import datetime as dt
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import plotly.graph_objs as go
    import plotly.express as px
    from yfinance.multi import download
    from sklearn.model_selection import train_test_split
    from sklearn.model_selection import GridSearchCV
    from sklearn.svm import SVR

    
    df= yf.download(code,period='60d')
    df.reset_index(inplace=True)
    df['Day'] = df.index

    days = list()
    for i in range(len(df.Day)):
        days.append([i])

    #splitting
    X=days
    y=df[['Close']]
    x_train,x_test,y_train,y_test= train_test_split(X,y,test_size=0.2,shuffle=False)

    
    gsc = GridSearchCV(
        estimator=SVR(kernel='rbf'),
        param_grid={
            'C': [0.001, 0.01, 0.1, 1, 100, 1000],
            'epsilon': [
                0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10,
                50, 100, 150, 1000
            ],
            'gamma': [0.0001, 0.001, 0.005, 0.1, 1, 3, 5, 8, 40, 100, 1000]
        },
        cv=5,
        scoring='neg_mean_absolute_error',
        verbose=0,
        n_jobs=-1)
    y_train = y_train.values.ravel()
    y_train
    grid_result = gsc.fit(x_train, y_train)
    best_params = grid_result.best_params_
    best_svr = SVR(kernel='rbf',
                   C=best_params["C"],
                   epsilon=best_params["epsilon"],
                   gamma=best_params["gamma"],
                   max_iter=-1)
    svr_rbf=best_svr
    svr_rbf.fit(x_train,y_train)

    output_days = list()
    for i in range(1, noDays):
        output_days.append([i + x_test[-1][0]])

    dates = []
    current = date.today()
    for i in range(noDays):
        current += timedelta(days=1)
        dates.append(current)

    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,  # np.array(tenDays).flatten(), 
            y=svr_rbf.predict(output_days),
            mode='lines+markers',
            name='data'))
    fig.update_layout(
        title="Predicted Close Price of next " + str(noDays - 1) + " days",
        xaxis_title="Date",
        yaxis_title="Closed Price",
       
    )

    return fig
