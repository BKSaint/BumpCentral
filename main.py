from flask import Flask, render_template, request, redirect
from flask_login import LoginManager
import pymysql
import pymysql.cursors

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

class User():
    def __init__(self, id, username, banned):
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = not banned

        self.username = username
        self.id = id

    def get_id(self):
        return(str(self.id))
        
    
@login_manager.user_loader
def user_loader(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `users` WHERE `id` = " + user_id)
    result = cursor.fetchone()
    if result is None:
        return None

    return User(result['id'], result['username'], result['banned'])

connection = pymysql.connect(
    host="10.100.33.60",
    user="swalker",
    password="221085269",
    database="swalker_appdatabase",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

@app.route("/")
def home():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `posts` JOIN `users` ON `posts`.`user_id` = `users`.`id` ORDER BY `timestamp` DESC" )
    results = cursor.fetchall()

    return render_template("main.html.jinja", posts=results)

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        cursor = connection.cursor()
        
        photo = request.files['pfp']
        file_name = photo.filename
        file_extension = file_name.split('.')[-1]

        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            photo.save('media/users/' + file_name)
        else:
            raise Exception('Invalid File Type')


        cursor.execute("""
            INSERT INTO `users` (`username`, `display_name`, `password`, `email`, `bio`, 
            `birthday`, `pfp`) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (request.form['username'], request.form['display_name'], request.form['password'], request.form['email'], request.form['bio'], request.form['birthday'], file_name))

        return redirect('/')
    elif request.method == 'GET':
        return render_template("signup.html.jinja")

@app.route("/login")
def login():
    return render_template("login.html.jinja")

if __name__ == '__main__':
    app.run(debug=True)