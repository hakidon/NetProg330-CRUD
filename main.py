import sqlite3
import json
from flask import *
from urllib.parse import urljoin
import requests

# progress
# -Done display table using rest 

# to do
# - crud on admin


app = Flask(__name__)
app.secret_key = 'yoursecretkey'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

def connect_to_db():
    conn = sqlite3.connect('330_project.db')
    return conn

def prepare_api(api_endpoint):
    return urljoin(request.url_root, api_endpoint)

def check_session(type):
    username = session.get('session_id')
    login_type = session.get('login_type')

    if not username or login_type != type:
        session.clear()
        return False
    return True

    # if not username or login_type != type:
    #     return 'tre'
    # else:
    #     return 'fal'

    
def check_admin(username):
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM admin_auth WHERE Username = ?', (username,))
    admin = cur.fetchone()

    if admin:
        return True
    else:
        return False

@app.route('/logout') 
def logout():
    session.clear()
    return redirect('/')


@app.route('/', methods=['GET', 'POST']) 
def main():
    if request.method == 'GET':
        temp_success_insert = session.get('insert_employee', '')
        session.clear()
        return render_template('login.html', success_signup=temp_success_insert)
    elif request.method == 'POST':
        name = request.form['username']
        passw = request.form['password']

        # get username and password admin from admin table 
        # auth 
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM admin_auth where Username = ? and Password = ?',(name, passw))
        admin = cur.fetchone()
        cur.execute('SELECT * FROM employee_info where Username = ? and Password = ?',(name, passw))
        employee = cur.fetchone()
        if admin or employee:
            # Admin is authenticated
            session['session_id'] = name
            if admin:
                session['login_type'] = 'admin'
                return redirect('/admin/view') 
            else:
                session['login_type'] = 'employee'
                return redirect('/employee/view') 
        else:
            return render_template('login.html', fail_signin=1)

@app.route('/employee/signup', methods=['POST']) 
def signup():
    data = request.form
    if not data:
        return redirect('/') 
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('INSERT INTO employee_info ("employee name", "Academic qualification", gender, email, address, Username, Password) VALUES (?,?,?,?,?,?,?)', (data['name'], data['academic_qualification'], data['gender'], data['email'], data['address'], data['username'], data['password']))
    conn.commit()
    session['insert_employee'] = True
    return redirect('/')

@app.route('/employee/view', methods=['GET', 'POST']) 
def employee_view():
    if not check_session('employee'):
        return redirect('/')

    # return render_template('view.html')
    # data = request.form
    # if not data:
    #     return redirect('/') 
    
    # conn = connect_to_db()
    # conn.row_factory = sqlite3.Row
    # cur = conn.cursor()
    
    # cur.execute('INSERT INTO employee_info ("employee name", "Academic qualification", gender, email, address, Username, Password) VALUES (?,?,?,?,?,?,?)', (data['name'], data['academic_qualification'], data['gender'], data['email'], data['address'], data['username'], data['password']))
    # conn.commit()
    # session['insert_employee'] = True
    # return redirect('/')

@app.route('/admin/view',  methods=['GET', 'POST']) 
def admin_view():
    if not check_session('admin'):
        return redirect('/')
    username = session.get('session_id')
    if check_admin(username):
        response = requests.get(prepare_api('/api/employee'))
        if request.method == 'POST':
            conn = connect_to_db()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            data = request.form
            submit_type = data['submit_type']
            if submit_type == 'add':
                cur.execute('INSERT INTO employee_info ("employee name", "Academic qualification", gender, email, address, Username, Password) VALUES (?,?,?,?,?,?,?)', (data['name'], data['academic_qualification'], data['gender'], data['email'], data['address'], data['username'], data['password']))
                conn.commit()
                session['insert_admin'] = True
                return redirect('/admin/view')
            elif submit_type == 'edit':
                cur.execute('UPDATE employee_info SET "employee name" = ?, "Academic qualification" = ?, gender = ?, email = ?, address = ?, Username = ?, Password = ? WHERE "employee id" = ?', (data['name'], data['academic_qualification'], data['gender'], data['email'], data['address'], data['username'], data['password'], data['employee_id']))                
                conn.commit()
                session['edit_admin'] = True
                return redirect('/admin/view')
            elif submit_type == 'delete':
                cur.execute('DELETE FROM employee_info WHERE "employee id"=?', ( data['employee_id'],))
                conn.commit()
                session['delete_admin'] = True
                return redirect('/admin/view')
        elif request.method == 'GET':
            temp_success_insert = session.get('insert_admin', '')
            if temp_success_insert:
                session.pop('insert_admin', '')

            temp_success_edit = session.get('edit_admin', '')
            if temp_success_edit:
                session.pop('edit_admin', '')

            temp_success_delete = session.get('delete_admin', '')
            if temp_success_delete:
                session.pop('delete_admin', '')

            return render_template('employee_table.html', employee_data=response.json(), success_insert=temp_success_insert, success_edit=temp_success_edit, success_delete=temp_success_delete)
    else:
        session.clear()
        return redirect('/')

