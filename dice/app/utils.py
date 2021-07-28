import click
import sys
import pandas as pd

# Fix Python 2.x.
try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = lambda s: str(s)


def printDebug(text, mystyle="", **kwargs):
    """
    util for printing in colors using click.secho()

    :kwargs = you can do printDebug("s", bold=True)

    2018-12-06: by default print to standard error (err=True)

    Styling output:
    <http://click.pocoo.org/5/api/#click.style>
    Styles a text with ANSI styles and returns the new string. By default the styling is self contained which means that at the end of the string a reset code is issued. This can be prevented by passing reset=False.

    Examples:

    click.echo(click.style('Hello World!', fg='green'))
    click.echo(click.style('ATTENTION!', blink=True))
    click.echo(click.style('Some things', reverse=True, fg='cyan'))
    Supported color names:

    black (might be a gray)
    red
    green
    yellow (might be an orange)
    blue
    magenta
    cyan
    white (might be light gray)
    reset (reset the color code only)
    New in version 2.0.

    Parameters:
    text – the string to style with ansi codes.
    fg – if provided this will become the foreground color.
    bg – if provided this will become the background color.
    bold – if provided this will enable or disable bold mode.
    dim – if provided this will enable or disable dim mode. This is badly supported.
    underline – if provided this will enable or disable underline.
    blink – if provided this will enable or disable blinking.
    reverse – if provided this will enable or disable inverse rendering (foreground becomes background and the other way round).
    reset – by default a reset-all code is added at the end of the string which means that styles do not carry over. This can be disabled to compose styles.

    """

    if mystyle == "comment":
        click.secho(text, dim=True, err=True)
    elif mystyle == "important":
        click.secho(text, bold=True, err=True)
    elif mystyle == "normal":
        click.secho(text, reset=True, err=True)
    elif mystyle == "red" or mystyle == "error":
        click.secho(text, fg='red', err=True)
    elif mystyle == "green":
        click.secho(text, fg='green', err=True)
    else:
        click.secho(text, **kwargs)




def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    import unicodedata, re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value.decode()).strip().lower())
    value = re.sub('[-\s]+', '-', value)
    return value



def safe_str(u, errors="replace"):
    """Safely print the given string.

    If you want to see the code points for unprintable characters then you
    can use `errors="xmlcharrefreplace"`.
    http://code.activestate.com/recipes/576602-safe-print/
    """
    s = u.encode(sys.stdout.encoding or "utf-8", errors)
    return s




def print_stats_score(concepts_unique):
    """From a concepts_unique dataframe, print out useful stats.

    Parameters
    ----------
    concepts_unique : pandas.DataFrame
        concepts_unique dataframe
    """    

    c = concepts_unique
    click.secho(f"""Total number of concepts: 
        {len(c)}""")

    # score bins
    filter_values = [0, 0.5, 0.6, 0.8, 0.9, 1]  
    out = pd.cut(c.score_avg, bins=filter_values)
    counts = pd.value_counts(out).sort_index().to_list()

    click.secho(f"""Score distribution (min={c.score_avg.min()} max={c.score_avg.max()} mean={"%.2f" % c.score_avg.mean()}):""")
    for n,v in enumerate(filter_values):
        if n < len(counts): # because filter values are taken two at a time
            click.secho(f"""\t{filter_values[n]}-{filter_values[n+1]}: {counts[n]}""")



def print_stats_freq(concepts_unique):
    """From a concepts_unique dataframe, print out useful stats.

    Parameters
    ----------
    concepts_unique : pandas.DataFrame
        concepts_unique dataframe
    """    

    c = concepts_unique
    click.secho(f"""Total number of concepts: 
        {len(c)}""")

    # freq bins
    filter_values = [0, 1, 2, 3, 4, 5, c.frequency.max()]  
    out = pd.cut(c.frequency, bins=filter_values)
    counts = pd.value_counts(out).sort_index().to_list()

    click.secho(f"""Frequency distribution (min={c.frequency.min()} max={c.frequency.max()}): 
        1: {counts[0]} concepts
        2: {counts[1]}
        3: {counts[2]}
        4: {counts[3]}
        5: {counts[4]}
        6-{c.frequency.max()}: {counts[5]}""")




def print_parameters(min_score, min_freq, min_edge_weight):
    """Prints out parameters used for the dataviz"""

    # average no of concepts per document
    click.secho(f"""**Filter parameters """)
    click.secho(f"""min_score: {min_score}""")
    click.secho(f"""min_freq: {min_freq}""")
    click.secho(f"""min_edge_weight: {min_edge_weight}""")




def dsl_search_term_from_query(dslquery):
    """Return the keyword search parameter from a DSL query

    Parameters
    ----------
    dslquery : string
        Full DSL query eg 'search publications for "napoleon" return publications[id+concepts_scores] limit 500'
    """
    #TODO improve
    l = dslquery.split()
    candidates = l[l.index("for")+1:l.index("return")]
    return " ".join(candidates)




# import json
# "{json.dumps(keywords)}" 

def dsl_generate_query_from_search_keywords(keywords):
    """Auto generate a valid DSL query"""
    # print(keywords)
    newk = keywords.replace('"', '\\"')
    # print(newk)
    q = f"""search publications 
        for "{newk}" 
        where concepts is not empty
        return publications[id+concepts_scores] 
        sort by times_cited limit 500"""
    return q 
