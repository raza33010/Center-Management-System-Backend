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



class URoleForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    screen = StringField('Screen', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)
    

mysql = MySQL(app)




@app.route('/add_role', methods=['POST'])
def add_role():
    form = URoleForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        screen = form.screen.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()  # Fetch a single row

        if result:
            cur.execute("INSERT INTO u_role(center_id, name, screen, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, name, screen, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'user role added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'user role addition failed'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

    
@app.route('/role/<int:role_id>', methods=['GET'])
def get_role(role_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM u_role WHERE id=%s", (role_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        response = {'code': '200', 'status': 'true', 'data': user}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)

@app.route('/role', methods=['GET'])
def get_all_roles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM u_role")
    users = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': users}
    return jsonify(response)

@app.route('/del_role/<int:id>', methods=['DELETE'])
def delete_role(id):
    cur = mysql.connection.cursor()
    user = cur.execute(f"DELETE FROM u_role WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if user > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'user role found', 'data': user}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'user role not found', 'data': user}
        return jsonify(final_response)


@app.route('/upd_role/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    form = URoleForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        screen = form.screen.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM u_role WHERE id=%s", (role_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'role not found'}
            return jsonify(final_response)
        else:
            cur.execute(f"SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()  # Fetch a single row

            if result:
                cur.execute("UPDATE u_role SET center_id=%s, name=%s, screen=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, screen, status, updated_at, role_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'user role updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'user role not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True)