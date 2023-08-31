from flask import Flask, render_template, request, redirect, send_from_directory, abort, g
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import pymysql
import pymysql.cursors
from PIL import Image


login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'something_random'

class User():
    def __init__(self, id, username, pfp, banned):
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = not banned

        self.username = username
        self.pfp = pfp 
        self.id = id

    def get_id(self):
        return(str(self.id))
        
def check(form):
    if form == None:
        form = "NULL"
    else:
        pass


    
@login_manager.user_loader
def user_loader(user_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `users` WHERE `id` = " + user_id)
    result = cursor.fetchone()
    if result is None:
        return None

    return User(result['id'], result['username'], result['pfp'], result['banned'])

def connect_db():
    return pymysql.connect(
    host="localhost",
    user="swalker",
    password="221085269",
    database="swalker_appdatabase",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
    )

def get_db():
    '''Opens a new database connection per request.'''        
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db    

@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close() 

@app.get('/media/<path:path>')
def send_media(path):
    return send_from_directory('media', path)

@app.errorhandler(404)
def page_not_found(err):
    return render_template('404.html.jinja'), 404

@app.route("/")
def branch():
    if current_user.is_authenticated:
        return redirect('/feed')
    print("in home page")
    return render_template("main.html.jinja")

@app.route("/profile/<username>")
def user_profile(username):

        
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `users` WHERE `username` = %s", (username))
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        abort(404)

    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `posts` WHERE `user_id` = %s", (result['id']))
    post_result = cursor.fetchall()
    cursor.close()

    if current_user.username == username:
        return render_template("personal.html.jinja", user=result, posts=post_result)
    else:
        return render_template("profile.html.jinja", user=result, posts=post_result)

@login_required
@app.route("/settings")
def settings():
    cursor = get_db().cursor()
    username = current_user.username
    cursor.execute("SELECT * FROM `users` WHERE `username`= %s", (username))
    results = cursor.fetchall()
    cursor.close()

    return render_template("settings.html.jinja", user=results)

@app.route("/feed")
def feed():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `posts` JOIN `users` ON `posts`.`user_id` = `users`.`id` ORDER BY `timestamp` DESC" )
    results = cursor.fetchall()
    cursor.close()

    # user_id = current_user.id
    # cursor = get_db().cursor()
    # cursor.execute("SELECT * FROM `likes` WHERE `user_id` = %s", (user_id))
    # liked_posts = cursor.fetchall()
    # cursor.close()

    return render_template("feed.html.jinja", posts=results) # liked_posts=liked_posts

@app.route("/like")
def like():
    post_id = int(request.json['post_id'])
    cursor = get_db().cursor()
    user_id = current_user.id
    cursor.execute("SELECT `liked` FROM `likes` WHERE `user_id` = %s AND `post_id` = %s;"), (user_id, post_id)
    result = cursor.fetchone()
    if result == 0:
        liked = False
    else:
        liked = True        

    
    data = request.json()
    liked = data.get('liked')
    post_id = data.get('post')
    cursor.execute("INSERT INTO `likes` (`user_id`, `post_id`) VALUES (%s, %s)"), (user_id, post_id)


@app.route("/post", methods=['POST'])
@login_required
def post_feed():
    cursor = get_db().cursor()

    caption = request.form['caption']
    media = request.files['media']
    media_name = media.filename
    file_extension = media_name.split('.')[-1]

    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
        media.save('media/posts/' + media_name)

    user_id = current_user.id
    # if media == None and caption == None:
    #     return redirect('/feed')
    
    # check(media)
    # check(caption)

    cursor.execute("""INSERT INTO `posts` (`user_id`, `media`, `caption`) VALUES (%s, %s, %s)""", (user_id, media_name, caption))
    cursor.close()
    return redirect('/feed')

@app.route('/create')
def create(): 
    return render_template("pfp.html.jinja")


@app.route('/upload', methods=['POST'])
def upload():
    image = request.form['formData']
    cursor = get_db().cursor()
    cursor.execute("""INSERT INTO `dump` (`dump`) VALUES (%s)""", (image))
    imagename = image.filename
    x = int(request.form['x'])
    y = int(request.form['y'])
    width = int(request.form['width'])
    height = int(request.form['height'])
    file = Image.open(image)
    cropped_image = file.crop((x, y, x+width, y+height))
    cropped_image.save('/media/users/' + imagename)
    
    return redirect('/profile/ ' + current_user.username)

@app.route("/logout")
def logout():
    logout_user()

    return redirect('/login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/feed')
    
    if request.method == 'POST':
        cursor = get_db().cursor()
        username = request.form['username']
        cursor.execute("SELECT * FROM `users` WHERE `username` = %s", (username))

        result = cursor.fetchone()

        if result is None:
            return render_template("login.html.jinja")
        
        if request.form['password'] == result['password']:
            user = User(result['id'], result['username'], result['pfp'], result['banned'])

            login_user(user)
            cursor.close()
            return redirect('/feed')
            
        else:
            return render_template("login.html.jinja")

    elif request.method == 'GET':
        return render_template("login.html.jinja")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    
    if current_user.is_authenticated:
        return redirect('/feed')

    if request.method == 'POST':
        cursor = get_db().cursor()
        
        photo = request.files['pfp']
        if photo == None:
            file_name = "default.png"
        else:
            file_name = photo.filename
        file_extension = file_name.split('.')[-1]

        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            photo.save('media/users/' + file_name)
        else:
            raise Exception('Invalid File Type')

        username = request.form['username']

        cursor.execute("""
            INSERT INTO `users` (`username`, `display_name`, `password`, `email`, `bio`, 
            `birthday`, `pfp`) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (request.form['username'], request.form['display_name'], request.form['password'], request.form['email'], request.form['bio'], request.form['birthday'], file_name))
        cursor.close()

        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM `users` WHERE `username` = %s", (username))
        result = cursor.fetchall()
    
        user = User(result[0]['id'], result[0]['username'], result[0]['pfp'], result[0]['banned'])
        cursor.close()
        
        login_user(user)
        return redirect('/')
    elif request.method == 'GET':
        return render_template("signup.html.jinja")

if __name__ == '__main__':
    app.run(debug=True)