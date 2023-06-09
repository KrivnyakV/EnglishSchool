import json

from sqlalchemy import select, insert, delete, update , and_

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

        response = list(profile_data[0])
        if not response[6]:
            response[6] = []
        if not response[7]:
            response[7] = []
        return response
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
    request = select(Courses).where(Courses.id_direction == id).order_by(Courses.id.desc())
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_courses_by_direction = response.fetchall()
        conn.commit()
        conn.close()

        response = []
        for item in all_courses_by_direction:
            response.append({'id': item[0], 'prevTitle': item[3], 'prevImage': item[4], 'prevAbout': item[5]})

        return json.dumps({'response': response})


    except Exception as e:
        print(e)
        return None


def get_all_courses():
    request = select(Courses).where()
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_courses_by_direction = response.fetchall()
        conn.commit()
        conn.close()

        response = []
        for item in all_courses_by_direction:
            response.append({'id': item[0], 'prevTitle': item[3], 'prevImage': item[4], 'prevAbout': item[5]})

        return json.dumps({'response': response})


    except Exception as e:
        print(e)
        return None


def get_last_id_of_course():
    request = select(Courses.id).order_by(Courses.id.desc()).limit(1)
    try:
        conn = engine.connect()
        response = conn.execute(request)
        last_id = response.fetchall()
        conn.commit()
        conn.close()

        if len(last_id) > 0:
            return json.dumps({'id': last_id[0][0]+1})
        else:
            return json.dumps({'id': 1})
    except Exception as e:

        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()



def add_course_to_db(data):

    request = insert(Courses).values(id=data['id'], id_direction=data['idDirections'], all=str(data), prevTitle=data['prevTitle'], prevImage=data['prevImage'], prevAbout=data['prevAbout'] )

    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()
    except Exception as e :
        print(e)


    req = select(Users.AdminCourse).where(Users.email == data['email'])
    try:
        conn = engine.connect()
        response = conn.execute(req)
        courses_of_admin = response.fetchone()
        conn.commit()
        conn.close()




        if not courses_of_admin[0]:
            to_insert= list()
            to_insert.append(int(data['id']))
            request_2 = update(Users).values(AdminCourse=str(to_insert)).where(Users.email == data['email'])

        else:
            to_insert = courses_of_admin[0]
            result = [int(x) for x in to_insert.strip('][').split(',')]
            result.append(int(data['id']))
            request_2 = update(Users).values(AdminCourse=str(result)).where(Users.email == data['email'])



    except Exception as e :
        print(e)



    try:

        conn = engine.connect()
        conn.execute(request_2)
        conn.commit()
        conn.close()

        return Response(status=200, response=json.dumps({"id":data['id']}))
    except Exception as e:

        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()



def add_course_to_user(data):


    #Добавляем в поле ActiveCourses user - id курса
    req = select(Users.ActiveCourse).where(Users.email == data['email'])
    try:
        conn = engine.connect()
        response = conn.execute(req)
        courses_of_user = response.fetchone()
        conn.commit()
        conn.close()



        print(courses_of_user[0])
        if not courses_of_user[0]:
            to_insert = list()
            to_insert.append(int(data['id']))
            request_2 = update(Users).values(ActiveCourse=str(to_insert)).where(Users.email == data['email'])

        else:
            to_insert = courses_of_user[0]
            if to_insert != '[]':
                result = [int(x) for x in to_insert.strip('][').split(',')]
            else:
                result = []
            result.append(int(data['id']))
            request_2 = update(Users).values(ActiveCourse=str(result)).where(Users.email == data['email'])




    except Exception as e :
        print("2", e)




