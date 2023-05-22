from uuid import uuid4
import json


TokenFile = 'D:\WorkSpace\my-money\\backend\services\session\session.txt'


def getIdByToken(tk):
    if not tk:
        return ''
    tokenFile = open(TokenFile, 'r')
    jsonData = tokenFile.read()
    tokens = json.loads(jsonData) if jsonData else {}
    tokenFile.close()
    id = None
    for x, y in tokens.items():
        if y == tk:
            id = x
    return id


def getTokenById(id):
    tokenFile = open(TokenFile, 'r')
    jsonData = tokenFile.read()
    tokens = json.loads(jsonData) if jsonData else {}
    tokenFile.close()
    token = ''
    for x, y in tokens.items():
        if x == id:
            token = y
    return token


def checkSession(id):
    tokenFile = open(TokenFile, 'r')
    jsonData = tokenFile.read()
    tokens = json.loads(jsonData) if jsonData else {}
    tokenFile.close()
    isLoggedIn = False
    for x, y in tokens.items():
        if x == id:
            isLoggedIn = True
    return isLoggedIn


def setNewSession(id):
    tokenFile = open(TokenFile, 'r')
    jsonData = tokenFile.read()
    tokens = json.loads(jsonData) if jsonData else {}
    tokenFile.close()

    tokenFile = open(TokenFile, 'w')
    tk = str(uuid4())
    tokens[id] = tk
    tokenFile.write(json.dumps(tokens))
    tokenFile.close()
    return tk


def removeSession(id):
    tokenFile = open(TokenFile, 'r')
    jsonData = tokenFile.read()
    tokens = json.loads(jsonData) if jsonData else {}
    tokenFile.close()

    tokenFile = open(TokenFile, 'w')
    tokens.pop(id)
    tokenFile.write(json.dumps(tokens))
    tokenFile.close()
