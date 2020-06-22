from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import app


db = SQLAlchemy(app)


#confi
app.config.update(
    DEBUG=True,
    SECRET_KEY='sekretny_klucz'
)


# ustawienie flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# model uzytkownika
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


#generacja uzytkownikow
users = [User(id) for id in range(1, 10)]


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(30))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


@app.route('/')
def main():
    dane = {'tytul': 'Prosty blog', 'tresc': '--------------------------------'}

    posts = Blogpost.query.all()

    return render_template('index.html', tytul=dane["tytul"], tresc=dane['tresc'], posts=posts)


@app.route("/about")
def omnie():
    dane = {'tytul': 'O mnie', 'tresc': '--------------------------------'}
    return render_template('omnie.html', tytul=dane['tytul'], tresc=dane['tresc'])


@app.route("/dodaj")
@login_required
def info():
    dane = {'tytul': 'Dodaj post', 'tresc': '--------------------------------'}
    return render_template("dodajpost.html", tytul=dane["tytul"], tresc=dane["tresc"])


@app.route("/kontent/<int:post_id>")
def kontent(post_id):
    # nie wyświetli tytułu ani treści jeśli tytułem będzie: "Strona główna"

    post = Blogpost.query.filter_by(id=post_id).one()

    date_posted = post.date_posted.strftime('%B %d %Y')

    return render_template("kontent.html", post=post, date_posted=date_posted)


@app.route("/login", methods=["GET", "POST"])
def login():
    tytul = 'Zaloguj się'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(url_for("main"))
        else:
            return abort(401)
    else:
        return render_template('formularz_logowania.html', tytul=tytul)





@app.errorhandler(401)
def page_not_found(e):
    tytul = "Coś poszło nie tak..."
    blad = "401"
    return render_template('blad.html', tytul=tytul, blad=blad)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    tytul="Wylogowanie"
    return render_template('logout.html', tytul=tytul)


@app.route("/addpost", methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('main'))


# przeladowanie uzytkownika
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == '__main__':
    app.run(debug=True)
