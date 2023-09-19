from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user')

    def __repr__(self):
        return f'<{self.id}. User {self.username}>'
    
    # validate the user's username to ensure that it is present and unique (no two users can have the same username).
    # decorator validates is used , mean this method will be called whenever 'username' attribute is set
    @validates('username')
    def validate_username(self, key, username):
        # validation logic, ensure username is present, unique.

        #checking username is present
        if not username:
            raise ValueError("Username must be present")
        #checking username is unique
        user_exist = User.query.filter(User.username == username).first()
        if user_exist and user_exist.id != self.id:
            raise ValueError("Username is not unique")
        # if user is unique and present return username
        return username

    # this is a special property decorator for sqlalchemy
    # it leaves all of the sqlalchemy characteristics of the column in place
    @hybrid_property
    def password_hash(self):
        raise AttributeError("password may not be viewed")

    # setter method for the password property
    @password_hash.setter
    def password_hash(self, password):
        # utf-8 encoding and decoding is required in python 3
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    # authentication method using user and password
    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<{self.id}. Recipe {self.title} has {self.instructions} belongs to {self.user_id}>'

    #decorator validates is used , mean this method will be called whenever 'title', attribute is set
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title must be present")
        return title
