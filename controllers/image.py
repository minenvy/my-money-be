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

        return jsonify({"message": 'Upload ảnh thành công', "image": filename}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Upload ảnh thất bại'}), 500
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
        note = '"""' + ner.get('NOTE') + '"""' if ner.get('NOTE') else ''

        money = re.sub("[^\d\.]", "", money.replace(
            'o', '0').replace('O', '0')) if money else 0

        if date:
            yearFirstRegex = '\d{4}\/\d{2}\/\d{2}|\d{4}\-\d{2}\-\d{2}'
            dayFirstRegex = '\d{2}\-\d{2}\-\d{4}|\d{2}\/\d{2}\/\d{4}'
            dateString = re.search(yearFirstRegex, date)
            if dateString:
                date = datetime.strptime(dateString.group(), '%Y/%m/%d')
            else:
                dateString = re.search(dayFirstRegex, date)
                if dateString:
                    date = datetime.strptime(dateString.group(), '%d/%m/%Y') 
        else:
            date = datetime.now()

        if note:
            textsInNote = note.split()
            note = ' '.join([str(ele)
                            for ele in textsInNote]).replace('"""', '')

        sql = 'insert into draft_transaction (id, user_id, money, money_type, created_at, note, image, access_permission) values (%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (uuid4(), userId, money,
                             'banking', date, note, filename, 'private'))
        conn.commit()

        return jsonify({'message': 'Trích xuất ảnh thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Trích xuất ảnh thất bại'}), 500
    finally:
        cursor.close()
        conn.close()
