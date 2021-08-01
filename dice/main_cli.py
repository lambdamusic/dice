#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import click

from .app import utils 
from .app import main 




CMD_LINE_EXAMPLES = """USAGE EXAMPLES:
$ dice --test
// Build visualization using local test data

$ dice -k '"solar cells"' 
// Extract concepts from full-text search

$ dice -k '"Terry Riley" AND music' 
// NOTE use outer single quotes for exact phrase

$ dice -k '"solar cells"' -s 0.2 -f 2 -n 300
// Override default settings for score, frequency and nodes

$ dice 'search publications for "cancer" return publications[id+concepts] limit 500' 
// Full API DSL query using outer single quotes
"""




@click.command()
@click.argument('dslquery', nargs=-1)
@click.option('--examples', is_flag=True, help='Show some examples')
@click.option('--test', is_flag=True, help='Build visualization using local test data')
@click.option('--keywords', "-k", help='Keywords for a Dimensions full-text search. Top 1000 most cited publications are used to build the concepts map.')
@click.option('--score', "-s", help='Concept min score: default is 0.6')
@click.option('--freq', "-f", help='Concept min frequency: default is 3')
@click.option('--nodes', "-n", help='Network max nodes: default is 200')
@click.option('--edges', "-e", help='Network max edges: default is 300')
@click.pass_context
def main_cli(ctx,   dslquery=None, 
                    examples=False, 
                    test=False, 
                    keywords=None, 
                    score=None, 
                    freq=None, 
                    nodes=None, 
                    edges=None, 
                    verbose=True):
    """Bootstrap a concept map from a Dimensions API search, expressed either as a full DSL query (must return concepts data) or, using the -k option, as a series of keywordss."""

    if examples:
        click.secho(CMD_LINE_EXAMPLES, fg="green")
        return

    elif test:
        click.secho("Building test visualization..", fg="green")
        main.test_run()
        return

    elif keywords or dslquery:
        # main action

        if keywords:
            q = utils.dsl_generate_query_from_search_keywords(keywords)
            final_query = q

        elif dslquery:
            # the main arg
            final_query = dslquery[0]
            if verbose: click.secho("Q = " + dslquery[0], dim=True)


        df  =  main.build_viz(final_query, None, score, freq, nodes, edges)

        while True:
            # keep re-rendering using extracted data (only if params were not passed)
            if not (score and freq and nodes and edges):
                if click.confirm('-------------\n> Try again?'):
                    main.build_viz(final_query, [df], use_defaults=False)  
                else:
                    break

    else:
        click.echo(ctx.get_help())
        return



if __name__ == '__main__':
    main_cli()
