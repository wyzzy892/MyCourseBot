import sqlite3
import datetime


def find_in_students(id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    result = cursor.execute('select * from students where user_id = ?', (id,)).fetchall()
    if len(result) > 0:
        return True
    else:
        return False

def find_course_id(name):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    result = cursor.execute('select course_id from courses where name = ?', (name,)).fetchall()
    if len(result)>0:
        return result[0][0]
    else:
        return -1

# def find_student_in_course(student_id, course_id):
#     db = sqlite3.connect('botdatabase.db')
#     cursor = db.cursor()
#     result = cursor.execute('select * from enrollment where stud_id = ? and course_id=?', (student_id,course_id)).fetchall()
#     if len(result) > 0:
#         return True
#     else:
#         return False

# def add_to_students(zach_num, surname, name, second_name, user_id):
#     db = sqlite3.connect('botdatabase.db')
#     cursor = db.cursor()
#     cursor.execute('insert into students(zach_num, surname, name, second_name, user_id) '
#                    'values(?, ?, ?, ?, ?)',(zach_num, surname, name, second_name, user_id))
#     db.commit()

def add_student_to_course(course_name, stud_id):
    conn = sqlite3.connect('botdatabase.db')
    cursor = conn.cursor()
    date = datetime.datetime.now()
    course_id = find_course_id(course_name)
    cursor.execute('insert into enrollment(stud_id, course_id, start_date) values '
                   '(?,?,?)', (stud_id, course_id, date))
    conn.commit()

#
def add_student_to_course_by_course_id(course_id, student_id):
    conn = sqlite3.connect('botdatabase.db')
    cursor = conn.cursor()
    on_course = cursor.execute('select * from enrollment '
                               'where stud_id = ? and course_id = ?', (student_id, course_id)).fetchone()
    if on_course is not None:
        return False
    date = datetime.datetime.now()
    cursor.execute('insert into enrollment(stud_id, course_id, start_date) values '
                   '(?,?,?)', (student_id, course_id, date))
    conn.commit()
    return True

# добавить chat_id студента по его номеру зачетки zach_num
def add_user_id(id, zach_num):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    cursor.execute('update students set user_id = ? where zach_num = ?', (id, zach_num))
    db.commit()

# получить список курсов
def get_courses():
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    c = cursor.execute('select * from courses;').fetchall()
    return c

# получить имя курса по его course_id
def get_course_name_by_id(id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    c = cursor.execute('select name from courses where course_id = ?;', (id,)).fetchall()
    return c[0][0]


def get_student_courses(zach_num):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    c = cursor.execute('select courses.course_id, courses.name, enrollment.start_date from courses '
                       'inner join enrollment on courses.course_id = enrollment.course_id '
                       'inner join students on students.zach_num = enrollment.stud_id '
                       'where students.zach_num = ?', (zach_num,)).fetchall()
    return c

# покинуть курс по номеру зачетки zach_num и course_id
def exit_course(zach_num, course_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    c = cursor.execute('select start_date from enrollment '
                       'where stud_id = ? and course_id = ?', (zach_num, course_id,)).fetchall()
    date = datetime.datetime.fromisoformat(c[0][0]) + datetime.timedelta(days=21)
    # date = datetime.datetime.fromisoformat("2021-02-10") + datetime.timedelta(days=21)
    if date>datetime.datetime.now():
        cursor.execute('delete from enrollment where stud_id = ? and course_id = ?', (zach_num, course_id,))
        db.commit()
        return True
    else:
        return False


# получить средний балл по course_id и zach_num в качестве student_id
def get_average_score_by_course_id(course_id, student_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    try:
        avg_score = cursor.execute('''select avg(score), avg(IIF(homework is null, 0, homework)) 
                                        from visits where course_id = ? and zach_num = ?''',
                                   (course_id, student_id)).fetchone()
        if avg_score is None:
            return 0
        avg_score = list(map(lambda item:0 if item is None else item, avg_score))
        return sum(avg_score) / len(avg_score)
    except Exception as e:
        print(e)

# проверка авторизации преподавателя
def get_info_by_loginpass(login, password):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    info_teacher = cursor.execute('select password, surname, name, last_name from teachers where login = ?',
                            (login,)).fetchone()
    if info_teacher[0] == password:
        return True, info_teacher[1:]
    return False, None



# добавление chat_id преподавателя, если его нет, обновление если chat_id есть
def update_teacher_chat_id(login, chat_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    cursor.execute('update teachers set chat_id = ? where login = ?', (chat_id, login))
    db.commit()

# получаем id препода для отправки ему уведомления
def get_teacher_chat_id_by_course_id(course_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    teacher_chat_id = cursor.execute('select chat_id from teachers where course_id = ?', (course_id,)).fetchone()[0]
    return teacher_chat_id

# Получим id курса преподавателя по его chat_id
def get_teachers_course_id(chat_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    course_id = cursor.execute('select course_id from teachers where chat_id = ?', (chat_id,)).fetchone()[0]
    return course_id



# Получаем инфо о студенте
def get_info_about_student(zach_num):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    info = cursor.execute('select * from students where zach_num = ?', (zach_num,)).fetchone()
    return info

def get_students_rating(course_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    students_list = cursor.execute('''
    select s.zach_num, s.surname,
s.name, s.second_name,
count(v.hooky)-sum(v.hooky), avg(v.score), count(v.homework), avg(v.homework)
from visits as v inner join students as s on v.zach_num=s.zach_num
where v.course_id = ?
group by v.zach_num
    ''', (course_id,)).fetchall()
    return students_list


def load_visits(data, course_id, date):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    for d in data:
        cursor.execute('insert into visits(zach_num, course_id, date, hooky, score, homework) values (?, ?, ?, ?, ?, ?)',
                       (d[0], course_id, date, d[4], d[5], d[6]))
    db.commit()

def update_list_students(data, course_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    students_on_course = cursor.execute('select stud_id from enrollment where course_id = ?', (course_id, )).fetchall()
    data = (map(lambda item: item[0], data))
    students_on_course = (map(lambda item: item[0], students_on_course))
    for student in students_on_course:
        if student not in data:
            cursor.execute('delete from enrollment where course_id = ? and stud_id = ?', (course_id, student))
    db.commit()

    date = datetime.datetime.now()
    for d in data:
        if d not in students_on_course:
            cursor.execute('insert into enrollment(stud_id, course_id, start_date) values(?,?,?)', (d, course_id, date))
    db.commit()

def get_students_chat_id_by_course(course_id):
    db = sqlite3.connect('botdatabase.db')
    cursor = db.cursor()
    chat_ids = cursor.execute('select s.user_id from students as s inner join enrollment as en on s.zach_num=en.stud_id '
                   'where en.course_id = ? and s.user_id is not null', (course_id, )).fetchall()
    return map(lambda item: item[0], chat_ids)



