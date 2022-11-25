from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user
from .models import User
import mysql.connector
from hashlib import sha256

auth = Blueprint('auth', __name__)

#users = {}

def retrieve_query_single(query):
    # helper function to establish connection and retrieve queries
    cnx = mysql.connector.connect(user = 'root', database = 'login')
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    if data == None:
        return None
    return data[0]

def submit_query(query):
    # helper function to establish connection and submit queries
    cnx = mysql.connector.connect(user = 'root', database = 'login')
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    cursor.close()

def validate_password(email, password):
    hashed_password = sha256(password.encode('utf-8')).hexdigest()
    user_password = retrieve_query_single(f"select password from user where email = '{email}'")
    return hashed_password == user_password

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = retrieve_query_single(f"select email from user where email = '{email}'")
    if user == None or not validate_password(email, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    uid = retrieve_query_single(f"select id from user where email = '{email}'")
    name = retrieve_query_single(f"select name from user where email = '{email}'") 
    user = User(uid, email, name, password)
    login_user(user, remember=remember)

    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    hashed_password = sha256(password.encode('utf-8')).hexdigest()

    user = retrieve_query_single(f"select email from user where email = '{email}'")

    if user != None:
        flash('Email address already exists')
        return redirect(url_for('auth.signup')) 

    submit_query(f'''insert into user(email, name, password) values ('{email}', '{name}', '{hashed_password}')''')

    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    return 'Logout'