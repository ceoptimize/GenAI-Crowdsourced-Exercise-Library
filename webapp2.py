from flask import Flask, render_template, request
from postgres import PostgresDatabase

app = Flask(__name__)

# Connect to your PostgreSQL database
postgres = PostgresDatabase()
conn = postgres.conn

# Define the route for the index page
@app.route('/')
def index():
    return render_template('index2.html')

# Define the route for the table page
@app.route('/table')
def table():
    # Get the filter values from the query string
    filter_params = {}
    for key, value in request.args.items():
        if key.startswith('filter_'):
            filter_params[key[7:]] = value

    # Construct the WHERE clause for filtering
    where_clause = ""
    filter_values = []
    for field, value in filter_params.items():
        if value:
            where_clause += f" AND {field} = %s"
            filter_values.append(value)

    # Get the sort column and order from the query string
    sort_column = request.args.get('sort_column', 'ExerciseID')
    sort_order = request.args.get('sort_order', 'asc')

    # Construct the SQL query with filters and sorting
    query = f"""
        SELECT * FROM (SELECT
            e.ExerciseID,
            e.ExerciseName,
            e.ExerciseDifficulty,
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
            LEFT JOIN YoutubeVideo yv ON ey.YoutubeVideoID = yv.VideoID) as mytable
        WHERE 1 = 1 {where_clause}
        ORDER BY {sort_column} {sort_order};
    """

    # Execute the SQL query with filter values
    cursor = conn.cursor()
    cursor.execute(query, filter_values)

    # Fetch all rows from the result
    table = cursor.fetchall()

    # Get the column names
    column_names = [desc[0] for desc in cursor.description]

    # Close the cursor
    cursor.close()

    return render_template('table.html', table=table, column_names=column_names,
                           sort_column=sort_column, sort_order=sort_order,
                           filter_params=filter_params)

if __name__ == '__main__':
    app.run(debug=True)
