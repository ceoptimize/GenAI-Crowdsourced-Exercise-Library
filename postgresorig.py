
import psycopg2
import re
import sqlparse
import json
import traceback
import stringfunctions
import log


'''
word_mapping = {
    'knee': 'kneeling',
    'kneeling': 'knee',
    'clap': 'clapping',
    'clapping': 'clap',
    'plyo': 'plyometric',
    'plyometric': 'plyo',
    'incline': 'inclined',
    'inclined': 'incline',
    'decline': 'declined',
    'declined': 'decline'
    # Add more mappings as needed.
}
'''

word_mapping = [
    ['knee', 'kneeling'],
    ['clap', 'clapping'],
    ['incline', 'inclined', 'inclining'],
    ['decline', 'declined', 'declining']
    # Add more mappings as needed.
]


def generate_aliases(exercise_name):
    exercise_name = stringfunctions.sanitize_string(exercise_name)
    print(f"Generating aliases for: {exercise_name}")
    words = exercise_name.split()
    new_aliases = set([exercise_name])  # Include the original name as well

    for word_set in word_mapping:
        for word in words:
            if word in word_set:
                # Generate all possible combinations with the synonyms
                for synonym in word_set:
                    if synonym != word:
                        new_alias = exercise_name.replace(word, synonym)
                        new_aliases.add(new_alias)

    # Remove the original name from the aliases
    new_aliases.remove(exercise_name)
    print(f"Generated aliases: {new_aliases}")
    return list(new_aliases)


'''
def generate_aliases(exercise_name):
    print(f"Generating aliases for: {exercise_name}")
    words = exercise_name.split()
    new_aliases = []

    for word in words:
        # Check if the word has an alternative.
        if word in word_mapping:
            # Create a new alias by replacing the word with its alternative.
            alternative_word = word_mapping[word]
            new_alias = exercise_name.replace(word, alternative_word)
            new_aliases.append(new_alias)
    print(f"Generated aliases: {new_aliases}")
    return new_aliases
'''


