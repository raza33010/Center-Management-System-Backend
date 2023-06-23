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

class AccountForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    user_id = IntegerField('User ID', [validators.InputRequired()])
    description = StringField('Description')
    bank_id = IntegerField('Bank ID', [validators.InputRequired()])
    amount = DecimalField('Amount', [validators.InputRequired()])
    transaction_id = StringField('Transaction ID')
    transaction_type = StringField('Transaction Type')
    status = IntegerField('Status', [validators.InputRequired(), validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

mysql = MySQL(app)


@app.route('/add_account', methods=['POST'])
def add_account():
    form = AccountForm(request.form)
    if form.validate():       
        center_id = form.center_id.data
        user_id = form.user_id.data
        description = form.description.data
        bank_id = form.bank_id.data
        amount = form.amount.data
        transaction_id = form.transaction_id.data
        transaction_type = form.transaction_type.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO account(center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'account added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/account/<int:account_id>', methods=['GET'])
def get_account(account_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
    account = cur.fetchone()
    cur.close()

    if account:
        response = {'code': '200', 'status': 'true', 'data': account}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'account not found'}
        return jsonify(response)

@app.route('/account', methods=['GET'])
def get_all_account():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM account")
    account = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': account}
    return jsonify(response)

@app.route('/del_account/<int:id>', methods=['DELETE'])
def delete_account(id):
    cur = mysql.connection.cursor()
    account = cur.execute("DELETE FROM account WHERE id= %s", (id,))
    mysql.connection.commit()

    if account:
        return jsonify({'message': f'result with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'result with id {id} not found'})


@app.route('/upd_account/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    form = AccountForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        user_id = form.user_id.data
        description = form.description.data
        bank_id = form.bank_id.data
        amount = form.amount.data
        transaction_id = form.transaction_id.data
        transaction_type = form.transaction_type.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM account WHERE id=%s", (account_id,))
        account = cur.fetchone()

        if not account:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'account not found'}
            return jsonify(final_response)
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM c_user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE account SET center_id=%s, user_id=%s, description=%s, bank_id=%s, amount=%s, transaction_id=%s, transaction_type=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, user_id, description, bank_id, amount, transaction_id, transaction_type, status, updated_at, account_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'account updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'account not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True)