#Возвращаем обьект пользователя с добавленным id  курса
    try:

        conn = engine.connect()
        conn.execute(request_2)
        conn.commit()
        conn.close()





        request = select(Users).where(Users.email == data['email'])

        conn = engine.connect()
        response = conn.execute(request)
        result = response.fetchone()
        conn.commit()
        conn.close()


        temp = list(result)

        if temp[6]and temp[6] != '[]':
            temp[6] = [int(x) for x in temp[6].strip('][').split(',')]



        if temp[7] and temp[7] != '[]':
            temp[7] = [int(x) for x in temp[7].strip('][').split(',')]

        if temp[6] == '[]':
            temp[6] = []

        if temp[7] == '[]':
            temp[7] = []

        # print(temp)
        result = {"email": temp[0], "family": temp[3], 'otchestvo': temp[4], "name":temp[2], "role": temp[5], "activeCourse": temp[6], "adminCourse": temp[7]}


        try:

            get_course_request = select(Courses.all).where(Courses.id == data['id'])

            conn = engine.connect()
            response = conn.execute(get_course_request)
            course = response.fetchall()
            conn.commit()
            conn.close()



            add_request = insert(UserCourse).values(id_course=data['id'], email_user=data['email'], all_object=course[0][0])
            conn = engine.connect()
            conn.execute(add_request)
            conn.commit()
            conn.close()

            rating_request = insert(UsersRating).values(id_course=data['id'], email_user=data['email'],
                                                    answers='{}')
            conn = engine.connect()
            conn.execute(rating_request)
            conn.commit()
            conn.close()

        except Exception as e:

            print(e)
            return Response(response=e.__str__(), status=401)











        return Response(status=200, response=json.dumps(result))

    except Exception as e:
        print("3", e)
        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()





def delete_course_from_user(data):



    req = select(Users.ActiveCourse).where(Users.email == data['email'])
    try:
        conn = engine.connect()
        response = conn.execute(req)
        courses_of_user = response.fetchone()
        conn.commit()
        conn.close()




        if not courses_of_user[0]:
            to_insert = list()
            to_insert.remove(int(data['id']))
            request_2 = update(Users).values(ActiveCourse=str(to_insert)).where(Users.email == data['email'])

        else:
            to_insert = courses_of_user[0]
            if to_insert != '[]':
                result = [int(x) for x in to_insert.strip('][').split(',')]
            else:
                result = []
            result.remove(int(data['id']))
            request_2 = update(Users).values(ActiveCourse=str(result)).where(Users.email == data['email'])

    except Exception as e:
        print("2", e)


    try:

        conn = engine.connect()
        conn.execute(request_2)
        conn.commit()
        conn.close()


        request = select(Users).where(Users.email == data['email'])

        conn = engine.connect()
        response = conn.execute(request)
        result = response.fetchone()
        conn.commit()
        conn.close()

        # print(result)
        # print(type(result))

        temp = list(result)

        if temp[6] != None and temp[6] != '[]':
            temp[6] = [int(x) for x in temp[6].strip('][').split(',')]





        if temp[7] != None and temp[7] != '[]':

            temp[7] = [int(x) for x in temp[7].strip('][').split(',')]

        if temp[6] == '[]':
            temp[6] = []

        if temp[7] == '[]':
            temp[7] = []
        result = {"email": temp[0], "family": temp[3], 'otchestvo': temp[4], "name":temp[2], "role": temp[5], "activeCourse": temp[6], "adminCourse": temp[7]}



        return Response(status=200, response=json.dumps(result))

    except Exception as e:
        print("3", e)
        return Response(response=e.__str__(), status=401)
    finally:
        conn.close()


