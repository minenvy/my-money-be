from flask import request, jsonify
from app import app
from services.database_config import mysql
from services.session.session import getIdByToken


@app.route('/custom-money-type/get-all', methods=['get'])
def getCustomMoneyType():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select name, type from custom_money_type where user_id=%s'
        cursor.execute(sql, (userId))
        moneyTypes = cursor.fetchall()

        data = []
        for moneyType in moneyTypes:
            data.append({
                "name": moneyType[0],
                "type": moneyType[1]
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/custom-money-type/add', methods=['post'])
def addCustomMoneyType():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        req = request.get_json()
        name = req.get('name')
        type = req.get('type')

        sql = 'insert into custom_money_type (user_id, name, type) values(%s, %s, %s)'
        cursor.execute(sql, (userId, name, type))
        conn.commit()

        return jsonify({"message": 'Thêm loại thu chi thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()
