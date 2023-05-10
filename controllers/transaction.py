from flask import request, request, jsonify
import pymysql
from app import app
from services.database_config import mysql
from dateutil import parser
from services.session.session import getIdByToken

moneyInTypes = ['luong', 'thunhapkhac']


@app.route('/transaction/add', methods=['post'])
def add():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        money = req.get('money')
        moneyType = req.get('type')
        note = req.get('note')
        date = parser.parse(req.get('createdAt'))

        sql = 'insert into transaction (id, user_id, money, money_type, created_at, note) values(%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, userId, money, moneyType, date, note))
        conn.commit()

        sql = 'delete from draft_transaction where user_id=%s'
        cursor.execute(sql, (userId, ))
        conn.commit()

        return jsonify({"message": 'ok'}), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/edit', methods=['post'])
def edit():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        money = req.get('money')
        moneyType = req.get('type')
        note = req.get('note')
        date = parser.parse(req.get('createdAt'))

        sql = 'update transaction set money=%s, money_type=%s, created_at=%s, note=%s where id=%s and user_id=%s'
        cursor.execute(sql, (money, moneyType, date, note, id, userId))
        conn.commit()

        return jsonify({"message": 'ok'}), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/delete', methods=['post'])
def delete():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        # print(username)

        sql = 'delete from transaction where id=%s and user_id=%s'
        cursor.execute(sql, (id, userId))
        conn.commit()

        return jsonify({"message": 'ok'}), 200
    except Exception as e:
        print(e)
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/get-in-month/<int:month>/<int:year>', methods=['get'])
def getInMonth(month, year):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        # print(month, year, username)
        sql = 'SELECT money_type, sum(money) as sum FROM transaction where user_id=%s and month(created_at)=%s and year(created_at)=%s group by money_type order by sum desc'
        cursor.execute(sql, (userId, month, year))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "type": str(transaction[0]),
                "money": float(transaction[1]),
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/get-separate-in-month/<int:month>/<int:year>', methods=['get'])
def getSeparateInMonth(month, year):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        # print(month, year, username)
        sql = 'select id, money, money_type, created_at, note from transaction where month(created_at)=%s and year(created_at)=%s and user_id=%s order by day(created_at) desc, money_type'
        cursor.execute(sql, (month, year, userId))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": str(transaction[0]),
                "money": float(transaction[1]),
                "type": str(transaction[2]),
                "createdAt": str(transaction[3]),
                "note": str(transaction[4] or '')
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/get-in-year/<int:year>', methods=['get'])
def getInYear(year):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        # print(year)
        sql = 'SELECT money_type, sum(money) as sum FROM transaction where user_id=%s and year(created_at)=%s group by money_type order by sum desc;'
        cursor.execute(sql, (userId, year))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "type": str(transaction[0]),
                "money": float(transaction[1]),
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/get-in-five-year/<int:year>', methods=['get'])
def getInFiveYear(year):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        yearsAgo = year - 5
        # print(year)
        sql = 'select id, money, money_type, created_at, note from transaction where year(created_at) between %s and %s and user_id=%s'
        cursor.execute(sql, (yearsAgo, year, userId))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": str(transaction[0]),
                "money": float(transaction[1]),
                "type": str(transaction[2]),
                "createdAt": str(transaction[3]),
                "note": str(transaction[4] or '')
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/recent', methods=['get'])
def recent():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select id, money, money_type, created_at, note from transaction where user_id=%s order by id desc limit 3'
        cursor.execute(sql, (userId, ))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": str(transaction[0]),
                "money": float(transaction[1]),
                "type": str(transaction[2]),
                "createdAt": str(transaction[3]),
                "note": str(transaction[4] or '')
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/get-by-id/<string:id>', methods=['get'])
def getById(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = 'select id, money, money_type, created_at, note from transaction where id=%s'
        cursor.execute(sql, (id, ))
        data = cursor.fetchone()

        transaction = {
            "id": str(data[0]),
            "money": float(data[1]),
            "type": str(data[2]),
            "createdAt": str(data[3]),
            "note": str(data[4] or '')
        }
        return jsonify(transaction), 200
    except Exception as e:
        print(e)
        return jsonify({}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/get-infinite/<string:id>/<int:offset>', methods=['get'])
def getInfinite(id, offset):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = 'select id, money, money_type, created_at from transaction where user_id=%s order by created_at desc limit 15 offset %s'
        cursor.execute(sql, (id, offset))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": str(transaction[0]),
                "money": float(transaction[1]),
                "type": str(transaction[2]),
                "createdAt": str(transaction[3]),
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/transaction/draft', methods=['get'])
def getDraft():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select id, money, money_type, created_at, note from draft_transaction where user_id=%s'
        cursor.execute(sql, (userId, ))
        drafts = cursor.fetchall()

        data = []
        for draft in drafts:
            data.append({
                "id": str(draft[0]),
                "money": float(draft[1]),
                "type": str(draft[2]),
                "createdAt": str(draft[3]),
                "note": str(draft[4] or '')
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()