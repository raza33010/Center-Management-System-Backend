import os
from flask import Flask, request, flash, jsonify, make_response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField, DecimalField, DateField, TimeField, PasswordField, SelectMultipleField
from datetime import datetime
from flask_wtf.file import FileField, FileAllowed, FileRequired
from collections import OrderedDict
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'
app.config['UPLOADED_DIRECTORY'] = 'uploads/'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.pdf']
# app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['CORS_ALLOW_ALL_ORIGINS'] = True
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# CORS(app, resources={r"/add_users": {"origins": "http://localhost:3000"}})
mysql = MySQL(app)

@app.route('/dropdown_center_id', methods=['GET'])
def get_all_cenyter_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM user")
    users = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for user in users:
        user_dict = dict(zip(column_names, user))
        data_with_columns.append(user_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


# Login Apis #...........................................................   ...


@app.route('/login', methods=['POST'])
def add_users():
    # form = UserForm(request.form)
    data = request.get_json()
  
    # if form.validate():
    email = data.get('email')
    password = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()
    print(user)
    if user:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        user_dict = dict(zip(column_names,user))
        data = {'code': '200', 'status': 'true', 'data': user_dict}
        return jsonify(data)
    else:
            # Authentication failed
        return jsonify({'status': 'false', 'message': 'Invalid email or password'}), 401

    # # Handle the case where form validation fails
    # return jsonify({'status': 'false', 'message': 'Invalid form data'}), 400

# Center Apis #..............................................................
class CenterForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())
    phone_no = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])
    address = StringField('Address', [validators.InputRequired()])




@app.route('/add_center', methods=['POST'])
def add_center():
    form = CenterForm(request.form)
    if form.validate():
        name = form.name.data
        logo = request.files['logo']
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        address = form.address.data
        phone_no = form.phone_no.data
        filename=logo.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
        logo.save(f'uploads/{logo.filename}')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO center(name, logo, status, created_at, updated_at, address, phone_no) VALUES( %s, %s, %s, %s, %s, %s, %s)", (name, str(filename), status, created_at, updated_at, address, phone_no))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'Center added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
        
@app.route('/center/<int:center_id>', methods=['GET'])
def get_center(center_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM center WHERE id=%s", (center_id,))
    center = cur.fetchone()
    cur.close()

    if center:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        center_dict = dict(zip(column_names, center))

        response = {'code': '200', 'status': 'true', 'data': center_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Center not found'}
        return jsonify(response)

@app.route('/center_id', methods=['GET'])
def get_all_centers_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM center")
    centers = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for center in centers:
        center_dict = dict(zip(column_names, center))
        data_with_columns.append(center_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/center', methods=['GET'])
def get_all_centers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM center")
    centers = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for center in centers:
        center_dict = dict(zip(column_names, center))
        data_with_columns.append(center_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM center")
    # centers = cur.fetchall()
    # cur.close()
    
    # print(centers)

    # response = {'code': '200', 'status': 'true', 'data': centers}
    # return jsonify(response)

@app.route('/del_center/<int:id>', methods=['DELETE'])
def delete_center(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM center WHERE id=%s", (id,))
    center = cur.fetchone()
    if center:
        logo_path = center[2]
        # delete the center from the database
        cur.execute("DELETE FROM center WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the center's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'Center with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'Center with id {id} not found'})


@app.route('/upd_center/<int:center_id>', methods=['PATCH'])
def update_center(center_id): 
    form = CenterForm(request.form)
    if form.validate():
        name = form.name.data
        logo = request.files['logo']
        status = form.status.data
        updated_at = form.updated_at.data
        address = form.address.data
        phone_no = form.phone_no.data                
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id=%s", (center_id,))
        center = cur.fetchone()

        if not center:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'Center not found'}
            return jsonify(final_response)
        else:
            logo_path = center[2]
            if logo_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
            filename = logo.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
            logo.save(f'uploads/{filename}')


        cur.execute("UPDATE center SET name=%s, logo=%s, status=%s, updated_at=%s, address=%s, phone_no=%s, WHERE id=%s", (name, filename, status, updated_at, address, phone_no, center_id))
        mysql.connection.commit()
        cur.close()
        
        response = {'code': '200', 'status': 'true', 'message': 'Center updated successfully'}
        return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# # Accounts Apis #..............................................................
# class AccountForm(Form):
#     center_id = IntegerField('Center ID', [validators.InputRequired()])
#     user_id = IntegerField('User ID', [validators.InputRequired()])
#     description = StringField('Description')
#     account_id = IntegerField('Bank ID', [validators.InputRequired()])
#     amount = DecimalField('Amount', [validators.InputRequired()])
#     transaction_id = StringField('Transaction ID')
#     transaction_type = StringField('Transaction Type')
#     status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
#     created_at = DateTimeField('Created At', default=datetime.utcnow)
#     updated_at = DateTimeField('Updated At', default=datetime.utcnow)

# @app.route('/add_account', methods=['POST'])
# def add_account():
#     form = AccountForm(request.form)
#     if form.validate():       
#         center_id = form.center_id.data
#         user_id = form.user_id.data
#         description = form.description.data
#         bank_id = form.bank_id.data
#         amount = form.amount.data
#         transaction_id = form.transaction_id.data
#         transaction_type = form.transaction_type.data
#         status = form.status.data
#         created_at = form.created_at.data
#         updated_at = form.updated_at.data

#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
#         result = cur.fetchone()
#         cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
#         result_1 = cur.fetchone()
#         if result and result_1:
#             cur.execute("INSERT INTO account(center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, created_at, updated_at))
#             mysql.connection.commit()
#             cur.close()
#             response = {'code': '200', 'status': 'true', 'message': 'account added successfully'}
#             return jsonify(response)
#         else:
#             response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
#             return jsonify(response)
#     else:
#         response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
#         return jsonify(response)



# @app.route('/account/<int:account_id>', methods=['GET'])
# def get_account(account_id):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
#     account = cur.fetchone()
#     cur.close() bank

#     if account:
#         column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

#         account_dict = dict(zip(column_names, account))

#         response = {'code': '200', 'status': 'true', 'data': account_dict}
#         return jsonify(response)
#     else:
#         response = {'code': '400', 'status': 'false', 'message': 'Center not found'}
#         return jsonify(response)

# @app.route('/account', methods=['GET'])
# def get_all_account():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM account")
#     accounts = cur.fetchall()
#     column_names = [desc[0] for desc in cur.description]
#     cur.close()
#     data_with_columns = []
#     for account in accounts:
#         account_dict = dict(zip(column_names, account))
#         data_with_columns.append(account_dict)

#     response = {
#         "code": "200",
#         "data": data_with_columns,
#         "status": "true"
#     }

#     return jsonify(response)

# @app.route('/del_account/<int:id>', methods=['DELETE'])
# def delete_account(id):
#     cur = mysql.connection.cursor()
#     account = cur.execute("DELETE FROM account WHERE id= %s", (id,))
#     mysql.connection.commit()

#     if account:
#         return jsonify({'message': f'result with id {id} deleted successfully'})
#     else:
#         return jsonify({'message': f'result with id {id} not found'})


# @app.route('/upd_account/<int:account_id>', methods=['PUT'])
# def update_account(account_id):
#     form = AccountForm(request.form)
#     if form.validate():
#         center_id = form.center_id.data
#         user_id = form.user_id.data
#         description = form.description.data
#         bank_id = form.bank_id.data
#         amount = form.amount.data
#         transaction_id = form.transaction_id.data
#         transaction_type = form.transaction_type.data
#         status = form.status.data
#         updated_at = form.updated_at.data

#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
#         account = cur.fetchone()

#         if not account:
#             cur.close()
#             final_response = {'code': '404', 'status': 'false', 'message': 'account not found'}
#             return jsonify(final_response)
#         else:
#             cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
#             result = cur.fetchone()
#             cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
#             result_1 = cur.fetchone()
#             if result and result_1:
#                 cur.execute("UPDATE account SET center_id=%s, user_id=%s, description=%s, bank_id=%s, amount=%s, transaction_id=%s, transaction_type=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, updated_at, account_id))
#                 mysql.connection.commit()
#                 cur.close()
#                 response = {'code': '200', 'status': 'true', 'message': 'account updated successfully'}
#                 return jsonify(response)
#             else:
#                 response = {'code': '400', 'status': 'false', 'message': 'account not updated successfully'}
#                 return jsonify(response)
#     else:
#         final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
#         return jsonify(final_response)

# Users Apis #..............................................................
class UserForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    role_id = StringField('Name', [validators.InputRequired()])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.InputRequired(),
        validators.Length(min=8, message='Password must be at least 8 characters long')
    ])
    phone_no = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])

class UPDUserForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    role_id = StringField('Name', [validators.InputRequired()])

    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ], default=1)
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.InputRequired(),
        validators.Length(min=8, message='Password must be at least 8 characters long')
    ])
    phone_no = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])


@app.route('/add_user', methods=['POST'])
def add_user():
    form = UserForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        role_id = form.role_id.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        email = form.email.data
        password = form.password.data        
        phone_no = form.phone_no.data

        
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO user(center_id, name, role_id, created_at, updated_at, email, password, phone_no) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (center_id, name, role_id, created_at, updated_at, email, password, phone_no))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'user added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'user addition failed'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

    
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # print(user_id)
    cur = mysql.connection.cursor()
    sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({user_id}) GROUP BY u.id"
    cur.execute(sql)    
    user = cur.fetchone()
    list(user)
    # print(user[-1])
    cur.close()

    if user:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        user_dict = dict(zip(column_names, user))

        response = {'code': '200', 'status': 'true', 'data': user_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)

@app.route('/user_ids/<int:center_id>', methods=['GET'])
def get_all_user_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT id, name 
    FROM user 
    WHERE center_id=%s AND role_id NOT IN (0, 2)
