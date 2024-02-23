import psycopg2
from postgres import PostgresDatabase


pg = PostgresDatabase()

#look at most updated version of joint and single mappings to populate the view
joint_mapping = pg.joint_mapping
single_mapping = pg.single_mapping

#keypair = ('support surface', 'body position')
keypair = ('joint', 'joint movement')

key1 = keypair[0]
key2 = keypair[1]
#to create key you must put in alphabetical order
jointkey = "_".join(sorted([key1, key2]))


#remove whitespace and capitalize first words and add 'AverageConfidence'
viewname = key1.title().replace(' ', '') + key2.title().replace(' ', '') + "AverageConfidence"



joint_table = joint_mapping[jointkey]['table']
joint_relation_id_column = joint_mapping[jointkey]['relation_id_column']
single_table1 = single_mapping[key1]['table']
single_id_columns1 = single_mapping[key1]['id_column']
single_name_columns1 = single_mapping[key1]['name_column']
single_table2 = single_mapping[key2]['table']
single_id_columns2 = single_mapping[key2]['id_column']
single_name_columns2 = single_mapping[key2]['name_column']

pg.generate_avg_confidence_view(viewname, joint_table, joint_relation_id_column, single_table1, single_id_columns1, single_name_columns1, single_table2, single_id_columns2, single_name_columns2)


pg.cursor.close()
pg.conn.close()