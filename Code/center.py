import os
from flask import Flask, request, flash, jsonify, make_response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField, DecimalField
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
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png']
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


if __name__ == "__main__":
    app.run(debug=True)