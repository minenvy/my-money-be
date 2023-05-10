import os
from app import app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']


def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def uploadImage(image):
    filename = ''
    if (allowedFile(image.filename)):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename
