import sqlite3
import json 
from flask import Flask, jsonify
app = Flask(__name__) #creating the Flask class object   

def connect_to_db():
    conn = sqlite3.connect('330_project.db')
    return conn

@app.route('/') 
def test_con():
    try:
        conn = connect_to_db()
        return "Connection established!"
    except:
        return "Fail"
    finally:
        conn.close()

@app.route('/view') 
def get_employee():
    employee_list = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM employee_info")
        rows = cur.fetchall()
        employees = [dict(row) for row in rows]
        return json.dumps(employees)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ =='__main__':  
    app.run(debug = True)  



    