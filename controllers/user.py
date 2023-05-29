from flask import request, make_response, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from app import app
from services.database_config import mysql
from services.session.session import getIdByToken, setNewSession, removeSession, checkSession, getTokenById
import datetime
from services.upload_image import uploadImage


@app.route('/user/login', methods=['post'])
def login():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        req = request.get_json()
        username = req.get('username')
        pw = req.get('password')

        sql = "select id, nickname, password, image, bio from user where username=%s"
        cursor.execute(sql, (username, ))
        user = cursor.fetchone()

        if (not user):
            return jsonify({"message": 'Tài khoản không tồn tại'}), 400

        id = user[0]
        nickname = user[1]
        password = user[2]
        image = user[3] or ''
        bio = user[4] or ''
        if check_password_hash(password, pw) != True:
            return jsonify({"message": 'Mật khẩu không chính xác'}), 400

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchall()

        sql = "select blocked from block where blocker=%s"
        cursor.execute(sql, (id, ))
        blockedNames = cursor.fetchall()

        user = {
            "id": id,
            "nickname": nickname,
            "image": image,
            "bio": bio,
            "followings": [data[0] for data in followings] if followings else [],
            "blockers": [data[0] for data in blockedNames] if blockedNames else []
        }
        res = make_response(jsonify(user), 200)
        if (not checkSession(id)):
            tk = setNewSession(id)
            res.set_cookie(
                'token', tk, domain=app.config['FRONTEND'], httponly=True)
        else:
            tk = getTokenById(id)
            res.set_cookie(
                'token', tk, domain=app.config['FRONTEND'], httponly=True)
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/register', methods=['POST'])
def register():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        req = request.get_json()
        id = req.get('id')
        username = req.get('username')
        password = req.get('password')

        sql = "select username from user where username=%s"
        cursor.execute(sql, (username, ))
        user = cursor.fetchone()

        if (user):
            return jsonify({"message": 'Tài khoản đã được sử dụng'}), 400

        sql = "insert into user (id, username, password) values (%s, %s, %s)"
        cursor.execute(sql, (id, username, generate_password_hash
                             (password)))
        conn.commit()

        user = {
            "id": id
        }
        tk = setNewSession(id)
        res = make_response(jsonify(user), 200)
        res.set_cookie(
            'token', tk, domain=app.config['FRONTEND'], httponly=True)
        return res
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-by-token', methods=['get'])
def getByToken():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)

        if (not id):
            return jsonify({"message": 'Lấy thông tin người dùng thất bại'}), 400

        sql = "select nickname, image, bio from user where id=%s"
        cursor.execute(sql, (id, ))
        user = cursor.fetchone()

        nickname = user[0]
        image = user[1] or ''
        bio = user[2] or ''

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchall()

        sql = "select blocked from block where blocker=%s"
        cursor.execute(sql, (id, ))
        blockedNames = cursor.fetchall()

        user = {
            "id": id,
            "nickname": nickname,
            "image": image,
            "bio": bio,
            "followings": [data[0] for data in followings] if followings else [],
            "blockers": [data[0] for data in blockedNames] if blockedNames else []
        }
        res = make_response(jsonify(user), 200)
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-by-id/<string:id>', methods=['get'])
def getByUsername(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "select nickname, image, bio from user where id=%s"
        cursor.execute(sql, (id, ))
        userData = cursor.fetchone()

        sql = "select count(*) from transaction where user_id=%s and access_permission=%s group by user_id"
        cursor.execute(sql, (id, 'public'))
        transactions = cursor.fetchone()

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchall()

        sql = "select follower from follow where following=%s"
        cursor.execute(sql, (id, ))
        followers = cursor.fetchall()

        user = {
            "id": id,
            "nickname": userData[0],
            "image": userData[1] or '',
            "bio": userData[2] or '',
            "transactions": int(transactions[0]) if transactions else 0,
            "followers": len(followers) if followers else 0,
            "followings": len(followings) if followings else 0,
        }
        res = make_response(jsonify(user), 200)
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-followers/<string:id>', methods=['get'])
def getFollowers(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (userId, ))
        followingsTuple = cursor.fetchall()
        followings = []
        for following in followingsTuple:
            followings.append(following[0])

        sql = "select id, nickname, image, bio from user where id in (select follower from follow where following=%s)"
        cursor.execute(sql, (id, ))
        followers = cursor.fetchall()

        data = []
        for follower in followers:
            data.append({
                "id": follower[0],
                "nickname": follower[1],
                "image": follower[2] or '',
                "bio": follower[3] or '',
                "isFollowed": True if follower[0] in followings else False
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin follow thất bại'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-followings/<string:id>', methods=['get'])
def getFollowings(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "select id, nickname, image, bio from user where id in (select following from follow where follower=%s)"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchall()

        data = []
        for following in followings:
            data.append({
                "id": following[0],
                "nickname": following[1],
                "image": following[2] or '',
                "bio": following[3] or '',
                "isFollowed": True
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin follow thất bại'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-proposers/<string:id>/<int:offset>/<string:search>', methods=['get'])
def getSearchProposers(id, offset, search):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = "select id, nickname, image, bio from user where nickname is not null and nickname like concat('%%', %s, '%%') and id!=%s and id not in (select following from follow where follower=%s) and id not in (select follower from follow where following=%s) and id not in (select blocker from block where blocked=%s) limit 15 offset %s"
        cursor.execute(sql, (search, id, id, id, userId, offset))
        proposers = cursor.fetchall()

        data = []
        for proposer in proposers:
            data.append({
                "id": proposer[0],
                "nickname": proposer[1],
                "image": proposer[2] or '',
                "bio": proposer[3] or '',
                "isFollowed": False
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin bạn đề xuất thất bại'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-proposers/<string:id>/<int:offset>', methods=['get'])
def getProposers(id, offset):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = "select id, nickname, image, bio from user where nickname is not null and id!=%s and id not in (select following from follow where follower=%s) and id not in (select follower from follow where following=%s) and id not in (select blocker from block where blocked=%s) limit 15 offset %s"
        cursor.execute(sql, (id, id, id, userId, offset))
        proposers = cursor.fetchall()

        data = []
        for proposer in proposers:
            data.append({
                "id": proposer[0],
                "nickname": proposer[1],
                "image": proposer[2] or '',
                "bio": proposer[3] or '',
                "isFollowed": False
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Lấy thông tin bạn đề xuất thất bại'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/change-profile', methods=['post'])
def changeBio():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        req = request.get_json()
        bio = req.get('bio')
        nickname = req.get('nickname')
        image = req.get('image')

        sql = "select nickname, bio, image from user where id=%s"
        cursor.execute(sql, (id, ))
        user = cursor.fetchone()
        myNickname = user[0]
        myBio = user[1]
        myImage = user[2]

        if (nickname and nickname != myNickname):
            sql = 'select count(*) from user where nickname=%s'
            cursor.execute(sql, (nickname, ))
            count = cursor.fetchone()
            isExistNickname = count[0] > 0 if count else False
            if isExistNickname:
                return jsonify({"message": 'Tên người dùng đã tồn tại'}), 400

            sql = "update user set nickname=%s, last_modified=%s where id=%s"
            cursor.execute(sql, (nickname,
                                 datetime.datetime.now(), id))
            conn.commit()

        if (bio and bio != myBio):
            sql = "update user set bio=%s where id=%s"
            cursor.execute(sql, (bio, id))
            conn.commit()

        if (image and image != myImage):
            sql = "update user set image=%s where id=%s"
            cursor.execute(sql, (image, id))
            conn.commit()

        return jsonify({'message': 'Thay đổi thông tin thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/change-password', methods=['post'])
def changePassword():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        req = request.get_json()
        now = req.get('now')
        new = req.get('new')

        sql = "select password from user where id=%s"
        cursor.execute(sql, (id, ))
        password = cursor.fetchone()[0]

        if check_password_hash(password, now) != True:
            return jsonify({"message": 'Mật khẩu cũ không chính xác'}), 400

        sql = 'update user set password=%s where id=%s'
        cursor.execute(sql, (generate_password_hash(new), id))
        conn.commit()

        return jsonify({'message': 'Thay đổi mật khẩu thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/check-block/<string:blocker>/<string:blocked>', methods=['get'])
def checkBlock(blocker, blocked):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "select count(*) from block where blocker=%s and blocked=%s"
        cursor.execute(sql, (blocker, blocked))
        count = cursor.fetchone()[0]

        return jsonify({'isBlocked': False if count == 0 else True}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/block', methods=['post'])
def block():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        req = request.get_json()
        blockedId = req.get('id')
        isBlocked = req.get('isBlocked')

        if isBlocked:
            sql = "insert into block (blocker, blocked) values (%s, %s)"
            cursor.execute(sql, (id, blockedId))
            conn.commit()

            sql = "delete from follow where follower=%s and following=%s"
            cursor.execute(sql, (blockedId, id))
            conn.commit()
        else:
            sql = "delete from block where blocker=%s and blocked=%s"
            cursor.execute(sql, (id, blockedId))
            conn.commit()

        return jsonify({'message': 'Block hoàn tất' if isBlocked else 'Unblock hoàn tất'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/check-follow/<string:id>', methods=['get'])
def checkFollow(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = "select count(*) from follow where follower=%s and following=%s"
        cursor.execute(sql, (userId, id))
        count = cursor.fetchone()[0]

        return jsonify({'isFollowed': False if count == 0 else True}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/follow', methods=['post'])
def follow():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        req = request.get_json()
        followedId = req.get('id')
        isFollowed = req.get('isFollowed')

        sql = 'select count(*) from block where blocker=%s and blocked=%s'
        cursor.execute(sql, (followedId, id))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({'message': 'Bạn đã bị block bởi người dùng này, không thể follow'}), 400

        sql = 'select count(*) from follow where follower=%s'
        cursor.execute(sql, (id, ))
        followings = cursor.fetchone()[0]

        if (followings >= 20):
            return jsonify({'message': 'Bạn chỉ có thể follow tối đa 20 người'}), 400

        sql = 'select count(*) from follow where following=%s'
        cursor.execute(sql, (id, ))
        followers = cursor.fetchone()[0]

        if (followers >= 50):
            return jsonify({'message': 'Số người có thể follow người dùng này đã đạt tối đa'}), 400

        if isFollowed:
            sql = "insert into follow (follower, following) values (%s, %s)"
            cursor.execute(sql, (id, followedId))
            conn.commit()
        else:
            sql = "delete from follow where follower=%s and following=%s"
            cursor.execute(sql, (id, followedId))
            conn.commit()

        return jsonify({'message': 'Follow thành công' if isFollowed else 'Unfollow thành công'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/logout', methods=['get'])
def logout():
    try:
        tk = request.cookies.get('token')
        id = getIdByToken(tk)

        removeSession(id)

        res = make_response(jsonify({'message': 'Đăng xuất thành công'}), 200)
        res.set_cookie(
            'token', '', domain=app.config['FRONTEND'], httponly=True, expires=0)
        return res
    except Exception as e:
        print(e)
        return jsonify({"message": 'Có lỗi xảy ra, vui lòng thử lại sau'}), 500
