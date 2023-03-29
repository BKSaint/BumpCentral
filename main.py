from flask import Flask, render_template, request, redirect
import pymysql
import pymysql.cursors


connection = pymysql.connect(
    host="10.100.33.60",
    user="swalker",
    password="221085269",
    database="swalker_appdatabase",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True

)

app = Flask(__name__)
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
        cursor.execute("""
            INSERT INTO `users` (`username`, `display_name`, `password`, `email`, `bio`, 
            `birthday`, `pfp`) VALUES ('%s, %s, %s, %s, %s, %s, %s')
        """)

        return request.form
    elif request.method == 'GET':
        return render_template("signup.html.jinja")

@app.route("/login")
def login():
    return render_template("login.html.jinja")

if __name__ == '__main__':
    app.run(debug=True)