import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from examples.heartbeat_rest_ui import alicia
from examples.heartbeat_rest_ui import enrico
from examples.heartbeat_rest_ui import bob
from examples.heartbeat_rest_ui.app import app

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.Div([
        html.Img(src='./assets/nucypher_logo.png'),
    ], className='banner'),
    html.A('ALICIA', href='/alicia', target='_alicia'),
    html.Br(),
    html.A('ENRICO (HEART_MONITOR)', href='/enrico', target='_enrico'),
    html.Br(),
    html.A('BOB', href='/bob', target='_bob'),
    html.Br(),
    html.Hr(),
    html.H2('Overview'),
    html.Div([
        html.Img(src='./assets/heartbeat_demo_overview.png'),
    ], className='overview')
])

# This is used to ensure that the first Bob is the 'Doctor'
# Subsequent Bob's can be other professions eg. Nutritionist, Dietitian etc.
first_bob_already_created = list()


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/alicia':
        return alicia.layout
    elif pathname == '/enrico':
        return enrico.layout
    elif pathname == '/bob':
        if not first_bob_already_created:
            first_bob_already_created.append(True)
            return bob.get_layout(True)
        else:
            return bob.get_layout(False)
    else:
        return index_page


if __name__ == '__main__':
    app.run_server()
