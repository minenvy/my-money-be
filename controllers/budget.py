from flask import request, request, jsonify
import pymysql
from app import app
from services.database_config import mysql
from dateutil import parser
from services.session import getIdByToken


@app.route('/budget/add', methods=['post'])
def addBudget():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        name = req.get('name')
        money = req.get('money')
        startDate = parser.parse(req.get('startDate'))
        endDate = parser.parse(req.get('endDate'))
        options = req.get('options')
        # print(username)

        sql = 'insert into budget (id, user_id, name, money, start_date, end_date, options) values (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, userId, name, money,
                       startDate, endDate, options))
        conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/budget/get-infinite/<int:offset>', methods=['get'])
def getBudget(offset):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        # print(username)

        sql = 'select id, name, money, start_date, end_date, options from budget where user_id=%s limit 15 offset %s'
        cursor.execute(sql, (userId, offset))
        budgets = cursor.fetchall()

        data = []
        for budget in budgets:
            sql = 'select sum(money) from transaction where user_id=%s and money_type not in ("luong", "thunhapkhac") and created_at between %s and %s group by username'
            cursor.execute(sql, (userId, budget[3], budget[4]))
            used_money = cursor.fetchone()

            data.append({
                "id": str(budget[0]),
                "name": str(budget[1]),
                "money": float(budget[2]),
                "usedMoney": float(used_money[0] if used_money else 0),
                "startDate": str(budget[3]),
                "endDate": str(budget[4]),
                "options": str(budget[5])
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/budget/delete', methods=['post'])
def deleteBudget():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        # print(username)

        sql = 'delete from budget where id=%s and user_id=%s'
        cursor.execute(sql, (id, userId))
        conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        return jsonify({}), 500
    finally:
        cursor.close()
        conn.close()