""", (center_id,))
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/user_ids', methods=['POST'])
def get_all_userses():
    data = request.get_json()
    center_id = data.get('center_id')
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT id, name FROM user WHERE FIND_IN_SET(4, role_id) > 0 AND center_id = {center_id}")
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/user', methods=['POST'])
def get_all_users():
    data = request.get_json()
    center_id = data.get('center_id')
    role_id = list(data.get('role_id'))
    role = data.get('role')
    print(role_id)
    cur = mysql.connection.cursor()
    print(role)

    cur.execute("SELECT id, center_id, role_id FROM user WHERE id <> 1")
    role1 = list(cur.fetchall())
    print(role1)
    abbas = []
    abbas2 = []
    abbas3 = []    
    # print(type(abbas1[-2]))
    for i in range(len(role1)):
        abbas1 = role1[i]
        # all(role_id in abbas1[-1].split(',') for role_id in role_id_list)
        if '2' in abbas1[-1]:
            abbas.append(abbas1[0])
        elif "4" in abbas1[-1]:
            abbas3.append(abbas1[0])
        else:
            abbas2.append(abbas1[0])
    abbas2 += abbas3
    print(abbas)
    print(abbas2)
    print(abbas3)

    placeholders_1 = ', '.join(['%s'] * len(abbas))
    placeholders_2 = ', '.join(['%s'] * len(abbas2))
    placeholders_3 = ', '.join(['%s'] * len(abbas3))
    if '0' in role_id:
        if role == "coo":
            sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({placeholders_1}) GROUP BY u.id"
            cur.execute(sql)
        elif role == 'user':
            sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({placeholders_2}) GROUP BY u.id"
            cur.execute(sql, abbas2)
        elif role == 'teacher':
            sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({placeholders_3}) GROUP BY u.id"
            cur.execute(sql, abbas3)    
    elif '2' in role_id:
        if role == "coo":
            sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({placeholders_1}) GROUP BY u.id"
            cur.execute(sql, abbas)
        elif role == 'user':
            sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({placeholders_2}) AND u.center_id = {center_id} GROUP BY u.id"
            cur.execute(sql, abbas2)
        elif role == 'teacher':
            sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM user u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({placeholders_3}) AND u.center_id = {center_id} GROUP BY u.id"
            cur.execute(sql, abbas3)
        
        
    users = cur.fetchall()
    print(users)
    
    column_names = [desc[0] for desc in cur.description]
    cur.close()

    data_with_columns = []
    for user in users:
        user_dict = dict(zip(column_names, user))
        # Split the role_names into a list
        user_dict['role_names'] = user_dict['role_names'].split(',')
        data_with_columns.append(user_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/del_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    cur = mysql.connection.cursor()
    user = cur.execute("DELETE FROM user WHERE id= %s", (id,))
    mysql.connection.commit()

    if user:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})



# @app.route('/upd_user/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     form = UPDUserForm(request.form)
#     if not form.validate():
#         for field, errors in form.errors.items():
#             for error in errors:
#                 flash(f"{field}: {error}", "error")
#         return jsonify(success=False, errors=form.errors)
#     else:
#         return jsonify('abbas')
#     ...
@app.route('/upd_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    print(user_id)
    form = UPDUserForm(request.form)
    center_id = form.center_id.data
    print(form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        role_id = form.role_id.data
        status = form.status.data
        updated_at = form.updated_at.data
        email = form.email.data
        password = form.password.data
        phone_no = form.phone_no.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'user not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            if result:
                cur.execute("UPDATE user SET center_id=%s, name=%s, role_id=%s, status=%s, updated_at=%s, email=%s, password=%s , phone_no=%sWHERE id=%s", (center_id, name, role_id, status, updated_at, email, password, phone_no, user_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'user updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'user not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)
    
    
# Batch Apis #..............................................................
class BatchForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    year = StringField('Year', [validators.InputRequired()])
    # status = IntegerField('Status', [
    #     validators.InputRequired(),
    #     validators.AnyOf([0, 1], 'Must be 0 or 1')
    # ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

class UBatchForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    year = StringField('Year', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)


@app.route('/add_batch', methods=['POST'])
def add_batch():
    form = BatchForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        year = form.year.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        
        if result:
            cur.execute("INSERT INTO batch(center_id, name, created_at, updated_at, year) VALUES( %s, %s, %s, %s, %s)", (center_id, name, created_at, updated_at, year))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'Batch added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)


@app.route('/batch_ids/<int:center_id>', methods=['GET'])
def get_batch_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT id,name FROM batch WHERE batch.center_id={center_id}")
    batch = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for batch in batch:
        batch_dict = dict(zip(column_names, batch))
        data_with_columns.append(batch_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)
    
@app.route('/batch/<int:batch_id>', methods=['GET'])
def get_batch(batch_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM batch WHERE id=%s", (batch_id,))
    batch = cur.fetchone()
    cur.close()

    if batch:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        batch_dict = dict(zip(column_names, batch))

        response = {'code': '200', 'status': 'true', 'data': batch_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'batch not found'}
        return jsonify(response)

@app.route('/batch', methods=['POST'])
def get_all_batch():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == '0':
        cur.execute("SELECT * FROM batch")
    else:
        cur.execute(f"SELECT * FROM batch WHERE Center_id = {center_id}")
    batch = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for batch in batch:
        batch_dict = dict(zip(column_names, batch))
        data_with_columns.append(batch_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_batch/<int:id>', methods=['DELETE'])
def delete_batch(id):
    cur = mysql.connection.cursor()
    user = cur.execute(f"DELETE FROM batch WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if user > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'batch found', 'data': user}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'batch not found', 'data': user}
        return jsonify(final_response)


@app.route('/upd_batch/<int:batch_id>', methods=['PUT'])
def update_batch(batch_id):
    form = UBatchForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        year = form.year.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM batch WHERE id=%s", (batch_id,))
        batch = cur.fetchone()

        if not batch:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'batch not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()

            if result:
                cur.execute("UPDATE batch SET center_id=%s, name=%s, status=%s, updated_at=%s, year=%s WHERE id=%s", (center_id, name, status, updated_at, year, batch_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'batch updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'batch not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Class Apis #..............................................................
class ClassForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    total_students = IntegerField('Total Students', [validators.InputRequired()])
    subjects_id = StringField('Subjects ID', [validators.InputRequired()])
    # status = IntegerField('Status', [
    #     validators.InputRequired(),
    #     validators.AnyOf([0, 1], 'Must be 0 or 1')
    # ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)
class UClassForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    total_students = IntegerField('Total Students', [validators.InputRequired()])
    subjects_id = StringField('Subjects ID', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_class', methods=['POST'])
def add_class():
    form = ClassForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        total_students = form.total_students.data        
        subjects_id = form.subjects_id.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO class(center_id, name, total_students, subjects_id, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, name, total_students, subjects_id, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'class added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'class addition failed'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

    
@app.route('/class/<int:class_id>', methods=['GET'])
def get_class(class_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT
    c.*,
    GROUP_CONCAT(s.name) AS subject_names
FROM class c
JOIN subject s ON FIND_IN_SET(s.id, c.subjects_id) > 0
WHERE c.id = {class_id}
GROUP BY c.id ;

    """)
    subject = cur.fetchone()
    cur.close()

    if subject:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        subject_dict = dict(zip(column_names, subject))

        response = {'code': '200', 'status': 'true', 'data': subject_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)


@app.route('/class_ids/<int:center_id>', methods=['GET'])
def get_all_class_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM class WHERE center_id=%s",(center_id,))
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/class', methods=['POST'])
def get_all_class():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == '0':
        cur.execute(f"""
            SELECT
        c.*,
        GROUP_CONCAT(s.name) AS subject_names
    FROM class c
    JOIN subject s ON FIND_IN_SET(s.id, c.subjects_id) > 0
    GROUP BY c.id ;

        """)
        
    else: 
        cur.execute(f"""
            SELECT
        c.*,
        GROUP_CONCAT(s.name) AS subject_names
    FROM class c
    JOIN subject s ON FIND_IN_SET(s.id, c.subjects_id) > 0
    WHERE c.center_id = {center_id}
    GROUP BY c.id ;

        """)
    subjects = cur.fetchall()
    print(subjects)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for subject in subjects:
        user_dict = dict(zip(column_names, subject))
        # Split the role_names into a list
        user_dict['subject_names'] = user_dict['subject_names'].split(',')
        data_with_columns.append(user_dict)


    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/del_class/<int:id>', methods=['DELETE'])
