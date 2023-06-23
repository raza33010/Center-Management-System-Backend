import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField, DateField
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'
app.config['UPLOADED_DIRECTORY'] = 'uploads/file/'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.pdf']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024




class SrecordForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    student_id = IntegerField('Student ID', [validators.InputRequired()])
    description = StringField('Description')
    date = DateField('Date')
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

    

mysql = MySQL(app)


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
    user = cur.fetchone()
    cur.close()

    if user:
        response = {'code': '200', 'status': 'true', 'data': user}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'srecord not found'}
        return jsonify(response)

@app.route('/srecord', methods=['GET'])
def get_all_srecord():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM srecord")
    users = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': users}
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


if __name__ == "__main__":
    app.run(debug=True)
