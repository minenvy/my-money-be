import json


SocketFile = 'D:\WorkSpace\my-money\\backend\services\socket\socket.txt'


def getIdfromSocketId(sid):
    socketFile = open(SocketFile, 'r')
    jsonData = socketFile.read()
    sockets = json.loads(jsonData) if jsonData else {}
    socketFile.close()
    id = ''
    for x, y in sockets.items():
        if y == sid:
            id = x
    return id


def getSocketIdfromId(id):
    socketFile = open(SocketFile, 'r')
    jsonData = socketFile.read()
    sockets = json.loads(jsonData) if jsonData else {}
    socketFile.close()
    sid = ''
    for x, y in sockets.items():
        if x == id:
            sid = y
            break
    return sid


def checkSocketSession(id):
    socketFile = open(SocketFile, 'r')
    jsonData = socketFile.read()
    sockets = json.loads(jsonData) if jsonData else {}
    socketFile.close()
    isConnected = False
    for x, y in sockets.items():
        if x == id:
            isConnected = True
    return isConnected


def setNewSocketSession(id, sid):
    socketFile = open(SocketFile, 'r')
    jsonData = socketFile.read()
    sockets = json.loads(jsonData) if jsonData else {}
    socketFile.close()

    socketFile = open(SocketFile, 'w')
    sockets[id] = sid
    socketFile.write(json.dumps(sockets))
    socketFile.close()


def removeSocketSession(id):
    if (not id):
        return
    socketFile = open(SocketFile, 'r')
    jsonData = socketFile.read()
    sockets = json.loads(jsonData) if jsonData else {}
    socketFile.close()

    socketFile = open(SocketFile, 'w')
    sockets.pop(id)
    socketFile.write(json.dumps(sockets))
    socketFile.close()
