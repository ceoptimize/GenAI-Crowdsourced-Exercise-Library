
import psycopg2
import re
import sqlparse
import pandas
import json




class PostgresDatabase:
    def __init__(self, dbname = "mydatabase", user = "postgres", password = "C$g$9292greer", host = "localhost", port = "5432"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()


    def execute_sql_file(self, filename):
        # Open and read the file
        with open(filename, 'r') as f:
            sql = f.read()

        # Replace 'CREATE TABLE' with 'CREATE TABLE IF NOT EXISTS'
        sql = re.sub(r'CREATE TABLE', 'CREATE TABLE IF NOT EXISTS', sql, flags=re.IGNORECASE)
        sql = re.sub(r'string', 'varchar(255)', sql, flags=re.IGNORECASE)
        sql = sql.replace('"', '')

        # Split SQL commands
        sql_commands = sqlparse.split(sql)

        # Execute each SQL command
        for command in sql_commands:
            # Check if the command is not empty
            if command.strip() != '':
                try:
                    # Remove NOT NULL condition for non-ID columns
                    command = re.sub(r' NOT NULL', '', command)
      
                    print("Command: " + command)
                    self.cursor.execute(command)
                    print("Success!")
                    if command.strip().lower().startswith('create table if not exists'):
                        table_name = command.split()[5]  # get the table name from the command
                        self.cursor.execute(f'SELECT * FROM {table_name};')
                        rows = self.cursor.fetchall()
                        print(f'Data in {table_name}: {rows}')
                except psycopg2.Error as e:
                    print(f"An error occurred while executing SQL command:\n{command}\nError: {e}")
                    self.conn.rollback()  # Rollback in case of error

        # Close the cursor and the connection
        self.conn.commit()

    """
    def execute_sql_file(self, filename):
        # Open and read the file
        with open(filename, 'r') as f:
            sql = f.read()

        # Replace 'CREATE TABLE' with 'CREATE TABLE IF NOT EXISTS'
        sql = re.sub(r'CREATE TABLE', 'CREATE TABLE IF NOT EXISTS', sql, flags=re.IGNORECASE)
        sql = re.sub(r'string', 'varchar(255)', sql, flags=re.IGNORECASE)
      #  sql = re.sub(r'boolean', 'bool', sql, flags=re.IGNORECASE)
        sql = sql.replace('"', '')

        # Split SQL commands
        sql_commands = sqlparse.split(sql)

        # Execute each SQL command
        for command in sql_commands:
            # Check if the command is not empty
            if command.strip() != '':
                try:
                    self.cursor.execute(command)
                    print("success!")
                    self.conn.commit() # Commit after each successful command
                    if command.strip().lower().startswith('create table if not exists'):
                        table_name = command.split()[5]  # get the table name from the command
                        self.cursor.execute(f'SELECT * FROM {table_name};')
                        rows = self.cursor.fetchall()
                        print(f'Data in {table_name}: {rows}')
                except psycopg2.Error as e:
                    print(f"An error occurred while executing SQL command:\n{command}\nError: {e}")
                    self.conn.rollback() # Rollback in case of error

        # Close the cursor and the connection
        self.conn.commit()"""

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.conn.commit()

    def create_table(self, table_name, columns):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()


    def insert_data(self, table_name, columns: list, values: list):
       # self.cursor.execute(f"INSERT INTO {table_name} (exercise, body_parts, equipment_used) VALUES (%s, %s), (exercise, body_parts, equipment_used)")
       # self.cursor.execute(f"INSERT INTO {table_name} (exercise, body_parts, equipment_used) VALUES (%s, %s)", (exercise, bodyparts))
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
        primarykey  = self.get_primary_key_columns(table_name)
        query += f" ON CONFLICT ({primarykey}) DO NOTHING"  # Specify the conflict resolution

        print("full query")
        print(query)
        self.cursor.execute(query, values)
        self.conn.commit()
        if self.cursor.rowcount == 0:
            print("No rows were inserted into the table.")

    def insert_data2(self, column1, column2):
       
        query = """
        INSERT INTO your_table (col1, col2)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM your_table WHERE col1=%s AND col2=%s
        )
        """

        self.cursor.execute(query, (column1, column2, column1, column2))
        self.conn.commit()
        self.cursor.close()
   
    """
    def load_data(self, table_name, data):
        columns = ",".join(data.keys())
        values = list(data.values())
        placeholders = ",".join(["%s"] * len(values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()"""


  

    def query_data(self, table_name, columns=None):
        if columns:
            columns_str = ', '.join(columns)
        else:
            columns_str = '*'

        query = f"SELECT {columns_str} FROM {table_name}"

        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        return rows
    """
    def postgres_table_to_dataframe(host, port, database, user, password, table_name):
    # Connect to the Postgres database
   

    # Execute a SELECT query to fetch all rows from the table
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, conn)

        # Close the database connection
        conn.close()

        return df

        """




    def get_table_columns(self, table_name):
        
        #query = f"SELECT attname FROM pg_attribute WHERE attrelid = '{table_name}'::regclass AND attnum > 0 AND NOT attisdropped;"
   
        query = f"select column_name from information_schema.columns where table_name = '{table_name}';"
        self.cursor.execute(query)
        columns = [row[0] for row in self.cursor.fetchall()]
        return columns

      
    

    def get_primary_key_columns(self, table_name):
      

        # Execute the SQL query to retrieve the column name(s) of the primary key
        query = f"""
        SELECT column_name
        FROM information_schema.key_column_usage
        WHERE table_name = '{table_name}'
        """
        print(query)
        self.cursor.execute(query)
        columns = [row[0] for row in self.cursor.fetchall()]
        return ', '.join(columns)


    
    def get_current_schema(self):
        
        
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT current_schema()")
        schema = self.cursor.fetchone()[0]
        
     
        
        return schema
    
    def get_current_database(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT current_database()")
        database = self.cursor.fetchone()[0]
        
        return database
    
    def get_tables(self, printenabled = True):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
        alltables = self.cursor.fetchall()
        table_names = [row[0] for row in alltables]
        if printenabled: 
            print(f"Tables in the database:")
            for table_name in table_names:
                  print(table_name)
        
        return table_names


    def get_columns(self, tablename, printenabled = True):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = {tablename}")
        allcolumns = self.cursor.fetchall()
        column_names = [row[0] for row in allcolumns]
        if printenabled: 
            print(f"Columns in the {tablename} table:")
            for column_name in column_names:
                  print(column_name)
        
        return column_names

    def drop_schema(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute("DROP SCHEMA public CASCADE")
        self.cursor.execute("CREATE SCHEMA public")
        self.conn.commit()
    
    def execute_query(self, query):
        self.cursor.execute(query)
      
    
    def fetch_query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.conn.commit()
        return result

    def close(self):
        self.cursor.close()
        self.conn.close()

    def test_create(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE PLANTS( what int   NOT NULL, mom VARCHAR NOT NULL)")
        self.conn.commit()


    def sanitize_string(self, value):
        return value.strip().lower()

    def check_existing_exercise(self, exercise_name):
        query = f"SELECT ExerciseID FROM Exercises WHERE ExerciseName = '{exercise_name}'"
        self.execute_query(query)
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
   
    def create_or_get_exercise(self, exercise_name, exercise_difficulty):
        sanitized_name = self.sanitize_string(exercise_name)

        if exercise_difficulty is None:
            query = f"SELECT ExerciseID FROM Exercises WHERE ExerciseName = '{sanitized_name}'"
        else:
            query = f"SELECT ExerciseID, ExerciseDifficulty FROM Exercises WHERE ExerciseName = '{sanitized_name}'"
        
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            exercise_id, existing_difficulty = result[0], result[1]
            if exercise_difficulty is not None:
                # Exercise already exists, update the exercise difficulty
                updated_difficulty = existing_difficulty + exercise_difficulty
                query = f"UPDATE Exercises SET ExerciseDifficulty = {updated_difficulty} WHERE ExerciseID = {exercise_id}"
                self.execute_query(query)
        else:
            if exercise_difficulty is None:
                query = f"INSERT INTO Exercises (ExerciseName) VALUES ('{sanitized_name}') RETURNING ExerciseID"
            else:
                query = f"INSERT INTO Exercises (ExerciseName, ExerciseDifficulty) VALUES ('{sanitized_name}', {exercise_difficulty}) RETURNING ExerciseID"
            self.execute_query(query)
            result = self.cursor.fetchone()
            exercise_id = result[0] if result else None
        
        return exercise_id
   

    def sanitize_and_check_equipment(self, equipment_name):
        sanitized_name = self.sanitize_string(equipment_name)

        query = f"SELECT EquipmentID FROM Equipment WHERE EquipmentName = '{sanitized_name}'"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            query = f"INSERT INTO Equipment (EquipmentName) VALUES ('{sanitized_name}') RETURNING EquipmentID"
            self.execute_query(query)
            result = self.cursor.fetchone()
            return result[0] if result else None

    
    def update_exercise_equipment(self, exercise_id, equipment_id, count):
        query = f"SELECT ExerciseEquipmentID, Count FROM ExerciseEquipment WHERE ExerciseID = {exercise_id} " \
                f"AND EquipmentID = {equipment_id}"
        self.execute_query(query)
        result = self.cursor.fetchone()
        print(result)

        if result:
            exercise_equipment_id = result[0]
         #   print("exercise_equipment_id" ) 
         #   print(exercise_equipment_id)
            existing_count = result[1]
         #   print("existing_count ") 
         #   print(existing_count)
          #  print(count)
            count = int(count)

            if existing_count == count:
           #     print("samecount")
                query = f"UPDATE ExerciseEquipment SET CountVotes = CountVotes + 1 WHERE ExerciseEquipmentID = {exercise_equipment_id}"
                self.execute_query(query)
            else:
                query = f"INSERT INTO ExerciseEquipment (ExerciseID, EquipmentID, Count, CountVotes) " \
                        f"VALUES ({exercise_id}, {equipment_id}, {count}, 1)"
                self.execute_query(query)
        else:
            query = f"INSERT INTO ExerciseEquipment (ExerciseID, EquipmentID, Count, CountVotes) " \
                    f"VALUES ({exercise_id}, {equipment_id}, {count}, 1)"
            self.execute_query(query)
    
    def sanitize_and_check_body_plane(self, body_plane):
        sanitized_plane = self.sanitize_string(body_plane)

        query = f"SELECT BodyPlaneID FROM BodyPlane WHERE BodyPlane = '{sanitized_plane}'"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            query = f"INSERT INTO BodyPlane (BodyPlane) VALUES ('{sanitized_plane}') RETURNING BodyPlaneID"
            self.execute_query(query)
            result = self.cursor.fetchone()
            return result[0] if result else None


    def update_exercise_plane(self, exercise_id, body_plane_id, plane_votes):
        query = f"SELECT ExercisePlaneID FROM ExercisePlane WHERE ExerciseID = {exercise_id} " \
                f"AND BodyPlaneID = {body_plane_id}"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            exercise_plane_id = result[0]
            query = f"UPDATE ExercisePlane SET PlaneVotes = PlaneVotes + {plane_votes} WHERE ExercisePlaneID = {exercise_plane_id}"
            self.execute_query(query)
        else:
            query = f"INSERT INTO ExercisePlane (ExerciseID, BodyPlaneID, PlaneVotes) " \
                    f"VALUES ({exercise_id}, {body_plane_id}, {plane_votes})"
            self.execute_query(query)


    def sanitize_and_check_body_area(self, body_area):
        sanitized_area = self.sanitize_string(body_area)

        query = f"SELECT BodyAreaID FROM BodyArea WHERE BodyArea = '{sanitized_area}'"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            query = f"INSERT INTO BodyArea (BodyArea) VALUES ('{sanitized_area}') RETURNING BodyAreaID"
            self.execute_query(query)
            result = self.cursor.fetchone()
            return result[0] if result else None


    def update_exercise_body_area(self, exercise_id, body_area_id, is_primary, is_primary_votes, is_secondary, is_secondary_votes):
        query = f"SELECT ExerciseBodyAreaID FROM ExerciseBodyArea WHERE ExerciseID = {exercise_id} " \
                f"AND BodyAreaID = {body_area_id}"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            exercise_body_area_id = result[0]
            query = f"UPDATE ExerciseBodyArea SET IsPrimaryVotes = IsPrimaryVotes + {is_primary_votes}, " \
                    f"IsSecondaryVotes = IsSecondaryVotes + {is_secondary_votes} WHERE ExerciseBodyAreaID = {exercise_body_area_id}"
            self.execute_query(query)
        else:
            query = f"INSERT INTO ExerciseBodyArea (ExerciseID, BodyAreaID, IsPrimary, IsPrimaryVotes, IsSecondary, IsSecondaryVotes) " \
                    f"VALUES ({exercise_id}, {body_area_id}, {is_primary}, {is_primary_votes}, {is_secondary}, {is_secondary_votes})"
            self.execute_query(query)

    def update_exercise_description(self, exercise_id, description):
        sanitized_description = self.sanitize_string(description)
        query = f"INSERT INTO ExerciseDescription (ExerciseID, ExerciseDescription) VALUES ({exercise_id}, '{sanitized_description}')"
        self.execute_query(query)
    
    def sanitize_and_check_exercise_relation(self, exercise_id, relation_id, relation_type):
        query = f"SELECT RelationVotes, RelationType FROM ExerciseRelation WHERE ExerciseID = {exercise_id} " \
                f"AND RelationID = {relation_id}"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            relation_votes = result[0]
            existing_relation_type = result[1]
            if existing_relation_type == relation_type:
                # Matching relation found, update votes
                query = f"UPDATE ExerciseRelation SET RelationVotes = RelationVotes + 1 " \
                        f"WHERE ExerciseID = {exercise_id} AND RelationID = {relation_id}"
                self.execute_query(query)
            else:
                # Different relation type, add new entry with relation_type as "regression"
                query = f"INSERT INTO ExerciseRelation (ExerciseID, RelationID, RelationType, RelationVotes) " \
                        f"VALUES ({exercise_id}, {relation_id}, '{relation_type}', 1)"
                self.execute_query(query)
        else:
            # No matching relation found, add new entry with relation_type as "regression"
            query = f"INSERT INTO ExerciseRelation (ExerciseID, RelationID, RelationType, RelationVotes) " \
                    f"VALUES ({exercise_id}, {relation_id}, '{relation_type}', 1)"
            self.execute_query(query)


    def update_exercise_relations(self, exercise_id, relation_list, relation_type):
        for relation in relation_list:
            relation_name = relation.strip().lower()

            # Sanitize and check relation exercise
            relation_id = self.create_or_get_exercise(relation_name, None)
            self.sanitize_and_check_exercise_relation(exercise_id, relation_id, relation_type)

    def update_exercise_youtube(self, exercise_id, video_id):
        sanitized_exercise_id = self.sanitize_and_check_exercise(exercise_id)
        sanitized_video_id = self.sanitize_and_check_video(video_id)

        query = f"SELECT ExerciseVideoMatch FROM ExerciseYouTube WHERE ExerciseID = {sanitized_exercise_id} " \
                f"AND VideoID = '{sanitized_video_id}'"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            exercise_video_match = result[0]
            query = f"UPDATE ExerciseYouTube SET ExerciseVideoMatch = ExerciseVideoMatch + 1 " \
                    f"WHERE ExerciseID = {sanitized_exercise_id} AND VideoID = '{sanitized_video_id}'"
            self.execute_query(query)
        else:
            query = f"INSERT INTO ExerciseYouTube (ExerciseID, VideoID, ExerciseVideoMatch) " \
                    f"VALUES ({sanitized_exercise_id}, '{sanitized_video_id}', 1)"
            self.execute_query(query)

    def load_json(self, json_data, youtubevideoId: str):
        # Parse JSON data
        try:
            exercise_name = json_data['exercise_name']
            exercise_difficulty = json_data.get('exercise_difficulty', 1)
            exercise_id = self.create_or_get_exercise(exercise_name, exercise_difficulty)
            print("Exercise ID:", exercise_id)

            # Process equipment
            equipment_list = json_data['equipment']
            for equipment in equipment_list:
                equipment_name = equipment['Name']
                equipment_count = equipment['Count']

                # Sanitize and check equipment
                equipment_id = self.sanitize_and_check_equipment(equipment_name)
                print("Equipment ID:", equipment_id)

                # Update exerciseequipment table
                self.update_exercise_equipment(exercise_id, equipment_id, equipment_count)

            # Process body planes
            planes_of_motion = json_data['planes_of_motion']
            for plane in planes_of_motion:
                body_plane_id = self.sanitize_and_check_body_plane(plane)
                self.update_exercise_plane(exercise_id, body_plane_id, 1)

            # Process body areas
            body_parts = json_data['body_parts']
            primary_body_area = body_parts['primary']
            secondary_body_areas = body_parts['secondary']
            primary_body_area_id = self.sanitize_and_check_body_area(primary_body_area)
            self.update_exercise_body_area(exercise_id, primary_body_area_id, True, 1, False, 0)
            for secondary_area in secondary_body_areas:
                secondary_body_area_id = self.sanitize_and_check_body_area(secondary_area)
                self.update_exercise_body_area(exercise_id, secondary_body_area_id, False, 0, True, 1)

            # Update exercise description
            description = json_data['description']
            self.update_exercise_description(exercise_id, description)

            # Process regressions
            regressions = json_data['regressions']
            self.update_exercise_relations(exercise_id, regressions, 'regression')

            # Process progressions
            progressions = json_data['progressions']
            self.update_exercise_relations(exercise_id, progressions, 'progression')

            # Process variations
            variations = json_data['variations']
            self.update_exercise_relations(exercise_id, variations, 'variation')

            # Update exerciseyoutube table
            if youtubevideoId:
                self.update_exercise_youtube(exercise_id, youtubevideoId)

            # Commit changes to the database
            self.conn.commit()

        except Exception as e:
            # Rollback changes on error
            self.conn.rollback()
            print("Rolling back any db updates - error occurred:", str(e))
            raise

    """        
    def load_json(self, json_data, youtubevideoId: str):
        # Parse JSON data
        try:
            exercise_name = json_data['exercise_name']
            exercise_difficulty = json_data.get('exercise_difficulty', 1)
            exercise_id = self.create_or_get_exercise(exercise_name, exercise_difficulty)
            print("Exercise ID:", exercise_id)

            # Process equipment
            equipment_list = json_data['equipment']
            for equipment in equipment_list:
                equipment_name = equipment['Name']
                equipment_count = equipment['Count']

                # Sanitize and check equipment
                equipment_id = self.sanitize_and_check_equipment(equipment_name)
                print("Equipment ID:", equipment_id)

                # Update exerciseequipment table
                self.update_exercise_equipment(exercise_id, equipment_id, equipment_count)

            # Process body planes
            planes_of_motion = json_data['planes_of_motion']
            for plane in planes_of_motion:
                body_plane_id = self.sanitize_and_check_body_plane(plane)
                self.update_exercise_plane(exercise_id, body_plane_id, 1)

            # Process body areas
            body_parts = json_data['body_parts']
            primary_body_area = body_parts['primary']
            secondary_body_areas = body_parts['secondary']
            primary_body_area_id = self.sanitize_and_check_body_area(primary_body_area)
            self.update_exercise_body_area(exercise_id, primary_body_area_id, True, 1, False, 0)
            for secondary_area in secondary_body_areas:
                secondary_body_area_id = self.sanitize_and_check_body_area(secondary_area)
                self.update_exercise_body_area(exercise_id, secondary_body_area_id, False, 0, True, 1)

             # Update exercise description
            description = json_data['description']
            self.update_exercise_description(exercise_id, description)

    # Process regressions
            regressions = json_data['regressions']
            self.update_exercise_relations(exercise_id, regressions, 'regression')

            # Process progressions
            progressions = json_data['progressions']
            self.update_exercise_relations(exercise_id, progressions, 'progression')

            # Process variations
            variations = json_data['variations']
            self.update_exercise_relations(exercise_id, variations, 'variation')

            # Commit changes to the database
            self.conn.commit()

        except Exception as e:
            # Rollback changes on error
            self.conn.rollback()
            print("Rolling back any db updates - error occurred:", str(e))
            raise"""


    def get_video_id_and_title_array(self, limit): 
        query = f"SELECT VideoId, VideoTitle from YoutubeVideo"
        self.execute_query(query)
        result = self.cursor.fetchall()
        if result:
           # return result[0]
           return [row[0] for row in result]
        return None

    def get_video_title(self, video_id):
        query = f"SELECT VideoTitle FROM YoutubeVideo WHERE VideoID = '{video_id}'"
        self.execute_query(query)
        result = self.cursor.fetchone()
       # result = self.cursor.fetchall()
        
        if result:
            return result[0]
          #  return [row[0] for row in result]
        return None

    

        
            