# @app.route("/success")
# def success():
#     return render_template('success.html')

# @app.route('/test', methods=['POST']) 
# def test():
#     name = request.form['username']
#     passw = request.form['password']
#     # return 'name: {} - password:{}'.format(name, passw)
#     response = requests.get(prepare_api('/api/employee/2'))
#     return response.json()


@app.route('/api/employee')
def get_employee_all():
    employee_list = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM employee_info')
        rows = cur.fetchall()
        employees = [dict(row) for row in rows]
        return json.dumps(employees)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/employee/')
def redirect_to_all():
    return redirect('/api/employee')

@app.route('/api/employee/<employee_id>', methods=['GET', 'DELETE', 'POST'])
def func_employee(employee_id=None):
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    if request.method == 'GET':
        # View Employee
        try:
            # cur.execute('SELECT "employee id", "employee name", "gender", "email", "address", "Academic qualification" FROM employee_info  WHERE "employee id"=?', (employee_id,))
            cur.execute('SELECT * FROM employee_info  WHERE "employee id"=?', (employee_id,))
            rows = cur.fetchone()

            if rows:
                return jsonify(dict(rows))
            else:
                return render_template('404.html'), 404
        except Exception as e:
            return jsonify({'error': str(e)})
    elif request.method == 'DELETE':
        # Delete Employee
        try:
            cur.execute('DELETE FROM employee_info WHERE "employee id"=?', (employee_id,))
            conn.commit()
            return jsonify({'message': 'Employee Deleted Successfully'})
        except Exception as e:
            return jsonify({'error': str(e)})
    elif request.method == 'POST':
        try:
            column_mapping = {
                'employee_name': '"employee name"',
                'employee_gender': 'gender',
                'employee_email': 'email',
                'employee_address': 'address',
                'employee_academic_qualification': '"Academic qualification"',
                'employee_username': 'Username',
                'employee_password': 'Password'
            }
            data = request.get_json()
            cur.execute('SELECT * FROM employee_info WHERE "employee id"=?', (employee_id,))
            if cur.fetchone():
                # Update Employee
                update_query = 'UPDATE employee_info SET'
                update_values = []
                for key, value in data.items():
                    if key in column_mapping:
                        update_query += f' {column_mapping[key]}=?,'
                        update_values.append(value)
                update_query = update_query[:-1] + ' WHERE "employee id"=?'
                update_values.append(employee_id)
                cur.execute(update_query,update_values)
                conn.commit()
                return jsonify({'message': 'Employee Updated Successfully'})
            else:
                # Create Employee
                cur.execute('INSERT INTO employee_info ("employee name", gender, email, address, "Academic qualification", Username, Password) VALUES (?,?,?,?,?,?,?)', (data['employee_name'], data['employee_gender'], data['employee_email'], data['employee_address'], data['employee_academic_qualification'], data['employee_username'], data['employee_password']))
                conn.commit()
                return jsonify({'message': 'Employee Created Successfully'})
        except Exception as e:
            return jsonify({'error': str(e)})
if __name__ =='__main__':  
    app.run(debug = True)  



    