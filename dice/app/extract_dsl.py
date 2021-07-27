#!/usr/bin/python
# -*- coding: utf-8 -*-

import dimcli
import pandas as pd
import click

from .utils import *
from .settings import *
from .fmanager import FileManager



def is_valid_dsl(query):
    """Simple text check"""

    if not "return" in query:
        raise Exception("\n----\nYour DSL query does not include a `return` statement. Should end with: '.. return publications[id+concepts_scores]'")
    
    q = query.split("return")[1]

    if "concepts" in q:
        return True
    else:
        raise Exception("\n----\nYour DSL query does not return concepts. Should end with: '.. return publications[id+concepts_scores]'")



def run_dsl_query(query, fileManager=None, docache=False, verbose=True):
    """Return a Dimensions dataset from a DSL query. 

    Query must include concepts or concepts_scores in the return statement. 
    """

    if is_valid_dsl(query):
        
        if verbose: click.secho(f"Querying Dimensions API...: \'{query}\'", fg="green")
        dimcli.login(verbose=False)
        dsl = dimcli.Dsl()
        dsldata = dsl.query(query)
        if dsldata.errors:
            click.secho("---------")
            raise Exception("\n----\nYour DSL query contains an error. Please verify its syntax --> https://docs.dimensions.ai/dsl")

        if docache:
            # UNUSED
            if verbose: click.secho(f"Saving..", fg="green")
            fileManager.saveDslData(dsldata)

        # return dsldata

        if verbose: click.secho(f"Extracting concepts data...", fg="green")

        concepts_and_pubs = dsldata.as_dataframe_concepts()

        if verbose: print(concepts_and_pubs.describe())

        return concepts_and_pubs





def generate_test_dataset():
    """INTERNAL Util to export DSL query results locally for testing

    NOTE called from quicktest.py eg `dice_quicktest 2`

    Then can be used as 
    > df = pd.read_json("testdata/dsl_dataframe.json")

    """

    q = """search publications for "napoleon" return publications[id+concepts_scores] limit 500"""
    fm = FileManager()
    df = run_dsl_query(q, fm)
    df.to_json("testdata/dsl_dataframe.json")


