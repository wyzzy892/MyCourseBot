import config
import telebot
from telebot import types
import sqlite3
from time import sleep
from database import *
import datetime
from convert import convert_to_excel, convert_to_list
import requests, time, random, xlrd
from databaseScript import create_tables, fill_tables, drop_tables

drop_tables()
create_tables()
fill_tables()
# подключаемся к боту
bot = telebot.TeleBot(config.TOKEN)


# start
@bot.message_handler(commands=['start'])
def command_handler(message):
    keyboard = types.InlineKeyboardMarkup()
    stud_btn = types.InlineKeyboardButton(text="Студент", callback_data='stud')
    teach_btn = types.InlineKeyboardButton(text="Преподаватель", callback_data='teach')
    keyboard.add(stud_btn)
    keyboard.add(teach_btn)
    bot.send_message(message.chat.id, config.start, reply_markup=keyboard)

# help
@bot.message_handler(commands=['help'])
def command_handler(message):
    bot.send_message(message.chat.id, config.help)

# показать студенту список всех курсов
@bot.message_handler(commands=['courses'])
def handle_command(message):
    courses = types.InlineKeyboardMarkup()
    for course in get_courses():
        courses.add(types.InlineKeyboardButton(text=course[1], callback_data=f'course_{course[0]}'))
    bot.send_message(message.chat.id, "Выберите курс", reply_markup=courses)

# показать студенту список курсов, на которые он записан
@bot.message_handler(commands=['mycourses'])
def handle_command(message):
    bot.send_message(message.chat.id, "номер зачетки")
    bot.register_next_step_handler(message, get_my_courses)


def get_my_courses(message):
    zach_num = message.text.strip()
    try:
        zach_num = int(zach_num)
        mycourses = get_student_courses(zach_num)
        if len(mycourses) == 0:
            bot.send_message(message.chat.id, 'Вы не записаны ни на один курс')
        else:
            spisok = []
            exit_buttons = types.InlineKeyboardMarkup()
            for mycourse in mycourses:
                info = mycourse[1]
                if datetime.datetime.now() < datetime.datetime.fromisoformat(mycourse[2]) + datetime.timedelta(days=21):
                    button = types.InlineKeyboardButton(text=f"Покинуть курс {mycourse[1]}",
                                                        callback_data=f'exit_{mycourse[0]}_{zach_num}')
                    exit_buttons.add(button)
                else:
                    info += " (невозможно покинуть)"
                spisok.append(info)
            bot.send_message(message.chat.id, 'Вы записаны на {}'.format(', '.join(spisok)), reply_markup=exit_buttons)
    except:
        bot.send_message(message.chat.id, "номер зачетки целое число без пробелов и др. знаков препинания")

# показать информацию о курсе
@bot.message_handler(commands=['about'])
def handle_command(message):
    courses = types.InlineKeyboardMarkup()
    for course in get_courses():
        courses.add(types.InlineKeyboardButton(text=course[1], callback_data=f'about_{course[0]}'))
    bot.send_message(message.chat.id, "Выберите курс, о котором хотите узнать", reply_markup=courses)

# показать текущие средние баллы по курсам
@bot.message_handler(commands=['myrating'])
def handle_command(message):
    bot.send_message(message.chat.id, "номер зачетки")
    bot.register_next_step_handler(message, get_myrating)

def get_myrating(message):
    zach_num = message.text.strip()
    try:
        zach_num=int(zach_num)
        mycourses = get_student_courses(zach_num)
        rating_list = []
        for course in mycourses:
            rating_list.append(f"{course[1]} {get_average_score_by_course_id(course[0], zach_num)}")
        bot.send_message(message.chat.id, "Ваши текущие баллы:\n" + "\n".join(rating_list))
    except:
        bot.send_message(message.chat.id, "номер зачетки целое число без пробелов и др. знаков препинания")

# покинуть курс
@bot.message_handler(commands=['exit'])
def handle_text(message):
    courses = types.InlineKeyboardMarkup()
    student_courses = get_student_courses(message.chat.id)
    if len(student_courses) == 0:
        bot.send_message(message.chat.id, "Вы не состоите ни в одном курсе")
    else:
        for course in student_courses:
            courses.add(types.InlineKeyboardButton(text=course[1], callback_data=f'exit_{course[0]}'))
        bot.send_message(message.chat.id, "Выберите курс, который хотите покинуть", reply_markup=courses)


