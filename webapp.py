from flask import Flask, request, render_template
import psycopg2
import psycopg2.extras
from loguru import logger

from flask import Flask, render_template, request
import psycopg2
import urllib.parse as urlparse
import os

app = Flask(__name__)

# PostgreSQL connection parameters.
params = {
    "host": '<host>',
    "database": '<database>',
    "user": '<user>',
    "password": '<password>'
}

# Establish connection.
conn = psycopg2.connect(**params)

@app.route('/', methods=['GET'])
def index():
    order_by = request.args.get('order_by', 'Exercise')
    order_type = request.args.get('order_type', 'asc')
    search = request.args.get('search', '')

    with conn.cursor() as cursor:
        sql_query = """
        SELECT * FROM Exercises 
        WHERE Exercise ILIKE %s 
        ORDER BY {} {}
        """.format(order_by, order_type)

        cursor.execute(sql_query, ('%' + search + '%',))
        rows = cursor.fetchall()

    return render_template('index.html', rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)



host="localhost"
dbname="mydatabase"
user="postgres"
password="C$g$9292greer"



app = Flask(__name__)

conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port="5432"
)

@app.route('/')
def index():
    # Get the filter parameters from the query string
    exercise_filter = request.args.get('exercise')
    body_parts_filter = request.args.get('body_parts')
    equipment_filter = request.args.get('equipment')

    # Construct the SQL query based on the filter parameters
    query = "SELECT * FROM EXERCISELIBRARY  WHERE 1=1"
    if exercise_filter:
        query += f" AND exercise = '{exercise_filter}'"
    if body_parts_filter:
        query += f" AND body_parts_worked = '{body_parts_filter}'"
    if equipment_filter:
        query += f" AND equipment_used = '{equipment_filter}'"

    # Apply sorting based on the "sort" query parameter
    sort_by = request.args.get('sort')
    if sort_by:
        query += f" ORDER BY {sort_by}"

    # Execute the query
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        entries = cursor.fetchall()

         # Close the cursor
        cursor.close()
    except psycopg2.Error as e:
        conn.rollback()  # Rollback the transaction to recover from the error
        print("Error executing the SQL query:", e)
    # Render the template with the entries
    return render_template('index.html', entries=entries)

def get_db():
    try: 
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port="5432"
        )
        return conn
    except Exception:
        logger.exception("An error occurred!")

@app.route('/exercises', methods=['GET'])
def get_exercises():
    try:
         # Get query parameters for sorting and filtering
         #logger.debug('Entering get_exercises route') # Log a debug message
         sort_by = request.args.get('sort_by', default='exercise', type=str)
         body_part = request.args.get('body_parts', default=None, type=str)
         equipment = request.args.get('equipment_used', default=None, type=str)
    except Exception:
        logger.exception("An error occurred!")
    # Query the database
    conn = get_db()
    print("success")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = f"SELECT * FROM EXERCISELIBRARY "
    params = []
    if body_part or equipment:
        query += "WHERE "
        if body_part:
            query += f"\"body_parts\" = %s "
            params.append(body_part)
        if equipment:
            if body_part:
                query += "AND "
            query += f"\"equipment_used\" = %s "
            params.append(equipment)
    query += f"ORDER BY \"{sort_by}\""
    cur.execute(query, params)

    # Return a list of exercises
    exercises = cur.fetchall()
    return { 'exercises': exercises }

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)