def get_one_course(data):
    print(data['id'])
    request_search = select(UserCourse).where(and_(UserCourse.email_user == data['email'], UserCourse.id_course == data['id']))
    conn = engine.connect()
    response = conn.execute(request_search)
    result = response.fetchone()
    conn.commit()
    conn.close()
    print("---", result)

    if not result:
        print("ОСНОВНАЯ ТАБЛИЦА")
        request = select(Courses.all).where(Courses.id == data['id'])
        try:
            conn = engine.connect()
            response = conn.execute(request)
            one_course = response.fetchall()
            conn.commit()
            conn.close()
            print("ONE COURSE", one_course)
            result = one_course[0][0].replace("False", '"false"').replace("'", '"')
            test = json.loads(result)
            print(data['id'])
            print(test)

            return json.dumps(test)


        except Exception as e:
            print(e)
            return None

    else:
        print("ВТОРАЯ ТАБЛИЦА")
        request = select(UserCourse.all_object).where(and_(UserCourse.email_user == data['email'], UserCourse.id_course == data['id']))
        try:
            conn = engine.connect()
            response = conn.execute(request)
            one_course = response.fetchall()
            conn.commit()
            conn.close()
            result = one_course[0][0].replace("False", '"false"').replace("'", '"')
            test = json.loads(result)
            print(data['id'])
            print(test)
            return json.dumps(test)


        except Exception as e:
            print(e)
            return Response(response=e.__str__(), status=401)









def courseStatus(data):
    print("courseStatus", data)





    try:
        add_request = update(UserCourse).values(id_course=data['id'], email_user=data['email'], all_object=str(data['course'])).where(and_(UserCourse.id_course==data['id'], UserCourse.email_user==data['email']))
        conn = engine.connect()
        conn.execute(add_request)
        conn.commit()
        conn.close()

        return Response(status=200, response=json.dumps(data['course']))
    except Exception as e:
        print(e)
        return Response(response=e.__str__(), status=401)



def add_rating(data):
    try:
        all_weight = 0
        correct_weight = 0
        print(type(data), data)

        #Для каждого вопроса
        for question in data['result']:
            #Считаем общий вес вопросов
            if type(question['idResponse']) == str:
                all_weight += int(question['name'])
                print("OOOO", all_weight)
            else:
                for response in question['idResponse']:
                    temporary_weight = int(response['name'])

                all_weight += temporary_weight

            id_chapter = question['idChapters']

            #Считаем кол-во набранных баллов
            if type(question['idResponse']) == str:
                if question['idResponse'] == question['correctId']:
                    correct_weight += int(question['name'])

            else:
                print([True if response['idRes'] in question['correctId'].split(",") else False for response in question['idResponse']])
                if all([True if response['idRes'] in question['correctId'].split(",") else False for response in question['idResponse']]):
                    correct_weight += int(question['idResponse'][0]['name'])


        print("all_weight", all_weight)
        print("idChapters", id_chapter)
        print("correct_weight", correct_weight)

        correct_percent = round(correct_weight * 100 / all_weight)
        print(f"{correct_percent} %")

    except Exception as e:
        print("Ошибка:", e)



    request = select(UsersRating.answers).where(and_(UsersRating.email_user == data['email'], UsersRating.id_course == data['id']))
    conn = engine.connect()
    response = conn.execute(request)
    one_answers = response.fetchone()
    conn.commit()
    conn.close()


    answers = json.loads(one_answers[0].replace("'", '"'))
    print(answers)

    answers[id_chapter] = correct_percent


    rating_request = update(UsersRating).values(id_course=data['id'], email_user=data['email'], answers=str(answers)).where(and_(UsersRating.id_course == data['id'], UsersRating.email_user == data['email']))



    conn = engine.connect()
    conn.execute(rating_request)
    conn.commit()
    conn.close()



    return Response(status=200, response=json.dumps(answers))
    # try:
    #     append_rating = update(UsersRating).values(id_course=data['id'], email_user=data['email'], answers=????)
    #     conn = engine.connect()
    #     conn.execute(add_request)
    #     conn.commit()
    #     conn.close()
    #
    #     return Response(status=200, response=json.dumps(data['course']))
    # except Exception as e:
    #     print(e)
    #     return Response(response=e.__str__(), status=401)






