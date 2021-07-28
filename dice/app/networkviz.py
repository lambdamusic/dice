#!/usr/bin/python
# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader, select_autoescape

from .utils import *
from .settings import *
from .fmanager import FileManager

# set up jinja2
env = Environment(
    loader=PackageLoader('dice.media', 'templates-bs4'),
    autoescape=select_autoescape(['html', 'xml'])
)

TEMPLATE_DATA_FILE = "template-data.js"
TEMPLATE_HTML_FILE = "template-main.html"  # ==> NEWEST IN DEVELOPMENT


# EG HOW TO ADD CUSTOM FILTERS 

def tag_style(input_freqn):
    """Custom filter for styling concept tags from freq-normalised"""
    MIN_OPAC, MAX_OPAC = 50, 90
    if input_freqn < MIN_OPAC:
        font, opac = 70, MIN_OPAC
    elif input_freqn > MAX_OPAC:
        font, opac = 120, input_freqn
    else:
        font, opac = 90, input_freqn
    return f"font-size: {font}%; opacity: {opac}%;"

env.filters['tag_style'] = tag_style




class NetworkViz(object):
    """
    Class to render a html network vis.js page. 
    Reference: https://visjs.github.io/vis-network/examples/

    Requires a list of nodes and edges. 

    Data should look like this (minimally)

    nodes =  [{'id': 1, 'label': 'Knowledge Graphs'},
                {'id': 2, 'label': 'RDF'},
                {'id': "3", 'label': 'Linked Data'}]

    edges = [
        {'from': 1, 'to': "3"},
        {'from': 1, 'to': 2},
        {'from': "3", 'to': 2}
    ]


    """

    def __init__(self, fileManager, nodes=None, edges=None, title="", dslquery=""):
        """
        Init
        """
        super(NetworkViz, self).__init__()
        self.nodes = nodes or []
        self.edges = edges or []
        self.fm = fileManager
        self.template_js = TEMPLATE_DATA_FILE
        self.template_html = TEMPLATE_HTML_FILE
        self.query = dslquery
        self.query_keywords = dsl_extract_search_terms(dslquery)
        self.title = title or self.query_keywords or self.fm.timestamp
        self.final_url = "" # set after build

    def add_nodes(self, llist):
        self.nodes += llist

    def add_edges(self, llist):
        self.edges += llist


    def render_js(self, verbose=True, output_file="data.js"):
        """Renders the nodes and edges JSON data to a single JS file `data.js`

        Using https://jinja.palletsprojects.com/en/2.11.x/templates/?highlight=tojson#tojson

        Parameters
        ----------
        verbose : bool, optional
            Verbose mode, by default False

        Returns
        -------
        str
            The full path where the data is saved
        """

        template = env.get_template(self.template_js)
        render_filename = output_file

        context = {
            'NODES' : self.nodes,
            'EDGES' : self.edges,
        }

        # QA
        # for x in self.nodes:
        #     print(x)

        contents = template.render(context)

        loc = self.fm.save2File(contents, render_filename)
        if verbose: printDebug("=> Rendered data.js", "comment")
        return loc



    def render_html(self, filename="", verbose=True, preview=False):
        """Render thee HTML template file containing the visualization.

        Parameters
        ----------
        filename : str, optional
            The output filename, by default a unique timestamp DOT html.
        verbose : bool, optional
            Verbose messages, by default True
        preview : bool, optional
            Open in a web browser, by default False
        """

        template = env.get_template(self.template_html)
        render_filename = filename or self.fm.timestamp + ".html"

        context = {
            'title' : self.title,
            'query_keywords' : self.query_keywords,
            'query' : self.query,
            'timestamp' : self.fm.timestamp,
            'nodes' : self.nodes,
        }

        contents = template.render(context)
        
        # self.final_url = self.save2File(contents, render_filename, self.output_path)
        self.final_url = self.fm.save2File(contents, render_filename)
        if verbose: printDebug(f"=> Rendered {render_filename}", "comment")
        if verbose: printDebug("DONE - %s" % (self.final_url), "comment")

        self._render_static_files()

        if preview:
            self.preview()


    
    def _render_static_files(self):
        """Simply copy the static resources needed by the boostrap template
        """
        self.fm.copyDir(STATIC_FILES_SOURCE, subpath="static")



    def preview(self):
        if self.final_url:
            import webbrowser
            webbrowser.open(self.final_url)
        else:
            printDebug("Nothing to preview")