@bot.message_handler(commands=["mystudents"])
def get_teachers_students(message):
    course_id = get_teachers_course_id(message.chat.id)
    studs = get_students_rating(course_id)
    filename = convert_to_excel(studs)
    with open(filename, "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=["uploadratings"])
def upload_current_ratings(message):
    bot.send_message(message.chat.id, 'Прикрепите документ')
    bot.register_next_step_handler(message, upload_rating)


@bot.message_handler(commands=["uploadstudents"])
def upload_new_students(message):
    bot.send_message(message.chat.id, 'Прикрепите документ')
    bot.register_next_step_handler(message, upload_student)


@bot.message_handler(commands=["uploadhomework"])
def upload_homework(message):
    bot.send_message(message.chat.id, 'Прикрепите документ или напишите сообщение')
    bot.register_next_step_handler(message, post_message)


@bot.message_handler(commands=["post"])
def upload_homework(message):
    bot.send_message(message.chat.id, 'Напишите сообщение')
    bot.register_next_step_handler(message, post_message)


# и для дз и для постов
def post_message(message):
    course_id = get_teachers_course_id(message.chat.id)
    student_list = get_students_chat_id_by_course(course_id)
    try:
        message.document.file_id
        for i in student_list:
            bot.send_document(i, message.document.file_id)
        bot.send_message(message.chat.id, 'ДЗ отправлено всем студентам данной группы')
    except AttributeError:
        for i in student_list:
            bot.send_message(i, message.text)
        bot.send_message(message.chat.id, 'Сообщение отправлено всем студентам данной группы')


def upload_rating(message):
    try:
        f = bot.get_file(message.document.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.TOKEN, f.file_path))
        list_ratings = convert_to_list(file.content)
        print(list_ratings)
        course_id = get_teachers_course_id(message.chat.id)
        current_date = datetime.datetime.now()
        load_visits(list_ratings, course_id, current_date)
        bot.send_message(message.chat.id, 'Рейтинги обновлены')
    except AttributeError:
        bot.send_message(message.chat.id, 'Прикрепите документ')


# загрузить список студентов
def upload_student(message):
    try:
        f = bot.get_file(message.document.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.TOKEN, f.file_path))

        list_students = convert_to_list(file.content)
        print(list_students)
        course_id = get_teachers_course_id(message.chat.id)
        update_list_students(list_students, course_id)
        bot.send_message(message.chat.id, 'Список студентов обновлен')
    except AttributeError:
        bot.send_message(message.chat.id, 'Прикрепите документ')


@bot.callback_query_handler(func=lambda call: True)
def callback_message(call):
    try:
        if call.message:
            if call.data == 'stud':
                bot.send_message(call.message.chat.id, config.for_student)  # get info for students
            elif call.data == 'teach':
                bot.send_message(call.message.chat.id, 'Введите ваш логин и пароль через пробел: ')
                bot.register_next_step_handler(call.message, login_teacher)
            elif call.data.startswith("about_"):
                course_id = int(call.data.split('_')[1])
                bot.send_message(call.message.chat.id, config.abouts[course_id])
            elif call.data.startswith("course_"):
                course_id = int(call.data.split('_')[1])
                bot.send_message(call.message.chat.id, 'Введите фамилию, имя и отчество и номер '
                                                       'зачетки в одно сообщение через пробел')
                bot.register_next_step_handler(call.message, add_to_course, course_id)
                # date_begin = "2021-02-10"
                # dt = datetime.datetime.fromisoformat(date_begin)+datetime.timedelta(days=21)
                # if datetime.datetime.now()<dt:
                #     course_id = int(call.data.split('_')[1])
                #     bot.send_message(call.message.chat.id, 'Введите фамилию, имя и отчество и номер '
                #                                            'зачетки в одно сообщение через пробел')
                #     bot.register_next_step_handler(call.message, add_to_course, course_id)
                # else:
                #     bot.send_message(call.message.chat.id, "Истекло время записи на курс")
            elif call.data.startswith("exit_"):
                course_id, zach_num = map(int, call.data.split('_')[1:])
                if exit_course(zach_num, course_id):
                    bot.send_message(call.message.chat.id, config.exit_course)
                    teacher_chat_id = get_teacher_chat_id_by_course_id(course_id)
                    student_info = get_info_about_student(zach_num)
                    response = f'Студент {student_info[1]} {student_info[2]} {student_info[3]} ' \
                               f'с номером зачетки {student_info[0]} покидает Ваш курс'
                    bot.send_message(teacher_chat_id, response)
                else:
                    bot.send_message(call.message.chat.id, "Поздно!!!")
                # course_ - запись
                # exit_ - выйти с курса
                # about_ - информация о курсе

    except Exception as e:
        print(repr(e))

# добавить на курс
def add_to_course(message, course_id):
    print(message.text)
    info = str(message.text).split(' ')
    add_user_id(message.chat.id, info[3])
    print(message.chat.id)
    if add_student_to_course_by_course_id(course_id, info[3]):
        bot.send_message(message.chat.id, "Вы успешно записаны на курс!")
    else:
        bot.send_message(message.chat.id, "Вы уже записаны на курс")

# авторизация преподавателя
def login_teacher(message):
    login, password = message.text.split(' ', 1)
    autorizied, FIO = get_info_by_loginpass(login, password)
    if autorizied == True:
        update_teacher_chat_id(login, message.chat.id)
        bot.send_message(message.chat.id, "Отлично! Вы авторизованы!")
        bot.send_message(message.chat.id, "Здравствуйте, "+" ".join(FIO))
        bot.send_message(message.chat.id, config.for_teachers)  # get info for teachers
    else:
        bot.send_message(message.chat.id, "Неверные данные для авторизации!")


bot.polling()