def all_rating_db(data):

    req = select(Users.AdminCourse).where(Users.email == data['email'])
    try:
        conn = engine.connect()
        response = conn.execute(req)
        courses_of_admin = response.fetchone()
        conn.commit()
        conn.close()

        if not courses_of_admin[0]:
            return Response(status=200, response=json.dumps({"response": []}))


        else:
            print(courses_of_admin[0])
            all_courses = [int(x) for x in courses_of_admin[0].strip('][').split(',')]


            response = []

            for course in all_courses:
                request = select(Courses).where(Courses.id == course)
                try:
                    conn = engine.connect()
                    response = conn.execute(request)
                    all_courses_by_id = response.fetchall()
                    conn.commit()
                    conn.close()
                    for item in all_courses_by_id:
                        response.append({"id":item[0],'prevTitle': item[3], 'prevImage': item[4], 'prevAbout': item[5]})
                except Exception as e:
                    print(e)

        return Response(status=200, response=json.dumps({"response": response}))

    except Exception as e:
        return Response(status=400, response=json.dumps({"response": f"{e}"}))



def add_rating_to_course(data):
    try:

        request = select(Courses.all).where(Courses.id == data['id'])

        conn = engine.connect()
        response = conn.execute(request)
        one_course = response.fetchall()
        conn.commit()
        conn.close()
        result = one_course[0][0].replace("False", '"false"').replace("'", '"')
        test = json.loads(result)
        test['rating'] = (test['rating'] + data["courseRating"]) / 2

        print(type(test), test)



    except Exception as e:
        print(e)

    request_2 = update(Courses).values(all=str(test)).where(Courses.id == data['id'])

    try:
        conn = engine.connect()
        conn.execute(request_2)
        conn.commit()
        conn.close()

        request_3 = select(UserCourse.all_object).where(UserCourse.id_course == data['id'])

        conn = engine.connect()
        response = conn.execute(request_3)
        all_course = response.fetchone()
        conn.commit()
        conn.close()
        all_course = json.loads(all_course[0].replace("'", '"'))

        all_course['rating'] = (all_course['rating'] + data["courseRating"]) / 2


        request_2 = update(UserCourse).values(all_object=str(all_course)).where(UserCourse.id_course == data['id'])


        conn = engine.connect()
        conn.execute(request_2)
        conn.commit()
        conn.close()








        return Response(status=200, response=json.dumps({"response": "OK"}))

    except Exception as e:
        print(e)
        return Response(status=400, response=json.dumps({"response": f"{e}"}))






















def get_all_rating(data):

    #Из таблицы UserCourse по id курса вытащить email
    #Из таблицы курса вытащить title
    #Для каждого из email:
        #{"surname": "", "name": "", "patronymic": "", "emailCourse": email, "nameCourse": title, "resultCourse": ""}
        #Из таблицы users вытаскиваем surname, name, patronymic и добавляем
        #Из таблицы UserRating достать answers

        #Добавить обьект к списку
    result = []
    request = select(UserCourse.email_user).where(UserCourse.id_course == data['id'])
    try:
        conn = engine.connect()
        response = conn.execute(request)
        all_emails = response.fetchall()
        print("all_emails", all_emails)
        conn.commit()
        conn.close()

        request = select(Courses.all).where(Courses.id == data['id'])

        conn = engine.connect()
        response = conn.execute(request)
        all_course = response.fetchone()
        conn.commit()
        conn.close()
        print("all_course", all_course)
        title = json.loads(all_course)['title']

        for email in all_emails:
            obj = {"surname": "", "name": "", "patronymic": "", "emailCourse": email, "nameCourse": title, "resultCourse": ""}

            req = select(Users).where(Users.email == email)

            conn = engine.connect()
            response = conn.execute(req)
            user = response.fetchone()
            conn.commit()
            conn.close()
            obj["surname"], obj["name"], obj["patronymic"] = user[3], user[2], user[4]



            req = select(UsersRating).where(UsersRating.email_user == email, UsersRating.id_course == data["id"])

            conn = engine.connect()
            response = conn.execute(req)
            user_rating = response.fetchone()
            conn.commit()
            conn.close()

            obj["resultCourse"] = user_rating

            result.append(obj)


            return Response(status=200, response=json.dumps({"response": result}))

    except Exception as e:
        print("Опаа", e)
        return Response(status=400, response=json.dumps({"response": "Ошибка"}))









    req = select(Users.AdminCourse).where(Users.email == data['email'])
    try:
        conn = engine.connect()
        response = conn.execute(req)
        courses_of_admin = response.fetchone()
        conn.commit()
        conn.close()

        if not courses_of_admin[0]:
            return Response(status=200, response=json.dumps({"response": []}))


        else:
            print(courses_of_admin[0])
            all_courses = [int(x) for x in courses_of_admin[0].strip('][').split(',')]


            response = []

            for course in all_courses:
                request = select(Courses).where(Courses.id == course)
                try:
                    conn = engine.connect()
                    response = conn.execute(request)
                    all_courses_by_id = response.fetchall()
                    conn.commit()
                    conn.close()
                    for item in all_courses_by_id:
                        response.append({"id":item[0],'prevTitle': item[3], 'prevImage': item[4], 'prevAbout': item[5]})
                except Exception as e:
                    print(e)

        return Response(status=200, response=json.dumps({"response": response}))

    except Exception as e:
        return Response(status=400, response=json.dumps({"response": f"{e}"}))



