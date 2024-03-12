"""
Plotter
"""

import pandas as pd
import os
import toml
import sqlite3
from matplotlib import pyplot as pp

this_dir = os.path.realpath(os.path.dirname(__name__)) + "/"
config_dir = this_dir + "config/"
out_dir = this_dir + "output_tables/"
sqlite_dir = this_dir + "input_sqlite/"

config = toml.load(config_dir + 'config.toml')

if config['input_sqlite_directory'] != '': sqlite_dir = config['input_sqlite_directory']
if config['output_tables_directory'] != '': out_dir = config['output_tables_directory']



def aggregate_by_database():

    df_cat = pd.read_csv(config_dir + 'categories.csv')
    df_cat = df_cat.loc[df_cat['run']]

    for _idx, cat_config in df_cat.iterrows():

        db = sqlite_dir + f"{cat_config['database']}.sqlite"

        aggregate_category(cat_config, db)
    
    pp.show()
        
        

def aggregate_category(cat_config, db):

    conn = sqlite3.connect(db)

    df_table = pd.read_csv(config_dir + f"{cat_config['table']}.csv")
    df_table = df_table.loc[df_table['include']]

    if cat_config['category'] not in df_table['category'].values:
        print(f"Tried to aggregate from table {cat_config['table']} for {cat_config['category']} but no corresponding rows were found!")

    df_cat = df_table.loc[df_table['category'] == cat_config['category']].drop('category', axis=1).groupby('aggregate')
    data = []

    for agg in df_cat.groups:
        
        df_agg = df_cat.get_group(agg).iloc[:,3:]

        for _idx, row in df_agg.iterrows():
            
            command = f"SELECT * FROM {config['tables'][cat_config['table']]} WHERE"

            for key, value in row.items():
                
                if pd.isna(value): continue
                command += f" {key} LIKE '%{value}%' AND"

            if command.endswith("WHERE"): continue # no conditions were set
            command = command[0:-4] # remove excess ' AND'

            df_fetch = pd.read_sql_query(command, conn)
            df_fetch['aggregate'] = agg

            if len(df_fetch) == 0: continue

            data.append(df_fetch)

    if len(data) == 0:
        print(f"Got no data for {cat_config['category']}!")
        return

    variables = cat_config['vary_over'].split('+')

    df_all: pd.DataFrame = pd.concat(data).drop_duplicates().groupby(['aggregate', *variables]).sum(numeric_only=True).iloc[:,-1].to_frame()
    df_all.columns = [cat_config['category']]
    df_all = df_all.reset_index().set_index('aggregate').pivot(columns=variables)
    df_all.columns = df_all.columns.droplevel()
    df_all.fillna(0, inplace=True)

    conn.close()

    df_all.to_csv(out_dir + f"results.{cat_config['database']}.{cat_config['category']}.csv")

    if cat_config['plot'] == 'stack':
        pp.figure()
        df_colours = df_table.loc[df_table['category'] == cat_config['category']].groupby('aggregate').first()['colour']
        colours = [df_colours.loc[agg] for agg in df_all.index]
        pp.stackplot(df_all.columns, df_all, colors=colours)
    #elif cat_config['plot'] == 'bar':
    #elif cat_config['plot'] == 'stacked bar':
    else: return
    
    pp.title(cat_config['category'])
    pp.xticks(df_all.columns)
    pp.legend(df_all.index)



# Collects sqlite databases into a database of name: path
def _get_sqlite_databases():

    databases = dict()

    for dirs in os.walk(sqlite_dir):
        files = dirs[2]

        for file in files:
            split = os.path.splitext(file)
            if split[1] == '.sqlite': databases[split[0]] = sqlite_dir + file

    return databases



if __name__ == "__main__":

    aggregate_by_database()