import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'



class ClassForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    total_students = IntegerField('Total Students', [validators.InputRequired()])
    subjects_id = IntegerField('Subjects ID', [validators.InputRequired()])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)
    

mysql = MySQL(app)

# @app.route('/add_class', methods=['POST'])
# def add_class():
#     form = CenterForm(request.form)
#     if not form.validate():
#         for field, errors in form.errors.items():
#             for error in errors:
#                 flash(f"{field}: {error}", "error")
#         return jsonify(success=False, errors=form.errors)
#     ...



@app.route('/add_class', methods=['POST'])
def add_class():
    form = ClassForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        status = form.status.data
        total_students = form.total_students.data        
        subjects_id = form.subjects_id.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO class(center_id, name, status, total_students, subjects_id, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)", (center_id, name, status, total_students, subjects_id, created_at, updated_at))
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
        response = {'code': '200', 'status': 'true', 'data': uclass}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'class not found'}
        return jsonify(response)

@app.route('/class', methods=['GET'])
def get_all_class():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM class")
    uclass = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': uclass}
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
        status = form.status.data
        total_students = form.total_students.data        
        subjects_id = form.subjects_id.data
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
                cur.execute("UPDATE class SET center_id=%s, name=%s, status=%s, total_students=%s, subjects_id=%s, updated_at=%s WHERE id=%s", (center_id, name, status, total_students, subjects_id, updated_at, class_id))
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