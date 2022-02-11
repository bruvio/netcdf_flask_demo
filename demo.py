import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


app = dash.Dash(name="EFIT_DEMO")
                
DATA = pd.read_csv('demo.txt', sep=';')


def create_figure(column_x, column_y):
    return px.scatter(DATA,x=column_x,y=column_y)
    
app.layout = html.Div([
                       html.Button(" add new scatter plot", id="scatter_plot", n_clicks=0),
                       html.Div(),
                       html.Div(id='new_scatter_plot', children=[]) 
                     ])

@app.callback( Output('new_scatter_plot', 'children'),
               [Input('scatter_plot', 'n_clicks')],
               [State('new_scatter_plot', 'children')])

def ajouter_graphe(n_clicks, children):
    
    new_scatter_plot = html.Div(
        style={'width': '23%', 'display': 'inline-block', 'outline': 'thin lightgrey solid', 'padding': 10},
        children=[
                  dcc.Graph(
                            id ={'type': 'Scatter_Plot',
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
    children.append(new_scatter_plot)
    return children
 
@app.callback( Output({'type':'Scatter_Plot', 'index':MATCH},'figure'),
              [Input({'type':'Selection_variable_X', 'index':MATCH}, 'value'),
               Input({'type':'Selection_variable_Y', 'index':MATCH}, 'value')]              
             )
def display_output(column_x,column_y):
    if column_x is None and column_y is None:
        raise dash.exceptions.PreventUpdate
    return create_figure(column_x, column_y)
  


if __name__ == '__main__':
    app.run_server(debug=True)