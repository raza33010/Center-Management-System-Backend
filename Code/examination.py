import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField, DateField, TimeField
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




class ExaminationForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    subject_id = IntegerField('Subject ID', [validators.InputRequired()])
    type = StringField('Paper Type')
    month = StringField('Month', [validators.InputRequired()])
    date = DateField('Date')
    total_marks = IntegerField('Total Marks')
    invigilator = StringField('Invigilator')
    schedule_start_time = TimeField('Schedule Start Time')
    schedule_end_time = TimeField('Schedule End Time')
    start_time = TimeField('Start Time')
    end_time = TimeField('End Time')
    checking_status = StringField('Checking Status')
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

    

mysql = MySQL(app)


@app.route('/add_examination', methods=['POST'])
def add_exmaination():
    form = ExaminationForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        subject_id = form.subject_id.data
        type = form.type.data
        month = form.month.data
        date = form.date.data
        total_marks = form.total_marks.data
        invigilator = form.invigilator.data
        schedule_start_time = form.schedule_start_time.data
        schedule_end_time = form.schedule_end_time.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        checking_status = form.checking_status.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO examination(center_id, name, subject_id, type, month, date, total_marks, invigilator, schedule_start_time, schedule_end_time, start_time, end_time, checking_status, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, name, subject_id, type, month, date, total_marks, invigilator, schedule_start_time, schedule_end_time, start_time, end_time, checking_status, status, created_at, updated_at))
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
    cur.execute("SELECT * FROM examination WHERE id=%s", (examination_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        response = {'code': '200', 'status': 'true', 'data': user}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'examination not found'}
        return jsonify(response)

@app.route('/examination', methods=['GET'])
def get_all_examination():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM examination")
    examinations = cur.fetchall()
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
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        subject_id = form.subject_id.data
        type = form.type.data
        month = form.month.data
        date = form.date.data
        total_marks = form.total_marks.data
        invigilator = form.invigilator.data
        schedule_start_time = form.schedule_start_time.data
        schedule_end_time = form.schedule_end_time.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        checking_status = form.checking_status.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM examination WHERE id=%s", (examination_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'examination not found'}
            return jsonify(final_response)
        else:    
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM subject WHERE id = %s", (subject_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE examination SET center_id=%s, name=%s, subject_id=%s, type=%s, month=%s, date=%s, total_marks=%s, invigilator=%s, schedule_start_time=%s, schedule_end_time=%s, start_time=%s, end_time=%s, checking_status=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, subject_id, type, month, date, total_marks, invigilator, schedule_start_time, schedule_end_time, start_time, end_time, checking_status, status, updated_at, examination_id))
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


if __name__ == "__main__":
    app.run(debug=True) 