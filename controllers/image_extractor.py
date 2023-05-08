from flask import request, make_response, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
import pymysql
from app import app
from services.database_config import mysql
from services.session import getIdByToken, setNewSession, removeSession
import os
from werkzeug.utils import secure_filename
from services.extract_data import extract


@app.route('/image/extract', methods=['post'])
def extractImage():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        username = getIdByToken(tk)
        image = request.files['file']

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()