def delete_course_from_database(id):
    request = delete(Courses).where(Courses.id == id)
    try:
        conn = engine.connect()
        conn.execute(request)
        conn.commit()
        conn.close()

        return Response(status=200, response=json.dumps({"response": "ok"}))
    except Exception as e:

        return Response(response=e.__str__(), status=500)
    finally:
        conn.close()



def teacher_result(data):
    try:
        request = select(Users.AdminCourse).where(Users.email == data["email"])
        conn = engine.connect()
        response = conn.execute(request)
        conn.commit()
        conn.close()
        result = [int(x) for x in response.fetchone()[0].strip('][').split(',')]
        print(result)
        print(type(result))

        if not result[0]:
            return Response(status=200, response=json.dumps({"result": []}))
        else:
            final_response = []

            for course in result:

                request = select(Courses).where(Courses.id == course)
                try:
                    conn = engine.connect()
                    response = conn.execute(request)
                    all_courses_by_id = response.fetchall()
                    conn.commit()
                    conn.close()
                    for item in all_courses_by_id:
                        final_response.append({"id": item[0], 'prevTitle': item[3], 'prevImage': item[4], 'prevAbout': item[5]})
                except Exception as e:
                    print(e)


            return Response(status=200, response=json.dumps({"response": final_response}))

    except:
        return Response(status=500, response=json.dumps({"response": "Ошибка"}))

#TODO !!!!!!!!!!!!!!!!!!!!!!!!
def student_result(data):
    try:
        request = select(Users.ActiveCourse).where(Users.email == data["email"])
        conn = engine.connect()
        response = conn.execute(request)
        conn.commit()
        conn.close()

        t = response.fetchone()

        print("t", t[0])

        if not t[0]:
            # result = [int(x) for x in response.fetchone()[0].strip('][').split(',')]
            #
            # print(result)
            # print(type(result))
            #
            # if not result[0]:
            return Response(status=200, response=json.dumps({"response": []}))
        else:
            final_response = []
            result = [int(x) for x in t[0].strip('][').split(',')]
            for course in result:

                request = select(Courses).where(Courses.id == course)
                try:
                    conn = engine.connect()
                    response = conn.execute(request)
                    all_courses_by_id = response.fetchall()
                    conn.commit()
                    conn.close()
                    for item in all_courses_by_id:
                        final_response.append(
                            {"id": item[0], 'prevTitle': item[3], 'prevImage': item[4], 'prevAbout': item[5]})
                except Exception as e:
                    print(e)
            print("final_response", final_response)
            return Response(status=200, response=json.dumps({"response": final_response}))

        # else:
        #     return Response(status=500, response=json.dumps({"response": "Ошибка"}))


    except Exception as e:
        print(e)
        return Response(status=500, response=json.dumps({"response": "Ошибка"}))




