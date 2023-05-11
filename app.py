from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt

UPLOAD_FOLDER = 'D:\WorkSpace\my-money\\backend\static\images'

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FRONTEND'] = '127.0.0.1'