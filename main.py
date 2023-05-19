from database.create_database import *
from flask import Flask, request, jsonify, Response, url_for
from database.db_api import *
from hash_pwd import hash_pwd
from generate_token import generate_auth_token, check_token, getUserData
from flask_cors import CORS, cross_origin
import os


app = Flask("englishschool")


cors = CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

app.config['CORS_SUPPORTS_CREDENTIALS'] = True

Upload = "static"
app.config['uploadFolder'] = Upload



#-----------------------------------------------------------------------------------------Роуты пользователя-----------------------------------------------------------------------------------


#Регистрация
@app.route("/signup", methods= ['POST', 'OPTIONS'])
@cross_origin()
def sign_up():

    datas = request.get_json()
    family = datas['family']
    name = datas['name']
    patremonial = datas['otchestvo']
    email = datas['email']
    password = hash_pwd(datas['password'])
    role = datas['role']
    if request.method == 'POST':
        response = user_register(family,name,patremonial, email, password, role)


        return response

    elif request.method == 'OPTIONS':
        response = user_register(family,name,patremonial, email, password, role)
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,HEAD, PATCH, POST,DELETE')
        response.headers.add('Access-Control-Allow-Headers', str(request.headers))


#Аутентификация
@app.route("/signin", methods= ['POST'])
def sign_in():

    data = request.get_json()
    email = data['email']
    password = hash_pwd(data['password'])

    if user_authentification(email, password):
        return generate_auth_token(email)
    else:
        return Response(status=500,response="Authentification failed")

#TODO
#Возвращение информации о пользователе по токену доступа
@app.route("/users/me", methods= ['GET'])
def check_user():

    real_token = request.headers['Authorization'].split(' ')[1]
    if check_token(real_token).status == '200 OK':
        user_data = getUserData(real_token)
        #------

        result = {'email':user_data[0], 'name':user_data[2], 'family': user_data[3], 'otchestvo':user_data[4], 'role':user_data[5], 'activeCourse': user_data[6], 'adminCourse': user_data[7]}
        if type(user_data[7]) == str and user_data[7] == "[]":
            result['adminCourse'] = []
        elif user_data[7] !=[]:
            print(user_data[7], type(user_data[7]))

            result['adminCourse'] = [int(x) for x in user_data[7].strip('][').split(',')]
        else:
            result['adminCourse'] = []






        print("DDDDDD", user_data[6], type(user_data[6]))
        if type(user_data[6]) == str and user_data[6] == "[]":
            result['activeCourse'] = []

        elif user_data[6] != []:
            print(user_data[6], type(user_data[6]))
            result['activeCourse'] =[int(x) for x in user_data[6].strip('][').split(',')]
        else:
            result['activeCourse'] = []

        print(result)
        return Response(status=200, response=json.dumps(result))


    else:
        return Response(status=500,response="Invalid token")




#Выход из учётной записи
@app.route("/signout", methods= ['GET'])
def sign_out():
    '''
    Устанавливает ошибочное значение токена в куках, для логаута.

    '''
    response = Response(status=200)
    response.set_cookie('token', '', expires=0)
    response.delete_cookie('token')
    return jsonify(response_code=response.status_code, cookie=request.cookies.get('token'))


#-----------------------------------------------------------------------КУРСЫ------------------------------------------------------------------------
@app.route("/lastCourseId", methods=['GET'])
def get_last_id():
    '''
    Возвращает ID  последнего курса
    '''
    try:

        return Response(status=200, response=get_last_id_of_course())
    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")





@app.route("/directions/<id>", methods= ['GET'])
def get_courses(id):
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:

        courses = get_all_courses_by_direction(id)
        if type(courses) == str or type(courses) == list:
            return Response(status=200, response=courses)
        else:
            return Response(status=500, response='Failed request')
    except Exception as e:
        print(e)
        return Response(status=500, response='Failed by exception')



@app.route("/create", methods= ['POST'])
def add_course():
    '''
    POST запрос на добавление новой новости
    Получает картинку, дату, заголовок, текст статьи
    :return: Все существующие новости
    '''
    try:

        files = request.files.to_dict()
        data = json.loads(request.form['courseObject'])

        print(type(data))

        for key, item in files.items():
            filename = key + ".pdf"
            item.save(os.path.join('static', filename))

        for chapter in  data['chapters']:
            if chapter['type'] == 'lection':
                for i in range(len(chapter['materials'])):
                    try:
                        chapter['materials'][i]['link'] = url_for("static", filename=f"{data['idDirections']}_{data['id']}_{chapter['id']}_{i+1}.pdf")

                    except Exception as e:
                        print("EXCEPTION:", e)

        return add_course_to_db(data)
    except Exception as e:
        print("EXCEPTION:", e)

        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")





