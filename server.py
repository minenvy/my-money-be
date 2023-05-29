from app import app, socketio
import controllers.user
import controllers.wallet
import controllers.transaction
import controllers.report
import controllers.budget
import controllers.image
import controllers.socket
import controllers.notification
import controllers.custom_money_type

if __name__ == '__main__':
    socketio.run(app, host=app.config['FRONTEND'], port=app.config['port'])
