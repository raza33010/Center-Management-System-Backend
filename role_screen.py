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

class RscreenForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

mysql = MySQL(app)


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
    rscreen = cur.fetchone()
    cur.close()

    if rscreen:
        response = {'code': '200', 'status': 'true', 'data': rscreen}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'rscreen not found'}
        return jsonify(response)

@app.route('/rscreen', methods=['GET'])
def get_all_rscreen():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rscreen")
    rscreen = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': rscreen}
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
