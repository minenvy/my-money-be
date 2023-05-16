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
        # print(username, pw)

        sql = "select id, nickname, password, money, image, bio from user where username=%s"
        cursor.execute(sql, (username, ))
        user = cursor.fetchone()

        id = user[0]
        nickname = user[1]
        password = user[2]
        money = user[3]
        image = user[4] or ''
        bio = user[5] or ''
        if check_password_hash(password, pw) != True:
            return {}, 500

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchall()

        sql = "select blocked from block where blocker=%s"
        cursor.execute(sql, (id, ))
        blockedNames = cursor.fetchall()

        user = {
            "id": id,
            "nickname": nickname,
            "money": money,
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
        return {}, 500
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
        # print(id, username, password)

        sql = "select username from user where username=%s"
        cursor.execute(sql, (username, ))
        user = cursor.fetchone()

        if (user):
            return {}, 500

        sql = "insert into user (id, username, password, money) values (%s, %s, %s, 0)"
        cursor.execute(sql, (id, username, generate_password_hash
                             (password)))
        conn.commit()

        user = {
            "id": id,
            "money": 0,
        }
        tk = setNewSession(id)
        res = make_response(jsonify(user), 200)
        res.set_cookie(
            'token', tk, domain=app.config['FRONTEND'], httponly=True)
        return res
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
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
            return {}, 200

        sql = "select nickname, money, image, bio from user where id=%s"
        cursor.execute(sql, (id, ))
        user = cursor.fetchone()

        nickname = user[0]
        money = user[1]
        image = user[2] or ''
        bio = user[3] or ''

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchall()

        sql = "select blocked from block where blocker=%s"
        cursor.execute(sql, (id, ))
        blockedNames = cursor.fetchall()

        user = {
            "id": id,
            "nickname": nickname,
            "money": money,
            "image": image,
            "bio": bio,
            "followings": [data[0] for data in followings] if followings else [],
            "blockers": [data[0] for data in blockedNames] if blockedNames else []
        }
        res = make_response(jsonify(user), 200)
        return res
    except Exception as e:
        print(e)
        return {}, 500
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

        sql = "select count(*) from transaction where user_id=%s group by user_id"
        cursor.execute(sql, (id, ))
        transactions = cursor.fetchone()

        sql = "select following from follow where follower=%s"
        cursor.execute(sql, (id, ))
        followings = cursor.fetchone()

        sql = "select follower from follow where following=%s"
        cursor.execute(sql, (id, ))
        followers = cursor.fetchone()

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
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-followers/<string:id>', methods=['get'])
def getFollowers(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

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
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify([]), 500
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
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-proposers/<string:id>/<int:offset>/<string:search>', methods=['get'])
def getSearchProposers(id, offset, search):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "select id, nickname, image, bio from user where nickname is not null and nickname like concat('%%', %s, '%%') and id!=%s and id not in (select following from follow where follower=%s) and id not in (select follower from follow where following=%s) limit 15 offset %s"
        cursor.execute(sql, (search, id, id, id, offset))
        proposers = cursor.fetchall()

        data = []
        for proposer in proposers:
            data.append({
                "id": proposer[0],
                "nickname": proposer[1],
                "image": proposer[2] or '',
                "bio": proposer[3] or '',
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/get-proposers/<string:id>/<int:offset>', methods=['get'])
def getProposers(id, offset):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "select id, nickname, image, bio from user where nickname is not null and id!=%s and id not in (select following from follow where follower=%s) and id not in (select follower from follow where following=%s) limit 15 offset %s"
        cursor.execute(sql, (id, id, id, offset))
        proposers = cursor.fetchall()

        data = []
        for proposer in proposers:
            data.append({
                "id": proposer[0],
                "nickname": proposer[1],
                "image": proposer[2] or '',
                "bio": proposer[3] or '',
            })

        res = jsonify(data), 200
        return res
    except Exception as e:
        print(e)
        return jsonify([]), 500
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
            sql = "select last_modified from user where id=%s"
            cursor.execute(sql, (id, ))
            last_modified = cursor.fetchone()[0]
            if (last_modified):
                datetimeLastModified = datetime.datetime(
                    last_modified.year, last_modified.month, last_modified.day)

                if last_modified and nickname and (datetime.datetime.now() - datetimeLastModified).days < 20:
                    return {}, 500
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

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
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
            return {}, 500

        sql = 'update user set password=%s where id=%s'
        cursor.execute(sql, (generate_password_hash(new), id))
        conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/change-money', methods=['post'])
def changeMoney():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        id = getIdByToken(tk)
        req = request.get_json()
        money = req.get('money')

        sql = 'update user set money=money + %s where id=%s'
        cursor.execute(sql, (money, id))
        conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/check-block/<string:id>', methods=['get'])
def checkBlock(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        tk = request.cookies.get('token')
        userId = getIdByToken(tk)

        sql = "select blocked from block where blocker=%s"
        cursor.execute(sql, (id, ))
        blockedNames = cursor.fetchall()

        isBlocked = False
        for blockedName in blockedNames:
            if blockedName[0] == userId:
                isBlocked = True
                break

        return jsonify({'isBlocked': isBlocked}), 200
    except Exception as e:
        print(e)
        return {}, 500
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
        else:
            sql = "delete from block where blocker=%s and blocked=%s"
            cursor.execute(sql, (id, blockedId))
            conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
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

        sql = 'select count(*) from follow where follower=%s'
        cursor.execute(sql, (id, ))
        followings = cursor.fetchone()[0]

        if (followings >= 20):
            return jsonify({'message': 'max your followers'}), 500

        sql = 'select count(*) from follow where following=%s'
        cursor.execute(sql, (id, ))
        followers = cursor.fetchone()[0]

        if (followers >= 50):
            return jsonify({'message': 'max your friend followers'}), 500

        if isFollowed:
            sql = "insert into follow (follower, following) values (%s, %s)"
            cursor.execute(sql, (id, followedId))
            conn.commit()
        else:
            sql = "delete from follow where follower=%s and following=%s"
            cursor.execute(sql, (id, followedId))
            conn.commit()

        return jsonify({'message': 'ok'}), 200
    except Exception as e:
        print(e)
        conn.rollback()
        return {}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/user/logout', methods=['get'])
def logout():
    try:
        tk = request.cookies.get('token')
        id = getIdByToken(tk)

        removeSession(id)

        res = make_response(jsonify({'message': 'ok'}), 200)
        res.set_cookie(
            'token', '', domain=app.config['FRONTEND'], httponly=True, expires=0)
        return res
    except Exception as e:
        print(e)
        return {}, 500
