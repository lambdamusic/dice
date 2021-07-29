
import sys
import click

from .networkviz import *
from .extract_dsl import *
from .transform import *
from .fmanager import FileManager
from . import settings





def build_viz(dslquery, cached_data=None, score=None, freq=None, nnodes=None, nedges=None, use_defaults=True):
    
    fm = FileManager()

    if not (score and freq) and use_defaults:
        # NOTE if all false, apply defaults
        score, freq  = MIN_CONCEPTS_SCORE_DEFAULT, MIN_CONCEPTS_FREQ_DEFAULT

    if not cached_data:
        df = run_dsl_query(dslquery, fm)
    else:
        df = cached_data[0]

    nnodes = nnodes or MAX_NETWORK_NODES_DEFAULT
    nedges = nedges or MAX_NETWORK_EDGES_DEFAULT
    
    dfpruned = prune_concepts(df, score, freq)
    ngraph = dsl_to_networkx(dfpruned, nnodes, nedges)
    nodes, edges = networkx_to_dict(ngraph)

    if len(nodes) and len(edges):

        n = NetworkViz(fileManager=fm, dslquery=dslquery)
        n.add_nodes(nodes)
        n.add_edges(edges)
        n.render_data_export(ngraph)
        n.render_js()
        n.render_html(preview=True)

    else:
        click.secho("Nothing to show.")

    return df





def test_run(filename="testdata/dsl_dataframe.json", score=0.5, freq=2):
    """Takes local JSON data from cached DSL query and build a viz with it.
    """
    fm = FileManager()

    df = pd.read_json(filename)
    # the query corresponding to the cached data
    dslquery = """search publications for "napoleon" return publications[id+concepts_scores] limit 500"""

    dfpruned = prune_concepts(df, score, freq)
    ngraph = dsl_to_networkx(dfpruned)
    nodes, edges = networkx_to_dict(ngraph)

    if len(nodes) and len(edges):

        n = NetworkViz(fileManager=fm, dslquery=dslquery)
        n.add_nodes(nodes)
        n.add_edges(edges)
        n.render_data_export(ngraph)
        n.render_js()
        n.render_html(preview=True)

    else:
        click.secho("Nothing to show.")