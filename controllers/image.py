from flask import request, make_response, jsonify
from app import app
from services.database_config import mysql
from services.session.session import getIdByToken, setNewSession, removeSession
from services.upload_image import uploadImage
from services.extract_data import extract, recognizeEntity
from datetime import datetime
from uuid import uuid4
import re


@app.route('/image/upload', methods=['post'])
def upload():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        image = request.files['file']

        filename = uploadImage(image)

        return jsonify({'image': filename}), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/image/extract', methods=['post'])
def extractImage():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        image = request.files['file']

        filename = uploadImage(image)
        textInImage = extract(filename)
        ner = recognizeEntity(textInImage)
        money = ner.get('MONEY')
        date = ner.get('DATE')
        note = '"""' + ner.get('NOTE') + '"""'

        money = re.sub("[^\d\.]", "", money.replace(
            'o', '0').replace('O', '0')) if money else 0
        date = datetime.strptime(
            date.replace('-',
                         '/'), '%d/%m/%Y') if date else datetime.now()

        textsInNote = note.split() if note else ''
        note = ' '.join([str(ele) for ele in textsInNote]).replace('"""', '')

        sql = 'insert into draft_transaction (id, user_id, money, money_type, created_at, note, image) values (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (uuid4(), userId, money,
                             'banking', date, note, filename))
        conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
    finally:
        cursor.close()
        conn.close()
