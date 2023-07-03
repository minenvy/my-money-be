from flask import request, jsonify
from app import app
from services.database_config import conn, cursor
from services.session.session import getIdByToken


message = [
    'đã thêm giao dịch mới!',
    'đã follow bạn!'
]


@app.route('/notification/get-infinite/<string:id>/<int:offset>', methods=['get'])
def getInfiniteNotification(id, offset):
    try:
        sql = 'select id, sender_id, type, status, created_at from notification where receiver_id=%s order by created_at desc limit 15 offset %s'
        cursor.execute(sql, (id, offset))
        notifications = cursor.fetchall()

        data = []
        for notification in notifications:
            sql = 'select nickname, image from user where id=%s'
            cursor.execute(sql, (notification[1], ))
            friend = cursor.fetchone()
            friendName = friend[0]
            friendImage = friend[1] or ''

            data.append({
                "id": notification[0],
                "userId": notification[1],
                "image": friendImage,
                "message": friendName + ' ' + message[int(notification[2])],
                "status": notification[3],
                "createdAt": str(notification[4]),
            })
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin thông báo thất bại'}), 500


@app.route('/notification/read', methods=['post'])
def readNotification():
    try:
        req = request.get_json()
        id = req.get('id')

        sql = 'update notification set status=%s where id=%s'
        cursor.execute(sql, ('read', id))
        conn.commit()

        return jsonify({"message": "Đã đọc thông báo"}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
