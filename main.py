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


#Возвращение информации о пользователе по токену доступа
@app.route("/users/me", methods= ['GET'])
def check_user():

    real_token = request.headers['Authorization'].split(' ')[1]
    if check_token(real_token).status == '200 OK':
        user_data = getUserData(real_token)
        #------

        return Response(status=200,response = json.dumps({'email':user_data[0], 'name':user_data[2], 'family': user_data[3], 'otchestvo':user_data[4], 'role':user_data[5]}))
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
    POST запрос на добавление новой новости
    Получает картинку, дату, заголовок, текст статьи
    :return: Все существующие новости
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
        # all_mentors = get_all_mentors()
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

        # data = json.loads(request.form['formValues'])
        # file = request.files.get("file")
        #
        # data = request.data
        # data = request.data
        data_2 = request.form
        data_3 = request.json

        try:
            s = request.form.get('form')
            print(s)
        except Exception as e :
            print(e)





        try:
            print(data_2)
            print(data_3)
        except Exception as e:
            print(e)

        try:
            file = request.files.get("file")
            print(file)
        except Exception as e:
            print(e)

        try:
            data = request.data
            print('data',data)
        except Exception as e:
            print(e)

        try:
            data_2 = request.form
            print('2', data_2)
        except Exception as e:
            print(e)

        try:
            data_3 = request.json
            print('3',data_3)
        except Exception as e:
            print(e)

        try:
            print('ok', request.get_data())
        except Exception as e:
            print(e)


        return json.dumps({"ХУЕТА": ":)"})
    except Exception as e:
        print(e)

        return Response(status=400, response="Неправильный запрос. Возможно ошибка с картинкой")






@app.route("/fullCourses", methods= ['GET'])
def get_full_courses():
    '''
    :return: Возвращает все мероприятия
    :rtype:
    '''
    try:

        courses = get_all_courses()
        # all_mentors = get_all_mentors()
        if type(courses) == str or type(courses) == list:
            return Response(status=200, response=json.loads(str(courses)))
        else:
            return Response(status=500, response='Failed request')
    except Exception as e:
        print(e)
        return Response(status=500, response='Failed by exception')


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
