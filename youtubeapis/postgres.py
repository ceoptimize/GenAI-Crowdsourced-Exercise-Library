
import psycopg2
from psycopg2 import sql
import re
import sqlparse
import json
import traceback
import stringfunctions as stringfunctions
import log
import os
from datetime import datetime
from bson import ObjectId

SINGLE_MAPPING_FILE = 'resources/jsondata/single_mapping.json'
JOINT_MAPPING_FILE = 'resources/jsondata/joint_mapping.json'

WORD_MAPPING = [
    ['knee', 'kneeling'],
    ['clap', 'clapping'],
    ['incline', 'inclined', 'inclining'],
    ['decline', 'declined', 'declining']
    # Add more mappings as needed.
]

def serialize_entry(entry):
    if isinstance(entry, dict):
        # Convert all ObjectId to str in dictionary
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in entry.items()}
    return entry

def generate_aliases(exercise_name):
    exercise_name = stringfunctions.sanitize_string(exercise_name)
    print(f"Generating aliases for: {exercise_name}")
    words = exercise_name.split()
    new_aliases = set([exercise_name])  # Include the original name as well

    for word_set in WORD_MAPPING:
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



class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            # Convert ObjectId to string
            return str(obj)
        elif isinstance(obj, dict):
            # Recursively apply serialization logic to dictionary entries
            return {k: self.default(v) for k, v in obj.items()}
        return super().default(obj)

