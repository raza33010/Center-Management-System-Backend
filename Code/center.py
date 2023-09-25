import os
from flask import Flask, request, flash, jsonify, make_response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField, DecimalField, DateField, TimeField
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
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['CORS_ALLOW_ALL_ORIGINS'] = True
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

mysql = MySQL(app)

# Center Apis #..............................................................
class CenterForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    coo = StringField('COO', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())



@app.route('/add_center', methods=['POST'])
def add_center():
    form = CenterForm(request.form)
    if form.validate():
        name = form.name.data
        logo = request.files['logo']
        coo = form.coo.data
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
        cur.execute("INSERT INTO center(name, logo, coo, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (name, str(filename), coo, status, created_at, updated_at))
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
    if request.method == 'OPTIONS':
        response_1 = make_response()
        response_1.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response_1.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response_1.headers.add("Access-Control-Allow-Methods", "PATCH")
        return response    
    form = CenterForm(request.form)
    if form.validate():
        name = form.name.data
        coo = form.coo.data
        logo = request.files['logo']
        status = form.status.data
        updated_at = form.updated_at.data
        
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


        cur.execute("UPDATE center SET name=%s, logo=%s, coo=%s, status=%s, updated_at=%s WHERE id=%s", (name, filename, coo, status, updated_at, center_id))
        mysql.connection.commit()
        cur.close()
        
        response = {'code': '200', 'status': 'true', 'message': 'Center updated successfully'}
        return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Accounts Apis #..............................................................
class AccountForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    user_id = IntegerField('User ID', [validators.InputRequired()])
    description = StringField('Description')
    bank_id = IntegerField('Bank ID', [validators.InputRequired()])
    amount = DecimalField('Amount', [validators.InputRequired()])
    transaction_id = StringField('Transaction ID')
    transaction_type = StringField('Transaction Type')
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_account', methods=['POST'])
def add_account():
    form = AccountForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        user_id = form.user_id.data
        description = form.description.data
        bank_id = form.bank_id.data
        amount = form.amount.data
        transaction_id = form.transaction_id.data
        transaction_type = form.transaction_type.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO account(center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, created_at, updated_at))
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



    
@app.route('/account/<int:account_id>', methods=['GET'])
def get_account(account_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
    account = cur.fetchone()
    cur.close()

    if account:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        account_dict = dict(zip(column_names, account))

        response = {'code': '200', 'status': 'true', 'data': account_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Center not found'}
        return jsonify(response)

@app.route('/account', methods=['GET'])
def get_all_account():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM account")
    accounts = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
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
        user_id = form.user_id.data
        description = form.description.data
        bank_id = form.bank_id.data
        amount = form.amount.data
        transaction_id = form.transaction_id.data
        transaction_type = form.transaction_type.data
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
            cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE account SET center_id=%s, user_id=%s, description=%s, bank_id=%s, amount=%s, transaction_id=%s, transaction_type=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, updated_at, account_id))
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

# Users Apis #..............................................................
class UserForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    role = StringField('Role', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_user', methods=['POST'])
def add_user():
    form = UserForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        role = form.role.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO c_user(center_id, name, role, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, name, role, status, created_at, updated_at))
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM c_user WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        user_dict = dict(zip(column_names, user))

        response = {'code': '200', 'status': 'true', 'data': user_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)

@app.route('/user', methods=['GET'])
def get_all_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM c_user")
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

