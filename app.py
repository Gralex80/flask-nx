from flask import Flask, jsonify, render_template, request, redirect, session
from flask_login import LoginManager, current_user, login_user, login_required, UserMixin, logout_user 
from flask_sqlalchemy  import SQLAlchemy
import requests, os

basedir = os.path.abspath(os.path.dirname(__file__))
#app = Flask(__name__)
app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.secret_key = "super secret key"

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),nullable=False ) 
    email = db.Column(db.String(30),nullable=False )     
#    def __repr__(self):
#       return '<User %r>' % self.username

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/healthcheck")
def api():
    json_out=[{'status':'started'}]
    return jsonify(json_out), 200

@app.route("/index")
def hello():
    text='Привет мир!'
    return render_template('hello.html',txt=text)

@app.route("/bootstrap")
def main():
    return render_template('bootstrap.html')

@app.route("/")
@login_required    
def index():
    return render_template('index.html')
    
@app.route('/logout') ## button logout
@login_required
def logout():
    session.pop(current_user.username, None)
    logout_user()
    return redirect("/") 

# @app.route('/users', methods=['GET']) 
# def get_run_requests():
#     response=requests.get('https://reqres.in/api/users?page=2')
#     txt=response.json()
#     txt=txt['data']
#     return render_template('users1.html',out_json=txt)

@app.route('/users/<page>', methods=['GET']) 
@login_required 
def get_run_requests_page(page):
    response=requests.get('https://reqres.in/api/users?page='+page)
    txt=response.json()
    pages=int(txt['total_pages'])
    txt=txt['data']

    return render_template('users1.html',out_json=txt,pages=pages)

@app.route('/login', methods=['GET','POST'])
def login():
    txt='авторизация'
    user =''
    if request.method == 'POST' :
        inputEmail= request.form.get('inputEmail')
        try:
            session.pop(current_user.username, None)
        except:
            user = User.query.filter_by(email=inputEmail).first()
        if user:
            login_user(user)
            next = request.args.get('next')
            return redirect(next)
        else:
            txt = 'доступ закрыт: '+str(user)
    return render_template('login.html',txt=txt)

@app.route('/form',methods=['GET','POST']) 
@login_required
def form():
    text=''
    if request.method == 'POST' :
        text = request.form.get('input_text')
    return render_template('form.html',text=text)

@app.route('/admin',methods=['GET','POST']) 
@login_required
def admin():
    name =''
    email =''
    if current_user.username != 'admin':
        return redirect('/')

    if request.method == 'POST' :
        name = request.form.get('name')
        email = request.form.get('email')
        try:
            user = User(username=name,email=email)
            db.session.add(user)
            db.session.commit()
        except:
            return('При добавлении пользователя произошла ошибка')
    users = User.query.all()
    return render_template('admin.html',users=users,name=name,email=email)

@app.route('/admin/deleteUser/<id>',methods=['POST']) 
@login_required
def admin_del(id):
    if current_user.username != 'admin':
        return redirect('/')
    if request.method == 'POST' :
        try:
            user = User.query.get(int(id))
            db.session.delete(user)
            db.session.commit()
        except:
            return('При удалении пользователя произошла ошибка')
    users = User.query.all()
    return redirect('/admin')

##############################################
if __name__ == "__main__":
    app.run(debug=True)