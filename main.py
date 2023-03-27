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
    cursor.execute("SELECT * FROM `posts` ORDER BY `timestamp`")
    results = cursor.fetchall()

    return render_template("main.html.jinja", posts=results)


if __name__ == '__main__':
    app.run(debug=True)