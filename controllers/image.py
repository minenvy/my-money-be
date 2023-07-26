from flask import request, make_response, jsonify
from app import app
from services.database_config import conn, cursor
from services.session.session import getIdByToken, setNewSession, removeSession
from services.upload_image import uploadImage
from services.extract_data import extract, recognizeEntity, getBankFromText, standardizedEntity, getClosestWalletName
from datetime import datetime
from uuid import uuid4


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

        extractedMoney = ner.get('MONEY')
        extractedDate = ner.get('DATE')
        extractedNote = ner.get('NOTE')
        extractedBank = ner.get('BANK') or getBankFromText(textInImage)
        [money, date, note, bank] = standardizedEntity(
            extractedMoney, extractedDate, extractedNote, extractedBank)

        sql = 'select id, name from wallet where user_id=%s order by created_at'
        cursor.execute(sql, (userId, ))
        wallets = cursor.fetchall()
        if len(wallets) == 1:
            walletId = wallets[0][0]
        else:
            walletId = getClosestWalletName(wallets, bank)

        sql = 'insert into draft_transaction (id, user_id, money, money_type, created_at, note, image, access_permission, wallet_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (uuid4(), userId, money,
                             'banking', date, note, filename, 'private', walletId))
        conn.commit()

        return jsonify({'message': 'Trích xuất ảnh thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Trích xuất ảnh thất bại'}), 500
