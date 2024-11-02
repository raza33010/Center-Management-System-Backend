
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators


class StudentForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    phone = StringField('Phone', [validators.InputRequired(), validators.Regexp(r'^\d{11}$', message='Phone number should be 11 digits')])
    # phone = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])


app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crud'

mysql = MySQL(app)


@app.route('/insert', methods=['POST'])
def insert():
    form = StudentForm(request.form)
    if form.validate():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        cur = mysql.connection.cursor()
        query = "INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)"
        fields = (name, email, phone)
        cur.execute(query, fields)
        mysql.connection.commit()
        final_response = {'code': '200', 'status': 'true', 'message': 'inserted successfully'}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'data not inserted successfully'}
        return jsonify(final_response)


@app.route('/student', methods=['GET'])
def student():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/student/<int:id>', methods=['GET'])
def student_id(id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM students WHERE id = {id}")
    data = cur.fetchone()
    cur.close()
    if data:
        return jsonify(data)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'data not found'}
        return jsonify(final_response)


@app.route('/delete/<int:id_data>', methods=['DELETE'])
def delete(id_data):
    cur = mysql.connection.cursor()
    data = cur.execute(f"DELETE FROM students WHERE id={id_data}")
    mysql.connection.commit()
    cur.close()
    if data > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'data found', 'data': data}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'data not found', 'data': data}
        return jsonify(final_response)


@app.route('/update', methods=['PUT'])
def update():
    form = StudentForm(request.form)
    if form.validate():
        id = request.form['id']
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE students SET name=%s, email=%s, phone=%s WHERE id=%s""", (name, email, phone, id))
        cur.close()
        final_response = {'code': '200', 'status': 'True', 'message': 'data changed'}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'data unchanged'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True)