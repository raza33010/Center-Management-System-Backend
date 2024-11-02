import os
from flask import Flask, request, flash, jsonify, make_response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, IntegerField, validators, DateTimeField, DecimalField, DateField, TimeField, PasswordField, SelectMultipleField
from datetime import datetime
from flask_wtf.file import FileField, FileAllowed, FileRequired
from collections import OrderedDict
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'center'
app.config['UPLOADED_DIRECTORY'] = 'uploads/'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.pdf']
# app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['CORS_ALLOW_ALL_ORIGINS'] = True
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# CORS(app, resources={r"/add_users": {"origins": "http://localhost:3000"}})
mysql = MySQL(app)


# Subject Apis #..............................................................
class SubjectForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    user_id = StringField('User ID', [validators.InputRequired()])
    # status = IntegerField('Status', [
    #     validators.InputRequired(),
    #     validators.AnyOf([0, 1], 'Must be 0 or 1')
    # ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)

class USubjectForm(Form):
    center_id = IntegerField('Center ID', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired()])
    user_id = StringField('User ID', [validators.InputRequired()])
    status = IntegerField('Status', [
        validators.InputRequired(),
        validators.AnyOf([0, 1], 'Must be 0 or 1')
    ])
    created_at = DateTimeField('Created At', default=datetime.utcnow)
    updated_at = DateTimeField('Updated At', default=datetime.utcnow)


@app.route('/add_subject', methods=['POST'])
def add_subject():
    form = SubjectForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        user_id = form.user_id.data
        created_at = form.created_at.data
        updated_at = form.updated_at.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
        result = cur.fetchone()
        cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        result_1 = cur.fetchone()
        if result and result_1:
            cur.execute("INSERT INTO subject(center_id, name, user_id, created_at, updated_at) VALUES( %s, %s, %s, %s, %s)", (center_id, name, user_id, created_at, updated_at))
            mysql.connection.commit()
            cur.close()
            response = {'code': '200', 'status': 'true', 'message': 'Subject added successfully'}
            return jsonify(response)
        else:
            response = {'code': '400', 'status': 'false', 'message': 'Invalid center ID'}
            return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(response)

