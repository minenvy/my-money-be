from flask import request, make_response, jsonify
from app import app
from services.database_config import conn, cursor
from services.session.session import getIdByToken, setNewSession, removeSession
from services.upload_image import uploadImage
from services.extract_data import extract, recognizeEntity
from datetime import datetime
from uuid import uuid4
import re


@app.route('/image/upload', methods=['post'])
def upload():
    try:
        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        image = request.files['file']

        filename = uploadImage(image)

        return jsonify({"message": 'Upload ảnh thành công', "image": filename}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Upload ảnh thất bại'}), 500


@app.route('/image/extract', methods=['post'])
def extractImage():
    try:
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

        if not date:
            date = datetime.now()
        else:
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

        sql = 'select id, name from wallet where user_id=%s order by created_at'
        cursor.execute(sql, (userId, ))
        wallets = cursor.fetchall()
        walletId = ''
        if len(wallets) == 1:
            walletId = wallets[0][0]
        else:
            for wallet in wallets:
                if wallet[1] != 'Tiền mặt':
                    walletId = wallet[0]
                    break

        sql = 'insert into draft_transaction (id, user_id, money, money_type, created_at, note, image, access_permission, wallet_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (uuid4(), userId, money,
                             'banking', date, note, filename, 'private', walletId))
        conn.commit()

        return jsonify({'message': 'Trích xuất ảnh thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Trích xuất ảnh thất bại'}), 500
