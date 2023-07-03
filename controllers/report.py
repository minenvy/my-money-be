from flask import request, jsonify
from app import app
from services.database_config import conn, cursor
from services.session.session import getIdByToken


@app.route('/report/month/<int:year>', methods=['get'])
def reportMonth(year):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

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
        return jsonify({"message": 'Lấy thông tin báo cáo thất bại'}), 500


@app.route('/report/year/<int:year>', methods=['get'])
def reportYear(year):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

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
        return jsonify({"message": 'Lấy thông tin báo cáo thất bại'}), 500
