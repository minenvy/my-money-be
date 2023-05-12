from flask import request, request, jsonify
from app import app
from services.database_config import mysql
from dateutil import parser
from services.session.session import getIdByToken


@app.route('/report/month/<int:year>', methods=['get'])
def reportMonth(year):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        # print(username)

        data = {}
        for i in range(1, 13):
            sql = 'SELECT money_type, sum(money) as sum FROM transaction where user_id=%s and month(created_at)=%s and year(created_at)=%s group by money_type;'
            cursor.execute(sql, (userId, i, year))
            transactions = cursor.fetchall()

            data[i] = []
            for transaction in transactions:
                data[i].append({
                    "type": transaction[0],
                    "money": float(transaction[1]),
                })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/report/year/<int:year>', methods=['get'])
def reportYear(year):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        # print(username)

        data = {}
        for i in range(5):
            sql = 'SELECT money_type, sum(money) as sum FROM transaction where user_id=%s and year(created_at)=%s group by money_type;'
            cursor.execute(sql, (userId, year - i))
            transactions = cursor.fetchall()

            data[year - i] = []
            for transaction in transactions:
                data[year - i].append({
                    "type": transaction[0],
                    "money": float(transaction[1]),
                })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()
