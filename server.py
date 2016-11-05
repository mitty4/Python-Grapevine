from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import datetime
app = Flask(__name__)
app.secret_key = 'blahblah'
mysql = MySQLConnector(app,'the_wall')


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
	email = request.form['email']
	database = mysql.query_db("SELECT * FROM users")
	for data in database:
		if email == data['email']:
			flash('email taken!')
			return redirect('/')
	data = {
		'first_name': request.form['first_name'],
		'last_name': request.form['last_name'],			
		'email': request.form['email'],
		'password': request.form['password'],
		'created_at': datetime.datetime.now(),
	}
	newUser = mysql.query_db("INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (:first_name, :last_name, :email, :password, :created_at); ", data)
	session['id'] = newUser
	return redirect('/wall')


@app.route('/login', methods=['POST'])
def login():
	email = session['email'] = request.form['email'] 
	password = session['password'] = request.form['password']
	data = {
		'email': session['email'],
	}
	row = mysql.query_db("SELECT * FROM users WHERE email = :email", data)
	if row != []:
		check_pwd =  mysql.query_db("SELECT * FROM users WHERE email = :email", data)[0]['password']
		user = mysql.query_db("SELECT id, first_name FROM users WHERE email = :email", data)[0]
		session['id'] = user['id']
		if session['password'] == check_pwd:
			return redirect('/wall')
		else:
			flash('Wrong Password')
			return redirect('/')
	else:
		flash('Email not recognized')
		flash('Wrong Password')
		return redirect('/')



@app.route('/wall')
def wall():
	rows = mysql.query_db("SELECT messages.created_at AS created_at, messages.meassage AS meassage, users.first_name AS first_name, users.last_name AS last_name, messages.id AS id  FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY created_at DESC")
	data = {
		'email': session['email'],
	}
	user = mysql.query_db("SELECT id, first_name FROM users WHERE email = :email", data)[0]
	if session['id']:
		current = user['first_name']
		return render_template('wall.html', rows = rows, current = current)
	else:
		return redirect('/')


@app.route('/message', methods=['POST'])
def create():
	data = {
		'id': session['id'],
		'message': request.form['message'],
		'created_at': datetime.datetime.now(),
		}
	mysql.query_db("INSERT INTO messages (meassage, created_at, user_id) VALUES (:message, :created_at, :id)", data)
	return redirect('/wall')




@app.route('/delete/<id>')
def delete(id):
	data = {
		'id': id
	}
	user_id = mysql.query_db("SELECT user_id FROM messages WHERE id = :id", data)[0]['user_id']
	print user_id
	print session['id']
	if session['id'] == user_id: 
		mysql.query_db("DELETE FROM messages WHERE messages.id = :id", data)
		return redirect('/wall')
	else:
		flash('HEY, not your message to delete!!')
		return redirect('/wall')




@app.route('/logoff')
def logoff():
	session['id'] = ''
	return redirect('/')


app.run(debug=False)








