#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
simple test queries [for DEVELOPMENT  / not part of official tests]
"""

import click

from ..app.settings import FileManager
from ..app.dsl import *
from ..app.transform import *
from ..app.networkviz import *



@click.command()
@click.argument('test_number')
def quicktest_cli(test_number=1):

    test_number = int(test_number)
    fm = FileManager()

    if test_number == 1:
        # TEST run a DSL query

        q = """search publications for "napoleon" return publications[id+concepts_scores] limit 400"""
        # quotes have to be escaped the Python way
        q = """search publications for "\\\"super bug\\\"" return publications[id+concepts_scores] limit 400"""
        df = run_dsl_query(q, fm)

    if test_number == 2:
        # TEST cache DSL query for test dataset  
        # Then can be used as 
        # > df = pd.read_json("testdata/dsl_dataframe.json")

        generate_test_dataset()

    if test_number == 3:
        # TEST prune concepts from cached df-dsl data  
        df = pd.read_json("testdata/dsl_dataframe.json")
        prune_concepts(df)

    if test_number == 4:
        # TEST dsl_to_networkx from cached df-dsl data  
        df = pd.read_json("testdata/dsl_dataframe.json")
        dsl_to_networkx(prune_concepts(df))

    if test_number == 5:
        # TEST networkx_to_dict from cached df-dsl data  
        df = pd.read_json("testdata/dsl_dataframe.json")
        networkx_to_dict(dsl_to_networkx(prune_concepts(df)))



# if __name__ == '__main__':
#     quicktest()
