import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, IntegerField, validators, DateTimeField, StringField, DateField, TimeField
from datetime import datetime
from flask import Flask, jsonify
from json import JSONEncoder
from datetime import timedelta

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            # Convert timedelta to a string representation in format HH:MM:SS
            hours, remainder = divmod(obj.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        return super().default(obj)
    
    def encode(self, obj):
        # Convert timedelta objects to strings before encoding
        obj = self.default(obj)
        return super().encode(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'

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

mysql = MySQL(app)

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
                "INSERT INTO duty(center_id, user_id, job, date, time, assigned_by, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
        response = {'code': '200', 'status': 'true', 'data': duty}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'duty not found'}
        return jsonify(response)

@app.route('/duty')
def get_all_duty():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM duty")
    duty = cur.fetchall()
    cur.close()
    response = {'code': '200', 'status': 'true', 'data': duty}
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

if __name__ == "__main__":
    app.run(debug=True)