@app.route('/subject/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT
    s.*,
    GROUP_CONCAT(u.name) AS user_names
FROM subject s
JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
WHERE s.id = {subject_id}
GROUP BY s.id ;

    """)
    subject = cur.fetchone()
    cur.close()

    if subject:
        column_names = [desc[0] for desc in cur.description]  # Get column names from cursor description

        subject_dict = dict(zip(column_names, subject))

        response = {'code': '200', 'status': 'true', 'data': subject_dict}
        return jsonify(response)
    else:
        response = {'code': '400', 'status': 'false', 'message': 'user not found'}
        return jsonify(response)


@app.route('/subjects', methods=['POST'])
def get_all_subjects():
    data = request.get_json()
    center_id = data.get('center_id')
    print(center_id)
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT id, name FROM subject WHERE  center_id = {center_id}")
    Uroles = cur.fetchall()
    print(Uroles)
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/subject', methods=['POST'])
def get_all_subject():
    data = request.get_json()
    center_id = data.get('center_id')
    user_id = data.get('user_id')
    cur = mysql.connection.cursor()
    if center_id == '0':            
        cur.execute(f"""
            SELECT
        s.*,
        GROUP_CONCAT(u.name) AS user_names
    FROM subject s
    JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
    GROUP BY s.id ;

        """)
    else:
        if user_id:
            cur.execute(f"""
                SELECT
            s.*,
            GROUP_CONCAT(u.name) AS user_names
        FROM subject s
        JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
        WHERE s.center_id = {center_id} AND s.user_id = {user_id}
        GROUP BY s.id ;

            """)
        else:
            cur.execute(f"""
                SELECT
            s.*,
            GROUP_CONCAT(u.name) AS user_names
        FROM subject s
        JOIN user u ON FIND_IN_SET(u.id, s.user_id) > 0
        WHERE s.center_id = {center_id}
        GROUP BY s.id ;

            """)
            
    subjects = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for subject in subjects:
        user_dict = dict(zip(column_names, subject))
        # Split the role_names into a list
        user_dict['user_names'] = user_dict['user_names'].split(',')
        data_with_columns.append(user_dict)


    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

@app.route('/del_subject/<int:id>', methods=['DELETE'])
def delete_subject(id):
    cur = mysql.connection.cursor()
    user = cur.execute(f"DELETE FROM subject WHERE id={id}")
    mysql.connection.commit()
    cur.close()
    if user > 0:
        final_response = {'code': '200', 'status': 'true', 'message': 'user found', 'data': user}
        return jsonify(final_response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'user not found', 'data': user}
        return jsonify(final_response)


@app.route('/upd_subject/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    form = USubjectForm(request.form)
    if form.validate():
        center_id = form.center_id.data
        name = form.name.data
        user_id = form.user_id.data
        status = form.status.data
        updated_at = form.updated_at.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM subject WHERE id=%s", (subject_id,))
        role = cur.fetchone()

        if not role:
            cur.close()
            final_response = {'code': '404', 'status': 'false', 'message': 'role not found'}
            return jsonify(final_response) 
        else:
            cur.execute("SELECT * FROM center WHERE id = %s", (center_id,))
            result = cur.fetchone()
            cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            result_1 = cur.fetchone()
            if result and result_1:
                cur.execute("UPDATE subject SET center_id=%s, name=%s, user_id=%s, status=%s, updated_at=%s WHERE id=%s", (center_id, name, user_id, status, updated_at, subject_id))
                mysql.connection.commit()
                cur.close()
                response = {'code': '200', 'status': 'true', 'message': 'subject updated successfully'}
                return jsonify(response)
            else:
                response = {'code': '400', 'status': 'false', 'message': 'subject not updated successfully'}
                return jsonify(response)
    else:
        final_response = {'code': '400', 'status': 'false', 'message': 'Invalid input'}
        return jsonify(final_response)

# Dashboard api ...................................................................






# Home Page Apis.......................................

# for subject drop down........................
@app.route('/subject_dropdown', methods=['POST'])
def subject_dropdown():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT teacher.subject_id, subject.name AS subject_names
FROM teacher
INNER JOIN subject ON subject.id= teacher.subject_id 
WHERE teacher.center_id =%s AND teacher.class_id = %s;
                
                """, (center_id,class_id,))

    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

# for student drop down........................
@app.route('/student_dropdown', methods=['POST'])
def student_dropdown():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM student WHERE center_id=%s AND class_id=%s", (center_id,class_id,))

    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

