from twisted.logger import Logger

from constant_sorrow.constants import NO_KNOWN_NODES

from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, Event
import dash_table

from flask import Flask

from nucypher.characters.lawful import Ursula


class NetworkStatus:
    def __init__(self,
                 title: str,
                 flask_server: Flask,
                 route_url: str,
                 *args,
                 **kwargs) -> None:
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.log = Logger(self.__class__.__name__)

        self.dash_app = Dash(__name__,
                             server=flask_server,
                             url_base_pathname=route_url,
                             external_stylesheets=external_stylesheets)
        self.dash_app.title = title


class MoeStatus(NetworkStatus):
    """
    Status app for 'Moe' monitoring nodes.
    """
    def __init__(self,
                 moe,
                 known_node: Ursula,
                 title: str,
                 flask_server: Flask,
                 route_url: str,
                 *args,
                 **kwargs) -> None:
        NetworkStatus.__init__(self, title, flask_server, route_url, args, kwargs)

        self.dash_app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='header'),
            html.Div(id='fleet-state', style={'backgroundColor': '#D9D9D9'}),
            html.Div(id='known-nodes'),
            dcc.Interval(id='status-update', interval=1000, n_intervals=0),
        ])

        @self.dash_app.callback(Output('header', 'children'),
                                [Input('url', 'pathname')])
        def header(pathname):
            return html.Div([
                html.Div('WARNING: Do not use checksum addressees found on this page for any transaction '
                         'of any kind or the funds will be irreversibly destroyed.',
                         style={'color': 'red', 'font-style': 'bold'},
                         className='row'),
                html.Div([
                    html.Div([
                        html.Img(src="/assets/nucypher_logo.png"),
                    ], className='banner'),
                    html.Div([
                        html.H2("Monitoring Application", className='app_name'),
                    ], className='row')
                ]),
                html.Hr(),
            ])

        @self.dash_app.callback(
            Output('fleet-state', 'children'),
            [Input('header', 'children')],
            events=[Event('status-update', 'interval')]
        )
        def fleet_state(header):
            fleet_state_dict = dict()
            if known_node.fleet_state_checksum is not NO_KNOWN_NODES:
                fleet_state_dict['Checksum'] = known_node.fleet_state_checksum[0:8]
            else:
                fleet_state_dict['Checksum'] = known_node.fleet_state_checksum

            fleet_state_dict['Timestamp'] = known_node.fleet_state_updated.rfc3339()
            fleet_state_dict['Name'] = known_node.fleet_state_nickname
            fleet_state_dict['Icon'] = '{}'.format(known_node.nickname_metadata[0][1])
            divs = list()

            divs.append(html.H2("Fleet State"))

            for key in fleet_state_dict:
                div = html.Div([
                    html.Div([
                        html.Strong([key])
                    ], className="two columns right-aligned"),
                    html.Div([
                        html.Div(fleet_state_dict[key])
                    ], className="ten columns")
                ], className="row")

                divs.append(div)

            return divs

        @self.dash_app.callback(
            Output('known-nodes', 'children'),
            [Input('fleet-state', 'children')],
            events=[Event('status-update', 'interval')]
        )
        def known_nodes(fleet_state):
            columns = ['Icon', 'Identity', 'Timestamp', 'Last Seen', 'Fleet State']

            nodes = list()

            nodes_dict = moe.known_nodes.abridged_nodes_dict()
            teacher_node = moe.current_teacher_node()
            teacher_index = None
            for checksum in nodes_dict:
                node_data = nodes_dict[checksum]
                node_dict = dict()
                node_dict[columns[0]] = '{} {}'.format(node_data["nickname_metadata"][0][1],
                                                       node_data["nickname_metadata"][1][1])
                node_dict[columns[1]] = node_data["nickname"]
                node_dict[columns[2]] = node_data["timestamp"]
                node_dict[columns[3]] = node_data["last_seen"]
                node_dict[columns[4]] = node_data["checksum_address"][0:10]

                if node_data['checksum_address'] == teacher_node.checksum_public_address:
                    teacher_index = len(nodes)

                nodes.append(node_dict)

            return html.Div([
                html.H2('Network Nodes'),
                html.Div([
                    html.Div('* Current Teacher',
                             style={'backgroundColor': '#1E65F3', 'color': 'white'},
                             className='two columns'),
                ], className='row'),
                html.Br(),
                dash_table.DataTable(
                    id='node-table',
                    columns=[{"name": i, "id": i} for i in columns],
                    data=nodes,
                    style_table={
                        'overflowY': 'scroll'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'minWidth': '0px',
                        'maxWidth': '200px',
                        'whiteSpace': 'no-wrap',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                    style_data_conditional=[{
                        "if": {"row_index": teacher_index},
                        "backgroundColor": "#1E65F3",
                        'color': 'white'
                    }]
                )
            ], className='row')
