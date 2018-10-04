from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildabear@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    post_date = db.Column(db.DateTime)

    def __init__(self, title, body, post_date=None):
        self.title = title
        self.body = body
        if post_date is None:
            post_date = datetime.now()
        self.post_date = post_date    



@app.route('/blog', methods=['POST', 'GET'])
def main_blog_page():
    blog_id = request.args.get('id')
    if not blog_id:
        entries =  Blog.query.order_by(Blog.post_date.desc()).all()
        return render_template('blog.html',title="Build-a-Blog", entries=entries)
    single_entry = Blog.query.get(blog_id)
    return render_template('entry_details.html',title="Blog Entry", entry=single_entry) 


@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add a new post")
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
            return render_template('newpost.html', title="Build-a-Blog", title_error=title_error, body_error=body_error, blog_title=blog_title, entry_body=entry_body)

        new_entry=Blog(blog_title,entry_body)        
        db.session.add(new_entry)
        db.session.commit()
      
        single_entry = str(new_entry.id)

    
        return redirect('/blog?id='+single_entry)


if __name__ == '__main__':
    app.run()