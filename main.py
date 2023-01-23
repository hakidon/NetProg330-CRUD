import sqlite3

from flask import Flask
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
        return rows
        # # convert row objects to dictionary
        # for i in rows:
        #     employee = {}
        #     employee["employee name"] = i["employee name"]
        #     employee["gender"] = i["gender"]
        #     employee["email"] = i["email"]
        #     employee["address"] = i["address"]
        #     employee["Academic qualification"] = i["Academic qualification"]
        #     employee["Username"] = i["Username"]
        #     employee["Password"] = i["Password"]

        #     employees.append(employee)

    except:
        employees = []
        return 'asdas'

    # return employees


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



    