# Use this encoder when dumping to JSON
# updated_log_json = json.dumps(existing_log_array, cls=CustomJSONEncoder)


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
        self.single_mapping = self.load_single_feature_mapping()
        self.joint_mapping = self.load_joint_feature_mapping()
        self.unimplemented_feature_keys = ["movement pattern", "difficulty"]
    
    def load_joint_feature_mapping(self):
        with open(JOINT_MAPPING_FILE, 'r') as file:
            return json.load(file)
    

    def get_feature_mapping(self, joint_key):
    # Directly return the mapping if exists
        return self.joint_mapping.get(joint_key, None)
        
    def load_single_feature_mapping(self):
        with open(SINGLE_MAPPING_FILE, 'r') as file:
            return json.load(file)

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

    # Continue for other keys in the JSON data...
    # You can create separate methods for each table if the insert logic is complex

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
        print(columns)
        print(values)
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
           # column_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
            column_query = f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position
                """
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

    def sanitize_and_check_mechanics(self, mechanics):
        try:
            sanitized_mechanics = stringfunctions.sanitize_string(mechanics)

            query = f"SELECT MechanicsID FROM Mechanics WHERE Mechanics = '{sanitized_mechanics}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                query = f"INSERT INTO Mechanics (Mechanics) VALUES ('{sanitized_mechanics}') RETURNING MechanicsID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_mechanics: {str(e)}")

    def update_exercise_mechanics(self, exercise_id, mechanics_id):
        try:
            query = f"SELECT ExerciseMechanicsID FROM ExerciseMechanics WHERE ExerciseID = {exercise_id} AND MechanicsID = {mechanics_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                exercise_mechanics_id = result[0]
                query = f"UPDATE ExerciseMechanics SET MechanicsVotes = MechanicsVotes + 1 WHERE ExerciseMechanicsID = {exercise_mechanics_id}"
                self.execute_query(query)
            else:
                query = f"INSERT INTO ExerciseMechanics (ExerciseID, MechanicsID, MechanicsVotes) VALUES ({exercise_id}, {mechanics_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_mechanics: {str(e)}")

    def sanitize_and_check_joint_usage(self, joint_usage):
        try:
            sanitized_joint_usage = stringfunctions.sanitize_string(
                joint_usage)

            query = f"SELECT JointUsageID FROM JointUsage WHERE JointUsage = '{sanitized_joint_usage}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                query = f"INSERT INTO JointUsage (JointUsage) VALUES ('{sanitized_joint_usage}') RETURNING JointUsageID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(
                f"Error in sanitize_and_check_joint_usage: {str(e)}")

    def update_exercise_joint_usage(self, exercise_id, joint_usage_id):
        try:
            query = f"SELECT ExerciseJointUsageID FROM ExerciseJointUsage WHERE ExerciseID = {exercise_id} AND JointUsageID = {joint_usage_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                exercise_joint_usage_id = result[0]
                query = f"UPDATE ExerciseJointUsage SET JointUsageVotes = JointUsageVotes + 1 WHERE ExerciseJointUsageID = {exercise_joint_usage_id}"
                self.execute_query(query)
            else:
                query = f"INSERT INTO ExerciseJointUsage (ExerciseID, JointUsageID, JointUsageVotes) VALUES ({exercise_id}, {joint_usage_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_joint_usage: {str(e)}")

    def sanitize_and_check_sides(self, sides):
        try:
            sanitized_sides = stringfunctions.sanitize_string(sides)

            query = f"SELECT SidesID FROM Sides WHERE SidesName = '{sanitized_sides}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                query = f"INSERT INTO Sides (SidesName) VALUES ('{sanitized_sides}') RETURNING SidesID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_sides: {str(e)}")

    def update_exercise_sides(self, exercise_id, sides_id):
        try:
            query = f"SELECT ExerciseSidesID FROM ExerciseSides WHERE ExerciseID = {exercise_id} AND SidesID = {sides_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                exercise_sides_id = result[0]
                query = f"UPDATE ExerciseSides SET SidesVotes = SidesVotes + 1 WHERE ExerciseSidesID = {exercise_sides_id}"
                self.execute_query(query)
            else:
                query = f"INSERT INTO ExerciseSides (ExerciseID, SidesID, SidesVotes) VALUES ({exercise_id}, {sides_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_sides: {str(e)}")

    def sanitize_and_check_opt(self, opt_phase):
        try:
            sanitized_opt = stringfunctions.sanitize_string(opt_phase)

            query = f"SELECT OptID FROM OPT WHERE OptPhase = '{sanitized_opt}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                query = f"INSERT INTO OPT (OptPhase) VALUES ('{sanitized_opt}') RETURNING OptID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_opt: {str(e)}")

    def update_exercise_opt(self, exercise_id, opt_id, opt_votes=1):
        try:
            query = f"SELECT ExerciseOptID FROM ExerciseOPT WHERE ExerciseID = {exercise_id} AND OptID = {opt_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                exercise_opt_id = result[0]
                query = f"UPDATE ExerciseOPT SET OptVotes = OptVotes + {opt_votes} WHERE ExerciseOptID = {exercise_opt_id}"
                self.execute_query(query)
            else:
                query = f"INSERT INTO ExerciseOPT (ExerciseID, OptID, OptVotes) VALUES ({exercise_id}, {opt_id}, {opt_votes})"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_opt: {str(e)}")

    def sanitize_and_check_category(self, category_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(category_name)

            # Check if the category already exists
            query = f"SELECT CategoryID FROM Category WHERE CategoryName = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]  # Return existing CategoryID
            else:
                # Insert new category
                query = f"INSERT INTO Category (CategoryName) VALUES ('{sanitized_name}') RETURNING CategoryID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_category: {str(e)}")

    def update_exercise_category(self, exercise_id, category_id):
        try:
            # Check if the relationship already exists
            query = f"SELECT ExerciseCategoryID FROM ExerciseCategory WHERE ExerciseID = {exercise_id} AND CategoryID = {category_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                # Relationship exists, update votes
                exercise_category_id = result[0]
                query = f"UPDATE ExerciseCategory SET CategoryVotes = CategoryVotes + 1 WHERE ExerciseCategoryID = {exercise_category_id}"
                self.execute_query(query)
            else:
                # Insert new relationship
                query = f"INSERT INTO ExerciseCategory (ExerciseID, CategoryID, CategoryVotes) VALUES ({exercise_id}, {category_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_category: {str(e)}")

    def sanitize_and_check_corrective(self, corrective_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(corrective_name)

            # Check if the corrective already exists
            query = f"SELECT CorrectiveID FROM Corrective WHERE CorrectiveName = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]  # Return existing CorrectiveID
            else:
                # Insert new corrective
                query = f"INSERT INTO Corrective (CorrectiveName) VALUES ('{sanitized_name}') RETURNING CorrectiveID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(
                f"Error in sanitize_and_check_corrective: {str(e)}")

    def update_exercise_corrective(self, exercise_id, corrective_id):
        try:
            # Check if the relationship already exists
            query = f"SELECT ExerciseCorrectiveID FROM ExerciseCorrective WHERE ExerciseID = {exercise_id} AND CorrectiveID = {corrective_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                # Relationship exists, update votes
                exercise_corrective_id = result[0]
                query = f"UPDATE ExerciseCorrective SET CorrectiveVotes = CorrectiveVotes + 1 WHERE ExerciseCorrectiveID = {exercise_corrective_id}"
                self.execute_query(query)
            else:
                # Insert new relationship
                query = f"INSERT INTO ExerciseCorrective (ExerciseID, CorrectiveID, CorrectiveVotes) VALUES ({exercise_id}, {corrective_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_corrective: {str(e)}")

    def sanitize_and_check_contraindication(self, contraindication_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(
                contraindication_name)

            # Check if the contraindication already exists
            query = f"SELECT ContraindicationID FROM Contraindication WHERE ContraindicationName = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]  # Return existing ContraindicationID
            else:
                # Insert new contraindication
                query = f"INSERT INTO Contraindication (ContraindicationName) VALUES ('{sanitized_name}') RETURNING ContraindicationID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(
                f"Error in sanitize_and_check_contraindication: {str(e)}")

    def update_exercise_contraindication(self, exercise_id, contraindication_id):
        try:
            # Check if the relationship already exists
            query = f"SELECT ExerciseContraindicationID FROM ExerciseContraindication WHERE ExerciseID = {exercise_id} AND ContraindicationID = {contraindication_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                # Relationship exists, update votes
                exercise_contraindication_id = result[0]
                query = f"UPDATE ExerciseContraindication SET ContraindicationVotes = ContraindicationVotes + 1 WHERE ExerciseContraindicationID = {exercise_contraindication_id}"
                self.execute_query(query)
            else:
                # Insert new relationship
                query = f"INSERT INTO ExerciseContraindication (ExerciseID, ContraindicationID, ContraindicationVotes) VALUES ({exercise_id}, {contraindication_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(
                f"Error in update_exercise_contraindication: {str(e)}")

    def sanitize_and_check_sport(self, sport_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(sport_name)

            # Check if the sport already exists
            query = f"SELECT SportID FROM Sport WHERE SportName = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]  # Return existing SportID
            else:
                # Insert new sport
                query = f"INSERT INTO Sport (SportName) VALUES ('{sanitized_name}') RETURNING SportID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_sport: {str(e)}")

    def update_exercise_sport(self, exercise_id, sport_id):
        try:
            # Check if the relationship already exists
            query = f"SELECT ExerciseSportID FROM ExerciseSport WHERE ExerciseID = {exercise_id} AND SportID = {sport_id}"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                # Relationship exists, update votes
                exercise_sport_id = result[0]
                query = f"UPDATE ExerciseSport SET SportVotes = SportVotes + 1 WHERE ExerciseSportID = {exercise_sport_id}"
                self.execute_query(query)
            else:
                # Insert new relationship
                query = f"INSERT INTO ExerciseSport (ExerciseID, SportID, SportVotes) VALUES ({exercise_id}, {sport_id}, 1)"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_sport: {str(e)}")

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

    def update_exercise_tags(self, exercise_id, tags):
        try:
            for tag in tags:
                sanitized_tag = stringfunctions.sanitize_string(tag)
                query = f"INSERT INTO ExerciseTag (ExerciseID, ExerciseTag) VALUES ({exercise_id}, '{sanitized_tag}') ON CONFLICT DO NOTHING"
                self.execute_query(query)
        except Exception as e:
            raise Exception(f"Error in update_exercise_tags: {str(e)}")

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

    def sanitize_and_check_feature(self, feature_name, feature_value, creator_generated=False):
        # Mapping of feature names to their database table and ID column names
        if feature_name not in self.single_mapping:
            raise ValueError(f"Invalid feature name: {feature_name}")

        feature_mapping = self.single_mapping[feature_name]
        table_name = feature_mapping['table']
        id_column_name = feature_mapping['id_column']

        try:
            # Sanitize the feature value
            sanitized_value = stringfunctions.sanitize_string(feature_value)

            # Construct and execute the SELECT query
            select_query = f"SELECT {id_column_name} FROM {table_name} WHERE {table_name} = '{sanitized_value}'"
            self.execute_query(select_query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                # Construct and execute the INSERT query
                insert_query = f"INSERT INTO {table_name} ({table_name}, CreatorGenerated) VALUES ('{sanitized_value}', {creator_generated}) RETURNING {id_column_name}"
                self.execute_query(insert_query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_feature: {str(e)}")

    def sanitize_and_check_support_surface(self, support_surface_name, creator_generated=False):

        try:

            sanitized_name = stringfunctions.sanitize_string(
                support_surface_name)
            print(sanitized_name)
            query = f"SELECT SupportSurfaceID FROM SupportSurface WHERE SupportSurface = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                # print(sanitized_name)
                return result[0]

            else:

                # Set CreatorGenerated to FALSE when inserting a new support surface
                query = f"INSERT INTO SupportSurface (SupportSurface, CreatorGenerated) VALUES ('{sanitized_name}', {creator_generated}) RETURNING SupportSurfaceID"
                print(query)
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:

            raise Exception(
                f"Error in sanitize_and_check_support_surface: {str(e)}")
    '''
    def sanitize_and_check_support_surface(self, support_surface_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(support_surface_name)
            query = f"SELECT SupportSurfaceID FROM SupportSurface WHERE SupportSurface = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                query = f"INSERT INTO SupportSurface (SupportSurface) VALUES ('{sanitized_name}') RETURNING SupportSurfaceID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_support_surface: {str(e)}")
    '''

    def sanitize_and_check_body_position(self, body_position_name, creator_generated=False):
        try:
            sanitized_name = stringfunctions.sanitize_string(
                body_position_name)
            query = f"SELECT BodyPositionID FROM BodyPosition WHERE BodyPosition = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                # Set CreatorGenerated to FALSE when inserting a new body position
                query = f"INSERT INTO BodyPosition (BodyPosition, CreatorGenerated) VALUES ('{sanitized_name}', {creator_generated}) RETURNING BodyPositionID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(
                f"Error in sanitize_and_check_body_position: {str(e)}")
    '''
    def sanitize_and_check_body_position(self, body_position_name):
        try:
            sanitized_name = stringfunctions.sanitize_string(body_position_name)
            query = f"SELECT BodyPositionID FROM BodyPosition WHERE BodyPosition = '{sanitized_name}'"
            self.execute_query(query)
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                query = f"INSERT INTO BodyPosition (BodyPosition) VALUES ('{sanitized_name}') RETURNING BodyPositionID"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error in sanitize_and_check_body_position: {str(e)}")
    '''
    '''
    def update_support_surface_body_position(self, support_surface_id, body_position_id, gpt_confidence, creator_generated=False):
        try:
            # Assuming that GPTVotes is a column that you want to update as well
            query = f"""
            INSERT INTO SupportSurfaceBodyPosition (SupportSurfaceID, BodyPositionID, CreatorGenerated, GPTVotes, GPTConfidence)
            VALUES (%s, %s, {creator_generated}, 1, %s)
            ON CONFLICT (SupportSurfaceID, BodyPositionID) DO
            UPDATE SET GPTVotes = SupportSurfaceBodyPosition.GPTVotes + 1, GPTConfidence = %s
            """
            self.cursor.execute(query, (support_surface_id, body_position_id, gpt_confidence, gpt_confidence))
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e
    
    '''

    def update_postgres_with_document_from_mongo(self, mongo_id, input_feature, input_value, output_feature, response_content):
     
        
        # Construct the key for joint mapping lookup

        input_feature = stringfunctions.to_singular(input_feature).lower()
        output_feature = stringfunctions.to_singular(output_feature).lower()
        joint_key = "_".join(sorted([input_feature, output_feature]))
        # Check if it's a joint mapping scenario
        if joint_key in self.joint_mapping:
            joint_mapping = self.joint_mapping[joint_key]
            input_id = self.sanitize_and_check_feature(input_feature, input_value)
          #  print("Available keys in response_data:", response_content.keys())
          #  print("Attempting to access output_feature:", output_feature)
          
            for output in response_content[output_feature]:
                output_value = output["name"]
                gpt_confidence = output["confidence score"]
                output_id = self.sanitize_and_check_feature(output_feature, output_value)
                self.update_feature1_feature2(joint_mapping, input_id, output_id, gpt_confidence, mongo_id)
            print("Successful load")
        else:
            # Handle scenario for single features or raise an error for unhandled features
            print(f"Unhandled mapping scenario for {input_feature} and {output_feature}")




    def get_tuple_feature_mapping(self, feature_tuple):
        # Normalize and sort the feature tuple
        normalized_tuple = tuple(sorted([stringfunctions.to_singular(feature).lower() for feature in feature_tuple]))

        # Iterate through the mappings in the config to find a matching entry
        for mapping in self.feature_mapping['joint_mappings']:
            # Normalize and sort the features from the mapping for comparison
            mapping_features = tuple(sorted([stringfunctions.to_singular(feature).lower() for feature in mapping['features']]))
            
            if normalized_tuple == mapping_features:
                print(mapping)
                return mapping

        # Return None if no matching mapping is found
        return None

    

    def update_postgres_based_on_feature_mapping(self, doc, feature1, feature2):
        # Assuming 'feature_mapping' is loaded from your JSON configuration file
        feature_key = f"{feature1}_{feature2}"
        mapping = self.feature_mapping[feature_key]
        
        # Extract necessary data from MongoDB document
        feature1_value = doc.get(feature1, {}).get('name')  # Adjust according to actual document structure
        feature2_value = doc.get(feature2, {}).get('name')  # Adjust accordingly
        gpt_confidence = doc.get('response_content', {}).get('confidence score')  # Example path, adjust as needed
        mongo_doc_id = str(doc['_id'])  # Convert ObjectId to string for storing in JSONB
        
        # You might need to adjust the 'sanitize_and_check_feature' to work with your actual data
        feature1_id = self.sanitize_and_check_feature(feature1, feature1_value)
        feature2_id = self.sanitize_and_check_feature(feature2, feature2_value)
        
        # Instead of using 'folder' and 'datefoldername', use 'mongo_doc_id'
        self.update_feature1_feature2(
            feature_key, feature1_id, feature2_id, gpt_confidence, mongo_doc_id)

    # Modify 'update_feature1_feature2' to include 'mongo_doc_id' instead of 'folder' and 'datefoldername'

    def update_feature1_feature2(self, mapping, feature1_id, feature2_id, confidence_score, mongo_doc_id, creator_generated = False):
        # Similar to your current implementation, but replace 'folder' and 'datefoldername' with 'mongo_doc_id'
        # and adjust the logic to insert or update the PostgreSQL table based on the new structure.
     
        try:
         

            # Construct the SELECT query dynamically
            select_query = f"""
            SELECT {mapping['relation_id_column']}, {mapping['votes_column']}, {mapping['log_column']}
            FROM {mapping['table']}
            WHERE {mapping['id_columns']['feature1_id']} = %s AND {mapping['id_columns']['feature2_id']} = %s
            """
            self.cursor.execute(select_query, (feature1_id, feature2_id))
            result = self.cursor.fetchone()

            new_entry = {"confidence_score": confidence_score,
                         "mongo_doc_id": mongo_doc_id}

            if result:
                relation_id, votes, existing_log_json = result
                new_votes = votes + 1

                # Initialize existing_log_array based on existing_log_json
                if isinstance(existing_log_json, str):
                    # Parse the JSON string into a Python list
                    existing_log_array = json.loads(existing_log_json)
                elif isinstance(existing_log_json, list):
                    # Use the list directly if existing_log_json is already a list
                    existing_log_array = existing_log_json
                elif isinstance(existing_log_json, dict):
                    # Wrap the dictionary in a list if existing_log_json is a dict
                    existing_log_array = [existing_log_json]
                else:
                    # Initialize as an empty list if existing_log_json is None or an unexpected type
                    existing_log_array = []

                # Append the new entry to the list
                existing_log_array.append(new_entry)

                # Serialize the updated list back to a JSON string
                updated_log_json = json.dumps(existing_log_array, cls=CustomJSONEncoder)

                # Update the database entry
                update_query = f"""
                UPDATE {mapping['table']}
                SET {mapping['votes_column']} = %s, {mapping['log_column']} = %s
                WHERE {mapping['relation_id_column']} = %s
                """
                self.cursor.execute(update_query, (new_votes, updated_log_json, relation_id))
            else:
                # Insert new relation
                new_entry_array = [new_entry]
                new_entry_serializable = json.dumps(new_entry_array, cls=CustomJSONEncoder)
                insert_query = f"""
                INSERT INTO {mapping['table']} ({mapping['id_columns']['feature1_id']}, {mapping['id_columns']['feature2_id']}, CreatorGenerated, {mapping['votes_column']}, {mapping['log_column']})
                VALUES (%s, %s, %s, 1, %s)
                """
                self.cursor.execute(
                    insert_query, (feature1_id, feature2_id, creator_generated, new_entry_serializable))

            self.conn.commit()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e
   

    def update_support_surface_body_position(self, support_surface_id, body_position_id, confidence_score, folder, datefoldername,  creator_generated=False):
        try:
            # Check if the relation already exists
            query = """
            SELECT SupportSurfaceBodyPositionID, GPTVotes, GPTLog
            FROM SupportSurfaceBodyPosition
            WHERE SupportSurfaceID = %s AND BodyPositionID = %s
            """
            self.cursor.execute(query, (support_surface_id, body_position_id))
            result = self.cursor.fetchone()

            new_entry = {"confidence_score": confidence_score,
                         "folder": folder, "timestamp": datefoldername}

            if result:
                # Update existing relation
                support_surface_body_position_id, gpt_votes, existing_log_json = result
                new_gpt_votes = gpt_votes + 1

                # Use existing_log_json directly if it's already a list, otherwise parse it
                if existing_log_json is not None:
                    existing_log_array = existing_log_json if isinstance(
                        existing_log_json, list) else json.loads(existing_log_json)
                else:
                    existing_log_array = []
                existing_log_array.append(new_entry)
                updated_log_json = json.dumps(existing_log_array)

                update_query = """
                UPDATE SupportSurfaceBodyPosition
                SET GPTVotes = %s, GPTLog = %s
                WHERE SupportSurfaceBodyPositionID = %s
                """
                self.cursor.execute(
                    update_query, (new_gpt_votes, updated_log_json, support_surface_body_position_id))

            else:
                # Insert new relation with the initial JSON structure for GPTLog and set GPTVotes to 1
                insert_query = """
                INSERT INTO SupportSurfaceBodyPosition (SupportSurfaceID, BodyPositionID, CreatorGenerated, GPTVotes, GPTLog) 
                VALUES (%s, %s, %s, 1, %s)
                """
                self.cursor.execute(insert_query, (support_surface_id,
                                    body_position_id, creator_generated, json.dumps([new_entry])))

        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e

   

    def read_json_data(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return data

    def insert_data_based_on_key(self, key, value):
        # Define mapping from JSON keys to database table names and columns

        table_mapping = {
            'joint': ('Joint', ['Joint']),
            'jointmovement': ('JointMovement', ['JointMovement']),
            'injury': ('Injury', ['Injury']),  # Adjusted for complex structure
            'healthcondition': ('HealthCondition', ['HealthCondition']),
            'compensation': ('Compensation', ['Compensation']),
            'muscle': ('Muscle', ['Muscle']),
            'bodyarea': ('BodyArea', ['BodyArea']),
            # Assuming 'EquipmentName' is the column name
            'equipment': ('Equipment', ['EquipmentName']),
            'bodyposition': ('BodyPosition', ['BodyPosition']),
            'supportsurface': ('SupportSurface', ['SupportSurface']),
            # Assuming 'SidesName' is the column name
            'sidetype': ('Sides', ['SidesName']),
            'measurement': ('Measurement', ['Measurement']),
            'chain': ('Chain', ['Chain']),
            'jointusage': ('JointUsage', ['JointUsage']),
            'utility:': ('Utility', ['Utility']),
            # Assuming 'SportName' is the column name
            'sports': ('Sport', ['SportName']),
            'bodystructure': ('BodyStructure', ['BodyStructure']),
            'bodyplane': ('BodyPlane', ['BodyPlane']),
            'opt': ('OPT', ['OPTPhase']),
            'focus': ('Focus', ['FocusName']),
            'characteristic': ('Characteristic', ['Characteristic']),
            'bodyregion': ('BodyRegion', ['BodyRegion']),
            'musclerole': ('MuscleRole', ['MuscleRole']),
            'equipmenttype': ('EquipmentType', ['EquipmentType']),
            'adjustmentarea': ('AdjustmentArea', ['AdjustmentArea'])
        }
        print (key)

        if key in self.unimplemented_feature_keys:
            print(f"Skipping unimplemented key: {key}")
            return # Skip unimplemented keys

        normalized_key = key.replace(" ", "").lower()
    
        

        if normalized_key in table_mapping:
            table_name, columns = table_mapping[normalized_key]
            # Add the CreatorGenerated column
            columns.append('CreatorGenerated')
           # query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))}) ON CONFLICT DO NOTHING"
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * (len(columns) - 1))}, TRUE) ON CONFLICT DO NOTHING"
            print(table_name)
            self.cursor.execute(query, (value,))
        else:
            raise KeyError(f"Key '{key}' not found in table mapping.")

    def get_id_by_name(self, entity_name, table_name, entity_name_column, entity_id_column):
        query = f"SELECT {entity_id_column} FROM {table_name} WHERE {entity_name_column} = %s"
        self.cursor.execute(query, (entity_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def insert_relationship_based_on_key(self, key, relationship_data):
        # Define mapping from JSON keys to database table names, columns, relationship type, entity and related entity columns
        relationship_table_mapping = {
            'muscle-muscle': ('MuscleRelation', ['MuscleID', 'RelationID', 'RelationType', 'CreatorGenerated'], 'subset', ('Muscle', 'Muscle', 'MuscleID')),
            # Add more mappings as needed for other relationships
            # 'key-in-json': ('TableName', ['Column1', 'Column2', ...], 'relationshipType', ('EntityTableName', 'EntityNameColumn', 'EntityIDColumn'))
        }

        normalized_key = key.replace(" ", "").lower()

        if normalized_key in relationship_table_mapping:
            table_name, columns, relation_type, (entity_table_name, entity_name_column,
                                                 entity_id_column) = relationship_table_mapping[normalized_key]
            try:
                for super_entity, sub_entities in relationship_data.items():
                    super_entity_id = self.get_id_by_name(
                        super_entity, entity_table_name, entity_name_column, entity_id_column)
                    if not super_entity_id:
                        print(
                            f"Entity {super_entity} not found in the database.")
                        continue

                    for sub_entity in sub_entities:
                        sub_entity_id = self.get_id_by_name(
                            sub_entity, entity_table_name, entity_name_column, entity_id_column)
                        if not sub_entity_id:
                            print(
                                f"Related entity {sub_entity} not found in the database.")
                            continue

                        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (%s, %s, %s, TRUE) ON CONFLICT DO NOTHING"
                        self.cursor.execute(
                            query, (super_entity_id, sub_entity_id, relation_type))

            except Exception as e:
                print(f"An error occurred: {e}")
                self.conn.rollback()
                raise e
        else:
            raise KeyError(
                f"Key '{key}' not found in relationship table mapping.")
        
    def generate_avg_confidence_view(self, view_name, main_table, main_table_id_column, join_table1, join_table1_id_column, join_table1_display_column, join_table2, join_table2_id_column, join_table2_display_column):
        try:  
            sql_query = f"""
            CREATE OR REPLACE VIEW {view_name} AS
            WITH MaxVotes AS (
                SELECT MAX(GPTVotes) AS MaxGPTVotes
                FROM {main_table}
            ), ConfidenceScores AS (
                SELECT
                    main_table.{main_table_id_column},
                    main_table.GPTVotes,
                    (SELECT MaxGPTVotes FROM MaxVotes) - main_table.GPTVotes AS ZeroCount,
                    jsonb_array_elements(main_table.GPTLog)->>'confidence_score' AS confidence_score
                FROM 
                    {main_table} main_table
            ), Averages AS (
                SELECT
                    cs.{main_table_id_column},
                    (SUM(cs.confidence_score::numeric) + (cs.ZeroCount * 0)) / (SELECT MaxGPTVotes FROM MaxVotes) AS AverageConfidence,
                    (SELECT MaxGPTVotes FROM MaxVotes) AS MaxGPTVotes,
                    cs.GPTVotes
                FROM 
                    ConfidenceScores cs
                GROUP BY 
                    cs.{main_table_id_column}, cs.GPTVotes, cs.ZeroCount
            )
            SELECT 
                main_table.{main_table_id_column},
                main_table.CreatorGenerated,
                join_table1.{join_table1_display_column} AS JoinTable1Display,
                join_table2.{join_table2_display_column} AS JoinTable2Display,
                av.GPTVotes,
                av.MaxGPTVotes,
                av.AverageConfidence AS AdjustedGPTConfidence,
                main_table.GPTLog AS OriginalGPTLog
            FROM 
                {main_table} main_table
            JOIN 
                {join_table1} join_table1 ON main_table.{join_table1_id_column} = join_table1.{join_table1_id_column}
            JOIN 
                {join_table2} join_table2 ON main_table.{join_table2_id_column} = join_table2.{join_table2_id_column}
            LEFT JOIN 
                Averages av ON main_table.{main_table_id_column} = av.{main_table_id_column}
            ORDER BY av.AverageConfidence DESC;"""
     
              # Execute the query to create the view
            self.cursor.execute(sql_query)
            self.conn.commit()
        

        
            print(f"View {view_name} has been created successfully.")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()


   
    '''
    def load_gpt_json_data(self):
        # Read the json data from questionsandanswers folder. Inside of this folder if there is any file that begins with 'answers_' then read it in as a json fild.
        # The answers_ files are in one folder down from questionsandanswers so you have to look in each subfolder to find the answers_ files.

        for root, dirs, files in os.walk('questionsandanswers'):
            for file in files:
                if file.startswith('answers_'):
                    json_data = self.read_json_data(os.path.join(root, file))
                    self.load_gpt_data(json_data)

   
    def load_gpt_data(self, json_data):
           
        for item in json_data:
            if 'timestamp' in item:
                timestamp = item['timestamp']
            else:
                timestamp = None  # or a default timestamp if you prefer
 
            if 'gpt model engine' in item:
                gpt_engine = item['gpt model engine']
            else:
                gpt_engine = ''  # Use an empty string as default

            for key, value in item.items():
                if key not in ['timestamp', 'gpt model engine']:
                    attribute1_type = key
                    attribute1 = value
                    print("attribute 1:     " + attribute1)
                    attribute2_type = next(iter(item.keys() - {key, 'timestamp', 'gpt_engine'}))
                    print("attribute2_type:     " + attribute2_type)
                    attribute2 = item[attribute2_type]
                    print(attribute2)
                    attribute2name = attribute2['name']
                    print(attribute2name)
                    gpt_confidence = attribute2['confidence score']
                    print(gpt_confidence)
                    self.insert_gpt_log(timestamp, gpt_engine, attribute1_type, attribute1, attribute2_type, attribute2name, gpt_confidence)
                 

    def insert_gpt_log(self, timestamp, gpt_engine, attribute1_type, attribute1, attribute2_type, attribute2, gpt_confidence):
        try:
            query = f"INSERT INTO GPTLog (Datetime, GPTEngine, Attribute1Type, Attribute1, Attribute2Type, Attribute2, GPTConfidence) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, (timestamp, gpt_engine, attribute1_type, attribute1, attribute2_type, attribute2, gpt_confidence))
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e

    '''

    def load_valid_data(self, json_filepath):
        # Read the JSON data
        with open(json_filepath, 'r') as file:
            data = json.load(file)

         # Normalize JSON keys
      #  data = {key.replace(" ", "").lower(): value for key,
      #          value in data.items()}

        # Begin transaction
        self.cursor.execute("BEGIN;")

        try:
            # Iterate through the JSON keys and insert data into respective tables
            for key, values in data.items():
                if isinstance(values, list):  # Ensure that the value is a list
                    for value in values:
                        self.insert_data_based_on_key(key, value)

            # Commit transaction
            self.conn.commit()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e

    def load_valid_relationships(self, json_filepath):
        # Read the JSON data
        with open(json_filepath, 'r') as file:
            data = json.load(file)

        # Normalize JSON keys
        data = {key.replace(" ", "").lower(): value for key,
                value in data.items()}

        # Begin transaction
        self.cursor.execute("BEGIN;")

        try:
            # Iterate through the JSON keys and insert relationship data into respective tables
            for key, relationship_groups in data.items():
                if isinstance(relationship_groups, list):  # Ensure that the value is a list
                    for relationship_data in relationship_groups:
                        self.insert_relationship_based_on_key(
                            key, relationship_data)

            # Commit transaction
            self.conn.commit()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e

    def load_manualgpt_feature1_feature2_data(self, json_filepath, datefoldername, feature1, feature2):

        folder_name = json_filepath.split(
            "questionsandanswers/")[-1].split("/")[0]

        # Read the JSON data
        with open(json_filepath, 'r') as file:
            data = json.load(file)

        # Begin transaction
        self.cursor.execute("BEGIN;")
        try:
            for item in data:
                feature1_value = item[feature1]
              #  timestamp = item.get('timestamp', None)  # Use None as default if not present
              #  gpt_model_engine = item.get('gpt model engine', '')  # Use empty string as default if not present
                # support_surface_id = self.sanitize_and_check_support_surface(support_surface_name)
                feature1_id = self.sanitize_and_check_feature(
                    feature1, feature1_value)

                for feature2_item in item[feature2]:
                    # Assuming the value is under 'name'
                    feature2_value = feature2_item['name']
                    # Assuming the confidence score is required for further processing
                    gpt_confidence = feature2_item['confidence score']
                    feature2_id = self.sanitize_and_check_feature(
                        feature2, feature2_value, creator_generated=False)

                #  self.update_support_surface_body_position(support_surface_id, body_position_id, gpt_confidence, creator_generated=False)

                    featurekey = feature1.replace(
                        ' ', '') + '_' + feature2.replace(' ', '')
                    self.update_feature1_feature2(
                        featurekey, feature1_id, feature2_id, gpt_confidence, folder_name, datefoldername,  creator_generated=False)

            # Commit transaction
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e
        

    
    def get_single_feature_values_from_db(self, feature):
        feature_name = self.single_mapping[feature]["name_column"]
        feature_table = self.single_mapping[feature]["table"]
        # Construct and execute the SELECT query
        select_query = f"SELECT {feature_name} FROM {feature_table}"
        self.execute_query(select_query)
        result = self.cursor.fetchall()
        return [item[0] for item in result]
     

    def load_manualgpt_body_position_support_surface_data(self, json_filepath, datefoldername):
        # Read the JSON data
        with open(json_filepath, 'r') as file:
            data = json.load(file)

        # Begin transaction
        self.cursor.execute("BEGIN;")
        try:
            for item in data:
                body_position_name = item['body position']
                # Use None as default if not present
                timestamp = item.get('timestamp', None)
                # Use empty string as default if not present
                gpt_model_engine = item.get('gpt model engine', '')
                body_position_id = self.sanitize_and_check_body_position(
                    body_position_name)

                for support_surface in item['support surface']:
                    support_surface_name = support_surface['name']
                    gpt_confidence = support_surface['confidence score']
                    support_surface_id = self.sanitize_and_check_support_surface(
                        support_surface_name, creator_generated=False)

                   # self.update_support_surface_body_position(support_surface_id, body_position_id, gpt_confidence, creator_generated=False)
                    self.update_support_surface_body_position(
                        support_surface_id, body_position_id, gpt_confidence, gpt_model_engine, timestamp, creator_generated=False)

            # Commit transaction
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            raise e

    def load_json(self, json_data, youtubevideoId: str, insertnewrelations=False):
        # print(json_data)
        # Parse JSON data
        print("WHAAAT")
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

            mechanics = json_data['exercise_mechanics']
            if mechanics:  # check if mechanics data is present
                mechanics_id = self.sanitize_and_check_mechanics(mechanics)
                self.update_exercise_mechanics(exercise_id, mechanics_id)

                # Inside load_json method
            joint_usage = json_data.get('joint_usage', '')
            if joint_usage:  # check if joint_usage data is present
                joint_usage_id = self.sanitize_and_check_joint_usage(
                    joint_usage)
                self.update_exercise_joint_usage(exercise_id, joint_usage_id)

                # Inside load_json method
            sides_data = json_data.get('sides', '')
            if sides_data:  # check if sides data is present
                sides_id = self.sanitize_and_check_sides(sides_data)
                self.update_exercise_sides(exercise_id, sides_id)

            opt_model_phases = json_data.get('OPT_model_phases', [])
            for opt_phase in opt_model_phases:
                opt_id = self.sanitize_and_check_opt(opt_phase)
                self.update_exercise_opt(exercise_id, opt_id)

                # Inside load_json method
            exercise_categories = json_data.get('exercise_category', [])
            for category in exercise_categories:
                category_id = self.sanitize_and_check_category(category)
                self.update_exercise_category(exercise_id, category_id)

            corrective_exercises = json_data.get('corrective_exercise', [])
            for corrective in corrective_exercises:
                corrective_id = self.sanitize_and_check_corrective(corrective)
                self.update_exercise_corrective(exercise_id, corrective_id)

            contraindications = json_data.get('contraindications', [])
            for contraindication in contraindications:
                contraindication_id = self.sanitize_and_check_contraindication(
                    contraindication)
                self.update_exercise_contraindication(
                    exercise_id, contraindication_id)

            sports_relevance = json_data.get('sports_relevance', [])
            for sport in sports_relevance:
                sport_id = self.sanitize_and_check_sport(sport)
                self.update_exercise_sport(exercise_id, sport_id)

            tags = json_data.get('additional_tags', [])
            if tags:
                self.update_exercise_tags(exercise_id, tags)

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
