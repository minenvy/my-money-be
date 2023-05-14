from app import app, socketio
import controllers.user
import controllers.transaction
import controllers.report
import controllers.budget
import controllers.image
import controllers.socket
import controllers.notification

if __name__ == '__main__':
    socketio.run(app, port='5000')
