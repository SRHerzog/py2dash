import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
from dash.dependencies import Output, Input

from py2dash import component_makers as cm


def dispatch_func_to_app(app, func):
    func_mint = cm.dash_mint_for_func(func)
    app.callback(Output(**func_mint['output_callback_spec']),
                 list(map(lambda x: Input(**x), func_mint['input_callback_specs'])))(func)


def dispatch_funcs_to_app(app, funcs):
    for func in funcs:
        dispatch_func_to_app(app, func)


def dispatch_funcs(funcs):
    app = dash.Dash(
        __name__,
        external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
    )

    url_bar_and_content_div = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    def page_of_func(func=None):
        if func is not None:
            return f"/{func.__name__}"
        else:
            return '/'

    layout_for_page = dict()
    layout_for_page['/'] = html.Div(children=[], id='/-div')

    for func in funcs:
        func_mint = cm.dash_mint_for_func(func)
        page = page_of_func(func)
        layout_for_page.update(
            {page: html.Div(func_mint['input_divs'] + [func_mint['output_div']],
                            id=func_mint['func_id'])})

    pages = list(layout_for_page.keys())
    for page, v in layout_for_page.items():
        v.children.extend(cm.mk_navigation_links_div_list(cm.list_diff(pages, page),
                                                          link_str_for=lambda x: f"{x}-div"))

    layout_for_page['url_bar_and_content_div'] = url_bar_and_content_div

    def serve_layout():
        if flask.has_request_context():
            return layout_for_page['url_bar_and_content_div']
        return html.Div(list(layout_for_page.values()))

    app.layout = serve_layout

    dflt_layout = layout_for_page['/']

    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        return layout_for_page.get(pathname, dflt_layout)

    dispatch_funcs_to_app(app, funcs)

    return app