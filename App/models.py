from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from App.app import db


class Teams(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer(),primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_by_name(name):
        return Teams.query.filter_by(name=name).first()

class FavTeams(db.Model):
    __tablename__ = 'teams_users'

    team_id = db.Column(db.Integer,db.ForeignKey('teams.id'),primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)

class Bet(db.Model):
    __tablename__ = 'bet'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100),nullable=False)

    winner = db.Column(db.String(100),nullable=True)
    quantity = db.Column(db.Float,nullable=False)
    guess = db.Column(db.String(100), nullable=False)
    opposite = db.Column(db.String(100), nullable=False)

    match_id = db.Column(db.Integer,db.ForeignKey('matches.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    #odds


    def setStatus(self,status):
        self.status = status

    def setWinner(self,winner):
        self.winner = winner

    def setQuantity(self,money):
        self.quantity = money

    def setGuess(self,guess,opposite):
        self.guess = guess
        self.opposite = opposite

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=False)

    teams = db.relationship('Teams', secondary="teams_users",backref=db.backref('users'))
    bets = db.relationship("Bet")



    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def set_age(self,age):
        self.age = age

    def set_balance(self,balance):
        self.balance = balance

    def set_username(self,username):
        self.username = username

    def getPass(self):
        return self.password

    def check_password(self, password):
        return check_password_hash(self.password, password)


    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()


class Matches(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(100),nullable=False)
    team2 = db.Column(db.String(100),nullable=False)
    result = db.Column(db.String(100),nullable=True)
    bets = db.relationship("Bet")

    def __str__(self):
        return self.id

    @staticmethod
    def get_by_id(id):
        return Matches.query.filter_by(id=id).first()



