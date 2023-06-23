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

class BankForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    balance = IntegerField('balance', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

mysql = MySQL(app)


@app.route('/add_bank', methods=['POST'])
def add_bank():
    form = BankForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        name = form.name.data
        balance = form.balance.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        if result:
            cur.execute("INSERT INTO bank(center_id, name, balance, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (center_id, name, balance, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'bank added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/bank/<int:bank_id>', methods=['GET'])
def get_bank(bank_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bank WHERE id=%s", (bank_id,))
    bank = cur.fetchone()
    cur.close()

    if bank:
        response = {'code': '200', 'status': 'true', 'data': bank}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'bank not found'}
        return jsonify(response)

@app.route('/bank', methods=['GET'])
def get_all_bank():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bank")
    bank = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': bank}
    return jsonify(response)

@app.route('/del_bank/<int:id>', methods=['DELETE'])
def delete_bank(id):
    cur = mysql.connection.cursor()
    bank = cur.execute("DELETE FROM bank WHERE id= %s", (id,))
    mysql.connection.commit()

    if bank:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_bank/<int:bank_id>', methods=['PUT'])
def update_bank(bank_id):
    form = BankForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        balance = form.balance.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM bank WHERE id=%s", (bank_id,))
        bank = cur.fetchone()

        if not bank:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'bank not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            if result:
                cur.execute("UPDATE bank SET center_id=%s, name=%s, balance=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, balance, status, updated_at, bank_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'bank updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'bank not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True)
