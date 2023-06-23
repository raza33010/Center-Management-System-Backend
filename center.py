import os
from flask import Flask, request, flash, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField
from datetime import datetime
from flask_wtf.file import FileField, FileAllowed, FileRequired


app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'
app.config['UPLOADED_DIRECTORY'] = 'uploads/'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024



class CenterForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    coo = StringField('COO', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow())
    updated_at = DateTimeField('Updated At', default=datetime.utcnow())
mysql = MySQL(app)


@app.route('/add_center', methods=['POST'])
def add_center():
    form = CenterForm(request.form)
    if form.validate():
        name = form.name.data
        logo = request.files['logo']
        coo = form.coo.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        filename=logo.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
        logo.save(f'uploads/{logo.filename}')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO center(name, logo, coo, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)", (name, str(filename), coo, status, created_at, updated_at))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'Center added successfully'}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)
    
@app.route('/center/<int:center_id>', methods=['GET'])
def get_center(center_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM center WHERE id=%s", (center_id,))
    center = cur.fetchone()
    cur.close()

    if center:
        response = {'code': '200', 'status': 'true', 'data': center}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Center not found'}
        return jsonify(response)

@app.route('/center', methods=['GET'])
def get_all_centers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM center")
    centers = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': centers}
    return jsonify(response)

@app.route('/del_center/<int:id>', methods=['DELETE'])
def delete_center(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM center WHERE id=%s", (id,))
    center = cur.fetchone()
    if center:
        logo_path = center[2]
        # delete the center from the database
        cur.execute("DELETE FROM center WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the center's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
        return jsonify({'message': f'Center with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'Center with id {id} not found'})


@app.route('/upd_center/<int:center_id>', methods=['PUT'])
def update_center(center_id):
    form = CenterForm(request.form)
    if form.validate():
        name = form.name.data
        coo = form.coo.data
        logo = request.files['logo']
        status = form.status.data
        updated_at = form.updated_at.data
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id=%s", (center_id,))
        center = cur.fetchone()

        if not center:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'Center not found'}
            return jsonify(final_response)
        else:
            logo_path = center[2]
            if logo_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], logo_path))
            filename = logo.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'E_400'}
                return jsonify(response)
            logo.save(f'uploads/{filename}')


        cur.execute("UPDATE center SET name=%s, logo=%s, coo=%s, status=%s, updated_at=%s WHERE id=%s", (name, filename, coo, status, updated_at, center_id))
        mysql.connection.commit()
        cur.close()

        response = {'code': '200', 'status': 'true', 'message': 'Center updated successfully'}
        return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True)