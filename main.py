import re
from postgres import PostgresDatabase
import pandas as pd
import tabulate
from youtube import Youtube
from videoloader import VideoLoader
from exerciseinfoloader import ExerciseLoader

postgres = PostgresDatabase()
#postgres.drop_table("EXERCISELIBRARY")
#postgres.drop_table("ExerciseYoutube")
#postgres.drop_table("EXERCISES")
#print(postgres.get_current_schema())
#print(postgres.query_data("YoutubeVideo"))
#print(postgres.query_data("EXERCISELIBRARY", ["exercise", "unilateral"]))
#postgres.drop_schema()
#print(postgres.get_table_columns("YoutubeVideo"))
#postgres.drop_table("PLANTS")
#postgres.test_create()
#postgres.get_table_columns("PLANTS")
#columns = ["WHAT", "MOM"]
#values = [5,"huh"]
#postgres.insert_data("PLANTS", columns, values)
#columns = postgres.get_table_columns('youtubevideo')
#print(columns)
#print(postgres.query_data("PLANTS"))
#print(postgres.get_primary_key_columns('youtubevideo'))


postgres.drop_schema()
postgres.execute_sql_file('QuickDBD-Free Diagram.sql')
postgres.get_tables()

vl = VideoLoader()
vl.load_videos_to_youtubevideo_table()

el = ExerciseLoader()
el.load_exercises_from_videos(insertnewrelations=False)

postgres.print_all_table_contents()





# Print the current database name
#print("Current Database:", current_db)
#print(queryresults)
postgres.close()
#df = pd.DataFrame(queryresults)
#print(df)
#print(tabulate.tabulate(df, headers='keys', tablefmt='psql'))