from flask import request, request, jsonify
from app import app
from services.database_config import mysql
from services.session.session import getIdByToken
from datetime import datetime
from uuid import uuid4


@app.route('/wallet/get-all-wallet', methods=['get'])
def getWallets():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select id, name, total from wallet where user_id=%s order by created_at'
        cursor.execute(sql, (userId))
        wallets = cursor.fetchall()

        data = []
        for wallet in wallets:
            data.append({
                "id": wallet[0],
                "name": wallet[1],
                "total": wallet[2]
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/wallet/add', methods=['post'])
def addWallet():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        name = req.get('name')
        total = req.get('total')
        id = uuid4()

        sql = 'select count(*) from wallet where name=%s and user_id=%s'
        cursor.execute(sql, (name, userId))
        count = cursor.fetchone()
        isExistWalletName = count[0] > 0 if count else False

        if isExistWalletName:
            return jsonify({"message": 'Tên ví đã tồn tại'}), 400

        sql = 'insert into wallet (id, user_id, name, total, created_at) values(%s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, userId, name, total, datetime.now()))
        conn.commit()

        return jsonify({"message": 'Tạo ví thành công'}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/wallet/delete', methods=['post'])
def deleteWallet():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        name = req.get('name')

        sql = 'delete from wallet where user_id=%s and name=%s'
        cursor.execute(sql, (userId, name))
        conn.commit()

        return jsonify({"message": 'Xóa ví thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()