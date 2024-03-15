from flask import Flask, render_template, flash, request

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from webforms import UserForm, NamerForm

# Create a Flask Instance (pra achar arquivos dos seu programa)
app = Flask(__name__)
#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = 'SENFLASK'
#Iniciando Database
db = SQLAlchemy(app)


#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #200 = maximo
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    pass
    
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
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("update.html",
                                   form=form,
                                   name_to_update = name_to_update)
        except:
            flash("Error")
            return render_template("update.html",
                                   form=form,
                                   name_to_update = name_to_update)
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
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)