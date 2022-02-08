import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


app = dash.Dash(name="EFIT_DEMO")
                
DATA = pd.read_csv('demo.txt', sep=';')
print(DATA)

#graphe_test= px.scatter(DATA,x=DATA.x,y=DATA.y)               


def create_figure(column_x, column_y):
    return px.scatter(DATA,x=column_x,y=column_y)
    
app.layout = html.Div([
                       html.Button(" + Add scatter plot", id="add-scatter-plot", n_clicks=0),
                       html.Div(),
                       html.Div(id='scatter-plot', children=[]) 
                     ])

@app.callback( Output('scatter-plot', 'children'),
               [Input('add-scatter-plot', 'n_clicks')],
               [State('scatter-plot', 'children')])

def ajouter_graphe(n_clicks, children):
    
    nouvelle_zone_graphe = html.Div(
        style={'width': '23%', 'display': 'inline-block', 'outline': 'thin lightgrey solid', 'padding': 10},
        children=[
                  dcc.Graph(
                            id ={'type': 'scatter-plot',
                                 'index': n_clicks}
                            ),
                  
                  dcc.Dropdown(
                               id={
                                   'type':'Selection_variable_X',
                                   'index': n_clicks
                                   },
                               options=[{'label':i, 'value':i} for i in DATA.columns],
                               value = None
                              ),
                  
                  dcc.Dropdown(
                               id={
                                   'type':'Selection_variable_Y',
                                   'index': n_clicks
                                   },
                               options=[{'label':i, 'value':i} for i in DATA.columns],
                               value = None
                              ), 
                 ])
    children.append(nouvelle_zone_graphe)
    return children
 
@app.callback( Output({'type':'add-scatter-plot', 'index':MATCH},'figure'),
              [Input({'type':'Selection_variable_X', 'index':MATCH}, 'value'),
               Input({'type':'Selection_variable_Y', 'index':MATCH}, 'value')]              
             )
def display_output(column_x,column_y):
    if column_x is None and column_y is None:
        raise dash.exceptions.PreventUpdate
    return create_figure(column_x, column_y)

  


if __name__ == '__main__':
    app.run_server(debug=True)