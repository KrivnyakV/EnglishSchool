import json

from sqlalchemy import select, insert, delete, update

from database.create_database import *
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from hash_pwd import hash_pwd
from flask import Response, jsonify

def user_register(family, name, patremonial, email, password, role):
    # request = Users.insert().values(email=email, password = password, Name= name, Surname = family, Patremonial= patremonial, Role= role)
    if role == "Студент":
        role = 'user'
    elif role == 'Преподаватель':
        role = 'teacher'
    req = insert(Users).values(email=email, password = password, Name= name, Surname = family, Patronymic= patremonial, Role= role)

    try:
        conn = engine.connect()
        conn.execute(req)
        conn.commit()
        return Response(status=200, response=json.dumps({'email': email, 'name': name, "family": family}))
    except IntegrityError:
        print(f'{email} уже зарегистрирован!')
        return Response(response="Пользователь уже зарегистрирован", status=401)
    finally:
        conn.close()


def user_authentification(email, password):
    # request = users.select().where(users.c.email == email).where( users.c.password == password)
    request = select(Users).where(Users.email == email).where( Users.password == password)

    try:
        conn = engine.connect()
        response = conn.execute(request)
        if len(response.fetchall()) > 0:
            conn.commit()
            return 1
        else:
            return 0
    except Exception as e:
        print(e)
        return 0
    finally:
        conn.close()


def getUser(email):
    request = select(Users).where(Users.email == email)
    try:
        conn = engine.connect()
        response = conn.execute(request)
        profile_data = response.fetchall()
        conn.commit()
        conn.close()
        return profile_data[0]
    except Exception as e:
        print(e)


def edit_user_from_db(data):
    request = update(Users).values(Name=data['name'], Surname=data['family'], Patremonial=data['otchestvo']).where(Users.email == data['email'])
    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()

        return Response(status=200, response=json.dumps({'name': data['name'], 'family': data['family'], "otchestvo": data['otchestvo'], 'email': data['email']}))
    except Exception as e:
        print(e)
        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()

#----------------------------------------------------------------------------------------------------------

def get_all_courses_by_direction(id):
    request = select(Courses).where(Courses.id_direction == id)
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_courses_by_direction = response.fetchall()
        conn.commit()
        conn.close()
        print(all_courses_by_direction)
        print(type(all_courses_by_direction))

        return all_courses_by_direction


    except Exception as e:
        print(e)
        return None


def get_all_courses():
    request = select(Courses)
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_courses = response.fetchall()
        conn.commit()
        conn.close()
        print(all_courses)
        print(type(all_courses))

        return all_courses


    except Exception as e:
        print(e)
        return None







def get_last_id_of_course():
    request = select(Courses).order_by(Courses.id.desc())
    try:
        conn = engine.connect()
        response = conn.execute(request)
        last_id = response.fetchall()
        conn.commit()
        conn.close()
        print(type(last_id))
        print(len(last_id))

        if len(last_id) > 0:
            print(int(last_id[0])+1)
            return json.dumps({'id': int(last_id[0])+1})
        else:
            return json.dumps({'id': 1})
    except Exception as e:

        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()



def add_course(data):
    request = insert(News).values(title=data['title'], about=data['about'], image=data['image'], date=str(data['date']))
    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()

        return Response(status=200, response=get_all_news())
    except Exception as e:

        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()


#------- NEW DB
def get_all_news():
    request = select(News).order_by(News.id.desc())
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_news = response.fetchall()
        conn.commit()
        conn.close()

        final_result = [dict(zip(response.keys(), all_news[i])) for i in range(len(all_news))]
        return json.dumps(final_result)
    except Exception as e:
        print(e)
        return None


def add_news_to_db(data):
    request = insert(News).values(title=data['title'], about=data['about'], image=data['image'], date=str(data['date']))
    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()

        return Response(status=200, response=get_all_news())
    except Exception as e:

        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()



def edit_news_from_db(data):

    if data['image'] != '/static/no_photo.jpg':
        request = update(News).values(title=data['title'], about=data['about'], image=data['image'], date=data['date']).where(News.id == data['id'])
    else:
        request = update(News).values(title=data['title'], about=data['about'], date=data['date']).where(News.id == data['id'])

    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()

        return Response(status=200, response=get_all_news())
    except Exception as e:

        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()



def delete_news_from_db(id):
    request = delete(News).where(News.id == id)
    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()

        return Response(status=200, response=json.dumps({}))
    except Exception as e:

        return Response(response=e.__str__(), status=500)
    finally:
        conn.close()




def get_news_with_limit():
    request = select(News).order_by(News.id.desc()).limit(8)
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_news = response.fetchall()

        final_result = [dict(zip(response.keys(), all_news[i])) for i in range(len(all_news))]

        conn.commit()
        conn.close()
        return json.dumps(final_result)
    except Exception as e:
        print(e)
        return None


#================================





# def to_camel_case(snake_str):
#     components = snake_str.split('_')
#     return components[0] + ''.join(x.title() for x in components[1:])
#

def sa_core_row_to_dict(row, key_camel_case: bool = False, dt_format: str = "%d/%m/%Y %H:%M:%S"):
    re = {}

    for column_name in row:
        value = row[column_name]
        if isinstance(value, datetime):
            value = datetime.strftime(value, dt_format)

        key = column_name

        re[key] = value

    return re

def sa_core_fetchall_to_dict(data, key_camel_case: bool = False, dt_format: str = "%d/%m/%Y %H:%M:%S"):
    return tuple(sa_core_row_to_dict(row, key_camel_case=key_camel_case, dt_format=dt_format) for row in data)