class PostgresDatabase:
    def __init__(self, dbname="mydatabase", user="postgres", password="C$g$9292greer", host="localhost", port="5432"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()
        # Open or create error log file in append mode
        self.error_log_file = open("error_log.txt", "a")

    def execute_sql_file(self, filename):
        # Open and read the file
        with open(filename, 'r') as f:
            sql = f.read()

        # Replace 'CREATE TABLE' with 'CREATE TABLE IF NOT EXISTS'
        sql = re.sub(r'CREATE TABLE', 'CREATE TABLE IF NOT EXISTS',
                     sql, flags=re.IGNORECASE)
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
                        # get the table name from the command
                        table_name = command.split()[5]
                        self.cursor.execute(f'SELECT * FROM {table_name};')
                        rows = self.cursor.fetchall()
                        print(f'Data in {table_name}: {rows}')
                except psycopg2.Error as e:
                    print(
                        f"An error occurred while executing SQL command:\n{command}\nError: {e}")
                    self.conn.rollback()  # Rollback in case of error

        # Close the cursor and the connection
        self.conn.commit()

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.conn.commit()

    def create_table(self, table_name, columns):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def insert_data(self, table_name,  columns: list, values: list, primarykey=None):
       # self.cursor.execute(f"INSERT INTO {table_name} (exercise, body_parts, equipment_used) VALUES (%s, %s), (exercise, body_parts, equipment_used)")
       # self.cursor.execute(f"INSERT INTO {table_name} (exercise, body_parts, equipment_used) VALUES (%s, %s)", (exercise, bodyparts))
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
        if primarykey is None:
            primarykey = self.get_primary_key_columns(table_name)
        # Specify the conflict resolution
        query += f" ON CONFLICT ({primarykey}) DO NOTHING"

        self.cursor.execute(query, values)
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

    def query_data(self, table_name, columns=None):
        if columns:
            columns_str = ', '.join(columns)
        else:
            columns_str = '*'

        query = f"SELECT {columns_str} FROM {table_name}"

        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        return rows

    def get_table_columns(self, table_name):

        # query = f"SELECT attname FROM pg_attribute WHERE attrelid = '{table_name}'::regclass AND attnum > 0 AND NOT attisdropped;"

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

    def get_tables(self, printenabled=True):
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
        alltables = self.cursor.fetchall()
        table_names = [row[0] for row in alltables]
        if printenabled:
            print(f"Tables in the database:")
            for table_name in table_names:
                print(table_name)
            print()
        return table_names

    def print_all_table_contents(self, limit=None):
        table_names = self.get_tables(printenabled=False)

        for table_name in table_names:
            # Get the column names for the table
            column_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
            columns = self.fetch_query(column_query)

            # Adjust for tuple result structure
            column_names = [column[0] for column in columns]

            # Print table name and column names
            print(f"{table_name} table:")
            print(", ".join(column_names))

            # Print rows
            data_query = f'SELECT * FROM {table_name}'
            if limit is not None:
                data_query += f' LIMIT {limit}'
            result = self.fetch_query(data_query)
            for row in result:
                print(row)

            # Print a newline for better separation between tables
            print()

    def get_columns(self, tablename, printenabled=True):
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"SELECT column_name FROM information_schema.columns WHERE table_name = {tablename}")
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

    def truncate_tables(self, tables_to_keep=[]):
        self.cursor = self.conn.cursor()

        # Get a list of all table names in the current schema
        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        rows = self.cursor.fetchall()

        for row in rows:
            table_name = row[0]
            if table_name not in tables_to_keep:
                # Truncate the table if it's not in the list of tables to keep
                truncate_query = f"TRUNCATE TABLE public.{table_name} RESTART IDENTITY CASCADE"
                self.cursor.execute(truncate_query)

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
        self.cursor.execute(
            "CREATE TABLE PLANTS( what int   NOT NULL, mom VARCHAR NOT NULL)")
        self.conn.commit()

    def get_denormalized_table(self):
        query = """
        SELECT
        e.ExerciseID,
        e.ExerciseName,
        e.ExerciseDifficultySum,
        eq.EquipmentName,
        ee.Count,
        bp.BodyPlane,
        ba.BodyArea,
        eba.IsPrimary,
        eba.IsSecondary,
        yv.VideoID,
        yv.VideoTitle,
        er.RelationID,
        er.RelationType
    FROM
        Exercises e
        LEFT JOIN ExerciseDescription ed ON e.ExerciseID = ed.ExerciseID
        LEFT JOIN ExerciseBodyArea eba ON e.ExerciseID = eba.ExerciseID
        LEFT JOIN ExerciseEquipment ee ON e.ExerciseID = ee.ExerciseID
        LEFT JOIN ExercisePlane ep ON e.ExerciseID = ep.ExerciseID
        LEFT JOIN ExerciseYoutube ey ON e.ExerciseID = ey.ExerciseID
        LEFT JOIN ExerciseRelation er ON e.ExerciseID = er.ExerciseID
        LEFT JOIN Equipment eq ON ee.EquipmentID = eq.EquipmentID
        LEFT JOIN BodyPlane bp ON ep.BodyPlaneID = bp.BodyPlaneID
        LEFT JOIN BodyArea ba ON eba.BodyAreaID = ba.BodyAreaID
        LEFT JOIN YoutubeVideo yv ON ey.YoutubeVideoID = yv.VideoID

        """
        self.cursor.execute(query)
        table = self.cursor.fetchall()
        return table

    '''
    def sanitize_string(self, value):
        sanitized_value = re.sub(r"'", "''", value)
        return sanitized_value.strip().lower()'''

    def check_existing_exercise(self, exercise_name):
        query = f"SELECT ExerciseID FROM Exercises WHERE ExerciseName = '{exercise_name}'"
        self.execute_query(query)
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_exercise(self, exercise_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(exercise_name)
            query = f"SELECT ExerciseID, ExerciseDifficultySum, ExerciseDifficultyCount FROM Exercises WHERE ExerciseName = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()
            if result:
                exercise_id, exercise_difficulty, exercise_difficulty_count = result[
                    0], result[1], result[2]
                return exercise_id, exercise_difficulty, exercise_difficulty_count
            else:
                return None, None, None
        except Exception as e:
            raise Exception(f"Error in get_exercise: {str(e)}")

    def get_exercise_description(self, exercise_id):
        query = f"SELECT ExerciseDescription FROM ExerciseDescription WHERE ExerciseID = {exercise_id}"
        self.execute_query(query)
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_exercise_name(self, exercise_id):
        query = f"SELECT ExerciseName FROM Exercises WHERE ExerciseID = {exercise_id}"
        self.execute_query(query)
        result = self.cursor.fetchone()
        return result[0] if result else None

    def create_or_get_exercise(self, exercise_name, exercise_difficulty, insertnew=True):
        try:
            exercise_id, existing_difficulty, existing_difficulty_count = self.get_exercise(
                exercise_name)

            if exercise_id:
                # Existing exercise
                if exercise_difficulty is not None:
                    try:
                        exercise_difficulty = float(exercise_difficulty)
                    except ValueError:
                        raise ValueError(
                            f"Invalid exercise difficulty value: {exercise_difficulty}")

                    updated_difficulty = existing_difficulty + exercise_difficulty
                    updated_difficulty_count = existing_difficulty_count + 1
                    query = f"UPDATE Exercises SET ExerciseDifficultySum = {updated_difficulty}, ExerciseDifficultyCount = {updated_difficulty_count} WHERE ExerciseID = {exercise_id}"
                    self.execute_query(query)
                return exercise_id, False  # Returning False as the exercise was found, not created
            else:
                # New exercise
                if insertnew:
                    sanitized_name = stringfunctions.sanitize_string(
                        exercise_name)
                    query = f"INSERT INTO Exercises (ExerciseName, ExerciseDifficultySum, ExerciseDifficultyCount) VALUES ('{sanitized_name}', {exercise_difficulty if exercise_difficulty is not None else 0}, 1) RETURNING ExerciseID"
                    self.execute_query(query)
                    result = self.cursor.fetchone()
                    exercise_id = result[0] if result else None
                    return exercise_id, True  # Returning True as the exercise was created
                else:
                    return None, False
        except Exception as e:
            raise Exception(f"Error in create_or_get_exercise: {str(e)}")

    def create_or_get_alias(self, main_exercise_id, alias_id):
        # Check if the alias relationship already exists
        check_query = f"SELECT * FROM ExerciseNameAlias WHERE ExerciseID = {main_exercise_id} AND AliasID = {alias_id}"
        self.execute_query(check_query)
        result = self.cursor.fetchone()

        if not result:
            # Insert new alias relationship
            insert_query = f"INSERT INTO ExerciseNameAlias (ExerciseID, AliasID, AliasVotes) VALUES ({main_exercise_id}, {alias_id}, 1)"
            self.execute_query(insert_query)

    def sanitize_and_check_equipment(self, equipment_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(equipment_name)

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
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_equipment: {str(e)}")

    def update_exercise_equipment(self, exercise_id, equipment_id, count):
        try:
            query = f"SELECT ExerciseEquipmentID, Count FROM ExerciseEquipment WHERE ExerciseID = {exercise_id} " \
                    f"AND EquipmentID = {equipment_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

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
        except Exception as e:
            raise Exception(f"Error in update_exercise_equipment: {str(e)}")

    def sanitize_and_check_body_plane(self, body_plane):
        try:
            sanitized_plane = stringfunctions.sanitize_string(body_plane)

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
        except Exception as e:
            raise Exception(
                f"Error in sanitize_and_check_body_plane: {str(e)}")

    def update_exercise_plane(self, exercise_id, body_plane_id, plane_votes):
        try:
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
        except Exception as e:
            raise Exception(f"Error in update_exercise_plane: {str(e)}")

    def sanitize_and_check_body_area(self, body_area):
        try:
            sanitized_area = stringfunctions.sanitize_string(body_area)

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
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_body_area: {str(e)}")

    def update_exercise_body_area(self, exercise_id, body_area_id, is_primary, is_primary_votes, is_secondary, is_secondary_votes):
        try:
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
        except Exception as e:
            raise Exception(f"Error in update_exercise_body_area: {str(e)}")

    def update_exercise_description(self, exercise_id, description):
        try:
            sanitized_description = stringfunctions.sanitize_string(
                description)
            query = f"INSERT INTO ExerciseDescription (ExerciseID, ExerciseDescription) VALUES ({exercise_id}, '{sanitized_description}')"
            self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_description: {str(e)}")

    def update_exercise_aliases(self, exercise_id, exercise_aliases):
        try:
            for alias_name in exercise_aliases:
                print("gpt aliases " + alias_name)
                # Find or create alias exercise
                alias_id, _ = self.create_or_get_exercise(
                    alias_name, None, insertnew=True)
                # Insert into ExerciseNameAlias
                insert_query = f"INSERT INTO ExerciseNameAlias (ExerciseId, AliasID, AliasVotes) VALUES ({exercise_id}, {alias_id}, 1) ON CONFLICT DO NOTHING"
                self.execute_query(insert_query)

        except Exception as e:
            raise Exception(f"Error in update_exercise_aliases: {str(e)}")
    '''     
    def update_exercise_aliases(self, exercise_id, exercise_aliases):
        try:
            for alias in exercise_aliases:
                # Ensure alias is present in the Exercises table
                alias_id, _ = self.create_or_get_exercise(alias, None, insertnew=True)

                # Check if relation already exists in ExerciseNameAlias table
                query = f"SELECT ExerciseAliasID FROM ExerciseNameAlias WHERE ExerciseID = {exercise_id} AND AliasID = {alias_id}"
                self.execute_query(query)
                result = self.cursor.fetchone()

                if result:
                    # Update existing relation
                    exercise_alias_id = result[0]
                    update_query = f"UPDATE ExerciseNameAlias SET AliasVotes = AliasVotes + 1 WHERE ExerciseAliasID = {exercise_alias_id}"
                    self.execute_query(update_query)
                else:
                    # Insert new relation
                    insert_query = f"INSERT INTO ExerciseNameAlias (ExerciseID, AliasID, AliasVotes) VALUES ({exercise_id}, {alias_id}, 1)"
                    self.execute_query(insert_query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_aliases: {str(e)}") 
    '''

    def get_existing_aliases(self, exercise_id):
        query = f"SELECT e.ExerciseName FROM ExerciseNameAlias ena JOIN Exercises e ON ena.AliasID = e.ExerciseID WHERE ena.ExerciseId = {exercise_id}"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def update_exercise_aliases_with_additional(self, exercise_id, exercise_name):
        print(
            f"Generating additional aliases for exercise name: {exercise_name}")
        additional_aliases = generate_aliases(exercise_name)
        print(f"Additional aliases generated: {additional_aliases}")
        existing_aliases = self.get_existing_aliases(exercise_id)
        print(f"Existing aliases: {existing_aliases}")

        for alias in additional_aliases:
            if alias not in existing_aliases:
                sanitized_alias = stringfunctions.sanitize_string(alias)
                alias_id, _ = self.create_or_get_exercise(
                    sanitized_alias, None, insertnew=True)
                if alias_id:
                    self.create_or_get_alias(exercise_id, alias_id)
                print(f"Adding new alias: {sanitized_alias}")

    def sanitize_and_check_exercise_relation(self, exercise_id, relation_id, relation_type):
        try:
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
        except Exception as e:
            raise Exception(
                f"Error in sanitize_and_check_exercise_relation: {str(e)}")

    def normalize_json_keys(self, adjustment_json):
        # Check and rename the 'regressions' key to 'regression' if it exists
        if 'regressions' in adjustment_json:
            adjustment_json['regression'] = adjustment_json.pop('regressions')

        # Similarly, check and rename the 'progressions' key to 'progression' if it exists
        if 'progressions' in adjustment_json:
            adjustment_json['progression'] = adjustment_json.pop(
                'progressions')

        return adjustment_json

    def handle_existing_exercises_adjustments(self, exercise_id, regression_ids, progression_ids, variation_ids, chatgpt):
        # For each list (regressions, progressions, variations), fetch the exercise details
        # and call the ChatGPT method for adjustments analysis.
        exercise_name = self.get_exercise_name(exercise_id)
        exercise_description = self.get_exercise_description(exercise_id)
        for rel_exercise_id_list, relation_type in [(regression_ids, 'regression'), (progression_ids, 'progression'), (variation_ids, 'variation')]:
            for rel_exercise_id in rel_exercise_id_list:
                rel_exercise_name = self.get_exercise_name(rel_exercise_id)
                rel_exercise_description = self.get_exercise_description(
                    rel_exercise_id)

                # Call the ChatGPT method for adjustments analysis.
                # Assuming chatgpt_instance is an instance of your ChatGPT class.
                gptresponse = chatgpt.get_related_exercise_adjustments(
                    exercise_name, exercise_description, rel_exercise_name, rel_exercise_description, relation_type)
                self.update_exercise_relation_details(
                    exercise_id, rel_exercise_id,  gptresponse)

    def update_exercise_relation_details(self, exercise_id, related_exercise_id, adjustment_json):
        try:
           # adjustment_data = json.loads(adjustment_json)
            adjustment_data = self.normalize_json_keys(adjustment_json)
            # Convert the dictionary to a JSON string for logging
            adjustment_data_str = json.dumps(adjustment_data, indent=4)
            log.log_details(adjustment_data_str)

            # Update regressions
            for area in adjustment_data.get('regression', []):
                self.insert_or_update_relation_detail(
                    exercise_id, related_exercise_id, 'regression', area)

            # Update progressions
            for area in adjustment_data.get('progression', []):
                self.insert_or_update_relation_detail(
                    exercise_id, related_exercise_id, 'progression', area)

        except json.JSONDecodeError as e:
            raise Exception(f"Error in parsing JSON data: {str(e)}")

    def insert_or_update_relation_detail(self, exercise_id, related_exercise_id, relation_type, adjustment_type):
        # Check if relation detail already exists
        query = f"SELECT ExerciseRelationDetailID FROM ExerciseRelationDetail WHERE ExerciseID = {exercise_id} AND RelationID = {related_exercise_id} AND RelationType = '{relation_type}' AND AdjustmentType = '{adjustment_type}'"
        self.execute_query(query)
        result = self.cursor.fetchone()

        if result:
            # Update existing relation detail
            exercise_relation_detail_id = result[0]
            update_query = f"UPDATE ExerciseRelationDetail SET RelationDetailVotes = RelationDetailVotes + 1 WHERE ExerciseRelationDetailID = {exercise_relation_detail_id}"
            self.execute_query(update_query)
        else:
            # Insert new relation detail
            insert_query = f"INSERT INTO ExerciseRelationDetail (ExerciseID, RelationID, RelationType, AdjustmentType, RelationDetailVotes) VALUES ({exercise_id}, {related_exercise_id}, '{relation_type}', '{adjustment_type}', 1)"
            self.execute_query(insert_query)

    def update_exercise_relations(self, main_exercise_id, relation_list, relation_type, insertnew):

        existing_relation_ids = set()  # Set to store unique existing relation IDs

        for relation_name in relation_list:
            # Sanitize and check relation exercise
            relation_id, is_new = self.create_or_get_exercise(
                relation_name, None, insertnew)
            if relation_id is None:
                continue

            if insertnew or not is_new:
                self.sanitize_and_check_exercise_relation(
                    main_exercise_id, relation_id, relation_type)
            # Add relation_id to existing_relation_ids set if it's not new
                if not is_new:
                    existing_relation_ids.add(relation_id)

        return existing_relation_ids

    def update_exercise_youtube(self, exercise_id, video_id):
        try:

            query = f"SELECT ExerciseVideoMatch FROM ExerciseYouTube WHERE ExerciseID = {exercise_id} " \
                    f"AND YoutubeVideoID = '{video_id}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                exercise_video_match = result[0]
                query = f"UPDATE ExerciseYouTube SET ExerciseVideoMatch = ExerciseVideoMatch + 1 " \
                        f"WHERE ExerciseID = {exercise_id} AND YoutubeVideoID = '{video_id}'"
                self.execute_query(query)
            else:
                query = f"INSERT INTO ExerciseYouTube (ExerciseID, YoutubeVideoID, ExerciseVideoMatch) " \
                        f"VALUES ({exercise_id}, '{video_id}', 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_youtube: {str(e)}")

    def load_json(self, json_data, youtubevideoId: str, insertnewrelations=False):
        # print(json_data)
        # Parse JSON data
        print(youtubevideoId)
        try:
            exercise_name = stringfunctions.sanitize_string(
                json_data['exercise_name_primary'])
            print(exercise_name)
            exercise_difficulty = json_data.get('difficulty', 1)
            exercise_id, is_new = self.create_or_get_exercise(
                exercise_name, exercise_difficulty)
            print(exercise_id)

            # Process exercise aliases
            exercise_aliases = json_data.get('exercise_aliases', [])
            if exercise_id:
                sanitized_aliases = [stringfunctions.sanitize_string(
                    alias) for alias in exercise_aliases]
                self.update_exercise_aliases(exercise_id, sanitized_aliases)

                # Call the method to handle additional aliases
                self.update_exercise_aliases_with_additional(
                    exercise_id, exercise_name)

            # Process equipment
            equipment_list = json_data['equipment']
            for equipment in equipment_list:
                equipment_name = equipment['Name']
                equipment_count = equipment['Count']

                # Sanitize and check equipment
                equipment_id = self.sanitize_and_check_equipment(
                    equipment_name)

                # Update exerciseequipment table
                self.update_exercise_equipment(
                    exercise_id, equipment_id, equipment_count)

            # Process body planes
            planes_of_motion = json_data['planes_of_motion']
            for plane in planes_of_motion:
                body_plane_id = self.sanitize_and_check_body_plane(plane)
                self.update_exercise_plane(exercise_id, body_plane_id, 1)

            # Process body areas
            body_parts = json_data['body_parts']
            primary_body_area = body_parts['primary']
            secondary_body_areas = body_parts['secondary']
            primary_body_area_id = self.sanitize_and_check_body_area(
                primary_body_area)
            self.update_exercise_body_area(
                exercise_id, primary_body_area_id, True, 1, False, 0)
            for secondary_area in secondary_body_areas:
                secondary_body_area_id = self.sanitize_and_check_body_area(
                    secondary_area)
                self.update_exercise_body_area(
                    exercise_id, secondary_body_area_id, False, 0, True, 1)

            # Update exercise description
            description = json_data['description']
            self.update_exercise_description(exercise_id, description)

            # Update exerciseyoutube table
            if youtubevideoId:
                self.update_exercise_youtube(exercise_id, youtubevideoId)

            # Process regressions
            regressions = json_data['regressions']
            existingregressionids = self.update_exercise_relations(
                exercise_id, regressions, 'regression', insertnew=insertnewrelations)

            # Process progressions
            progressions = json_data['progressions']
            existingprogressionids = self.update_exercise_relations(
                exercise_id, progressions, 'progression', insertnew=insertnewrelations)

            # Process variations
            variations = json_data['variations']
            existingvariationids = self.update_exercise_relations(
                exercise_id, variations, 'variation', insertnew=insertnewrelations)

            return exercise_id, existingregressionids, existingprogressionids, existingvariationids
            # Commit changes to the database
           # self.conn.commit()

        except Exception as e:
            # Rollback changes on error
            # self.conn.rollback()
            # print(f"Rolling back any db updates for video {youtubevideoId} - error occurred:", str(e))

            # Log the error, including the exercise ID and the reason for the failure
            error_message = f"Video ID: {youtubevideoId}, Error: {str(e)}\n"
           # self.error_log_file.write(error_message)
            raise

    def get_video_id_and_title_array(self, limit=None):
        query = f"SELECT VideoId, VideoTitle from YoutubeVideo"
        if limit is not None:
            query += f' LIMIT {limit}'
        self.execute_query(query)
        result = self.cursor.fetchall()
        if result:
            print("result")
            # return result[0]
            return [row for row in result]
        return None

    def get_video_id_array(self, limit=None):
        query = f"SELECT VideoId from YoutubeVideo"
        if limit is not None:
            query += f' LIMIT {limit}'
        self.execute_query(query)
        result = self.cursor.fetchall()
        if result:
            print("result")
            print([row for row in result])
            # return result[0]
            return [row for row in result]
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