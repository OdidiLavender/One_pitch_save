from flask import Flask, request, render_template, session, redirect, url_for,flash

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,BooleanField,PasswordField
from wtforms.validators import DataRequired,Email,EqualTo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from wtforms.widgets import TextArea

from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash

#our app starts here

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))

# Create Login Form
# class LoginForm(FlaskForm):
# 	username = StringField("Username", validators=[DataRequired()])
# 	password = PasswordField("Password", validators=[DataRequired()])
# 	submit = SubmitField("Submit")

#creating a model for login
# class User(db.Model):

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), nullable=False, unique=True)
#     name = db.Column(db.String(200), nullable=False)
#     email= db.Column(db.String(120), nullable=False, unique=True)
#     date_added= db.Column(db.DateTime, default=datetime.utcnow)
#     password_hash = db.Column(db.String(128))

    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute!')
        
        
    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password)
        
    # def verify_password(self, password):
    #     return check_password_hash(self.password_hash, password)






#Add Datebase
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://skcwleqfuxggit:ca5b24e89691c1b102420d8b7590226911be46c69504a8c64b0f24eab94e0811@ec2-52-3-2-245.compute-1.amazonaws.com:5432/d4h534hv3mu0d6'

#Secret Key!
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

#Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")
# Creating a Show Post


@app.route('/posts')
def posts():
    # Grabing all pitches from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("pitches.html", posts=posts)


# Add Post Page
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear The Form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return Message
        flash("Pitch Post was Submitted Successfully!")

    return render_template("add_post.html", form=form) 


#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email= db.Column(db.String(120), nullable=False, unique=True)
    date_added= db.Column(db.DateTime, default=datetime.utcnow)

    #Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

# Creating a form class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    submit  = SubmitField('submit')

# Creating a form class
class NamerForm(FlaskForm):
    name = StringField('What is you name?', validators=[DataRequired()])
    submit  = SubmitField('submit')



@app.route('/')


def index():
    first_name = "John"
    return render_template("index.html",first_name=first_name)




@app.route('/user/<name>')
def user(name):
    return render_template("user.html",user_name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/name', methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submmitted Successfully!")
    return render_template('name.html', form=form, name=name)

@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None: 
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    

    return render_template('add_user.html', form=form ,name=name ,our_users=our_users)
@login_manager.user_loader
def get(id):
    return User.query.get(id)

@app.route('/login',methods=['GET'])
# @login_required
def get_home():
    return render_template('login.html')

@app.route('/signup',methods=['GET'])
def get_signup():
    return render_template('signup.html')

@app.route('/login',methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    login_user(user)
    return redirect('/add_post')

@app.route('/signup',methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    user = User(username=username,email=email,password=password)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(email=email).first()
    login_user(user)
    flash("Signup Successful!")
    return redirect('/login')

@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return redirect('/')




if __name__ == "__main__":
    app.run(debug=True)