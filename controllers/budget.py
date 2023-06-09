from flask import request, jsonify
from app import app
from services.database_config import conn, cursor
from dateutil import parser
from services.session.session import getIdByToken


@app.route('/budget/add', methods=['post'])
def addBudget():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        name = req.get('name')
        money = req.get('money')
        startDate = parser.parse(req.get('startDate'))
        endDate = parser.parse(req.get('endDate'))
        options = req.get('options')

        sql = 'insert into budget (id, user_id, name, money, start_date, end_date, options) values (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, userId, name, money,
                       startDate, endDate, options))
        conn.commit()

        return jsonify({'message': 'Thêm ngân sách thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500


@app.route('/budget/get-infinite/<int:offset>', methods=['get'])
def getBudget(offset):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select id, name, money, start_date, end_date, options from budget where user_id=%s limit 15 offset %s'
        cursor.execute(sql, (userId, offset))
        budgets = cursor.fetchall()

        data = []
        for budget in budgets:
            sql = "select sum(money) from transaction where user_id=%s and money_type not in ('luong', 'thunhapkhac') and %s like concat('%%', money_type, '%%') and created_at between %s and %s group by user_id"
            cursor.execute(sql, (userId, budget[5], budget[3], budget[4]))
            used_money = cursor.fetchone()

            data.append({
                "id": budget[0],
                "name": budget[1],
                "money": float(budget[2]),
                "usedMoney": float(used_money[0]) if used_money else 0,
                "startDate": str(budget[3]),
                "endDate": str(budget[4]),
                "options": budget[5]
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin ngân sách thất bại'}), 500


@app.route('/budget/get-day-expense/<string:id>', methods=['get'])
def getDayExpense(id):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select start_date, end_date, options from budget where user_id=%s and id=%s'
        cursor.execute(sql, (userId, id))
        budget = cursor.fetchone()
        startDate = budget[0]
        endDate = budget[1]
        options = budget[2]

        data = []
        sql = "select created_at, sum(money) from transaction where user_id=%s and money_type not in ('luong', 'thunhapkhac') and %s like concat('%%', money_type, '%%') and created_at between %s and %s group by user_id, created_at"
        cursor.execute(sql, (userId, options, startDate, endDate))
        usedMoneyDays = cursor.fetchall()

        for usedMoney in usedMoneyDays:
            data.append({
                "createdAt": str(usedMoney[0]),
                "money": float(usedMoney[1]),
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin chi tiêu trong ngân sách thất bại'}), 500


@app.route('/budget/delete', methods=['post'])
def deleteBudget():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')

        sql = 'delete from budget where id=%s and user_id=%s'
        cursor.execute(sql, (id, userId))
        conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({}), 500
