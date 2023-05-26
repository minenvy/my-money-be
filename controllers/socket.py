from flask_socketio import emit
from app import socketio
from flask import request
from services.database_config import mysql
from services.socket.socket import setNewSocketSession, getSocketIdfromId, removeSocketSession
from uuid import uuid4
from datetime import datetime


message = [
    'đã thêm giao dịch mới!',
    'đã follow bạn!'
]


@socketio.on('connect socket')
def connect(data):
    userId = data.get('id')
    socketId = request.sid
    setNewSocketSession(userId, socketId)


@socketio.on('new transaction')
def addTransactionNotification(data):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        id = data.get('id')

        sql = 'select nickname, image from user where id=%s'
        cursor.execute(sql, (id, ))
        friend = cursor.fetchone()

        sql = 'select follower from follow where following=%s'
        cursor.execute(sql, (id, ))
        followers = cursor.fetchall()

        for follower in followers:
            follower = follower[0]
            notificationId = uuid4().hex
            createdAt = str(datetime.now())
            sql = 'insert into notification (id, sender_id, receiver_id, type, status, created_at) values (%s, %s, %s, %s, %s, %s)'
            cursor.execute(
                sql, (notificationId, id, follower, 0, 'unread', createdAt))
            conn.commit()

            sid = getSocketIdfromId(follower)
            if (sid):
                emit('notification', {
                    "id": notificationId,
                    "userId": id,
                    "image": friend[1] or '',
                    "message": friend[0] + ' ' + message[0],
                    "createdAt": createdAt
                }, room=sid)

    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


@socketio.on('follow')
def addFollowNotification(data):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        senderId = data.get('senderId')
        receiverId = data.get('receiverId')

        notificationId = uuid4().hex
        createdAt = str(datetime.now())
        sql = 'insert into notification (id, sender_id, receiver_id, type, status, created_at) values (%s, %s, %s, %s, %s, %s)'
        cursor.execute(
            sql, (notificationId, senderId, receiverId, 1, 'unread', createdAt))
        conn.commit()

        sql = 'select nickname, image from user where id=%s'
        cursor.execute(sql, (senderId, ))
        friend = cursor.fetchone()

        sid = getSocketIdfromId(receiverId)
        emit('notification', {
            "id": notificationId,
            "userId": senderId,
            "image": friend[1] or '',
            "message": friend[0] + ' ' + message[1],
            "createdAt": createdAt
        }, room=sid)

    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
