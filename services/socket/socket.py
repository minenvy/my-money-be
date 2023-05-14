import json


def getIdfromSocketId(sid):
    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'r')
    sockets = json.loads(socketFile.read())
    socketFile.close()
    id = None
    for x, y in sockets.items():
        if y == sid:
            id = x
    return id


def getSocketIdfromId(id):
    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'r')
    sockets = json.loads(socketFile.read())
    socketFile.close()
    sid = ''
    for x, y in sockets.items():
        if x == id:
            sid = y
            break
    return sid


def checkSocketSession(id):
    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'r')
    sockets = json.loads(socketFile.read())
    socketFile.close()
    isConnected = False
    for x, y in sockets.items():
        if x == id:
            isConnected = True
    return isConnected


def setNewSocketSession(id, sid):
    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'r')
    sockets = json.loads(socketFile.read())
    socketFile.close()

    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'w')
    sockets[id] = sid
    socketFile.write(json.dumps(sockets))
    socketFile.close()


def removeSocketSession(id):
    if (not id):
        return
    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'r')
    sockets = json.loads(socketFile.read())
    socketFile.close()

    socketFile = open(
        'D:\WorkSpace\my-money\\backend\services\socket\socket.txt', 'w')
    sockets.pop(id)
    socketFile.write(json.dumps(sockets))
    socketFile.close()
