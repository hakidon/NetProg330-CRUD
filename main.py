import sqlite3

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
    employees = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM employee_info")
        rows = cur.fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({'error': str(e)})


# def get_user_by_id(user_id):
#     user = {}
#     try:
#         conn = connect_to_db()
#         conn.row_factory = sqlite3.Row
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM users WHERE user_id = ?", 
#                        (user_id,))
#         row = cur.fetchone()

#         # convert row object to dictionary
#         user["user_id"] = row["user_id"]
#         user["name"] = row["name"]
#         user["email"] = row["email"]
#         user["phone"] = row["phone"]
#         user["address"] = row["address"]
#         user["country"] = row["country"]
#     except:
#         user = {}

#     return user

if __name__ =='__main__':  
    app.run(debug = True)  



    