def delete_class(id):
    cur = mysql.connection.cursor()
    uclass = cur.execute(f"DELETE FROM class WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if uclass > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'class found', 'data': uclass}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'class not found', 'data': uclass}
        return jsonify(final_response)


@app.route('/upd_class/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    form = UClassForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        total_students = form.total_students.data        
        subjects_id = form.subjects_id.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM class WHERE id=%s", (class_id,))
        uclass = cur.fetchone()

        if not uclass:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'class not found'}
            return jsonify(final_response)
        else:
            cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()  # Fetch a single row

            if result:
                cur.execute("UPDATE class SET center_id=%s, name=%s, total_students=%s, subjects_id=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, total_students, subjects_id, status, updated_at, class_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'class updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'class not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Duty Apis #..............................................................
class DutyForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    user_id = StringField('User Id', [validators.InputRequired()])
    job = StringField('Job', [validators.InputRequired()])
    date = DateField('Date')
    duty_time = StringField('duty_time')
    description = StringField('Assigned By', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')],default = 1)
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_duty', methods=['POST'])
def add_duty():
    form = DutyForm(request.form)
    status = form.status.data
    print(status)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        job = form.job.data
        date = form.date.data
        duty_time = form.duty_time.data
        description = form.description.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        print(duty_time)
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute(
                "INSERT INTO duty(center_id, user_id, job, date, duty_time, description, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (center_id, user_id, job, date, duty_time, description, status, created_at, updated_at)
            )
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'duty added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

@app.route('/duty/<int:duty_id>', methods=['GET'])
def get_duty(duty_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT
    d.*,
    GROUP_CONCAT(u.name) AS user_names
FROM duty d
JOIN user u ON FIND_IN_SET(u.id, d.user_id) > 0
WHERE d.id = {duty_id}
GROUP BY d.id ;

    """)
    duty = cur.fetchone()
    cur.close()

    if duty:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        duty_dict = dict(zip(column_names, duty))

        response = {'code': '200', 'status': 'true', 'data': duty_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'duty not found'}
        return jsonify(response)

@app.route('/duty', methods=['POST'])
def get_all_duty():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == 0:
        cur.execute(f"""
            SELECT duty.*, user.name AS user_names
FROM duty
INNER JOIN user ON user.id=duty.user_id 
        """)
    else:
        cur.execute(f"""
            SELECT
        d.*,
        GROUP_CONCAT(u.name) AS user_names
    FROM duty d
    JOIN user u ON FIND_IN_SET(u.id, d.user_id) > 0
    WHERE d.center_id = {center_id}
    GROUP BY d.id ;

        """) 

    dutys = cur.fetchall()
    print(dutys)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for duty in dutys:
        account_dict = dict(zip(column_names, duty))
        data_with_columns.append(account_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }
    # print(response)
    return jsonify(response)


@app.route('/del_duty/<int:id>', methods=['DELETE'])
def delete_duty(id):
    cur = mysql.connection.cursor()
    duty = cur.execute("DELETE FROM duty WHERE id= %s", (id,))
    mysql.connection.commit()
    if duty:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})

@app.route('/upd_duty/<int:duty_id>', methods=['PUT'])
def update_duty(duty_id):
    form = DutyForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        job = form.job.data
        date = form.date.data
        duty_time = form.duty_time.data
        description = form.description.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM duty WHERE id=%s", (duty_id,))
        duty = cur.fetchone()
        if not duty:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'duty not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute(
                    "UPDATE duty SET center_id=%s, user_id=%s, job=%s, date=%s, duty_time=%s, description=%s, status=%s, updated_at=%s WHERE id=%s",
                    (center_id, user_id, job, date, duty_time, description, status, updated_at, duty_id)
                )
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'duty updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'duty not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Students Apis #..............................................................
class StudentForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    phone = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])
    father_name = StringField('Father Name', [validators.InputRequired()])
    father_phone = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    address = StringField('Address', [validators.InputRequired()])
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    batch_id = IntegerField('Batch ID', [validators.InputRequired()])
    class_id = IntegerField('Class ID', [validators.InputRequired()])
    group_id = IntegerField('Group ID', [validators.InputRequired()])
    percentage = IntegerField('Percentage', [validators.InputRequired()])
    description = StringField('Description', [validators.InputRequired()])
    ref_name = StringField('Reference Name', [validators.InputRequired()])
    ref_phone_no =  StringField('Reference Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])
    last_class = StringField('Last Class', [validators.InputRequired()])
    last_grade = StringField('Last Grade', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_student', methods=['POST'])
def add_student():
    form = StudentForm(request.form)
    if form.validate():
        image = request.files['image']
        name = form.name.data
        phone = form.phone.data
        father_name = form.father_name.data
        father_phone = form.father_phone.data
        email = form.email.data
        address = form.address.data
        bform = request.files['bform']
        marksheet = request.files['marksheet']        
        center_id = form.center_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        group_id = form.group_id.data
        percentage = form.percentage.data
        description = form.description.data
        ref_name = form.ref_name.data
        ref_phone_no = form.ref_phone_no.data
        last_class = form.last_class.data
        last_grade = form.last_grade.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        filename=image.filename
        filename1=bform.filename
        filename2=marksheet.filename
        if filename != '' and filename1 != '':
            file_ext = os.path.splitext(filename)[1]
            file_ext1 = os.path.splitext(filename1)[1]
            file_ext2 = os.path.splitext(filename2)[1]
            if (file_ext and file_ext1 and file_ext2) not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
        image.save(f'uploads/image and bform/{image.filename}')
        bform.save(f'uploads/image and bform/{bform.filename}')
        marksheet.save(f'uploads/{marksheet.filename}')


        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM batch WHERE id = %s", (batch_id,))
        result_1 = cur.fetchone()
        cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
        result_2 = cur.fetchone()  # Fetch a single row
        cur.execute("SELECT * FROM `group` WHERE id = %s", (group_id,))
        result_3 = cur.fetchone()  # Fetch a single row
        if result and result_1 and result_2 and result_3:
            cur.execute(f"""SELECT id
FROM student
ORDER BY id DESC
LIMIT 1;
""")
            id = cur.fetchone()
            id = str(id)
            cur.execute(f"SELECT name FROM batch WHERE id = {batch_id}")
            batch = cur.fetchone()
            batch = str(batch)
            roll_no = batch+'-'+id
            cur.execute("INSERT INTO student(image, name, phone, father_name, father_phone, email, address, bform, roll_no, center_id, batch_id, class_id, status, created_at, updated_at, group_id, description, ref_name, ref_phone_no, last_class, last_grade, percentage, marksheet) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(filename), name, phone, father_name, father_phone, email, address, str(filename1), roll_no, center_id, batch_id, class_id, status, created_at, updated_at, group_id, description, ref_name, ref_phone_no, last_class, last_grade, percentage, str(filename2)))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'Student added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
    
@app.route('/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
    SELECT 
        student.*, 
        class.name AS class_names,
        batch.name AS batch_names,
        `group`.name AS group_names
    FROM 
        student
    INNER JOIN 
        batch ON batch.id = student.batch_id 
    INNER JOIN 
        class ON class.id = student.class_id 
    INNER JOIN 
        `group` ON `group`.id = student.group_id 
    WHERE 
        student.id = {student_id};
""")
    student = cur.fetchone()
    cur.close()

    if student:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        student_dict = dict(zip(column_names, student))

        response = {'code': '200', 'status': 'true', 'data': student_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'student not found'}
        return jsonify(response)

@app.route('/student', methods=['POST'])
def get_all_student():
    cur = mysql.connection.cursor()
    data = request.get_json()
    center_id = data.get('center_id')
    if center_id == '0':
        cur.execute(f"""
            SELECT student.*, class.name AS class_names,batch.name AS batch_names,group.name AS group_names
FROM student
INNER JOIN batch ON batch.id=student.batch_id 
INNER JOIN class ON class.id=student.class_id 
INNER JOIN group ON group.id=student.group_id;

        """)
    else:
        cur.execute(f"""
    SELECT 
        student.*, 
        class.name AS class_names,
        batch.name AS batch_names,
        `group`.name AS group_names
    FROM 
        student
    INNER JOIN 
        batch ON batch.id = student.batch_id 
    INNER JOIN 
        class ON class.id = student.class_id 
    INNER JOIN 
        `group` ON `group`.id = student.group_id 
    WHERE 
        student.center_id = {center_id};
""")
    students = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for student in students:
        student_dict = dict(zip(column_names, student))
        data_with_columns.append(student_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_student/<int:id>', methods=['DELETE'])
def delete_student(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student WHERE id=%s", (id,))
    student = cur.fetchone()
    if student: 
        image_path = student[1]
        bform_path = student[8]
        marksheet_path = student[23]
        # delete the center from the database
        cur.execute("DELETE FROM student WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the center's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], image_path))
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], bform_path))
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], marksheet_path))
        return jsonify({'message': f'student with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'student with id {id} not found'})


@app.route('/upd_student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    form = StudentForm(request.form)
    if form.validate():
        image = request.files['image']
        name = form.name.data
        phone = form.phone.data
        father_name = form.father_name.data
        father_phone = form.father_phone.data
        email = form.email.data
        address = form.address.data
        bform = request.files['bform']
        marksheet = request.files['marksheet']        
        center_id = form.center_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        group_id = form.group_id.data
        percentage = form.percentage.data
        description = form.description.data
        ref_name = form.ref_name.data
        ref_phone_no = form.ref_phone_no.data
        last_class = form.last_class.data
        last_grade = form.last_grade.data
        status = form.status.data
        updated_at = form.updated_at.data
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student WHERE id=%s", (student_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'student not found'}
            return jsonify(final_response)
        else:
            image_path = role[1]
            bform_path = role[8]
            marksheet_path = role[23]
            if image_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], image_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],image_path))
            if bform_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], bform_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],bform_path))
            if marksheet_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], marksheet_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],marksheet_path))            
            
            filename=image.filename
            filename1=bform.filename
            filename2=marksheet.filename
            if filename != '' and filename1 != '' and filename2 != '':
                file_ext = os.path.splitext(filename)[1]
                file_ext1 = os.path.splitext(filename1)[1]
                file_ext2 = os.path.splitext(filename2)[1]
            if (file_ext and file_ext1 and file_ext2) not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
            image.save(f'uploads/image and bform/{image.filename}')
            bform.save(f'uploads/image and bform/{bform.filename}')            
            marksheet.save(f'uploads/{marksheet.filename}') 
            
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM batch WHERE id = %s", (batch_id,))
            result_1 = cur.fetchone()
            cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
            result_2 = cur.fetchone()  # Fetch a single row
            if result and result_1 and result_2:
                cur.execute("UPDATE student SET image=%s, name=%s, phone=%s, father_name=%s, father_phone=%s, email=%s, address=%s, bform=%s, center_id=%s, batch_id=%s, class_id=%s, status=%s, updated_at=%s, group_id=%s, description=%s, ref_name=%s, ref_phone_no=%s, last_class=%s, last_grade=%s, percentage=%s, marksheet=%s WHERE id=%s", (str(filename), name, phone, father_name, father_phone, email, address, str(filename1), center_id, batch_id, class_id, status, updated_at, group_id, description, ref_name, ref_phone_no, last_class, last_grade, percentage, str(filename2), student_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'student updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'student not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Subject Apis #..............................................................
class SubjectForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    user_id = StringField('User ID', [validators.InputRequired()])
    # status = IntegerField('Status', [
    #     validators.InputRequired(),
    #     validators.AnyOf([0, 1], 'Must be 0 or 1')
    # ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

class USubjectForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    user_id = StringField('User ID', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)


@app.route('/add_subject', methods=['POST'])
def add_subject():
    form = SubjectForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        user_id = form.user_id.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO subject(center_id, name, user_id, created_at, updated_at) VALUES( %s, %s, %s, %s, %s)", (center_id, name, user_id, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'Subject added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

@app.route('/subject_ids/<int:center_id>', methods=['GET'])
def get_all_subject_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM subject WHERE center_id=%s",(center_id,))
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/subject/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT
    s.*,
    GROUP_CONCAT(u.name) AS user_names
FROM subject s
JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
WHERE s.id = {subject_id}
GROUP BY s.id ;

    """)
    subject = cur.fetchone()
    cur.close()

    if subject:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        subject_dict = dict(zip(column_names, subject))

        response = {'code': '200', 'status': 'true', 'data': subject_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)


@app.route('/subjects', methods=['POST'])
def get_all_subjects():
    data = request.get_json()
    center_id = data.get('center_id')
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT id, name FROM subject WHERE  center_id = {center_id}")
    Uroles = cur.fetchall()
    print(Uroles)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/subject', methods=['POST'])
def get_all_subject():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == '0':            
        cur.execute(f"""
            SELECT
        s.*,
        GROUP_CONCAT(u.name) AS user_names
    FROM subject s
    JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
    GROUP BY s.id ;

        """)
    else:
        cur.execute(f"""
            SELECT
        s.*,
        GROUP_CONCAT(u.name) AS user_names
    FROM subject s
    JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
    WHERE s.center_id = {center_id}
    GROUP BY s.id ;

        """)

    subjects = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for subject in subjects:
        user_dict = dict(zip(column_names, subject))
        # Split the role_names into a list
        user_dict['user_names'] = user_dict['user_names'].split(',')
        data_with_columns.append(user_dict)


    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_subject/<int:id>', methods=['DELETE'])
def delete_subject(id):
    cur = mysql.connection.cursor()
    user = cur.execute(f"DELETE FROM subject WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if user > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'user found', 'data': user}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'user not found', 'data': user}
        return jsonify(final_response)


@app.route('/upd_subject/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    form = USubjectForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        user_id = form.user_id.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM subject WHERE id=%s", (subject_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'role not found'}
            return jsonify(final_response) 
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE subject SET center_id=%s, name=%s, user_id=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, user_id, status, updated_at, subject_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'subject updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'subject not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# # # Teacher Apis #..............................................................
# class ExpenseForm(Form):
#     user_id = IntegerField('Exam ID', [validators.InputRequired()])
#     account_id = IntegerField('Student ID', [validators.InputRequired()])
#     transaction_id = IntegerField('Student ID', [validators.InputRequired()])
#     amount = IntegerField('Student ID', [validators.InputRequired()])
#     description = StringField('Name', [validators.InputRequired()])  
#     status = IntegerField('Status', [validators.InputRequired(),
#                                      validators.AnyOf([0, 1], 'Must be 0 or 1')])
#     created_at = DateTimeField('Created At', default=datetime.utcnow)
#     updated_at = DateTimeField('Updated At', default=datetime.utcnow)

# Result Apis #..............................................................
class ResultForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    exam_id = IntegerField('Exam ID', [validators.InputRequired()])
    student_id = IntegerField('Student ID', [validators.InputRequired()])
    mark = IntegerField('Marks', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_result', methods=['POST'])
def add_result():
    form = ResultForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        exam_id = form.exam_id.data
        student_id = form.student_id.data
        mark = form.mark.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM examination WHERE id = %s", (exam_id,))
        result_1 = cur.fetchone()
        cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
        result_2 = cur.fetchone()  # Fetch a single row
        if result and result_1 and result_2:
            cur.execute("INSERT INTO result(center_id, exam_id, student_id, mark, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)", (center_id, exam_id, student_id, mark, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'result added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)


    
@app.route('/result/<int:result_id>', methods=['GET'])
def get_result(result_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM result WHERE id=%s", (result_id,))
    result = cur.fetchone()
    cur.close()

    if result:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        result_dict = dict(zip(column_names, result))

        response = {'code': '200', 'status': 'true', 'data': result_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'result not found'}
        return jsonify(response)

@app.route('/result', methods=['GET'])
def get_all_result():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM result")
    results = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for result in results:
        result_dict = dict(zip(column_names, result))
        data_with_columns.append(result_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_result/<int:id>', methods=['DELETE'])
def delete_result(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM result WHERE id= %s", (id,))
    result = cur.fetchone()
    mysql.connection.commit()

    if result:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})

@app.route('/upd_result/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    form = ResultForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        exam_id = form.exam_id.data
        student_id = form.student_id.data
        mark = form.mark.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM result WHERE id=%s", (result_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'result not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM examination WHERE id = %s", (exam_id,))
            result_1 = cur.fetchone()
            cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
            result_2 = cur.fetchone()  # Fetch a single row
            if result and result_1 and result_2:
                cur.execute("UPDATE result SET center_id=%s, exam_id=%s, student_id=%s, mark=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, exam_id, student_id, mark, status, updated_at, result_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'rersult updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'result not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# User Role Apis #..............................................................
class URoleForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    screen = StringField('Screen', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_role', methods=['POST'])
def add_role():
    form = URoleForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        screen = form.screen.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO u_role(center_id, name, screen, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, name, screen, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'user role added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'user role addition failed'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

    
@app.route('/role/<int:role_id>', methods=['GET'])
def get_role(role_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM u_role WHERE id=%s", (role_id,))
    Urole = cur.fetchone()
    cur.close()

    if Urole:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Urole_dict = dict(zip(column_names, Urole))

        response = {'code': '200', 'status': 'true', 'data': Urole_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)

@app.route('/role', methods=['GET'])
def get_all_roles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM u_role")
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/role_id', methods=['GET'])
def get_all_roles_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM u_role WHERE id <> 0")
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/role_ids', methods=['GET'])
def get_all_roles_ids():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM u_role WHERE id NOT IN (0, 2)")
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_role/<int:id>', methods=['DELETE'])
def delete_role(id):
    cur = mysql.connection.cursor()
    user = cur.execute(f"DELETE FROM u_role WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if user > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'user role found', 'data': user}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'user role not found', 'data': user}
        return jsonify(final_response)


@app.route('/upd_role/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    form = URoleForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        screen = form.screen.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM u_role WHERE id=%s", (role_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'role not found'}
            return jsonify(final_response)
        else:
            cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()  # Fetch a single row

            if result:
                cur.execute("UPDATE u_role SET center_id=%s, name=%s, screen=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, screen, status, updated_at, role_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'user role updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'user role not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Student Record Apis #..............................................................
class SrecordForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    student_id = IntegerField('Student ID', [validators.InputRequired()])
    description = StringField('Description')
    date = DateField('Date')
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_srecord', methods=['POST'])
def add_srecord():
    form = SrecordForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        student_id = form.student_id.data
        file = request.files['file']
        description = form.description.data
        date = form.date.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        filename=file.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
        file.save(f'uploads/file/{file.filename}')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO srecord(center_id, student_id, file, description, date, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (center_id, student_id, str(filename), description, date, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'Srecord added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/srecord/<int:srecord_id>', methods=['GET'])
def get_srecord(srecord_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM srecord WHERE id=%s", (srecord_id,))
    Srecord = cur.fetchone()
    cur.close()

    if Srecord:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Srecord_dict = dict(zip(column_names, Srecord))

        response = {'code': '200', 'status': 'true', 'data': Srecord_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'srecord not found'}
        return jsonify(response)

@app.route('/srecord', methods=['GET'])
def get_all_srecord():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM srecord")
    Srecords = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Srecord in Srecords:
        Srecord_dict = dict(zip(column_names, Srecord))
        data_with_columns.append(Srecord_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_srecord/<int:id>', methods=['DELETE'])
def delete_srecord(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM srecord WHERE id=%s", (id,))
    srecord = cur.fetchone()
    if srecord:
        file_path = srecord[3]
        # delete the center from the database
        cur.execute("DELETE FROM srecord WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the center's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], file_path))
        return jsonify({'message': f'srecord with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'srecord with id {id} not found'})


@app.route('/upd_srecord/<int:srecord_id>', methods=['PUT'])
def update_srecord(srecord_id):
    form = SrecordForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        student_id = form.student_id.data
        file = request.files['file']
        description = form.description.data
        date = form.date.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM srecord WHERE id=%s", (srecord_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'srecord not found'}
            return jsonify(final_response)
        else:
            file_path = role[3]
            if file_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], file_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],file_path))
            
            filename=file.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
            file.save(f'uploads/file/{file.filename}') 
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE srecord SET center_id=%s, student_id=%s, file=%s, description=%s, date=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, student_id, str(filename), description, date, status, updated_at, srecord_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'srecord updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'srecord not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Role Screen Apis #..............................................................
class RscreenForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_rscreen', methods=['POST'])
def add_rscreen():
    form = RscreenForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        name = form.name.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        if result:
            cur.execute("INSERT INTO rscreen(center_id, name, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s)", (center_id, name, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'rscreen added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/rscreen/<int:rscreen_id>', methods=['GET'])
def get_rscreen(rscreen_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rscreen WHERE id=%s", (rscreen_id,))
    Rscreen = cur.fetchone()
    cur.close()

    if Rscreen:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Rscreen_dict = dict(zip(column_names, Rscreen))

        response = {'code': '200', 'status': 'true', 'data': Rscreen_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'rscreen not found'}
        return jsonify(response)

@app.route('/rscreen', methods=['GET'])
def get_all_rscreen():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rscreen")
    Rscreens = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Rscreen in Rscreens:
        Rscreen_dict = dict(zip(column_names, Rscreen))
        data_with_columns.append(Rscreen_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_rscreen/<int:id>', methods=['DELETE'])
def delete_rscreen(id):
    cur = mysql.connection.cursor()
    rscreen = cur.execute("DELETE FROM rscreen WHERE id= %s", (id,))
    mysql.connection.commit()

    if rscreen:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_rscreen/<int:rscreen_id>', methods=['PUT'])
def update_rscreen(rscreen_id):
    form = RscreenForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM rscreen WHERE id=%s", (rscreen_id,))
        rscreen = cur.fetchone()

        if not rscreen:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'rscreen not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            if result:
                cur.execute("UPDATE rscreen SET center_id=%s, name=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, status, updated_at, rscreen_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'rscreen updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'rscreen not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Examination Apis #..............................................................
class ExaminationForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    class_id = IntegerField('Name', [validators.InputRequired()])
    subject_id = IntegerField('Subject ID', [validators.InputRequired()])
    type = StringField('Paper Type')
    month = StringField('Month', [validators.InputRequired()])
    duration = StringField('Duration', [validators.InputRequired()])
    date = DateField('Date')
    total_marks = IntegerField('Total Marks')
    user_id = StringField('Invigilator')
    schedule_start_time = StringField('Schedule Start Time')
    schedule_end_time = StringField('Schedule End Time')
    start_time = StringField('Start Time')
    end_time = StringField('End Time')
    checking_status = StringField('Checking Status')
    status = IntegerField('Status', 
                      [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')],
                      default=1)
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)


@app.route('/add_examination', methods=['POST'])
def add_exmaination():
    form = ExaminationForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        class_id = form.class_id.data
        subject_id = form.subject_id.data
        type = form.type.data
        month = form.month.data
        duration = form.duration.data
        date = form.date.data
        total_marks = form.total_marks.data
        user_id = form.user_id.data
        schedule_start_time = form.schedule_start_time.data
        schedule_end_time = form.schedule_end_time.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        checking_status = form.checking_status.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        logo = request.files['logo']

        filename=logo.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
        logo.save(f'uploads/{logo.filename}')


        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO examination(center_id, class_id, subject_id, type, month, date, total_marks, user_id, schedule_start_time, schedule_end_time, start_time, end_time, checking_status, status, created_at, updated_at, file, duration) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, class_id, subject_id, type, month, date, total_marks, user_id, schedule_start_time, schedule_end_time, start_time, end_time, checking_status, status, created_at, updated_at, filename, duration))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'examination added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

    
@app.route('/examination/<int:examination_id>', methods=['GET'])
def get_examination(examination_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT
        e.*,
        GROUP_CONCAT(s.name) AS subject_names,
        GROUP_CONCAT(u.name) AS user_names,
        GROUP_CONCAT(c.name) AS class_names
    FROM examination e
    JOIN subject s ON s.id = e.subject_id
    JOIN class c ON c.id = e.subject_id
    JOIN user u ON u.id = e.user_id
    WHERE e.id = {examination_id}
    GROUP BY e.id ;

        """)
    Exam = cur.fetchone()
    cur.close()

    if Exam:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Exam_dict = dict(zip(column_names, Exam))

        response = {'code': '200', 'status': 'true', 'data': Exam_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'examination not found'}
        return jsonify(response)

@app.route('/examination', methods=['POST'])
def get_all_examination():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == 0:
        cur.execute( """
SELECT
        e.*,
        GROUP_CONCAT(s.name) AS subject_names,
        GROUP_CONCAT(u.name) AS user_names,
        GROUP_CONCAT(c.name) AS class_names
    FROM examination e
    JOIN subject s ON s.id = e.subject_id
    JOIN class c ON c.id = e.subject_id
    JOIN user u ON u.id = e.user_id
    GROUP BY e.id ;
""")
    else:
        abbas =(f"""
            SELECT examination.*, subject.name AS subject_names,class.name AS class_names,user.name AS user_names
FROM examination
INNER JOIN subject ON subject.id=examination.subject_id 
INNER JOIN class ON class.id=examination.class_id 
INNER JOIN user ON user.id=examination.user_id 
WHERE examination.center_id ='1';

        """) 
        print(abbas)
        cur.execute(f"""
            SELECT examination.*, subject.name AS subject_names,class.name AS class_names,user.name AS user_names
FROM examination
INNER JOIN subject ON subject.id=examination.subject_id 
INNER JOIN class ON class.id=examination.class_id 
INNER JOIN user ON user.id=examination.user_id 
WHERE examination.center_id ='1';

        """) 

    examinations = cur.fetchall()
    print(examinations)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for examination in examinations:
        account_dict = dict(zip(column_names, examination))
        data_with_columns.append(account_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }
    # print(response)
    return jsonify(response)

@app.route('/del_examination/<int:id>', methods=['DELETE'])
def delete_examination(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM examination WHERE id= %s", (id,))
    student = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    if student:
        return jsonify({'message': f'examination with id {id} not found'})
    else:
        return jsonify({'message': f'examination with id {id} deleted successfully'})


@app.route('/upd_examination/<int:examination_id>', methods=['PUT'])
def update_examination(examination_id):
    form = ExaminationForm(request.form)
    print(request.data)
    print(request.form)
    if form.validate():
        center_id = form.center_id.data
        class_id = form.class_id.data
        subject_id = form.subject_id.data
        type = form.type.data
        month = form.month.data
        duration = form.duration.data
        date = form.date.data
        total_marks = form.total_marks.data
        user_id = form.user_id.data
        schedule_start_time = form.schedule_start_time.data
        schedule_end_time = form.schedule_end_time.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        checking_status = form.checking_status.data
        status = form.status.data
        updated_at = form.updated_at.data
        logo = request.files.get('file')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM examination WHERE id=%s", (examination_id,))
        role = cur.fetchone()
        print(role)
        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'examination not found'}
            return jsonify(final_response)
        else:  
            # logo_path = role[2]
            # if logo_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], str(logo_path))):

            #     os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
            # filename = ''
            # file_ext = ''

            # if logo:
            #     filename = logo.filename
            #     if filename != '':
            #         file_ext = os.path.splitext(filename)[1]

            # if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            #     response = {'code':'E_400'}
            #     return jsonify(response)
            # logo.save(f'uploads/{filename}')
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE examination SET center_id=%s, class_id=%s, subject_id=%s, type=%s, month=%s, date=%s, total_marks=%s, user_id=%s, schedule_start_time=%s, schedule_end_time=%s, start_time=%s, end_time=%s, checking_status=%s, status=%s, updated_at=%s, file=%s, duration=%s WHERE id=%s", (center_id, class_id, subject_id, type, month, date, total_marks, user_id, schedule_start_time, schedule_end_time, start_time, end_time, checking_status, status, updated_at, logo, duration, examination_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'examination updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'examination not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# @app.route('/upd_examination/<int:examination_id>', methods=['PATCH'])
# def update_examination(examination_id): 
#     form = ExaminationForm(request.form)
#     if form.validate():
        # center_id = form.center_id.data
        # class_id = form.class_id.data
        # subject_id = form.subject_id.data
        # type = form.type.data
        # month = form.month.data
        # date = form.date.data
        # total_marks = form.total_marks.data
        # user_id = form.user_id.data
        # schedule_start_time = form.schedule_start_time.data
        # schedule_end_time = form.schedule_end_time.data
        # start_time = form.start_time.data
        # end_time = form.end_time.data
        # checking_status = form.checking_status.data
        # status = form.status.data
        # updated_at = form.updated_at.data
        # logo = request.files['logo']

#         if not examination:
#             cur.close()
#             final_response = {'code': '404', 'status': 'false', 'message': 'examination not found'}
#             return jsonify(final_response)
#         else:
#             logo_path = examination[2]
#             if logo_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path)):
#                 os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
#             filename = logo.filename
#             if filename != '':
#                 file_ext = os.path.splitext(filename)[1]
#             if file_ext not in app.config['UPLOAD_EXTENSIONS']:
#                 response = {'code':'E_400'}
#                 return jsonify(response)
#             logo.save(f'uploads/{filename}')


#         cur.execute("UPDATE examination SET name=%s, logo=%s, status=%s, updated_at=%s, address=%s, phone_no=%s, WHERE id=%s", (name, filename, status, updated_at, address, phone_no, examination_id))
#         mysql.connection.commit()
#         cur.close()
        
#         response = {'code': '200', 'status': 'true', 'message': 'examination updated successfully'}
#         return jsonify(response)
#     else:
#         final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
#         return jsonify(final_response)



# Course Chapter Apis #..............................................................
class CchapterForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    subject_id = IntegerField('subject_id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_cchapter', methods=['POST'])
def add_cchapter():
    form = CchapterForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        subject_id = form.subject_id.data
        name = form.name.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO cchapter(center_id, subject_id, name, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, subject_id, name, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'cchapter added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
    
@app.route('/cchapter/<int:cchapter_id>', methods=['GET'])
def get_cchapter(cchapter_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cchapter WHERE id=%s", (cchapter_id,))
    Cchapter = cur.fetchone()
    cur.close()

    if Cchapter:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Cchapter_dict = dict(zip(column_names, Cchapter))

        response = {'code': '200', 'status': 'true', 'data': Cchapter_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'cchapter not found'}
        return jsonify(response)

@app.route('/cchapter', methods=['GET'])
def get_all_cchapter():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cchapter")
    Cchapters = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Cchapter in Cchapters:
        cchapter_dict = dict(zip(column_names, Cchapter))
        data_with_columns.append(cchapter_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_cchapter/<int:id>', methods=['DELETE'])
def delete_cchapter(id):
    cur = mysql.connection.cursor()
    cchapter = cur.execute("DELETE FROM cchapter WHERE id= %s", (id,))
    mysql.connection.commit()

    if cchapter:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_cchapter/<int:cchapter_id>', methods=['PUT'])
def update_cchapter(cchapter_id):
    form = CchapterForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        subject_id = form.subject_id.data
        name = form.name.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cchapter WHERE id=%s", (cchapter_id,))
        cchapter = cur.fetchone()

        if not cchapter:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'cchapter not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE cchapter SET center_id=%s, subject_id=%s, name=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, subject_id, name, status, updated_at, cchapter_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'cchapter updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'cchapter not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Account Apis ..........
class AccountForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    balance = IntegerField('balance', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)


@app.route('/add_account', methods=['POST'])
def add_account():
    form = AccountForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        name = form.name.data
        balance = form.balance.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        if result:
            cur.execute("INSERT INTO account(center_id, name, balance, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, name, balance, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'account added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

@app.route('/account_ids/<int:center_id>', methods=['GET'])
def get_account_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM account WHERE center_id=%s", (center_id,))
    accounts = cur.fetchall()  # Use fetchall() instead of fetchone()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for account in accounts:
        account_dict = dict(zip(column_names, account))
        data_with_columns.append(account_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


    
@app.route('/account/<int:account_id>', methods=['GET'])
def get_account(account_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
    accounts = cur.fetchone()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for account in accounts:
        account_dict = dict(zip(column_names, account))
        data_with_columns.append(account_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/account', methods=['POST'])
def get_all_account():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == '0':
        cur.execute("SELECT * FROM account")
    else:
        cur.execute(f"SELECT * FROM account WHERE center_id = {center_id}")
    accounts = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for account in accounts:
        account_dict = dict(zip(column_names, account))
        data_with_columns.append(account_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/del_account/<int:id>', methods=['DELETE'])
def delete_account(id):
    cur = mysql.connection.cursor()
    account = cur.execute("DELETE FROM account WHERE id= %s", (id,))
    mysql.connection.commit()

    if account:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_account/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    form = AccountForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        balance = form.balance.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
        account = cur.fetchone()

        if not account:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'account not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            if result:
                cur.execute("UPDATE account SET center_id=%s, name=%s, balance=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, balance, status, updated_at, account_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'account updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'account not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Transaction Apis ..........
class TransactionForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    form = TransactionForm(request.form)
    if form.validate():       
        name = form.name.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO transaction(name, status, created_at, updated_at) VALUES(%s, %s, %s, %s)", (name, status, created_at, updated_at))
        mysql.connection.commit()
        cur.close()
        response = {'code': '200', 'status': 'true', 'message': 'transaction added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

@app.route('/transaction/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    # print(transaction_id)
    cur = mysql.connection.cursor()
    sql = f"SELECT u.*, GROUP_CONCAT(r.name) AS role_names FROM transaction u JOIN u_role r ON FIND_IN_SET(r.id, u.role_id) WHERE u.id IN ({transaction_id}) GROUP BY u.id"
    cur.execute(sql)    
    transaction = cur.fetchone()
    list(transaction)
    # print(transaction[-1])
    cur.close()

    if transaction:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        transaction_dict = dict(zip(column_names, transaction))

        response = {'code': '200', 'status': 'true', 'data': transaction_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'transaction not found'}
        return jsonify(response)

@app.route('/transaction_ids', methods=['GET'])
def get_all_transaction_ids():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT id, name 
    FROM transaction 
""")
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)




@app.route('/transaction', methods=['POST'])
def get_all_transactions():
    data = request.get_json()
    center_id = data.get('center_id')
    role_id = list(data.get('role_id'))
    role = data.get('role')
    print(role_id)
    cur = mysql.connection.cursor()
    print(role)

    cur.execute("SELECT id, center_id, role_id FROM transaction WHERE id <> 1")
        
        
    transactions = cur.fetchall()
    print(transactions)
    
    column_names = [desc[0] for desc in cur.description]
    cur.close()

    data_with_columns = []
    for transaction in transactions:
        transaction_dict = dict(zip(column_names, transaction))
        # Split the role_names into a list
        transaction_dict['role_names'] = transaction_dict['role_names'].split(',')
        data_with_columns.append(transaction_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_transaction/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    cur = mysql.connection.cursor()
    transaction = cur.execute("DELETE FROM transaction WHERE id= %s", (id,))
    mysql.connection.commit()

    if transaction:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_transaction/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    form = TransactionForm(request.form)
    if form.validate():
        name = form.name.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM transaction WHERE id=%s", (transaction_id,))
        transaction = cur.fetchone()

        if not transaction:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'transaction not found'}
            return jsonify(final_response)
        else:
            cur.execute("UPDATE transaction SET name=%s, status=%s, updated_at=%s WHERE id=%s", (name, status, updated_at, transaction_id))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'transaction updated successfully'}
            return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Expense Apis ..........
class ExpenseForm(Form):
    user_id = IntegerField('user ID', [validators.InputRequired()])
    account_id = IntegerField('account ID', [validators.InputRequired()])
    transaction_id = IntegerField('transaction ID', [validators.InputRequired()]) 
    center_id = IntegerField('center ID', [validators.InputRequired()]) 
    description = StringField('Name', [validators.InputRequired()])
    amount = IntegerField('amount', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')],default=1)
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)


@app.route('/add_expense', methods=['POST'])
def add_expense():
    form = ExpenseForm(request.form)
    if form.validate():       
        user_id = form.user_id.data
        account_id = form.account_id.data
        transaction_id = form.transaction_id.data
        center_id = form.center_id.data
        description = form.description.data
        amount = form.amount.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM account WHERE id = %s", (account_id,))
        result1 = cur.fetchone()
        cur.execute("SELECT * FROM transaction WHERE id = %s", (transaction_id,))
        result2 = cur.fetchone()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result2 = cur.fetchone()
        if result and result1 and result2:
            cur.execute("SELECT balance FROM account WHERE id = %s", (account_id,))
            expense = int(cur.fetchone()[0])
            if transaction_id == 1:
                balance = expense - int(amount)
            else:
                balance = expense + int(amount)
            cur.execute("UPDATE account SET balance = %s WHERE id = %s", (balance, account_id))
 
            cur.execute("INSERT INTO expense(user_id, account_id, transaction_id, center_id, description, balance, amount, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, account_id, transaction_id, center_id, description, balance, amount, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'expense added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/expense/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT expense.*, expense.description, account.name AS account_names,transaction.name AS transaction_names,user.name AS user_names, account.balance AS balances
FROM expense
INNER JOIN transaction ON transaction.id=expense.transaction_id 
INNER JOIN account ON account.id=expense.account_id 
INNER JOIN user ON user.id=expense.user_id 
WHERE expense.id ={expense_id};

        """) 
    Exam = cur.fetchone()
    print(Exam)
    cur.close()

    if Exam:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Exam_dict = dict(zip(column_names, Exam))

        response = {'code': '200', 'status': 'true', 'data': Exam_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'examination not found'}
        return jsonify(response)

@app.route('/expense', methods=['POST'])
def get_all_expense():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == 0:
        cur.execute(f"""
            SELECT expense.*, subject.name AS subject_names,class.name AS class_names,user.name AS user_names
FROM expense
INNER JOIN subject ON subject.id=expense.subject_id 
INNER JOIN class ON class.id=expense.class_id 
INNER JOIN user ON user.id=expense.user_id ;

        """)
    else:
        cur.execute(f"""
            SELECT expense.*, account.name AS account_names,transaction.name AS transaction_names,user.name AS user_names, account.balance AS balances
FROM expense
INNER JOIN transaction ON transaction.id=expense.transaction_id 
INNER JOIN account ON account.id=expense.account_id 
INNER JOIN user ON user.id=expense.user_id 
WHERE expense.center_id ={center_id};

        """) 
    examinations = cur.fetchall()
    print(examinations)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for examination in examinations:
        account_dict = dict(zip(column_names, examination))
        data_with_columns.append(account_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }
    # print(response)
    return jsonify(response)

@app.route('/del_expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    cur = mysql.connection.cursor()
    expense = cur.execute("DELETE FROM expense WHERE id= %s", (id,))
    mysql.connection.commit()

    if expense:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_expense/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    form = ExpenseForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        account_id = form.account_id.data
        transaction_id = form.transaction_id.data
        description = form.description.data
        amount = form.amount.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM expense WHERE id=%s", (expense_id,))
        expense = cur.fetchone()

        if not expense:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'expense not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM account WHERE id = %s", (account_id,))
            result1 = cur.fetchone()
            cur.execute("SELECT * FROM transaction WHERE id = %s", (transaction_id,))
            result2 = cur.fetchone()
            cur.execute("SELECT balance FROM account WHERE id = %s", (account_id,))
            expense = int(cur.fetchone()[0])
            cur.execute(f"""
            SELECT expense.*, expense.description, account.name AS account_names,transaction.name AS transaction_names,user.name AS user_names, account.balance AS balances
FROM expense
INNER JOIN transaction ON transaction.id=expense.transaction_id 
INNER JOIN account ON account.id=expense.account_id 
INNER JOIN user ON user.id=expense.user_id 
WHERE expense.id ={expense_id};

        """)
            abbas = cur.fetchone()
            old_amount = int(abbas[8])
            old_TType = int(abbas[3])
            if (old_amount != amount and old_TType != transaction_id):
                Double_amount = 2*(old_amount)
                diff = old_amount - amount
                if transaction_id == 1:
                    expense = expense - Double_amount
                    balance = expense + diff
                else:    
                    expense = expense + Double_amount
                    balance = expense - diff
            elif old_amount != amount:
                diff = old_amount - amount
                if transaction_id == 1:
                    balance = expense + diff
                else:
                    balance = expense - diff
            elif old_TType != transaction_id:
                Double_amount = 2*(old_amount)
                if transaction_id == 1:
                    balance = expense - Double_amount
                else:
                    balance = expense + Double_amount
            else:
                balance = expense
            
            cur.execute("UPDATE account SET balance = %s WHERE id = %s", (balance, account_id))
            if result and result1 and result2:
                cur.execute("UPDATE expense SET center_id=%s, user_id=%s, transaction_id=%s, account_id=%s, amount=%s, balance=%s, description=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, user_id, transaction_id, account_id, amount, balance, description, status, updated_at, expense_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'expense updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'expense not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


# Group Apis #..............................................................
class GroupForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    subject_id = StringField('Subject Id', [validators.InputRequired()])
    batch_id =  IntegerField('Batch ID', [validators.InputRequired()])
    class_id =IntegerField('class ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')],default = 1)
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_group', methods=['POST'])
def add_group():
    form = GroupForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        subject_id = form.subject_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        name = form.name.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        print(name)
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM user WHERE id = %s", (subject_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute(
                "INSERT INTO `group`(center_id, subject_id, batch_id, class_id, name, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                (center_id, subject_id, batch_id, class_id, name, status, created_at, updated_at)
            )
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'group added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

@app.route('/group/<int:group_id>', methods=['GET'])
def get_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
SELECT
       `group`.*,
        GROUP_CONCAT(s.name) AS subject_names,
        u.name AS batch_names,
        c.name AS class_names
    FROM `group` 
    JOIN subject s ON FIND_IN_SET(s.id, `group`.subject_id) > 0
    JOIN class c ON c.id = `group`.class_id
    JOIN batch u ON u.id =`group`.batch_id
    WHERE `group`.id = {group_id}
    GROUP BY `group`.id ;

        """)
    group = cur.fetchone()
    cur.close()

    if group:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        group_dict = dict(zip(column_names, group))

        response = {'code': '200', 'status': 'true', 'data': group_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'group not found'}
        return jsonify(response)

@app.route('/group', methods=['POST'])
def get_all_group():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == 0:
        cur.execute(f"""
            SELECT `group`.*, user.name AS user_names
FROM `group`
INNER JOIN user ON user.id=`group`.subject_id 
        """)
    else:
        cur.execute(f"""
SELECT
       `group`.*,
        GROUP_CONCAT(s.name) AS subject_names,
        u.name AS batch_names,
        c.name AS class_names
    FROM `group` 
    JOIN subject s ON FIND_IN_SET(s.id, `group`.subject_id) > 0
    JOIN class c ON c.id = `group`.class_id
    JOIN batch u ON u.id =`group`.batch_id
    WHERE `group`.center_id = {center_id}
    GROUP BY `group`.id ;

        """) 

    group = cur.fetchall()
    print(group)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for subject in group:
        user_dict = dict(zip(column_names, subject))
        # Split the role_names into a list
        user_dict['subject_names'] = user_dict['subject_names'].split(',')
        data_with_columns.append(user_dict)


    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/del_group/<int:id>', methods=['DELETE'])
def delete_group(id):
    cur = mysql.connection.cursor()
    group = cur.execute("DELETE FROM `group` WHERE id= %s", (id,))
    mysql.connection.commit()
    if group:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})

@app.route('/upd_group/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    form = GroupForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        subject_id = form.subject_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        name = form.name.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `group` WHERE id=%s", (group_id,))
        group = cur.fetchone()
        if not group:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'group not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM user WHERE id = %s", (subject_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute(
                    "UPDATE `group` SET center_id=%s, subject_id=%s, batch_id=%s, class_id=%s, name=%s, status=%s, updated_at=%s WHERE id=%s",
                    (center_id, subject_id, batch_id, class_id, name, status, updated_at, group_id)
                )
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'group updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'group not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


@app.route('/group_ids/<int:center_id>', methods=['GET'])
def get_all_group_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `group`.id, `group`.name, class.name AS class_names
FROM `group`
INNER JOIN class ON class.id= `group`.class_id 
WHERE `group`.center_id ={center_id};

        """)
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


# Absent Form
class AbsForm(Form):
    center_id = IntegerField('Center Id', [validators.InputRequired()])
    student_id = IntegerField('Student Id', [validators.InputRequired()])
    user_id = IntegerField('User Id', [validators.InputRequired()])
    reason = StringField('Reason', [validators.InputRequired()])
    date = DateField('Date')
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())


@app.route('/student/add_Aform', methods=['POST'])
def add_Aform():
    form = AbsForm(request.form)
    if form.validate():
        logo = request.files['logo']
        center_id = form.center_id.data
        user_id = form.user_id.data
        student_id = form.student_id.data
        date = form.date.data
        reason = form.reason.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        filename=logo.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
        logo.save(f'uploads/{logo.filename}')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `absent_form`(center_id, student_id, user_id, reason, date, absent_file, status, created_at, updated_at) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, student_id, user_id, reason, date, str(filename), status, created_at, updated_at))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'Aform added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
        
@app.route('/student/Aform/<int:Aform_id>', methods=['GET'])
def get_Aform(Aform_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
    SELECT `absent_form`.*, user.name AS user_names, student.name AS student_names
    FROM `absent_form`
    INNER JOIN user ON user.id = `absent_form`.user_id 
    INNER JOIN student ON student.id = `absent_form`.student_id 
    WHERE `absent_form`.id = {Aform_id};
""")
    Aform = cur.fetchone()
    cur.close()

    if Aform:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Aform_dict = dict(zip(column_names, Aform))

        response = {'code': '200', 'status': 'true', 'data': Aform_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Aform not found'}
        return jsonify(response)

@app.route('/student/Aform_id', methods=['GET'])
def get_all_Aforms_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM Aform")
    Aforms = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for Aform in Aforms:
        Aform_dict = dict(zip(column_names, Aform))
        data_with_columns.append(Aform_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/student/Aform', methods=['POST'])
def get_all_Aforms():
    data = request.get_json()
    center_id = data.get('center_id')
    student_id = data.get('student_id')
    print(student_id)
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"""
    SELECT `absent_form`.*, user.name AS user_names
    FROM `absent_form`
    INNER JOIN user ON user.id = `absent_form`.user_id 
    WHERE `absent_form`.center_id = {center_id} 
    AND `absent_form`.student_id = {student_id};
""")
    Aforms = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for Aform in Aforms:
        Aform_dict = dict(zip(column_names, Aform))
        data_with_columns.append(Aform_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM Aform")
    # Aforms = cur.fetchall()
    # cur.close()
    
    # print(Aforms)

    # response = {'code': '200', 'status': 'true', 'data': Aforms}
    # return jsonify(response)

@app.route('/del_Aform/<int:id>', methods=['DELETE'])
def delete_Aform(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `absent_form` WHERE id=%s", (id,))
    Aform = cur.fetchone()
    if Aform:
        logo_path = Aform[2]
        # delete the Aform from the database
        cur.execute("DELETE FROM `absent_form` WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the Aform's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'Aform with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'Aform with id {id} not found'})


@app.route('/student/upd_Aform/<int:Aform_id>', methods=['PUT'])
def update_Aform(Aform_id): 
    form = AbsForm(request.form)
    if form.validate():
        logo = request.files['logo']
        center_id = form.center_id.data
        user_id = form.user_id.data
        student_id = form.student_id.data
        date = form.date.data
        reason = form.reason.data
        status = form.status.data
        updated_at = form.updated_at.data
                
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `absent_form` WHERE id=%s", (Aform_id,))
        Leave_Form = cur.fetchone()
        print(Leave_Form)

        if not Leave_Form:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'Leave_Form not found'}
            return jsonify(final_response)
        else:
            logo_path = Leave_Form[6]
            if logo_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
            filename = logo.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
            logo.save(f'uploads/{filename}')


        cur.execute("UPDATE `absent_form` SET center_id=%s, student_id=%s, user_id=%s, date=%s, reason=%s, absent_file=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, student_id, user_id, date, reason,  str(filename), status, updated_at, Aform_id))
        mysql.connection.commit()
        cur.close()
        
        response = {'code': '200', 'status': 'true', 'message': 'Absent_Form updated successfully'}
        return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Late Form
class LaForm(Form):
    center_id = IntegerField('Center Id', [validators.InputRequired()])
    student_id = IntegerField('Student Id', [validators.InputRequired()])
    user_id = IntegerField('User Id', [validators.InputRequired()])
    time = StringField('time')
    reason = StringField('Reason', [validators.InputRequired()])
    date = DateField('Date')
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())

@app.route('/student/add_lform', methods=['POST'])
def add_lform():
    form = LaForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        student_id = form.student_id.data
        time = form.time.data
        reason = form.reason.data
        date = form.date.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO lform( center_id, student_id, user_id, time, reason, date, status, created_at, updated_at) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, student_id, user_id, time, reason, date, status, created_at, updated_at))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'lform added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
        
@app.route('/student/lform/<int:lform_id>', methods=['GET'])
def get_lform(lform_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT lform.*,user.name AS user_names,student.name AS student_names
FROM lform
INNER JOIN student ON student.id=lform.student_id
INNER JOIN user ON user.id=lform.user_id  
WHERE lform.id ={lform_id};

        """)
    lform = cur.fetchone()
    cur.close()

    if lform:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        lform_dict = dict(zip(column_names, lform))

        response = {'code': '200', 'status': 'true', 'data': lform_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'lform not found'}
        return jsonify(response)

@app.route('/lform_id', methods=['GET'])
def get_all_lforms_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM lform")
    lforms = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for lform in lforms:
        lform_dict = dict(zip(column_names, lform))
        data_with_columns.append(lform_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/student/lform', methods=['POST'])
def get_all_lforms():
    data = request.get_json()
    center_id = data.get('center_id')
    student_id = data.get('student_id')
    print(student_id)
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT lform.*,user.name AS user_names
FROM lform
INNER JOIN user ON user.id=lform.user_id 
WHERE lform.center_id ={center_id} AND lform.student_id ={student_id};

        """)
    lforms = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for lform in lforms:
        lform_dict = dict(zip(column_names, lform))
        data_with_columns.append(lform_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM lform")
    # lforms = cur.fetchall()
    # cur.close()
    
    # print(lforms)

    # response = {'code': '200', 'status': 'true', 'data': lforms}
    # return jsonify(response)

@app.route('/student/del_lform/<int:id>', methods=['DELETE'])
def delete_lform(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM lform WHERE id=%s", (id,))
    lform = cur.fetchone()
    if lform:
        logo_path = lform[2]
        # delete the lform from the database
        cur.execute("DELETE FROM lform WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the lform's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'lform with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'lform with id {id} not found'})


@app.route('/student/upd_lform/<int:lform_id>', methods=['PUT'])
def update_lform(lform_id): 
    form = LaForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        student_id = form.student_id.data
        time = form.time.data
        reason = form.reason.data
        date = form.date.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM lform WHERE id=%s", (lform_id,))
        lform = cur.fetchone()

        if not lform:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'lform not found'}
            return jsonify(final_response)
        else:

            cur.execute("UPDATE lform SET center_id=%s, time=%s, status=%s, updated_at=%s, user_id=%s, student_id=%s, reason=%s, date=%s  WHERE id=%s", (center_id, time, status, updated_at, user_id, student_id, reason, date, lform_id))
            mysql.connection.commit()
            cur.close()
            
            response = {'code': '200', 'status': 'true', 'message': 'lform updated successfully'}
            return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Half Leave Form
class LeaveForm(Form):
    center_id = IntegerField('Center Id', [validators.InputRequired()])
    student_id = IntegerField('Student Id', [validators.InputRequired()])
    user_id = IntegerField('User Id', [validators.InputRequired()])
    start_date_time = StringField('time')
    end_date_time = StringField('time')
    reason = StringField('Reason', [validators.InputRequired()])
    type = IntegerField('type', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())



@app.route('/student/add_leave_form', methods=['POST'])
def add_Leave_Form():
    form = LeaveForm(request.form)
    if form.validate():
        logo = request.files['logo']
        center_id = form.center_id.data
        user_id = form.user_id.data
        student_id = form.student_id.data
        start_date_time = form.start_date_time.data
        end_date_time = form.end_date_time.data
        reason = form.reason.data
        type = form.type.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        filename=logo.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
        logo.save(f'uploads/{logo.filename}')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `leave_form`(center_id, student_id, user_id, start_date_time, end_date_time, reason, type, leave_file, status, created_at, updated_at) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, student_id, user_id, start_date_time, end_date_time, reason, type, str(filename), status, created_at, updated_at))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'Leave_Form added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
        
@app.route('/student/leave_form/<int:Leave_Form_id>', methods=['GET'])
def get_Leave_Form(Leave_Form_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `leave_form`.*,user.name AS user_names,student.name AS student_names
FROM `leave_form`
INNER JOIN student ON student.id=`leave_form`.student_id
INNER JOIN user ON user.id=`leave_form`.user_id  
WHERE `leave_form`.id ={Leave_Form_id};

        """)
    Leave_Form = cur.fetchone()
    cur.close()

    if Leave_Form:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        Leave_Form_dict = dict(zip(column_names, Leave_Form))

        response = {'code': '200', 'status': 'true', 'data': Leave_Form_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Leave_Form not found'}
        return jsonify(response)

@app.route('/student/Leave_Form_id', methods=['GET'])
def get_all_Leave_Forms_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM leave_form")
    Leave_Forms = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for Leave_Form in Leave_Forms:
        Leave_Form_dict = dict(zip(column_names, Leave_Form))
        data_with_columns.append(Leave_Form_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/student/leave_form', methods=['POST'])
def get_all_Leave_Forms():
    data = request.get_json()
    center_id = data.get('center_id')
    student_id = data.get('student_id')
    abbas = data.get('type')
    print(student_id)
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"""
    SELECT `leave_form`.*, user.name AS user_names
    FROM `leave_form`
    INNER JOIN user ON user.id = `leave_form`.user_id 
    WHERE `leave_form`.center_id = {center_id} 
    AND `leave_form`.student_id = {student_id} 
    AND `leave_form`.type = {abbas};
""")

    Leave_Forms = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for Leave_Form in Leave_Forms:
        Leave_Form_dict = dict(zip(column_names, Leave_Form))
        data_with_columns.append(Leave_Form_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM Leave_Form")
    # Leave_Forms = cur.fetchall()
    # cur.close()
    
    # print(Leave_Forms)

    # response = {'code': '200', 'status': 'true', 'data': Leave_Forms}
    # return jsonify(response)

@app.route('/student/del_leave_form/<int:id>', methods=['DELETE'])
def delete_Leave_Form(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `leave_form` WHERE id=%s", (id,))
    Leave_Form = cur.fetchone()
    if Leave_Form:
        logo_path = Leave_Form[2]
        # delete the Leave_Form from the database
        cur.execute("DELETE FROM `leave_form` WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the Leave_Form's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'Leave_Form with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'Leave_Form with id {id} not found'})


@app.route('/student/upd_leave_form/<int:Leave_Form_id>', methods=['PUT'])
def update_Leave_Form(Leave_Form_id): 
    form = LeaveForm(request.form)
    if form.validate():
        logo = request.files['logo']
        center_id = form.center_id.data
        user_id = form.user_id.data
        student_id = form.student_id.data
        start_date_time = form.start_date_time.data
        end_date_time = form.end_date_time.data
        reason = form.reason.data
        type = form.type.data
        status = form.status.data
        updated_at = form.updated_at.data
                
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `leave_form` WHERE id=%s", (Leave_Form_id,))
        Leave_Form = cur.fetchone()
        print(Leave_Form)

        if not Leave_Form:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'Leave_Form not found'}
            return jsonify(final_response)
        else:
            logo_path = Leave_Form[6]
            if logo_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
            filename = logo.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
            logo.save(f'uploads/{filename}')


        cur.execute("UPDATE `leave_form` SET center_id=%s, student_id=%s, user_id=%s, start_date_time=%s, end_date_time=%s, reason=%s, type=%s, leave_file=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, student_id, user_id, start_date_time, end_date_time, reason, type, str(filename), status, updated_at, Leave_Form_id))
        mysql.connection.commit()
        cur.close()
        
        response = {'code': '200', 'status': 'true', 'message': 'Leave_Form updated successfully'}
        return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Late Form
class TTForm(Form):
    center_id = IntegerField('Center Id', [validators.InputRequired()])
    class_id = IntegerField('Class Id', [validators.InputRequired()])
    user_id = IntegerField('User Id', [validators.InputRequired()])
    subject_id = IntegerField('Subject Id', [validators.InputRequired()])
    day = StringField('time')
    start_slot_time = StringField('Slot Time', [validators.InputRequired()])
    end_slot_time = StringField('Slot Time', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())

@app.route('/add_timetable', methods=['POST'])
def add_timetable():
    form = TTForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        subject_id = form.subject_id.data
        class_id = form.class_id.data
        day = form.day.data
        start_slot_time = form.start_slot_time.data
        end_slot_time = form.end_slot_time.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `timetable`( center_id, subject_id, user_id, class_id, day, start_slot_time, status, created_at, updated_at, end_slot_time) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, subject_id, user_id, class_id, day, start_slot_time, status, created_at, updated_at, end_slot_time))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'timetable added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
        
@app.route('/timetable/<int:timetable_id>', methods=['GET'])
def get_timetable(timetable_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `timetable`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
FROM `timetable`
INNER JOIN user ON user.id=`timetable`.user_id
INNER JOIN class ON class.id=`timetable`.class_id
INNER JOIN subject ON subject.id=`timetable`.subject_id 
WHERE `timetable`.id ={timetable_id};

        """)
    timetable = cur.fetchone()
    cur.close()

    if timetable:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        timetable_dict = dict(zip(column_names, timetable))

        response = {'code': '200', 'status': 'true', 'data': timetable_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'timetable not found'}
        return jsonify(response)

@app.route('/timetable_id', methods=['GET'])
def get_all_timetables_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM `timetable`")
    timetables = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for timetable in timetables:
        timetable_dict = dict(zip(column_names, timetable))
        data_with_columns.append(timetable_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/timetable', methods=['POST'])
def get_all_timetables():
    data = request.get_json()
    center_id = data.get('center_id')
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `timetable`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
FROM `timetable`
INNER JOIN user ON user.id=`timetable`.user_id
INNER JOIN class ON class.id=`timetable`.class_id
INNER JOIN subject ON subject.id=`timetable`.subject_id 
WHERE `timetable`.center_id ={center_id};

        """)
    timetables = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for timetable in timetables:
        timetable_dict = dict(zip(column_names, timetable))
        data_with_columns.append(timetable_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM timetable")
    # timetables = cur.fetchall()
    # cur.close()
    
    # print(timetables)

    # response = {'code': '200', 'status': 'true', 'data': timetables}
    # return jsonify(response)

@app.route('/del_timetable/<int:id>', methods=['DELETE'])
def delete_timetable(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `timetable` WHERE id=%s", (id,))
    timetable = cur.fetchone()
    if timetable:
        logo_path = timetable[2]
        # delete the timetable from the database
        cur.execute("DELETE FROM `timetable` WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the timetable's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'timetable with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'timetable with id {id} not found'})


@app.route('/upd_timetable/<int:timetable_id>', methods=['PUT'])
def update_timetable(timetable_id): 
    form = TTForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        subject_id = form.subject_id.data
        class_id = form.class_id.data
        day = form.day.data
        start_slot_time = form.start_slot_time.data
        end_slot_time = form.end_slot_time.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `timetable` WHERE id=%s", (timetable_id,))
        timetable = cur.fetchone()

        if not timetable:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'timetable not found'}
            return jsonify(final_response)
        else:

            cur.execute("UPDATE `timetable` SET center_id=%s, subject_id=%s, status=%s, updated_at=%s, user_id=%s, class_id=%s, start_slot_time=%s, end_slot_time=%s, day=%s  WHERE id=%s", (center_id, subject_id, status, updated_at, user_id, class_id, start_slot_time, end_slot_time, day, timetable_id))
            mysql.connection.commit()
            cur.close()
            
            response = {'code': '200', 'status': 'true', 'message': 'timetable updated successfully'}
            return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Teacher attendance Form
class TeacherAttendanceForm(Form):
    center_id = IntegerField('Center Id', [validators.InputRequired()])
    class_id = IntegerField('Class Id', [validators.InputRequired()])
    user_id = IntegerField('User Id', [validators.InputRequired()])
    subject_id = IntegerField('Subject Id', [validators.InputRequired()])
    day = StringField('time')
    start_slot_time = StringField('Slot Time', [validators.InputRequired()])
    end_slot_time = StringField('Slot Time', [validators.InputRequired()])
    teacher_status = StringField('Class Id', [validators.InputRequired()])
    user_replacement_id = IntegerField('User Id', [validators.InputRequired()])
    subject_replacement_id = IntegerField('Subject Id', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())

@app.route('/add_teacher_attendance', methods=['POST'])
def add_teacher_attendance():
    form = TeacherAttendanceForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        subject_id = form.subject_id.data
        class_id = form.class_id.data
        day = form.day.data
        start_slot_time = form.start_slot_time.data
        end_slot_time = form.end_slot_time.data
        day = form.day.data
        start_slot_time = form.start_slot_time.data
        end_slot_time = form.end_slot_time.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `teacher_attendance`( center_id, subject_id, user_id, class_id, day, start_slot_time, status, created_at, updated_at, end_slot_time) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, subject_id, user_id, class_id, day, start_slot_time, status, created_at, updated_at, end_slot_time))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'teacher_attendance added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
        
@app.route('/teacher_attendance/<int:teacher_attendance_id>', methods=['GET'])
def get_teacher_attendance(teacher_attendance_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `teacher_attendance`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
FROM `teacher_attendance`
INNER JOIN user ON user.id=`teacher_attendance`.user_id
INNER JOIN class ON class.id=`teacher_attendance`.class_id
INNER JOIN subject ON subject.id=`teacher_attendance`.subject_id 
WHERE `teacher_attendance`.id ={teacher_attendance_id};

        """)
    teacher_attendance = cur.fetchone()
    cur.close()

    if teacher_attendance:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        teacher_attendance_dict = dict(zip(column_names, teacher_attendance))

        response = {'code': '200', 'status': 'true', 'data': teacher_attendance_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'teacher_attendance not found'}
        return jsonify(response)

@app.route('/teacher_attendance_id', methods=['GET'])
def get_all_teacher_attendances_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM `teacher_attendance`")
    teacher_attendances = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for teacher_attendance in teacher_attendances:
        teacher_attendance_dict = dict(zip(column_names, teacher_attendance))
        data_with_columns.append(teacher_attendance_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/teacher_attendance', methods=['POST'])
def get_all_teacher_attendances():
    data = request.get_json()
    center_id = data.get('center_id')
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `teacher_attendance`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
FROM `teacher_attendance`
INNER JOIN user ON user.id=`teacher_attendance`.user_id
INNER JOIN class ON class.id=`teacher_attendance`.class_id
INNER JOIN subject ON subject.id=`teacher_attendance`.subject_id 
WHERE `teacher_attendance`.center_id ={center_id};

        """)
    teacher_attendances = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description
    cur.close()

    data_with_columns = []
    for teacher_attendance in teacher_attendances:
        teacher_attendance_dict = dict(zip(column_names, teacher_attendance))
        data_with_columns.append(teacher_attendance_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM teacher_attendance")
    # teacher_attendances = cur.fetchall()
    # cur.close()
    
    # print(teacher_attendances)

    # response = {'code': '200', 'status': 'true', 'data': teacher_attendances}
    # return jsonify(response)

@app.route('/del_teacher_attendance/<int:id>', methods=['DELETE'])
def delete_teacher_attendance(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `teacher_attendance` WHERE id=%s", (id,))
    teacher_attendance = cur.fetchone()
    if teacher_attendance:
        logo_path = teacher_attendance[2]
        # delete the teacher_attendance from the database
        cur.execute("DELETE FROM `teacher_attendance` WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the teacher_attendance's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'teacher_attendance with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'teacher_attendance with id {id} not found'})


@app.route('/upd_teacher_attendance/<int:teacher_attendance_id>', methods=['PUT'])
def update_teacher_attendance(teacher_attendance_id): 
    form = TeacherAttendanceForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        subject_id = form.subject_id.data
        class_id = form.class_id.data
        day = form.day.data
        start_slot_time = form.start_slot_time.data
        end_slot_time = form.end_slot_time.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `teacher_attendance` WHERE id=%s", (teacher_attendance_id,))
        teacher_attendance = cur.fetchone()

        if not teacher_attendance:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'teacher_attendance not found'}
            return jsonify(final_response)
        else:

            cur.execute("UPDATE `teacher_attendance` SET center_id=%s, subject_id=%s, status=%s, updated_at=%s, user_id=%s, class_id=%s, start_slot_time=%s, end_slot_time=%s, day=%s  WHERE id=%s", (center_id, subject_id, status, updated_at, user_id, class_id, start_slot_time, end_slot_time, day, teacher_attendance_id))
            mysql.connection.commit()
            cur.close()
            
            response = {'code': '200', 'status': 'true', 'message': 'teacher_attendance updated successfully'}
            return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Teacher Apis #..............................................................
class TeacherForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    user_id = IntegerField('Subjects ID', [validators.InputRequired()])
    class_id = IntegerField('Subjects ID', [validators.InputRequired()])
    subject_id = IntegerField('Subjects ID', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    form = TeacherForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        class_id = form.class_id.data        
        subject_id = form.subject_id.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO teacher(center_id, user_id, class_id, subject_id, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)", (center_id, user_id, class_id, subject_id, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'teacher added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'teacher addition failed'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

    
@app.route('/teacher/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
            SELECT `teacher`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
FROM `teacher`
INNER JOIN user ON user.id=`teacher`.user_id
INNER JOIN class ON class.id=`teacher`.class_id
INNER JOIN subject ON subject.id=`teacher`.subject_id 
WHERE `teacher`.id ={teacher_id};

        """)
    subject = cur.fetchone()
    cur.close()

    if subject:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        subject_dict = dict(zip(column_names, subject))

        response = {'code': '200', 'status': 'true', 'data': subject_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)

@app.route('/teacher/user_class_ids/subjects', methods=['GET'])
def get_teacher_by_user_id_class_id():
    cur = mysql.connection.cursor()
    user_id = request.args.get('user_id')
    class_id = request.args.get('class_id')
    cur.execute(f"""
            SELECT `teacher`.*,subject.name AS subject_names
FROM `teacher`
INNER JOIN subject ON subject.id=`teacher`.subject_id 
WHERE `teacher`.user_id ={user_id} AND `teacher`.class_id ={class_id};

        """)
    subject = cur.fetchone()
    print(subject)
    cur.close()

    if subject:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        subject_dict = dict(zip(column_names, subject))

        response = {'code': '200', 'status': 'true', 'data': subject_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found', 'data': {'subject_id': '0', 'subject_names': 'No Subject'}}
        return jsonify(response)



@app.route('/teacher_ids/<int:center_id>', methods=['GET'])
def get_all_teacher_ids(center_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM teacher WHERE center_id=%s",(center_id,))
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/teacher', methods=['POST'])
def get_all_teacher():
    data = request.get_json()
    center_id = data.get('center_id')
    cur = mysql.connection.cursor()
    if center_id == '0':
        cur.execute(f"""
                SELECT `teacher`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
    FROM `teacher`
    INNER JOIN user ON user.id=`teacher`.user_id
    INNER JOIN class ON class.id=`teacher`.class_id
    INNER JOIN subject ON subject.id=`teacher`.subject_id;

            """)        
    else: 
        cur.execute(f"""
                SELECT `teacher`.*,user.name AS user_names ,class.name AS class_names ,subject.name AS subject_names
    FROM `teacher`
    INNER JOIN user ON user.id=`teacher`.user_id
    INNER JOIN class ON class.id=`teacher`.class_id
    INNER JOIN subject ON subject.id=`teacher`.subject_id 
    WHERE `teacher`.center_id ={center_id};

            """)
    subjects = cur.fetchall()
    print(subjects)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for subject in subjects:
        user_dict = dict(zip(column_names, subject))
        # Split the role_names into a list
        user_dict['subject_names'] = user_dict['subject_names'].split(',')
        data_with_columns.append(user_dict)


    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)


@app.route('/del_teacher/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    cur = mysql.connection.cursor()
    uteacher = cur.execute(f"DELETE FROM teacher WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if uteacher > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'teacher found', 'data': uteacher}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'teacher not found', 'data': uteacher}
        return jsonify(final_response)


@app.route('/upd_teacher/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    form = TeacherForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        class_id = form.class_id.data        
        subject_id = form.subject_id.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teacher WHERE id=%s", (teacher_id,))
        uteacher = cur.fetchone()

        if not uteacher:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'teacher not found'}
            return jsonify(final_response)
        else:
            cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()  # Fetch a single row

            if result:
                cur.execute("UPDATE teacher SET center_id=%s, user_id=%s, class_id=%s, subject_id=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, user_id, class_id, subject_id, status, updated_at, teacher_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'teacher updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'teacher not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True)