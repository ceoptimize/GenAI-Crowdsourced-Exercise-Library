import psycopg2
import json
import openai

# Connect to the PostgreSQL database
conn = psycopg2.connect(host="localhost", dbname="mydatabase", user="postgres", password="C$g$9292greer")
print(conn)

# Create a table to store the JSON results
cur = conn.cursor()
print("hello")
table = ""

#cur.execute("CREATE TABLE CHATGPTRESULTS (id SERIAL PRIMARY KEY, conversation_id TEXT, message TEXT)")
cur.execute("DROP TABLE CHATGPTRESULTS")
#cur.execute("CREATE TABLE someinfo (name TEXT, age INT, city TEXT)")
cur.execute("CREATE TABLE CHATGPTRESULTS (exercise TEXT, bodyparts text)")

# Read the ChatGPT JSON results from a file
#with open("example.json", "r") as f:
 #   results = json.load(f)
with open("jsonoutput.json", "r") as f:
    results = json.load(f)

# Insert each JSON object into the database
#for result in results:
#    name = result["name"]
#    age= result["age"]
#    city= result["city"]
  #  cur.execute("INSERT INTO chat_results (conversation_id, message) VALUES (%s, %s)", (conversation_id, message))
#    cur.execute("INSERT INTO someinfo (name, age, city) VALUES (%s, %s, %s)", (name, age, city))

for result in results:
    exercise = result["Exercise"]
    bodyparts= result["Body parts worked"]
    cur.execute("INSERT INTO CHATGPTRESULTS (exercise, bodyparts) VALUES (%s, %s)", (exercise, bodyparts))
# Commit the changes and close the database connection
cur.execute("SELECT * FROM CHATGPTRESULTS WHERE EXERCISE = 'Bicep curls'")
for row in cur:
    print(row)
conn.commit()
conn.close()

import requests
import json
import psycopg2