# for teacher drop down........................
@app.route('/teacher_dropdown', methods=['POST'])
def teacher_dropdown():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT teacher.id, user.name AS user_names
FROM teacher
INNER JOIN user ON user.id= teacher.user_id 
WHERE teacher.center_id =%s AND teacher.class_id = %s;
                
                """, (center_id,class_id,))

    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)

# for teacher/invagilator drop down........................
# for month drop down........................

# for home page card........................
@app.route('/home_card_data', methods=['POST'])
def get_card_data():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    
    if not center_id or not class_id:
        return jsonify({"code": "400", "status": "false", "message": "center_id and class_id are required"}), 400

    subject_id = data.get('subject_id')
    month = data.get('month')
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')
    
    cur = mysql.connection.cursor()
    
    # Card 1: Count for teachers
    if teacher_id:
        cur.execute("""
        SELECT COUNT(id) AS teacher_count
        FROM teacher
        WHERE center_id = %s AND class_id = %s AND user_id = %s
    """, (center_id, class_id, teacher_id))
    else:
        cur.execute("""
        SELECT COUNT(id) AS teacher_count
        FROM teacher
        WHERE center_id = %s AND class_id = %s
    """, (center_id, class_id))
    teacher_count = cur.fetchone()[0]
    
    # Card 2: Count for students
    if student_id:
        cur.execute("""
        SELECT COUNT(id) AS student_count
        FROM student
        WHERE center_id = %s AND class_id = %s AND id = %s
    """, (center_id, class_id, student_id))
    else:
        cur.execute("""
        SELECT COUNT(id) AS student_count
        FROM student
        WHERE center_id = %s AND class_id = %s
    """, (center_id, class_id))

    student_count = cur.fetchone()[0]
    
    # Card 3: Percentage of course covered
    if teacher_id and month:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND cchapter.user_id = %s AND ctopic.month = %s AND ctopic.status = 1;
        """, (center_id, class_id, teacher_id, month))
        course_covered_present = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND cchapter.user_id = %s AND ctopic.month = %s;
        """, (center_id, class_id, teacher_id, month))
        course = cur.fetchone()[0]

    elif teacher_id:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND cchapter.user_id = %s AND ctopic.status = 1;
        """, (center_id, class_id, teacher_id))
        course_covered_present = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND cchapter.user_id = %s;
        """, (center_id, class_id, teacher_id))
        course = cur.fetchone()[0]

    elif month:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND ctopic.month = %s AND ctopic.status = 1;
        """, (center_id, class_id, month))
        course_covered_present = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND ctopic.month = %s;
        """, (center_id, class_id, month))
        course = cur.fetchone()[0]

    else:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND ctopic.status = 1;
        """, (center_id, class_id))
        course_covered_present = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s;
        """, (center_id, class_id))
        course = cur.fetchone()[0]

    course_covered = (int(course_covered_present) / int(course)) * 100
    # Card 4: Percentage of invigilator covered
    if teacher_id and month:
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.status = 1 AND duty.user_id = %s AND duty.date = %s;    
        """, (center_id, class_id, teacher_id, month))
        invigilator_attendance_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.user_id = %s AND duty.date = %s;    
        """, (center_id, class_id, teacher_id, month))
        invigilator = cur.fetchone()[0]
    elif teacher_id:
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.status = 1 AND duty.user_id = %s;    
        """, (center_id, class_id, teacher_id))
        invigilator_attendance_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.user_id = %s;    
        """, (center_id, class_id, teacher_id))
        invigilator = cur.fetchone()[0]
    elif month:
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.status = 1 AND duty.date = %s;    
        """, (center_id, class_id, month))
        invigilator_attendance_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.date = %s;    
        """, (center_id, class_id, month))
        invigilator = cur.fetchone()[0]
    else:
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator' AND duty.status = 1;    
        """, (center_id, class_id))
        invigilator_attendance_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(duty.id) AS invigilator_attendance_present
            FROM duty
            INNER JOIN teacher ON teacher.user_id= duty.user_id 
            WHERE duty.center_id =%s AND teacher.class_id = %s AND duty.job = 'invagilator';    
        """, (center_id, class_id))
        invigilator = cur.fetchone()[0]
    
    invigilator_attendance = (int(invigilator_attendance_present)/int(invigilator))*100
    
    # Card 5: Percentage of teacher attendance
    
    if teacher_id and month:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present' AND timetable.user_id = %s AND teacher_attendance.date = %s; 
    """, (center_id, class_id, teacher_id, month))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND   timetable.user_id = %s AND teacher_attendance.date = %s; 
    """, (center_id, class_id, teacher_id, month))
        teacher = cur.fetchone()[0]
    elif teacher_id:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present' AND timetable.user_id = %s; 
    """, (center_id, class_id, teacher_id))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND timetable.user_id = %s; 
    """, (center_id, class_id, teacher_id))
        teacher = cur.fetchone()[0]
    elif month:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present' AND teacher_attendance.date = %s; 
    """, (center_id, class_id, month))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.date = %s; 
    """, (center_id, class_id, month))
        teacher = cur.fetchone()[0]
    else:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present'; 
    """, (center_id, class_id))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s; 
    """, (center_id, class_id))
        teacher = cur.fetchone()[0]   
    

    teacher_attendance = (int(teacher_attendance_present)/int(teacher))*100
    
   # Card 6: Percentage of targeted course covered
    if teacher_id and month:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND cchapter.user_id = %s AND ctopic.month = %s;
        """, (center_id, class_id, teacher_id, month))
        course_covered_present = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND cchapter.user_id = %s;
        """, (center_id, class_id, teacher_id))
        course = cur.fetchone()[0]

    else:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON (class.subject_ids LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_ids LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_ids = cchapter.subject_id)
            WHERE ctopic.center_id = %s AND class.id = %s AND ctopic.month = %s;
        """, (center_id, class_id, month))
        course_covered_present = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id = ctopic.chapter_id
            INNER JOIN class ON class.id = %s
                            AND (class.subject_id LIKE CONCAT('%,', cchapter.subject_id, ',%')
                                OR class.subject_id LIKE CONCAT(cchapter.subject_id, ',%')
                                OR class.subject_id LIKE CONCAT('%,', cchapter.subject_id)
                                OR class.subject_id = cchapter.subject_id)
            WHERE ctopic.center_id = %s;
        """, (class_id, center_id))
        course = cur.fetchone()[0]       
    
    targeted_course_covered = (int(course_covered_present)/int(course))*100

    # card 7:class average
    if month and subject_id:
        cur.execute("""
            SELECT SUM(r.number) AS total_marks
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.subject_id = %s AND r.month = %s;    
        """, (center_id, class_id, subject_id, month))
        total_marks = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(r.id) AS total_student
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.subject_id = %s;    
        """, (center_id, class_id, subject_id))
        total_student = cur.fetchone()[0]
    else:
        cur.execute("""
            SELECT SUM(r.number) AS total_marks
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.month = %s;    
        """, (center_id, class_id, month))
        total_marks= cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(r.id) AS total_student
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.subject_id = %s;    
        """, (center_id, class_id, subject_id))
        total_student= cur.fetchone()[0]
    class_average= (int(total_marks)/int(total_student))*100
    # student attendance
   
    
    cur.close()
    
    response = {
        "code": "200",
        "status": "true",
        "data": {
            "teacher_count": teacher_count,
            "student_count": student_count,
            "course_covered": course_covered,
            "invigilator_attendance": invigilator_attendance,
            "teacher_attendance": teacher_attendance,
            "targeted_course_covered": targeted_course_covered,
            "class_average": class_average,
        }
    }
    
    return jsonify(response)

@app.route('/average_graph', methods=['POST'])
def average_graph():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    month = data.get('month')
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')

    # Start building the SQL query
    query = """
        SELECT month, AVG(percentage) AS average_percentage
        FROM results
        WHERE center_id = %s AND class_id = %s
    """
    
    # Prepare parameters and append optional filters
    params = [center_id, class_id]
    
    if subject_id:
        query += " AND subject_id = %s"
        params.append(subject_id)
    
    if month:
        query += " AND month = %s"
        params.append(month)
    
    if teacher_id:
        query += " AND teacher_id = %s"
        params.append(teacher_id)
    
    if student_id:
        query += " AND student_id = %s"
        params.append(student_id)
    
    # Group by month
    query += " GROUP BY month"
    
    # Execute the query
    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    
    Uroles = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    
    data_with_columns = []
    for Urole in Uroles:
        Urole_dict = dict(zip(column_names, Urole))
        data_with_columns.append(Urole_dict)

    response = {
        "code": "200",
        "data": data_with_columns,
        "status": "true"
    }

    return jsonify(response)





# Result.png page Apis .......................................

@app.route('/grade_count_graph', methods=['POST'])
def grade_count():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    month = data.get('month')
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')

    # Start buildg the SQL query
    query = """
        SELECT grade, COUNT(*) AS count
        FROM results
        WHERE center_id = %s AND class_id = %s
    """
    
    # Prepare parameters and append optional filters
    params = [center_id, class_id]
    
    if subject_id:
        query += " AND subject_id  %s"
        params.append(subject_id)
    
    if month:
        query += " AND month  %s"
        params.append(month)
    
    if teacher_id:
        query += " AND teacher_id  %s"
        params.append(teacher_id)
    
    if student_id:
        query += " AND student_id  %s"
        params.append(student_id)
    
    # Group by grade
    query += " GROUP BY grade"
    
    # Execute the query
    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    
    grade_counts = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    
    # Convert result to JSON format
    grade_count_dict = {}
    for grade_count in grade_counts:
        grade, count = grade_count
        grade_count_dict[grade] = count

    response = {
        "code": "200",
        "data": grade_count_dict,
        "status": "true"
    }

    return jsonify(response)

# studuent average graph
@app.route('/class_average', methods=['POST'])
def student_average():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    month = data.get('month')
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')

    # Start building the SQL query
    query = """
            SELECT s.name, AVG(r.percentage) AS average_percentage
            FROM results r
            JOIN student s ON r.student_id = s.id
            WHERE r.center_id = %s AND r.class_id = %s
        """
    
    # Prepare parameters and append optional filters
    params = [center_id, class_id]
    
    if subject_id:
        query += " AND r.subject_id = %s"
        params.append(subject_id)
    
    if month:
        query += " AND r.month = %s"
        params.append(month)
    
    if teacher_id:
        query += " AND r.teacher_id = %s"
        params.append(teacher_id)
    
    if student_id:
        query += " AND r.student_id = %s"
        params.append(student_id)
    
    # Group by student_name
    query += " GROUP BY s.name"
    
    # Execute the query
    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    
    student_averages = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    
    # Convert result to JSON format
    student_average_dict = {}
    for student_average in student_averages:
        student_name, average_percentage = student_average
        student_average_dict[student_name] = average_percentage

    response = {
        "code": "200",
        "data": student_average_dict,
        "status": "true"
    }

    return jsonify(response)


#overall result graph: display all student percentage/subject wise marks
@app.route('/overall_result', methods=['POST'])
def student_overallmarks():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    month = data.get('month')
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')

    # Start building the SQL query
    query=""
    if month and subject_id:
        query += """
            SELECT s.name, r.number AS student_marks
            FROM results r
            JOIN student s ON r.student_id = s.id
            WHERE r.center_id = %s AND r.class_id = %s
        """
    else:
        query += """
            SELECT s.name, AVG(r.percentage) AS student_percentage
            FROM results r
            JOIN student s ON r.student_id = s.id
            WHERE r.center_id = %s AND r.class_id = %s
        """
    
    
    # Prepare parameters and append optional filters
    params = [center_id, class_id]
    
    if subject_id:
        query += " AND r.subject_id = %s"
        params.append(subject_id)
    
    if month:
        query += " AND r.month = %s"
        params.append(month)
    
    # Group by student_name
    query += " GROUP BY s.name"
    
    # Execute the query
    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    
    student_results = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    
    # Convert result to JSON format
    student_overall_dict = {}
    for student_result in student_results:
        student_name = student_result[0]
        average_percentage = student_result[1] if len(student_result) > 1 else 0  
        student_overall_dict[student_name] = average_percentage

    response = {
        "code": "200",
        "data": student_overall_dict,
        "status": "true"
    }


    return jsonify(response)


#Admin.png page Apis ......................................

    #Teacher attendance graph
@app.route('/teacher_attendance_graph', methods=['POST'])
def Teacher_Attendance():
    data = request.get_json()
    center_id = data.get('center_id') #1
    class_id = data.get('class_id') #2
    
    if not center_id or not class_id:
        return jsonify({"code": "400", "status": "false", "message": "center_id and class_id are required"}), 400

    month = data.get('month') #2024-04-03
    teacher_id = data.get('teacher_id') #24
    
    cur = mysql.connection.cursor()
    
    attendance_data = {}

    if teacher_id and month:
        # Retrieve attendance percentage for a specific teacher in a specific month
        cur.execute("""
            SELECT u.id AS user_id, 
                   u.name AS teacher_name, 
                   COUNT(ta.id) AS teacher_attendance_present
            FROM teacher_attendance ta
            INNER JOIN timetable t ON t.id = ta.timetable_id 
            INNER JOIN teacher te ON te.id = t.user_id
            INNER JOIN user u ON u.id = te.user_id
            WHERE ta.center_id = %s 
            AND t.class_id = %s 
            AND ta.teacher_status = 'Present' 
            AND t.user_id = %s 
            AND ta.date = %s
            GROUP BY u.id;
        """, (center_id, class_id, teacher_id, month))
        
        result = cur.fetchall()
        
        if result:  # Check if result is not empty
            teacher_attendance_present = result[0][2]
            total_teachers = 1  # Since we are fetching only one teacher
            attendance_data[result[0][1]] = (int(teacher_attendance_present) / total_teachers) * 100 if total_teachers > 0 else 0
        else:
            attendance_data["No data"] = 0  # Handle case when no data is returned

    elif month:
        # Retrieve attendance percentages for all teachers in a specific month
        cur.execute("""
            SELECT u.id AS user_id, 
                   u.name AS teacher_name, 
                   COUNT(ta.id) AS teacher_attendance_present
            FROM teacher_attendance ta
            INNER JOIN timetable t ON t.id = ta.timetable_id 
            INNER JOIN teacher te ON te.id = t.user_id
            INNER JOIN user u ON u.id = te.user_id
            WHERE ta.center_id = %s 
            AND t.class_id = %s 
            AND ta.teacher_status = 'Present' 
            AND ta.date = %s 
            GROUP BY u.id;
        """, (center_id, class_id, month))
        
        attendance_present = cur.fetchall()

        for row in attendance_present:
            teacher_name = row[1]
            attendance_present_count = row[2]
            total_count = attendance_present_count  # Modify as needed if total teachers differ
            attendance_data[teacher_name] = (int(attendance_present_count) / int(total_count)) * 100 if total_count > 0 else 0

    elif teacher_id:
        # Retrieve attendance percentages for all months of a specific teacher
        cur.execute("""
            SELECT MONTH(ta.date) AS month, 
                   u.name AS teacher_name, 
                   COUNT(ta.id) AS teacher_attendance_present
            FROM teacher_attendance ta
            INNER JOIN timetable t ON t.id = ta.timetable_id 
            INNER JOIN teacher te ON te.id = t.user_id
            INNER JOIN user u ON u.id = te.user_id
            WHERE ta.center_id = %s 
            AND t.class_id = %s 
            AND ta.teacher_status = 'Present' 
            AND t.user_id = %s 
            GROUP BY MONTH(ta.date), u.id;
        """, (center_id, class_id, teacher_id))
        
        attendance_present = cur.fetchall()

        for row in attendance_present:
            month = row[0]
            teacher_name = row[1]
            attendance_present_count = row[2]
            attendance_data[teacher_name] = (int(attendance_present_count) / int(attendance_present_count)) * 100 if attendance_present_count > 0 else 0

    cur.close()

    return jsonify({
        "code": "200",
        "status": "true",
        "attendance_data": attendance_data
    })
    #Invagilator attendance graph

@app.route('/invigilator_attendance_graph', methods=['POST'])
def Invigilator_Attendance():
    data = request.get_json()
    center_id = data.get('center_id') #1
    class_id = data.get('class_id')   #2
    teacher_id = data.get('teacher_id')  #27
    month = data.get('month')  #2024-02

    if not center_id or not class_id:
        return jsonify({"code": "400", "status": "false", "message": "center_id and class_id are required"}), 400

    cur = mysql.connection.cursor()

    # List to hold the attendance data for each invigilator
    invigilator_data = []

    # Determine which parameters to use for queries
    if teacher_id and month:
        # Get the attendance and total count for the specific teacher and month
        query = """
            SELECT u.name, 
                   COUNT(d.id) AS invigilator_attendance_present,
                   (SELECT COUNT(d.id) 
                    FROM duty d 
                    WHERE d.center_id = %s 
                      AND d.job = 'invagilator' 
                      AND d.user_id = t.user_id 
                      AND d.date = %s) AS total_invigilator
            FROM duty d
            INNER JOIN teacher t ON t.user_id = d.user_id 
            INNER JOIN user u ON u.id = t.user_id  -- Joining with user table to get names
            WHERE d.center_id = %s 
              AND t.class_id = %s 
              AND d.job = 'invagilator' 
              AND d.status = 1 
              AND d.user_id = %s 
              AND d.date = %s
            GROUP BY u.name;
        """
        cur.execute(query, (center_id, month, center_id, class_id, teacher_id, month))

    elif teacher_id:
        query = """
            SELECT u.name, 
                   COUNT(d.id) AS invigilator_attendance_present,
                   (SELECT COUNT(d.id) 
                    FROM duty d 
                    WHERE d.center_id = %s 
                      AND d.job = 'invagilator' 
                      AND d.user_id = t.user_id) AS total_invigilator
            FROM duty d
            INNER JOIN teacher t ON t.user_id = d.user_id 
            INNER JOIN user u ON u.id = t.user_id  -- Joining with user table to get names
            WHERE d.center_id = %s 
              AND t.class_id = %s 
              AND d.job = 'invagilator' 
              AND d.status = 1 
              AND d.user_id = %s
            GROUP BY u.name;
        """
        cur.execute(query, (center_id, center_id, class_id, teacher_id))

    elif month:
        query = """
            SELECT u.name, 
                   COUNT(d.id) AS invigilator_attendance_present,
                   (SELECT COUNT(d.id) 
                    FROM duty d 
                    WHERE d.center_id = %s 
                      AND d.job = 'invagilator' 
                      AND d.date = %s) AS total_invigilator
            FROM duty d
            INNER JOIN teacher t ON t.user_id = d.user_id 
            INNER JOIN user u ON u.id = t.user_id  -- Joining with user table to get names
            WHERE d.center_id = %s 
              AND t.class_id = %s 
              AND d.job = 'invagilator' 
              AND d.status = 1 
              AND d.date = %s
            GROUP BY u.name;
        """
        cur.execute(query, (center_id, month, center_id, class_id, month))

    else:
        query = """
            SELECT u.name, 
                   COUNT(d.id) AS invigilator_attendance_present,
                   (SELECT COUNT(d.id) 
                    FROM duty d 
                    WHERE d.center_id = %s 
                      AND d.job = 'invagilator') AS total_invigilator
            FROM duty d
            INNER JOIN teacher t ON t.user_id = d.user_id 
            INNER JOIN user u ON u.id = t.user_id  -- Joining with user table to get names
            WHERE d.center_id = %s 
              AND t.class_id = %s 
              AND d.job = 'invagilator' 
              AND d.status = 1
            GROUP BY u.name;
        """
        cur.execute(query, (center_id, center_id, class_id))

    rows = cur.fetchall()

    for row in rows:
        name = row[0]  # Invigilator name from user table
        invigilator_attendance_present = row[1]
        total_invigilator = row[2] if row[2] else 1  # Avoid division by zero

        invigilator_attendance_percentage = (invigilator_attendance_present / total_invigilator) * 100
        invigilator_data.append({
            "name": name,
            "attendance_percentage": invigilator_attendance_percentage
        })

    cur.close()

    return jsonify({
        "code": "200",
        "status": "true",
        "invigilator_data": invigilator_data
    })

    #Student Attendance
# @app.route('/student_attendance', methods=['POST'])
# def Invigilator_Attendance():






#Academic.png Apis  ..........................................

    #academic cards data
@app.route('/invigilator_attendance_graph', methods=['POST'])
def get_academic_Card_Data():
    data = request.get_json()
    center_id = data.get('center_id')
    class_id = data.get('class_id')
    
    if not center_id or not class_id:
        return jsonify({"code": "400", "status": "false", "message": "center_id and class_id are required"}), 400

    subject_id = data.get('subject_id')
    month = data.get('month')
    teacher_id = data.get('teacher_id')
    cur = mysql.connection.cursor()

    # Card 4: Percentage of course covered
    if teacher_id and month:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND cchapter.user_id = %s AND ctopic.month = %s AND ctopic.status = 1;    
        """, (center_id, class_id, teacher_id, month))
        course_covered_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND cchapter.user_id = %s AND ctopic.month = %s;    
        """, (center_id, class_id, teacher_id, month))
        course = cur.fetchone()[0]
    elif teacher_id:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND cchapter.user_id = %s AND ctopic.status = 1;    
        """, (center_id, class_id, teacher_id))
        course_covered_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND cchapter.user_id = %s;    
        """, (center_id, class_id, teacher_id))
        course = cur.fetchone()[0]
    elif month:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND ctopic.month = %s AND ctopic.status = 1;    
        """, (center_id, class_id, month))
        course_covered_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND ctopic.month = %s;    
        """, (center_id, class_id, month))
        course = cur.fetchone()[0]
    else:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND ctopic.status = 1;    
        """, (center_id, class_id))
        course_covered_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s;    
        """, (center_id, class_id))
        course = cur.fetchone()[0]

    course_covered = (int(course_covered_present)/int(course))*100
    
    # Card 1: Percentage of teacher attendance
    
    if teacher_id and month:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present' AND timetable.user_id = %s AND teacher_attendance.date = %s; 
    """, (center_id, class_id, teacher_id, month))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND   timetable.user_id = %s AND teacher_attendance.date = %s; 
    """, (center_id, class_id, teacher_id, month))
        teacher = cur.fetchone()[0]
    elif teacher_id:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present' AND timetable.user_id = %s; 
    """, (center_id, class_id, teacher_id))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND timetable.user_id = %s; 
    """, (center_id, class_id, teacher_id))
        teacher = cur.fetchone()[0]
    elif month:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present' AND teacher_attendance.date = %s; 
    """, (center_id, class_id, month))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.date = %s; 
    """, (center_id, class_id, month))
        teacher = cur.fetchone()[0]
    else:
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s AND teacher_attendance.teacher_status = 'Present'; 
    """, (center_id, class_id))
        teacher_attendance_present = cur.fetchone()[0]
        cur.execute("""
         SELECT COUNT(teacher_attendance.id) AS teacher_attendance_present
            FROM teacher_attendance
            INNER JOIN timetable ON timetable.id= teacher_attendance.timetable_id 
            WHERE teacher_attendance.center_id =%s AND timetable.class_id = %s; 
    """, (center_id, class_id))
        teacher = cur.fetchone()[0]   
    

    teacher_attendance = (int(teacher_attendance_present)/int(teacher))*100
    
    # Card 3: Percentage of targeted course covered
    if teacher_id and month:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND cchapter.user_id = %s AND ctopic.month = %s;    
        """, (center_id, class_id, teacher_id, month))
        course_covered_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND cchapter.user_id = %s;    
        """, (center_id, class_id, teacher_id))
        course = cur.fetchone()[0]
    else:
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s AND ctopic.month = %s;    
        """, (center_id, class_id, month))
        course_covered_present = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(ctopic.id) AS course_covered_present
            FROM ctopic
            INNER JOIN cchapter ON cchapter.id= ctopic.chapter_id 
            WHERE ctopic.center_id =%s AND cchapter.class_id = %s;    
        """, (center_id, class_id,))
        course = cur.fetchone()[0]       
    
    targeted_course_covered = (int(course_covered_present)/int(course))*100

    
    # card 2:subject average
    if month and subject_id:
        cur.execute("""
            SELECT SUM(r.number) AS total_marks
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.subject_id = %s AND r.month = %s;    
        """, (center_id, class_id, subject_id, month))
        total_marks = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(r.id) AS total_student
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.subject_id = %s;    
        """, (center_id, class_id, subject_id))
        total_student = cur.fetchone()[0]
    else:
        cur.execute("""
            SELECT SUM(r.number) AS total_marks
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.month = %s;    
        """, (center_id, class_id, month))
        total_marks= cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(r.id) AS total_student
            FROM results r
            WHERE r.center_id =%s AND r.class_id = %s AND r.subject_id = %s;    
        """, (center_id, class_id, subject_id))
        total_student= cur.fetchone()[0]
    class_average= (int(total_marks)/int(total_student))*100
    cur.close()


#Student.png Apis  .............................

#SubjectResults.png Apis. ...............................


if __name__ == "__main__":
    app.run(debug=True)