@app.route("/fullCourses", methods= ['GET'])
def get_full_courses():
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:

        return Response(status=200, response=get_all_courses())

    except Exception as e:
        print(e)
        return Response(status=500, response='Failed by exception')



@app.route("/postCourse", methods= ['POST'])
def send_course():
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:
        data = json.loads(request.data.decode('utf-8'))


        one_course = get_one_course(data)
        if type(one_course) == str or type(one_course) == list:
            return Response(status=200, response=one_course)
        else:
            return Response(status=500, response='Failed request')
    except Exception as e:
        print(e)
        return Response(status=500, response='Failed by exception')







@app.route("/writeCourse", methods= ['POST'])
def write_course():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))


        return add_course_to_user(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")




@app.route("/deleteCourse", methods= ['POST'])
def delete_course():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))

        return delete_course_from_user(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")


@app.route("/fullDirection/<id>", methods= ['GET'])
def delete_course_from_db(id):
    '''
    '''
    return delete_course_from_database(id)












@app.route("/courseStatus", methods= ['POST'])
def course_status():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))


        return courseStatus(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")



@app.route("/resultTest", methods= ['POST'])
def rating():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))


        return add_rating(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")


@app.route("/resultTestTeacher/<id>", methods= ['GET'])
def result_for_teacher(id):
    '''
    '''
    try:




        return result_for_teacher_by_id(id)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")



















#
# #TODO ПРОВЕРИТЬ РАБОТОСПОСОБНОСТЬ
# @app.route("/getCcoursesByID", methods= ['POST'])
# def courses_by_id():
#     '''
#     '''
#     try:
#
#         data = json.loads(request.data.decode('utf-8'))
#
#
#         return get_courses_by_id(data)
#     except Exception as e:
#         print("1", e)
#
#         return Response(status=400, response="Неправильный запрос.")


#TODO ПРОВЕРИТЬ РАБОТОСПОСОБНОСТЬ



@app.route("/ratingCourse", methods= ['POST'])
def rating_course():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))
        print(data)

        return add_rating_to_course(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")








@app.route("/allRating", methods= ['POST'])
def all_rating():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))


        return all_rating_db(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")



@app.route("/resultTestTeacher", methods= ['POST'])
def result_teacher():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))
        print(data)

        return teacher_result(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")


@app.route("/resultTestStudent", methods= ['POST'])
def result_student():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))
        print(data)

        return student_result(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")



#TODO ПРОВЕРИТЬЬЬЬ!!!!!!!!!
@app.route("/resultTestStudentBlock", methods= ['POST'])
def result_student_block():
    '''
    '''
    try:

        data = json.loads(request.data.decode('utf-8'))
        print(data)
        #data['email'], data['id']

        return result_for_student_by_id(data)
    except Exception as e:
        print("1", e)

        return Response(status=400, response="Неправильный запрос.")














#-----------------------------------------------------------------------Роуты новостей---------------------------------------------------------------



@app.route("/news", methods=['POST'])
def add_news():
    '''
    POST запрос на добавление новой новости
    Получает картинку, дату, заголовок, текст статьи
    :return: Все существующие новости
    '''
    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])


        return add_news_to_db(data)
    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")

@app.route("/news", methods=['PATCH'])
def edit_news():
    '''
    Редактирует существующую новость.
    Получает id, картинку, дату, заголовок, текст статьи
    :return: Все существующие новости
    '''

    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])



        return edit_news_from_db(data)
    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")

@app.route("/news/<id>", methods=['DELETE'])
def delete_news(id):
    '''
    Удаляет новость из базы данных
    Получает id
    :return: Возвращает статус запроса
    '''

    return delete_news_from_db(id)


@app.route("/news", methods=['GET'])
def get_news():
    '''
    :return: Возвращает все новости
    :rtype:
    '''
    try:
        all_news = get_all_news()
        if type(all_news) == str:
            return Response(status=200, response=all_news)
        else:

            return Response(status=500, response='Failed request')

    except Exception as e:
        print(e)
        return Response(status=500, response=f'{e}')



#------------------eventsLimit--------------------------------------------------Роуты направлений-------------------------------------------------------------------------------------------
@app.route("/directions", methods=['POST'])
def add_direction():
    '''
    POST запрос на добавление нового направления
    Получает картинку, заголовок, описание
    :return: Все направления
    '''

    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])

        return add_direction_to_db(data)
    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")

@app.route("/directions/<id>", methods=['DELETE'])
def delete_direction(id):
    '''
    Удаляет мероприятие из базы данных
    Получает id
    :return: Возвращает статус запроса
    '''

    return delete_direction_from_db(id)


