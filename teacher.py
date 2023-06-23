import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, IntegerField, validators, DateTimeField
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'

class TeacherForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    user_id = IntegerField('Exam ID', [validators.InputRequired()])
    subject_id = IntegerField('Student ID', [validators.InputRequired()])
    class_id = IntegerField('Student ID', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

    

mysql = MySQL(app)

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
        response = {'code': '200', 'status': 'true', 'data': teacher}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'teacher not found'}
        return jsonify(response)

@app.route('/teacher', methods=['GET'])
def get_all_teacher():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM teacher")
    teacher = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': teacher}
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


if __name__ == "__main__":
    app.run(debug=True) 