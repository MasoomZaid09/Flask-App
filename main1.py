#importing usefull modules
from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
import math
from datetime import datetime
from werkzeug.utils import secure_filename



local_server = True
# importing json file in our main.py
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

#initialization of secret_key,flask app,file uploading location
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']


#connecting to database
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


#home enpoint with pagination logic
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))

    #pagination logic
    page = request.args.get('page')
    if (not (str(page).isnumeric())):
        page = 1
    page = int(page)
    #slicing
    posts = posts[(page-1)*int(params['no_of_posts']):int(page-1)*(params['no_of_posts']) + int(params['no_of_posts'])]

    #first page
    if (page==1):
        prev = '#'
        next = "/?page=" + str(page + 1)
    #last page
    elif(page == last):
        prev = "/?page=" + str(page - 1)
        next = '#'
    #mid page
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html',posts=posts,params=params,next=next,prev=prev)

#edit posts from blogs
@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            content = request.form.get('content')
            slug = request.form.get('slug')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno == '0':
                post = Posts(title=box_title, content=content, img_file=img_file, slug=slug, tag_line=tline,
                             date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.content =content
                post.slug = slug
                post.tag_line = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return  redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params,post=post,sno=sno)



#delete posts from blog
@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')




#about page endoint
@app.route("/about")
def about():
    return render_template('about.html', params=params)

#logout logic
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

#post endpoint
@app.route("/post/<string:post_slug>", methods = ['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',post=post,params=params)

#dashboards logic
@app.route("/dashboard" , methods = ['GET','POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.filter_by().all()
        return render_template('dashboard.html',params=params,posts=posts)

    if (request.method == 'POST'):
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_pass']):
            session['user'] = username
            posts = Posts.query.filter_by().all()
            return render_template('dashboard.html',params=params,posts=posts)

    return render_template('login.html', params=params)



#making class for joining contacts in database
class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
#making class for joining posts in database
class Posts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tag_line = db.Column(db.String(25), nullable=True)
    img_file = db.Column(db.String(25), nullable=False)
    date = db.Column(db.String(20), nullable=False)


#making  files uploader
@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            # take files from user
            f = request.files['file1']
            #save files and secure files
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"




@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html',params=params)




app.run(debug=True)