@app.route("/directions", methods=['PATCH'])
def edit_directions():
    '''
    Редактирует мероприятия в базе данных
    Получает id
    :return: Возвращает статус запроса
    '''


    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])

        return edit_direction_from_db(data)
    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")




@app.route("/directions", methods= ['GET'])
def get_directions():
    '''
    :return: Возвращает все направления
    :rtype:
    '''
    try:
        all_directions = get_all_directions()
        if type(all_directions) == str:
            return Response(status=200, response=all_directions)
        else:
            return Response(status=500, response='Failed request')
    except:
        return Response(status=500, response='Failed request')


#-----------------------------------------------------------------------------------------Роуты мероприятий-------------------------------------------------------------------------------------------
@app.route("/events", methods= ['GET'])
def get_events():
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:
        all_events = get_all_events()
        if type(all_events) == str:
            return Response(status=200, response=all_events)
        else:
            return Response(status=500, response='Failed request')
    except:
        return Response(status=500, response='Failed request')


@app.route("/events", methods=['PATCH'])
def edit_event():
    '''
    Редактирует мероприятия в базе данных
    Получает id
    :return: Возвращает статус запроса
    '''

    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])

        return edit_event_from_db(data)

    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")



@app.route("/events", methods=['POST'])
def add_event():
    '''
        POST запрос на добавление нового мероприятия
        Получает картинку, заголовок, описание
        :return: Все направления
        '''


    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])



        return add_event_to_db(data)

    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")



@app.route("/events/<id>", methods=['DELETE'])
def delete_event(id):
    '''
    Удаляет мероприятие из базы данных
    Получает id
    :return: Возвращает статус запроса
    '''

    return delete_event_from_db(id)


#--------------------------------------------------------------------------Роуты наставников---------------------------------------------------------------------------------------------------------------





@app.route("/curators/<id>", methods= ['GET'])
def get_one_mentors(id):
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:

        mentor = get_one_mentor(id)
        # all_mentors = get_all_mentors()
        if type(mentor) == str:
            return Response(status=200, response=mentor)
        else:
            return Response(status=500, response='Failed request')
    except Exception as e:
        print(e)
        return Response(status=500, response='Failed by exception')



# @app.route("/create", methods=['POST'])
# def add_mentor():
#     '''
#         POST запрос на добавление нового ментора
#         Получает картинку, фио, описание, опыт
#         :return: Все направления
#         '''
#     try:
#         data = json.loads(request.form['formValues'])
#         file = request.files.get("file")
#         if file:
#             filename = file.filename
#             file.save(os.path.join(app.config['uploadFolder'], filename))
#             data['photo'] = url_for("static", filename=filename)
#         else:
#
#             data['photo'] = url_for("static", filename="no_photo.jpg")
#
#         print(data['photo'])
#
#
#         return add_mentor_to_db(data)
#
#     except:
#         return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")





@app.route("/curators/<id>", methods=['DELETE'])
def delete_mentor(id):
    '''
    Удаляет мероприятие из базы данных
    Получает id
    :return: Возвращает статус запроса
    '''

    return delete_mentor_from_db(id)


@app.route("/curators", methods=['PATCH'])
def edit_mentor():
    '''
    Редактирует мероприятия в базе данных
    Получает id
    :return: Возвращает статус запроса
    '''
    try:
        data = json.loads(request.form['formValues'])
        file = request.files.get("file")
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['uploadFolder'], filename))
            data['image'] = url_for("static", filename=filename)
        else:

            data['image'] = url_for("static", filename="no_photo.jpg")

        print(data['image'])


        return edit_mentor_from_db(data)

    except:
        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")



@app.route("/curators", methods= ['GET'])
def get_mentors():
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:
        all_mentors = get_all_mentors()
        if all_mentors:
            return Response(status=200, response=all_mentors)
        else:
            return Response(status=500, response='Failed request')
    except:
        return Response(status=500, response='Failed request')


@app.route("/newsLimit", methods=['GET'])
def get_last_8_news():
    try:
        last_8_news = get_news_with_limit()
        if type(last_8_news) == str:
            return Response(status=200, response=last_8_news)
        else:
            return Response(status=500, response='Failed request')
    except:
        return Response(status=500, response='Failed request')



@app.route("/eventsLimit", methods=['GET'])
def get_last_8_events():
    try:
        last_8_events = get_events_with_limit()
        if type(last_8_events) == str:
            return Response(status=200, response=last_8_events)
        else:
            return Response(status=500, response='Failed request')
    except Exception as e:
        print(e)
        return Response(status=500, response=e.__str__())



@app.route("/users/me", methods= ['PATCH'])
def updataUserProfile():
    data = request.get_json()
    return edit_user_from_db(data)











app.run(host='0.0.0.0', port=8000, debug=False)
