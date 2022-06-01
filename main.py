from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
from sqlalchemy import exc

app = Flask(__name__)
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable


db = MySQLAlchemy(app)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


class ListForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

    submit = SubmitField('Submit')


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/add', methods=["GET", "POST"])
def add_list():
    form = ListForm()
    if form.validate_on_submit():
        new_list = List(name=request.form["name"])
        try:
            db.session.add(new_list)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('lists'))
    return render_template('add.html', form=form)


@app.route("/delete/<int:list_id>")
def delete_list(list_id):
    post_to_delete = List.query.get(list_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('lists'))


@app.route('/list')
def lists():
    todos = db.session.query(List).all()
    todos = [item.to_dict() for item in todos]
    header = ["ID", "Name"]
    return render_template('todos.html', todos=todos, header=header)


if __name__ == '__main__':
    app.run(debug=True)
