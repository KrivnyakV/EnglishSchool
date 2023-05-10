import json

import jwt
import os
from dotenv import load_dotenv
import datetime
from flask import jsonify, Response
from database.db_api import getUser


def generate_auth_token(email):
    """

    Генерирует JWT токен
    :return: string
    """
    load_dotenv()
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'sub': email
        }
        token = jwt.encode(
            payload,
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )
        print(token)
        return Response(status=200, response=json.dumps({'token':token}))

    except Exception as e:
        print(e)
        return Response(status=500, response= "Token generation failed")



def check_token(token):
    """
        Декодирует полученный токен
        :param token:
        :return: string
        """
    try:
        jwt.decode(token, os.getenv('SECRET_KEY'), algorithms='HS256')
        return Response(status=200)
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return Response(status=500, response='Invalid token. Please log in again.')
    except Exception as e:
        return Response(status=500, response='Invalid token. Please log in again.')


def getUserData(token):

    data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms='HS256')
    user_data = getUser(data['sub'])



    return user_data
