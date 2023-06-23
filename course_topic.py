import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, IntegerField, validators, DateTimeField, StringField, DecimalField
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'

class CtopicForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    course_id = IntegerField('Course_id', [validators.InputRequired()])
    unit_id = IntegerField('Unit_id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    month = StringField('Month', [validators.InputRequired()])
    description = StringField('Description', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

mysql = MySQL(app)

@app.route('/add_ctopic', methods=['POST'])
def add_ctopic():
    form = CtopicForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        course_id = form.course_id.data
        unit_id = form.unit_id.data
        name = form.name.data
        month = form.month.data
        description = form.description.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM cchapter WHERE id = %s", (course_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO ctopic(center_id, course_id, unit_id, name, month, description, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, course_id, unit_id, name, month, description, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'ctopic added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
    
@app.route('/ctopic/<int:ctopic_id>', methods=['GET'])
def get_ctopic(ctopic_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ctopic WHERE id=%s", (ctopic_id,))
    ctopic = cur.fetchone()
    cur.close()
    if ctopic:
        response = {'code': '200', 'status': 'true', 'data': ctopic}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'ctopic not found'}
        return jsonify(response)

@app.route('/ctopic', methods=['GET'])
def get_all_ctopic():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ctopic")
    ctopic = cur.fetchall()
    cur.close()
    response = {'code': '200', 'status': 'true', 'data': ctopic}
    return jsonify(response)

@app.route('/del_ctopic/<int:id>', methods=['DELETE'])
def delete_ctopic(id):
    cur = mysql.connection.cursor()
    ctopic = cur.execute("DELETE FROM ctopic WHERE id= %s", (id,))
    mysql.connection.commit()
    if ctopic:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})

@app.route('/upd_ctopic/<int:ctopic_id>', methods=['PUT'])
def update_ctopic(ctopic_id):
    form = CtopicForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        course_id = form.course_id.data
        unit_id = form.unit_id.data
        name = form.name.data
        month = form.month.data
        description = form.description.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM ctopic WHERE id=%s", (ctopic_id,))
        ctopic = cur.fetchone
        if not ctopic:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'ctopic not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM cchapter WHERE id = %s", (course_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE ctopic SET center_id=%s, course_id=%s, unit_id=%s, name=%s, month=%s, descritpion=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, course_id, unit_id, name, month, description, status, updated_at, ctopic_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'ctopic updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'ctopic not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=True)
