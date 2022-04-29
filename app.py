import logging
import os
import pathlib
from flask import Flask, render_template, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisisbeboproject'
logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# sqlalchemy .db location (for sqlite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# sqlalchemy track modifications in sqlalchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# enable debugging mode
app.config["DEBUG"] = True
PARENT_PATH = str(pathlib.Path(__file__).parent.resolve())
UPLOAD_FOLDER = PARENT_PATH + '\static'

# Upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    filename = db.Column(db.String(80))
    password = db.Column(db.String(80))
    repassword = db.Column(db.String(80))


class TrackRecords(db.Model):
    __tablename__ = 'trackrecords'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    year = db.Column(db.String(80))
    artist = db.Column(db.String(80))
    composer = db.Column(db.String(80))

db.create_all()
db.session.commit()


def parseCSV(filePath):
    temp = list()

    # CVS Column Names
    col_names = ['Name', 'Year', 'Artist', 'Composer']
    try:
        app.logger.info('fILE Processed')
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(filePath, names=col_names, header=None)
        loggedin = session['user']
        user = User.query.filter_by(email=loggedin).first()
        # Loop through the Rows
        for i, row in csvData.iterrows():
            temp.append([i[0], i[1], i[2], i[16]])
            entry = TrackRecords(user_id=user.id, name=i[0], year=i[16], artist=i[1], composer=i[2])
            db.session.add(entry)
            db.session.commit()
    except:
        pass

    return temp
    # print(i, row['Name'], row['Year'], row['Artist'], row['Composer'], )


@app.route('/')
@app.route('/', methods=['POST', 'GET'])
def home():
    if 'user' not in session:
        return redirect('/signin')

    app.logger.info('Logged In')
    loggedin = session['user']
    user = User.query.filter_by(email=loggedin).first()
    trackes_record = TrackRecords.query.filter_by(user_id=user.id).all()

    if request.method == 'POST':
        app.logger.info('fILE UPLOADED')
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            filenameforlater = file_path
            # set the file path
            uploaded_file.save(file_path)
            loggedin = session['user']
            user = User.query.filter_by(email=loggedin).first()
            user.filename = uploaded_file.filename
            db.session.commit()
            recieveddata = parseCSV(file_path)
        # save the file
        return render_template('index.html', check=1, temp_data=recieveddata, trackes_record=trackes_record)
    return render_template('index.html', check=0, temp_data='', trackes_record=trackes_record)


@app.route('/signin')
@app.route('/signin', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        if username and password is not None:
            user = User.query.filter_by(email=username).first()
            if user:
                if user.password == password:
                    session['user'] = username
                    return redirect('/')

    return render_template('signin.html')


"""
    This route is for Signup to create new account
"""


@app.route('/signup')
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        if username and password is not None:
            entry = User(username=username, email=email, filename=None, password=password, repassword=re_password)
            db.session.add(entry)
            db.session.commit()
            app.logger.info('New Account Created')
            return redirect('/signin')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    if 'user' in session:
        app.logger.info('Logged out')
        session.pop('user')
    return redirect('/signin')


if __name__ == '__main__':
    app.run(debug=True)
