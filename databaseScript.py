import sqlite3
from sqlite3 import Error

# def create_database():
#     connection = sqlite3.connect("botdatabase.db")

def create_tables():
    conn = sqlite3.connect("botdatabase.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Students(
                zach_num INTEGER NOT NULL PRIMARY KEY,
                surname TEXT NOT NULL,
                name TEXT NOT NULL,
                second_name TEXT NOT NULL,
                user_id INTEGER
            );
    """)
    conn.commit()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Teachers(
                surname TEXT NOT NULL,
                name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                login TEXT NOT NULL PRIMARY KEY,
                password TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                chat_id INTEGER UNIQUE 
            );""")
    conn.commit()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Courses(
                    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );""")
    conn.commit()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Enrollment(
                        stud_id INTEGER NOT NULL,
                        course_id INTEGER NOT NULL,
                        start_date DATE NOT NULL
                    );""")
    conn.commit()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Visits(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            zach_num INTEGER NOT NULL,
                            course_id INTEGER NOT NULL,
                            date DATE NOT NULL,
                            hooky INTEGER NOT NULL,
                            score INTEGER NOT NULL,
                            homework INTEGER NOT NULL
                        );""")
    conn.commit()
    conn.close()


def drop_tables():
    conn = sqlite3.connect("botdatabase.db")
    cursor = conn.cursor()
    cursor.execute("""DROP TABLE IF EXISTS Students;""")
    conn.commit()
    cursor.execute("""DROP TABLE IF EXISTS Teachers;""")
    conn.commit()
    cursor.execute("""DROP TABLE IF EXISTS Courses;""")
    conn.commit()
    cursor.execute("""DROP TABLE IF EXISTS Enrollment;""")
    conn.commit()
    cursor.execute("""DROP TABLE IF EXISTS Visits;""")
    conn.commit()
    conn.close()


def fill_tables():
    conn = sqlite3.connect("botdatabase.db")
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO Students(zach_num, surname, name, second_name) 
                        VALUES(1000, 'Багаутдинов', 'Рамиль', 'Шамилевич'),
                        (1001, 'Биктимиров', 'Владимир', 'Олегович'),
                        (1002, 'Гавриличев', 'Павел', 'Николаевич'),
                        (1003, 'Галеева', 'Аделя', 'Азатовна'),
                        (1004, 'Давлятшин', 'Роберт', 'Айратович'),
                        (1005, 'Ефимов', 'Данила', 'Вадимович'),
                        (1006, 'Багаутдинов', 'Рамиль', 'Шамилевич'),
                        (1007, 'Закиев', 'Эмиль', 'Рамилевич'),
                        (1008, 'Коробов', 'Александр', 'Александрович'),
                        (1009, 'Кадочников', 'Артем', 'Игоревич'),
                        (1010, 'Лапинский', 'Васислий', 'Александрович'),
                        (1011, 'Макисмов', 'Никита', 'Михайлович'),
                        (1012, 'Миннуллина', 'Регина', 'Алмазовна'),
                        (1013, 'Палий', 'Элина', 'Алмазовна'),
                        (1014, 'Садыков', 'Ильдар', 'Наилевич'),
                        (1015, 'Салимуллина', 'Айгуль', 'Альбертовна'),
                        (1016, 'Салимуллина', 'Айгуль', 'Альбертовна'),
                        (1017, 'Ситдикова', 'Алсу', 'Айдаровна'),
                        (1018, 'Шахова', 'Анастасия', 'Юрьевна'),
                        (1019, 'Тощев', 'Георгий', 'Андреевич'),
                        (1020, 'Фаттахова', 'Ильсияр', 'Фархатовна'),
                        (1021, 'Корягин', 'Сергей', 'Евгеньевич');""")
    conn.commit()
    cursor.execute("""INSERT INTO Courses(course_id, name)
                            VALUES(1, 'Python'),
                            (2, 'C++'),
                            (3, 'Java'),
                            (4, 'Базы данных');""")
    conn.commit()
    cursor.execute("""INSERT INTO Teachers(surname, name, last_name, login, password, course_id)
                        VALUES('Абдуллин','Адель','Ильдусович','Abd12','4567',1),
                        ('Мосин','Сергей','Геннадьевич','msn23','12365',2),
                        ('Байрашева','Венера','Рустамовна','bsh9','1110',3),
                        ('Хайруллин','Альфред','Фаридович','khf','12367',4);""")
    conn.commit()
    conn.close()

