from flask import request, jsonify
from app import app
from services.database_config import conn, cursor
from dateutil import parser
from services.session.session import getIdByToken


incomeTypes = ['luong', 'thunhapkhac']


@app.route('/transaction/add', methods=['post'])
def add():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        money = req.get('money')
        moneyType = req.get('type')
        note = req.get('note')
        date = parser.parse(req.get('createdAt'))
        image = req.get('image')
        permission = req.get('accessPermission')
        walletId = req.get('walletId')

        sql = 'insert into transaction (id, user_id, money, money_type, created_at, wallet_id, note, image, access_permission) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, userId, money, moneyType,
                       date, walletId, note, image, permission))
        conn.commit()

        changedMoney = money if moneyType in incomeTypes else -money
        sql = 'update wallet set total=total + %s where id=%s'
        cursor.execute(sql, (changedMoney, walletId))
        conn.commit()

        sql = 'delete from draft_transaction where user_id=%s'
        cursor.execute(sql, (userId, ))
        conn.commit()

        return jsonify({"message": 'Thêm giao dịch thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500


@app.route('/transaction/edit', methods=['post'])
def edit():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')
        money = req.get('money')
        moneyType = req.get('type')
        note = req.get('note')
        date = parser.parse(req.get('createdAt'))
        image = req.get('image')
        permission = req.get('accessPermission')
        walletId = req.get('walletId')

        sql = 'select money, money_type from transaction where id=%s'
        cursor.execute(sql, (id, ))
        transaction = cursor.fetchone()
        nowMoney = transaction[0] if transaction[1] in incomeTypes else -transaction[0]

        sql = 'update transaction set money=%s, money_type=%s, created_at=%s, note=%s, image=%s, access_permission=%s where id=%s and user_id=%s'
        cursor.execute(sql, (money, moneyType, date, note,
                       image, permission, id, userId))
        conn.commit()

        changedMoney = money if moneyType in incomeTypes else -money
        sql = 'update wallet set total=total + %s where id=%s'
        cursor.execute(sql, (changedMoney - nowMoney, walletId))
        conn.commit()

        return jsonify({"message": 'Cập nhật giao dịch thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500


@app.route('/transaction/delete', methods=['post'])
def delete():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)
        req = request.get_json()
        id = req.get('id')

        sql = 'select money, money_type from transaction where id=%s'
        cursor.execute(sql, (id, ))
        transaction = cursor.fetchone()
        nowMoney = transaction[0] if transaction[1] in incomeTypes else -transaction[0]

        sql = 'update user set money=money + %s where id=%s'
        cursor.execute(sql, (- nowMoney, userId))
        conn.commit()

        sql = 'delete from transaction where id=%s and user_id=%s'
        cursor.execute(sql, (id, userId))
        conn.commit()

        return jsonify({"message": 'Xóa giao dịch thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500


@app.route('/transaction/get-in-month/<int:month>/<int:year>', methods=['get'])
def getInMonth(month, year):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'SELECT money_type, sum(money) as sum FROM transaction where user_id=%s and month(created_at)=%s and year(created_at)=%s group by money_type order by sum desc'
        cursor.execute(sql, (userId, month, year))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "type": transaction[0],
                "money": float(transaction[1]),
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin giao dịch thất bại'}), 500


@app.route('/transaction/get-separate-in-month/<int:month>/<int:year>/<string:walletName>', methods=['get'])
def getSeparateInMonth(month, year, walletName):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select transaction.id, money, money_type, transaction.created_at, note, image, name from transaction join wallet on transaction.wallet_id = wallet.id where month(transaction.created_at)=%s and year(transaction.created_at)=%s and name=%s and transaction.user_id=%s order by day(transaction.created_at) desc, money_type'
        cursor.execute(sql, (month, year, walletName, userId))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": transaction[0],
                "money": float(transaction[1]),
                "type": transaction[2],
                "createdAt": str(transaction[3]),
                "note": transaction[4] or '',
                "image": transaction[5] or '',
                "walletName": transaction[6]
            })

        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin giao dịch thất bại'}), 500


@app.route('/transaction/get-in-year/<int:year>', methods=['get'])
def getInYear(year):
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'SELECT money_type, sum(money) as sum FROM transaction where user_id=%s and year(created_at)=%s group by money_type order by sum desc;'
        cursor.execute(sql, (userId, year))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "type": transaction[0],
                "money": float(transaction[1]),
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin giao dịch thất bại'}), 500


@app.route('/transaction/recent', methods=['get'])
def recent():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select id, money, money_type, created_at, note, image from transaction where user_id=%s order by id desc limit 3'
        cursor.execute(sql, (userId, ))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": transaction[0],
                "money": float(transaction[1]),
                "type": transaction[2],
                "createdAt": str(transaction[3]),
                "note": transaction[4] or '',
                "image": transaction[5] or ''
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin giao dịch thất bại'}), 500


@app.route('/transaction/get-by-id/<string:id>', methods=['get'])
def getById(id):
    try:
        sql = 'select transaction.id, money, money_type, transaction.created_at, note, image, name, access_permission, wallet.id from transaction join wallet on transaction.wallet_id = wallet.id where transaction.id=%s'
        cursor.execute(sql, (id, ))
        data = cursor.fetchone()

        transaction = {
            "id": data[0],
            "money": float(data[1]),
            "type": data[2],
            "createdAt": str(data[3]),
            "note": data[4] or '',
            "image": data[5] or '',
            "walletName": data[6],
            "accessPermission": data[7],
            "walletId": data[8]
        }
        return jsonify(transaction), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin giao dịch thất bại'}), 500


@app.route('/transaction/get-infinite/<string:id>/<int:offset>', methods=['get'])
def getInfinite(id, offset):
    try:
        sql = 'select id, money, money_type, created_at from transaction where user_id=%s and access_permission=%s order by created_at desc limit 15 offset %s'
        cursor.execute(sql, (id, 'public', offset))
        transactions = cursor.fetchall()

        data = []
        for transaction in transactions:
            data.append({
                "id": transaction[0],
                "money": float(transaction[1]),
                "type": transaction[2],
                "createdAt": str(transaction[3]),
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin giao dịch thất bại'}), 500


@app.route('/transaction/draft', methods=['get'])
def getDraft():
    try:
        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = 'select draft_transaction.id, money, money_type, draft_transaction.created_at, note, image, access_permission, name, wallet.id from draft_transaction join wallet on draft_transaction.wallet_id = wallet.id where draft_transaction.user_id=%s order by created_at desc'
        cursor.execute(sql, (userId, ))
        drafts = cursor.fetchall()

        data = []
        for draft in drafts:
            data.append({
                "id": draft[0],
                "money": float(draft[1]),
                "type": draft[2],
                "createdAt": str(draft[3]),
                "note": draft[4] or '',
                "image": draft[5] or '',
                "accessPermission": draft[6],
                "walletName": draft[7],
                "walletId": draft[8]
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Lấy thông tin giao dịch nháp thất bại'}), 500
