from uuid import uuid1
import json


def getIdByToken(tk):
    tokenFile = open(
        'D:\WorkSpace\my-money\\backend\services\session\session.txt', 'r')
    token = json.loads(tokenFile.read())
    tokenFile.close()
    id = None
    for x, y in token.items():
        if y == tk:
            id = x
    return id


def setNewSession(id):
    tokenFile = open(
        'D:\WorkSpace\my-money\\backend\services\session\session.txt', 'r')
    token = json.loads(tokenFile.read())
    tokenFile.close()

    tokenFile = open(
        'D:\WorkSpace\my-money\\backend\services\session\session.txt', 'w')
    tk = str(uuid1())
    token[id] = tk
    tokenFile.write(json.dumps(token))
    tokenFile.close()
    return tk


def removeSession(id):
    if (not id):
        return
    tokenFile = open(
        'D:\WorkSpace\my-money\\backend\services\session\session.txt', 'r')
    token = json.loads(tokenFile.read())
    tokenFile.close()

    tokenFile = open(
        'D:\WorkSpace\my-money\\backend\services\session\session.txt', 'w')
    tk = str(uuid1())
    token.pop(id)
    tokenFile.write(json.dumps(token))
    tokenFile.close()