@app.route('/del_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    cur = mysql.connection.cursor()
    user = cur.execute("DELETE FROM c_user WHERE id= %s", (id,))
    mysql.connection.commit()

    if user:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    form = UserForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        role = form.role.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM c_user WHERE id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'user not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            if result:
                cur.execute("UPDATE c_user SET center_id=%s, name=%s, role=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, role, status, updated_at, user_id))
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
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        
        if result:
            cur.execute("INSERT INTO batch(center_id, name, status, created_at, updated_at) VALUES( %s, %s, %s, %s, %s)", (center_id, name, status, created_at, updated_at))
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
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)

@app.route('/batch', methods=['GET'])
def get_all_batch():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM batch")
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
    form = BatchForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
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
                cur.execute("UPDATE batch SET center_id=%s, name=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, status, updated_at, batch_id))
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
    subjects_id = IntegerField('Subjects ID', [validators.InputRequired()])
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
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO class(center_id, name, total_students, subjects_id, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)", (center_id, name, total_students, subjects_id, status, created_at, updated_at))
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
    cur.execute("SELECT * FROM class WHERE id=%s", (class_id,))
    uclass = cur.fetchone()
    cur.close()

    if uclass:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        class_dict = dict(zip(column_names, uclass))

        response = {'code': '200', 'status': 'true', 'data': class_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'class not found'}
        return jsonify(response)

@app.route('/class', methods=['GET'])
def get_all_class():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM class")
    uclass = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for clas in uclass:
        clas_dict = dict(zip(column_names, clas))
        data_with_columns.append(clas_dict)

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
    form = ClassForm(request.form)
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
    user_id = IntegerField('User_id', [validators.InputRequired()])
    job = StringField('Job', [validators.InputRequired()])
    date = DateField('Date')
    time = TimeField('Time')
    assigned_by = StringField('Assigned By', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_duty', methods=['POST'])
def add_duty():
    form = DutyForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        job = form.job.data
        date = form.date.data
        time = form.time.data
        assigned_by = form.assigned_by.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute(
                "INSERT INTO duty(center_id, user_id, job, date, duty_time, assigned_by, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (center_id, user_id, job, date, time, assigned_by, status, created_at, updated_at)
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
    cur.execute("SELECT * FROM duty WHERE id=%s", (duty_id,))
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

@app.route('/duty')
def get_all_duty():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM duty")
    duty = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for clas in duty:
        clas_dict = dict(zip(column_names, clas))
        data_with_columns.append(clas_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

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
        time = form.time.data
        assigned_by = form.assigned_by.data
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
            cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute(
                    "UPDATE duty SET center_id=%s, user_id=%s, job=%s, date=%s, time=%s, assigned_by=%s, status=%s, updated_at=%s WHERE id=%s",
                    (center_id, user_id, job, date, time, assigned_by, status, updated_at, duty_id)
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
    roll_no = StringField('Roll No', [validators.InputRequired()])
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    batch_id = IntegerField('Batch ID', [validators.InputRequired()])
    class_id = IntegerField('Class ID', [validators.InputRequired()])
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
        roll_no = form.roll_no.data
        center_id = form.center_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        filename=image.filename
        filename1=bform.filename
        if filename != '' and filename1 != '':
            file_ext = os.path.splitext(filename)[1]
            file_ext1 = os.path.splitext(filename1)[1]
            if (file_ext and file_ext1) not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
        image.save(f'uploads/image and bform/{image.filename}')
        bform.save(f'uploads/image and bform/{bform.filename}')


        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM batch WHERE id = %s", (batch_id,))
        result_1 = cur.fetchone()
        cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
        result_2 = cur.fetchone()  # Fetch a single row
        if result and result_1 and result_2:
            cur.execute("INSERT INTO student(image, name, phone, father_name, father_phone, email, address, bform, roll_no, center_id, batch_id, class_id, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(filename), name, phone, father_name, father_phone, email, address, str(filename1), roll_no, center_id, batch_id, class_id, status, created_at, updated_at))
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
    cur.execute("SELECT * FROM student WHERE id=%s", (student_id,))
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

@app.route('/student', methods=['GET'])
def get_all_student():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student")
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
        # delete the center from the database
        cur.execute("DELETE FROM student WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the center's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], image_path))
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], bform_path))
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
        roll_no = form.roll_no.data
        center_id = form.center_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
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
            if image_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], image_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],image_path))
            if bform_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], bform_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],bform_path))
            
            filename=image.filename
            filename1=bform.filename
            if filename != '' and filename1 != '':
                file_ext = os.path.splitext(filename)[1]
                file_ext1 = os.path.splitext(filename1)[1]
            if (file_ext and file_ext1) not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
            image.save(f'uploads/image and bform/{image.filename}')
            bform.save(f'uploads/image and bform/{bform.filename}')            
            
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM batch WHERE id = %s", (batch_id,))
            result_1 = cur.fetchone()
            cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
            result_2 = cur.fetchone()  # Fetch a single row
            if result and result_1 and result_2:
                cur.execute("UPDATE student SET image=%s, name=%s, phone=%s, father_name=%s, father_phone=%s, email=%s, address=%s, bform=%s, roll_no=%s, center_id=%s, batch_id=%s, class_id=%s, status=%s, updated_at=%s WHERE id=%s", (str(filename), name, phone, father_name, father_phone, email, address, str(filename1), roll_no, center_id, batch_id, class_id, status, updated_at, student_id))
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
    class_id = IntegerField('Class ID', [validators.InputRequired()])
    user_id = IntegerField('User ID', [validators.InputRequired()])
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
        class_id = form.class_id.data
        user_id = form.user_id.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
        result_2 = cur.fetchone()  # Fetch a single row
        if result and result_1 and result_2:
            cur.execute("INSERT INTO subject(center_id, name, class_id, user_id, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)", (center_id, name, class_id, user_id, status, created_at, updated_at))
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

