from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogsrus@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'R}gXrv#G<"Ay=k.'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    post_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, post_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if post_date is None:
            post_date = datetime.now()
        self.post_date = post_date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'main_blog_page']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog')
def main_blog_page():
    # get params (if any) from url 
    author_id=request.args.get('user')
    page_num=request.args.get('page', 1, type=int)
    if author_id:
        entries = Blog.query.filter_by(owner_id=author_id).order_by(Blog.post_date.desc()).paginate(page=page_num, per_page=2)
        author = User.query.get(author_id)
        return render_template('blog.html',title="Blogz",page_title=author.username+"'s blog posts",entries=entries, user=author.id)

    blog_id = request.args.get('id')
    if not blog_id:
        entries =  Blog.query.order_by(Blog.post_date.desc()).paginate(per_page=3)
        return render_template('blog.html',title="Blogz v1.0", page_title="Blogz v1.0", entries=entries)
    single_entry = Blog.query.get(blog_id)
    return render_template('entry_details.html',title="Blog Entry", entry=single_entry) 

@app.route('/')
def index():
    authors = User.query.all()
    return render_template('index.html', title="Blogz v1.0", page_title="Blogz v1.0", authors=authors)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username =  request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # if user exists and password is valid, login and redirect
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            #TODO add error messages on validation
            if user and user.password != password:
                flash('password is incorrect', 'error')
            if not user:
                flash('username does not exist', 'error')
            if not username and not password:
                # error message for both fields blank
                flash('input fields blank are blank, please enter a value', 'error')
            if not username or not password:    
                if not username:
                    # error message for username blank or invalid
                    flash('username field is blank, please enter a value', 'error')
                if not password:
                    # error message for password blank or invalid
                    flash('password field is blank, please enter a value', 'error')
            return redirect('/login')
                
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate inputs, minimum 3 character length for username/password
        pattern=re.compile(r"^[\S]{3,}$")

        if not pattern.match(username):
            # return username error
            flash('username is invalid, please re-enter', 'error')

        if not pattern.match(password):
            # return password error
            flash('password is invalid, please re-enter', 'error')

        if password != verify:
            # return password mismatch error
            flash('passwords do not match, please re-enter', 'error')    
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('username already exists, please re-enter', 'error')

        if existing_user or not pattern.match(username) or not pattern.match(password) or password != verify:
            return redirect('/signup')    
        
        # if user doesnt exist, create new user, add to db, redirect to add new post page
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')


    return render_template('signup.html')        
            

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
            


@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add a new post", page_title="Add a new post")

    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        entry_body = request.form['entry_body']
        # error checks here for blank title or body

        title_error=""
        body_error=""

        if not blog_title or not entry_body:
            if not blog_title:
                title_error="Title is blank. Please enter a title."
            if not entry_body:
                body_error="Blog entry is blank. Please enter some content."
            return render_template('newpost.html', title="Build-a-Blog", page_title="Add a new post", title_error=title_error, body_error=body_error, blog_title=blog_title, entry_body=entry_body)

        new_entry=Blog(blog_title,entry_body,owner)        
        db.session.add(new_entry)
        db.session.commit()
      
        single_entry = str(new_entry.id)

    
        return redirect('/blog?id='+single_entry)


if __name__ == '__main__':
    app.run()