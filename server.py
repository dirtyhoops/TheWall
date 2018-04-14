from flask import Flask, redirect, render_template, request, flash, session
# import the function connectToMySQL from the file mysqlconnection.pycopy
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
app.secret_key = 'denvernuggets'

# invoke the connectToMySQL function and pass it the name of the database we're using
# connectToMySQL returns an instance of MySQLConnection, which we will store in the variable 'mysql'
mysql = connectToMySQL('useraccounts')
# now, we may invoke the query_db method

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def addFriend():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']  

    if len(first_name) < 1  or len(last_name) < 1 or len(email) < 1 or len(password) < 1:
        flash("Must Fill out everything")
        return redirect('/')

    if len(first_name) < 2:
        print("First Name Should be atleast 2 characters")
        return redirect('/')

    if len(last_name) < 2:
        flash("Last Name Should be atleast 2 characters")
        return redirect('/')

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect('/')

    #checking if the email address is already taken
    query_select = "SELECT email FROM users WHERE email = %(email)s;"
    data1 = {
             'email': request.form['email']
           }

    email_dup = mysql.query_db(query_select, data1)
    if email_dup:
        flash("Email is Already Taken!")
        return redirect('/')

    if password != confirm_password:
        flash("password didnt match")
        return redirect('/')

    add_query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': request.form['password']
        }

    #adds user in the table 
    mysql.query_db(add_query, data)

    flash("Registered Successfully")
    return redirect('/success')

@app.route('/success')
def success():
    if session['userId']:
        #to display all the messages
        query_allMessages = "SELECT messages.id, message, first_name, last_name, messages.created_at FROM users JOIN messages ON users.id = messages.user_id"
        all_messages = mysql.query_db(query_allMessages)

        #to display all the comments
        query_allComments = "SELECT * FROM comments JOIN users ON users.id = comments.user_id"
        all_comments = mysql.query_db(query_allComments)
        
        return render_template("success.html", all_messages = all_messages, all_comments = all_comments)
    else:
        flash("You're currently not logged in!")
        return redirect('/')
    

@app.route('/delete', methods=['POST'])
def deleteEmail():
    id = int(request.form['deleteId'])
    query1 = "DELETE FROM users WHERE id = '{}'".format(id)
    mysql.query_db(query1)
    return redirect('/success')


@app.route('/logout', methods=['POST'])
def clear():
    session['firstName'] = ''
    session['userId'] = ''
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    query2 = "SELECT id, first_name, email FROM users WHERE email = %(email)s AND password = %(password)s;"
    email = request.form['email']
    password = request.form['password']
    data = {
        'email': request.form['email'],
        'password': request.form['password']
        }
    savedid = mysql.query_db(query2, data)
    if savedid:
        session['userId'] = savedid[0]['id']
        session['firstName'] = savedid[0]['first_name']
        return redirect('success')

    else: 
        flash("pass and email didnt match")
        return redirect('/')
        



# ROUTES FOR POSTING MESSAGES, POSTING COMMENTS
@app.route('/post', methods=['POST'])
def postData():
    if session['userId']:
        addMessage = str(request.form['message'])
        query_addMessage = "INSERT INTO messages (user_id, message) VALUES ('{}','{}')".format(session['userId'], addMessage)
        mysql.query_db(query_addMessage)
        return redirect('/success')
    else:
        flash("cant post since youre not logged in")
        return redirect('/success')




@app.route('/comment', methods=['POST'])
def postComment():
    if session['userId']:
        messageID = request.form['messageID']
        commentMessage = str(request.form['comment'])
        query_addComment = "INSERT INTO comments (message_id, user_id, comment) VALUES ('{}', '{}', '{}')".format(messageID, session['userId'], commentMessage)
        mysql.query_db(query_addComment)
        return redirect('/success')
    else:
        return redirect('/success')

if __name__ == "__main__":
    app.run(debug=True)