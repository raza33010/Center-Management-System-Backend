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
app.config['UPLOADED_DIRECTORY'] = 'uploads/image and bform/'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.pdf']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024




class ResultForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    exam_id = IntegerField('Exam ID', [validators.InputRequired()])
    student_id = IntegerField('Student ID', [validators.InputRequired()])
    mark = IntegerField('Marks', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

    

mysql = MySQL(app)

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
    user = cur.fetchone()
    cur.close()

    if user:
        response = {'code': '200', 'status': 'true', 'data': user}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'result not found'}
        return jsonify(response)

@app.route('/result', methods=['GET'])
def get_all_result():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM result")
    users = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': users}
    return jsonify(response)

@app.route('/del_result/<int:id>', methods=['DELETE'])
def delete_result(id):
    cur = mysql.connection.cursor()
    result = cur.execute("DELETE FROM result WHERE id= %s", (id,))
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
                response = {'code': '200', 'status': 'true', 'message': 'result updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'result not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True) 