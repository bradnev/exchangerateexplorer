import pymongo
import ssl #SSL does not work properly.  We will have an insecure connection but I do not care.
import time
import pandas as pd
import plotly.express as px
from dash import Dash, html, dash_table, dcc

app = Dash(__name__)
server = app.server

while 0==0:

    uri = "mongodb+srv://robertneville083:h@cluster0.i6sbepa.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri, ssl_cert_reqs=ssl.CERT_NONE)
    
    db = client.currency
    collection = db.currency #enter the collection
    df = pd.DataFrame(list(collection.find({}))) #Convert MongoDB database into Pandas Dataframe.
    df["Percent Difference From 30 Day Average"] = 100 * (df["Exchange Rate (1 USD)"] - df["30 Day Average"])/df["30 Day Average"]
    df["Percent Difference From 90 Day Average"] = 100 * (df["Exchange Rate (1 USD)"] - df["90 Day Average"])/df["90 Day Average"]
    fig = px.bar(df, x="Currency", y="90 Day Volatility")
    fig2 = px.bar(df, x="Currency", y="Percent Difference From 90 Day Average")
    app.layout = html.Div([
        html.H1(children='Currency Exchange Information'),
        html.P(children='Sourced From xe.com'),
        dash_table.DataTable(data=df.to_dict('records'), page_size=10),
        dcc.Graph(id='graph1',figure=fig),
        dcc.Graph(id='graph2',figure=fig2)
    ])

    if __name__ == '__main__':
        app.run_server(port = 2223, debug=False) #Note port errors exist, 2223 is free for me but the default was not.
    
    time.sleep(60*60*24) #1 day wait
