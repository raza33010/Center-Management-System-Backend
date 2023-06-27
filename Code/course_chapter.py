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

class CchapterForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    subject_id = IntegerField('subject_id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

mysql = MySQL(app)


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
    cchapter = cur.fetchone()
    cur.close()

    if cchapter:
        response = {'code': '200', 'status': 'true', 'data': cchapter}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'cchapter not found'}
        return jsonify(response)

@app.route('/cchapter', methods=['GET'])
def get_all_cchapter():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cchapter")
    cchapter = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': cchapter}
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


if __name__ == "__main__":
    app.run(debug=True)
