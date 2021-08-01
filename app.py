# app.py
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_mongoengine import \
    MongoEngine  # ModuleNotFoundError: No module named 'flask_mongoengine' = (venv) C:\flaskmyproject>pip install flask-mongoengine
from werkzeug.utils import secure_filename
import os
import MongoDbConnector as mdbc
# import magic
import urllib.request

app = Flask(__name__)
app.secret_key = "caircocoders-ednalan-2020"

app.config['MONGODB_SETTINGS'] = {
    'db': 'dbmongocrud',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

UPLOAD_FOLDER = 'static/media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','wav'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Document):
    name = db.StringField()
    email = db.StringField()
    profile_pic = db.StringField()


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/transcribe/')
def transcribe():
    return render_template('transcribe.html')

@app.route('/upload', methods=['POST'])
def upload():
    flash('Uploading....... Please wait to redirect .....')
    file = request.files['inputFile']

    filename = secure_filename(file.filename)
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        mdbc.insert_audio_file(file.filename)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded ' + str(filename)+ ' to the database!')
        return redirect('/transcribe/')
    else:
        flash('Invalid Upload only WAV files allowed')
    return redirect('/transcribe/')


if __name__ == '__main__':
    app.run(debug=False)