1. Add new tables/plots to aggregate to the config/categories.csv file.
	- category: name of the plot/table
	- database: which sqlite database to pull data from (exclude .sqlite from the end)
	- table: short name for Output_... results table to pull from
	- run: whether to aggregate this plot/table right now
	- vary_over: dependent variable of plot/table. For plots must be a single variable that is a column of the pulled data table e.g. 't_periods', if not plotting then can be multiple variables such as 'regions+t_periods'
	- plot: which kind of plot to draw. Only 'stack' is configured for now which produces a stacked lineplot. If not plotting, just set blank

2. For any category configured, configure aggregates in the relevant table csv, e.g. config/flow_out.csv
	- category: which plot/table this aggregate is for
	- aggregate: name of the aggregate, e.g. 'Natural Gas'. Typical to have several aggregates (rows) per category
	- colour: colour of this aggregate when plotting (RGB hexidecimal, #000000 is black, #ffffff white, #ff0000 red etc)
	- include: whether to include this aggregate in the category. Might want to skip one or two aggregates sometimes
	- remaining columns: each of these corresponds to a data column in the Output_... table of the sqlite database. The script will filter these using the LIKE sql operator as e.g. tech LIKE 'foo' where foo is the value in the tech column for that aggregate row. Can set values like foo% or %foo% which will catch any techs starting with or containing foo, respectively. This will sum values of all rows in the data table where the tech column contains the string 'foo'. Multiple filters may be set.

3. Run using temoa-py3
	>conda activate temoa-py3
	>cd C:/.../results_aggregation/
	>python aggregate_results.py

4. Any configured plots will show automatically.

5. Aggregated results tables will be written as csv files to the output_tables directory with the format results.database_name.category_name

Optional. In config/config.toml, can change the input sqlite directory to, e.g. temoa/data_files/ so that databases can be processed in-situ. Same for output tables. If either are set to an empty string ( = '') then the directories are set to default within the script folder.