@app.route('/subject/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subject WHERE id=%s", (subject_id,))
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

@app.route('/subject', methods=['GET'])
def get_all_subject():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subject")
    subjects = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for subject in subjects:
        subject_dict = dict(zip(column_names, subject))
        data_with_columns.append(subject_dict)

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
    form = SubjectForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        class_id = form.class_id.data
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
            cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
            result_2 = cur.fetchone()  # Fetch a single row
            if result and result_1 and result_2:
                cur.execute("UPDATE subject SET center_id=%s, name=%s, class_id=%s, user_id=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, class_id, user_id, status, updated_at, subject_id))
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

# Teacher Apis #..............................................................
class TeacherForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    user_id = IntegerField('Exam ID', [validators.InputRequired()])
    subject_id = IntegerField('Student ID', [validators.InputRequired()])
    class_id = IntegerField('Student ID', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    form = TeacherForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        user_id = form.user_id.data
        subject_id = form.subject_id.data
        class_id = form.class_id.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
        result_2 = cur.fetchone()  # Fetch a single row
        cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
        result_3 = cur.fetchone()
        if result and result_1 and result_2 and result_3:
            cur.execute("INSERT INTO teacher(center_id, user_id, subject_id, class_id, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)", (center_id, user_id, subject_id, class_id, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'teacher added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/teacher/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM teacher WHERE id=%s", (teacher_id,))
    teacher = cur.fetchone()
    cur.close()

    if teacher:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        teacher_dict = dict(zip(column_names, teacher))

        response = {'code': '200', 'status': 'true', 'data': teacher_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'teacher not found'}
        return jsonify(response)

@app.route('/teacher', methods=['GET'])
def get_all_teacher():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM teacher")
    teachers = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for teacher in teachers:
        teacher_dict = dict(zip(column_names, teacher))
        data_with_columns.append(teacher_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_teacher/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    cur = mysql.connection.cursor()
    teacher = cur.execute("DELETE FROM teacher WHERE id= %s", (id,))
    mysql.connection.commit()

    if teacher:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_teacher/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    form = TeacherForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        subject_id = form.subject_id.data
        class_id = form.class_id.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teacher WHERE id=%s", (teacher_id,))
        teacher = cur.fetchone()

        if not teacher:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'teacher not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
            result_2 = cur.fetchone()  # Fetch a single row
            cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
            result_3 = cur.fetchone()
            if result and result_1 and result_2 and result_3:
                cur.execute("UPDATE teacher SET center_id=%s, user_id=%s, subject_id=%s, class_id=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, user_id, subject_id, class_id, status, updated_at, teacher_id))
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


if __name__ == "__main__":
    app.run(debug=True)