#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import click

from .app import networkviz 
from .app import main 




CMD_LINE_EXAMPLES = """USAGE EXAMPLES:
$ dice --test
// Run test with local data

$ dice -k "solar cells" -s 0.6 -f 2 -e 2
// keywords search: defaults to 500 top records

$ dice 'search publications for "cancer" return publications[id+concepts] limit 500' -f 2 -s 0.5 -e 3
// Full DSL query using outer single quotes

$ dice 'search publications for "\"brain cancer\"" return publications[id+concepts] limit 500' -f 2 -s 0.7 -e 3
// Full DSL query with escaped inner quotes 
"""




@click.command()
@click.argument('dslquery', nargs=-1)
@click.option('--examples', is_flag=True, help='Show some examples')
@click.option('--test', is_flag=True, help='Test network viz using local data')
@click.option('--queryprompt', "-q",  is_flag=True, help='Interactive query prompt (easier for quoted text)')
@click.option('--keywords', "-k", help='Keywords to search in publications full text - defaults to 500 publications')
@click.option('--score', "-s", help='Score threshold: 0 to 1')
@click.option('--freq', "-f", help='Frequency threshold: 1 to 20')
@click.option('--edgeweight', "-e", help='Edges weight threshold: 1 to X')
@click.pass_context
def main_cli(ctx,   dslquery=None, 
                    examples=False, 
                    test=False, 
                    queryprompt=None, 
                    keywords=None, 
                    score=None, 
                    freq=None, 
                    edgeweight=None, 
                    verbose=True):
    """Main CLI."""

    if examples:
        click.secho(CMD_LINE_EXAMPLES, fg="green")
        return

    elif test:
        click.secho("Building test visualization..", fg="green")
        main.test_run()
        return

    elif keywords or queryprompt or dslquery:
        # main action

        if keywords:
            q = f'search publications for "{keywords}" return publications[id+concepts_scores] sort by times_cited limit 500'
            final_query = q
            if verbose: click.secho("Q = " + q, dim=True)

        elif dslquery:
            # the main arg
            final_query = dslquery[0]
            if verbose: click.secho("Q = " + dslquery[0], dim=True)

        elif queryprompt:
            final_query = click.prompt('> Please enter a DSL query:\n')

        df  =  main.build_viz(final_query, None, score, freq, edgeweight)

        while True:
            # keep re-rendering using extracted data (only if params were not passed)
            if not (score and freq and edgeweight):
                if click.confirm('> Try again?'):
                    main.build_viz(final_query, [df])  # as list to allow boolean check
                else:
                    break

    else:
        click.echo(ctx.get_help())
        return



if __name__ == '__main__':
    main_cli()