def result_for_teacher_by_id(id):
    request = select(Users)

    try:
        conn = engine.connect()
        response = conn.execute(request)
        conn.commit()
        conn.close()
        all_users = response.fetchall()
        final_result = []
        for user in all_users:

            print(user[6])
            if type(user[6]) == str and user[6] == "[]":
                print("111")
                active_Courses = []
            elif user[6] == None:
                print("222")

                active_Courses = []

            elif user[6] != []:
                print("333")

                active_Courses = [int(x) for x in user[6].strip('][').split(',')]
            else:
                print("444")

                active_Courses = []


            print(active_Courses , type(active_Courses))

            # print("ID",type(id), active_Courses , int(id) in active_Courses)
            if int(id) in active_Courses:
                print("Пользователь проходил курс")
                object_to_append = {"surname": user[3], "name": user[2], "patronymic": user[4], "emailCourse": user[0], "nameCourse": "", "resultCourse": ""}
                print(object_to_append)
                request = select(Courses).where(Courses.id == id)
                try:
                    conn = engine.connect()
                    response = conn.execute(request)
                    all_courses_by_id = response.fetchone()
                    title = all_courses_by_id[3]
                    conn.commit()
                    conn.close()
                    object_to_append['nameCourse'] = title


                    #Посчитать рейтинг
                    request = select(UsersRating.answers).where(and_(UsersRating.email_user == user[0], UsersRating.id_course == id))

                    conn = engine.connect()
                    response = conn.execute(request)
                    user_rating = response.fetchone()
                    conn.commit()
                    conn.close()
                    print("user_rating", user_rating)

                    if user_rating[0]:
                        user_rating_dict: dict = json.loads(user_rating[0].replace("'",'"'))
                        final_rating = 0
                        for item in user_rating_dict.values():
                            final_rating +=item

                        final_rating = final_rating / len(user_rating)

                        object_to_append['resultCourse'] = final_rating
                        final_result.append(object_to_append)

                    else:
                        object_to_append['resultCourse'] = 0
                        final_result.append(object_to_append)

                except Exception as e:
                    print(e)
                    return Response(status=500, response=json.dumps({"response": "Ошибка"}))

        return Response(status=200, response=json.dumps({"response": final_result}))





    except Exception as e:
        return Response(status=500, response=json.dumps({"response": "Ошибка"}))





def result_for_student_by_id(data):
    try:
        final_result ={}

        request = select(UserCourse.all_object).where(and_(UserCourse.email_user == data['email'], UserCourse.id_course == data['id']))

        conn = engine.connect()
        response = conn.execute(request)
        one_course = response.fetchall()
        conn.commit()
        conn.close()
        result = one_course[0][0].replace("False", '"false"').replace("'", '"')
        test = json.loads(result)
        # final_result['title'] = test['prevTitle']
        final_result['chapters'] = []
        request = select(UsersRating.answers).where(and_(UsersRating.email_user == data['email'], UsersRating.id_course == data['id']))

        conn = engine.connect()
        response = conn.execute(request)
        user_rating = response.fetchone()
        conn.commit()
        conn.close()
        user_rating = json.loads(user_rating[0].replace("'",'"'))
        for chapter in test['chapters']:
            id_chapter = str(chapter['id'])
            print(chapter)
            print("=====", user_rating)

            try:
                final_result['chapters'].append({"name": chapter['title'], "result": user_rating[id_chapter]})

                print(final_result)
            except Exception as e:
                print(e)
                final_result['chapters'].append({"name":chapter['title'], "result": 0})


        return Response(status=200, response=json.dumps(final_result))


    except Exception as e:
        return Response(status=500, response=json.dumps({"response": "Ошибка"}))





























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


