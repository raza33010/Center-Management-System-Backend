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




class StudentForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    phone = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])
    father_name = StringField('Father Name', [validators.InputRequired()])
    father_phone = StringField('Phone', [validators.InputRequired(), validators.Regexp('^\d{11}$', message='Phone number should be 11 digits')])
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    address = StringField('Address', [validators.InputRequired()])
    roll_no = StringField('Roll No', [validators.InputRequired()])
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    batch_id = IntegerField('Batch ID', [validators.InputRequired()])
    class_id = IntegerField('Class ID', [validators.InputRequired()])
    status = IntegerField('Status', [validators.InputRequired(),
                                     validators.AnyOf([0, 1], 'Must be 0 or 1')])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

    

mysql = MySQL(app)

# @app.route('/add_class', methods=['POST'])
# def add_class():
#     form = CenterForm(request.form)
#     if not form.validate():
#         for field, errors in form.errors.items():
#             for error in errors:
#                 flash(f"{field}: {error}", "error")
#         return jsonify(success=False, errors=form.errors)
#     ...



@app.route('/add_student', methods=['POST'])
def add_student():
    form = StudentForm(request.form)
    if form.validate():
        image = request.files['image']
        name = form.name.data
        phone = form.phone.data
        father_name = form.father_name.data
        father_phone = form.father_phone.data
        email = form.email.data
        address = form.address.data
        bform = request.files['bform']        
        roll_no = form.roll_no.data
        center_id = form.center_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        status = form.status.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        filename=image.filename
        filename1=bform.filename
        if filename != '' and filename1 != '':
            file_ext = os.path.splitext(filename)[1]
            file_ext1 = os.path.splitext(filename1)[1]
            if (file_ext and file_ext1) not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
        image.save(f'uploads/image and bform/{image.filename}')
        bform.save(f'uploads/image and bform/{bform.filename}')


        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM batch WHERE id = %s", (batch_id,))
        result_1 = cur.fetchone()
        cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
        result_2 = cur.fetchone()  # Fetch a single row
        if result and result_1 and result_2:
            cur.execute("INSERT INTO student(image, name, phone, father_name, father_phone, email, address, bform, roll_no, center_id, batch_id, class_id, status, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(filename), name, phone, father_name, father_phone, email, address, str(filename1), roll_no, center_id, batch_id, class_id, status, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'Student added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)



    
@app.route('/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student WHERE id=%s", (student_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        response = {'code': '200', 'status': 'true', 'data': user}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'student not found'}
        return jsonify(response)

@app.route('/student', methods=['GET'])
def get_all_student():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student")
    users = cur.fetchall()
    cur.close()

    response = {'code': '200', 'status': 'true', 'data': users}
    return jsonify(response)

@app.route('/del_student/<int:id>', methods=['DELETE'])
def delete_student(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student WHERE id=%s", (id,))
    student = cur.fetchone()
    if student:
        image_path = student[1]
        bform_path = student[8]
        # delete the center from the database
        cur.execute("DELETE FROM student WHERE id= %s", (id,))
        mysql.connection.commit()
        # delete the center's logo file
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], image_path))
        os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'], bform_path))
        return jsonify({'message': f'student with id {id} deleted successfully'})
    else:
        return jsonify({'message': f'student with id {id} not found'})


@app.route('/upd_student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    form = StudentForm(request.form)
    if form.validate():
        image = request.files['image']
        name = form.name.data
        phone = form.phone.data
        father_name = form.father_name.data
        father_phone = form.father_phone.data
        email = form.email.data
        address = form.address.data
        bform = request.files['bform']        
        roll_no = form.roll_no.data
        center_id = form.center_id.data
        batch_id = form.batch_id.data
        class_id = form.class_id.data
        status = form.status.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student WHERE id=%s", (student_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'student not found'}
            return jsonify(final_response)
        else:
            image_path = role[1]
            bform_path = role[8]
            if image_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], image_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],image_path))
            if bform_path and os.path.exists(os.path.join(app.config['UPLOADED_DIRECTORY'], bform_path)):
                os.remove(os.path.join(app.config['UPLOADED_DIRECTORY'],bform_path))
            
            filename=image.filename
            filename1=bform.filename
            if filename != '' and filename1 != '':
                file_ext = os.path.splitext(filename)[1]
                file_ext1 = os.path.splitext(filename1)[1]
            if (file_ext and file_ext1) not in app.config['UPLOAD_EXTENSIONS']:
                response = {'code':'this file extension is not allowed'}
                return jsonify(response)
            image.save(f'uploads/image and bform/{image.filename}')
            bform.save(f'uploads/image and bform/{bform.filename}')            
            
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM batch WHERE id = %s", (batch_id,))
            result_1 = cur.fetchone()
            cur.execute("SELECT * FROM class WHERE id = %s", (class_id,))
            result_2 = cur.fetchone()  # Fetch a single row
            if result and result_1 and result_2:
                cur.execute("UPDATE student SET image=%s, name=%s, phone=%s, father_name=%s, father_phone=%s, email=%s, address=%s, bform=%s, roll_no=%s, center_id=%s, batch_id=%s, class_id=%s, status=%s, updated_at=%s WHERE id=%s", (str(filename), name, phone, father_name, father_phone, email, address, str(filename1), roll_no, center_id, batch_id, class_id, status, updated_at, student_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'student updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'student not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)


if __name__ == "__main__":
    app.run(debug=True) 