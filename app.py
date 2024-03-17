from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor

from webforms import UserForm, NamerForm, PostForm, LoginForm, SearchForm

# Create a Flask Instance (pra achar arquivos dos seu programa)
app = Flask(__name__)
ckeditor = CKEditor(app)
#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = 'SENFLASK'
#Iniciando Database
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#Create Admin Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template("admin.html")
    else:
        flash("You must have admin acess to see this page")
        return redirect(url_for('dashboard'))

# Create Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        # Query the Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html",
                               form=form,
                               searched = post.searched,
                               posts = posts)

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfull!")
                return redirect(url_for('dashboard'))
            else:
                flash("Não foi possível realizar o login")
        else:
            flash("Não foi possível realizar o login!")
    return render_template('login.html', form=form)


#Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        #adicione aqui
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update = name_to_update,
                                   id = id)
        except:
            flash("Error")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update = name_to_update,
                                   id = id)
    else:
        return render_template("dashboard.html",
                                   form=form,
                                   name_to_update = name_to_update,
                                   id = id)
    #return render_template('dashboard.html')

def login():
    form = LoginForm()
    return render_template('login.html')


#Create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now)
    slug = db.Column(db.String(255)) #nome na url
    # Foreign Key to Link with a User
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            
            flash("Blog Post Was Deleted!")
            #Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
            
        except:
            flash("There was a problem on delete the post")
            #Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("You can't delete Posts of Other Users!")
        #Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    
@app.route('/posts')
def posts():
    #Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)
    
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        #Update Database
        db.session.add(post)
        db.session.commit()
        
        flash("Post Has Been Updated!")
        
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You don't have autorization to edit this post")
        #Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    
# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()    
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            poster_id=poster,
            slug=form.slug.data
            #adicione aqui
        )
        #clear form
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''
        
        # Add post data to database
        db.session.add(post)
        db.session.commit()
        
        flash("Blog Post Submitted Successfully!")
        
    #Redirect to webpage (outside if)
    return render_template("add_post.html", form=form)
            
            

#Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)    
    username = db.Column(db.String(20), nullable=False, unique=True)
    #200 = maximo
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    #adicione aqui
    date_added = db.Column(db.DateTime, default=datetime.now)
    
    #password stuff
    password_hash = db.Column(db.String(128))
    #users can have many posts
    posts = db.relationship('Posts', backref='poster')
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", 
                            form=form,
                            name=name,
                            our_users=our_users)
        
    except:
        flash("Erro ao deletar usuário")
        return render_template("add_user.html", 
                            form=form,
                            name=name,
                            our_users=our_users)

    
#Update Database
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        #adicione aqui
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("update.html",
                                   form=form,
                                   name_to_update = name_to_update,
                                   id = id)
        except:
            flash("Error")
            return render_template("update.html",
                                   form=form,
                                   name_to_update = name_to_update,
                                   id = id)
    else:
        return render_template("update.html",
                                   form=form,
                                   name_to_update = name_to_update,
                                   id = id)


#Create route "decorator"
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hashing password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            user = Users(
                username=form.username.data,                
                name=form.name.data, 
                email=form.email.data, 
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw
                #adicione aqui
                )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        #adicione aqui
        flash("User Added Sucessufully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
                           form=form,
                           name=name,
                           our_users=our_users)

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)

#Create Name Page
@app.route('/name', methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Sucessufully")
        
    return render_template("name.html",
                           name = name,
                           form = form)
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template("")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)