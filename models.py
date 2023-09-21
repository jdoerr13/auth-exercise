#REMEMBER MODEL.PY IS THE DATABASE TABLES THAT REPRESEND THE STRUCTURE OF MY APPLICATIONS DATA- USING ORM FRAMEWORK LIKE SQLALCHEMY- Responsibilities: models.py handles tasks related to data storage, retrieval, and manipulation. It defines the fields, relationships, and constraints of your application's data.
#FORMS.PY IS FOR HANDELING USER IMPUT AND VALIDATION Used to collect data from users, validate that data, and then convert it into a format that can be used in your application.- TYPICALLY WORKS FROM A WEB FRAMEWORK SUCH AS FLASKFORM- rendering HTML forms, handling form submissions, validating user input, and converting that input into data that can be stored in the database.

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
#INNITIALIZE BCRYPT TO USE
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
    app.app_context().push()
    
    db.create_all()


class Feedback(db.Model): 
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)

    user = db.relationship('User', backref='feedback', lazy=True)

class User(db.Model):

    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    user_feedbacks = db.relationship('Feedback', backref='user_ref', lazy=True)

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""
#OUR SPECIAL LOGIC IN THIS CASE IS GENERATING A BCRYPT PASSWORD SO IT DOESN'T MAKE SINCE TO STORE IT AS AN INSTANCE METHOD ON A USER
        hashed = bcrypt.generate_password_hash(pwd) #PWD TURNED INTO HASH
        # turn bytestring into normal (unicode utf8) string SO WE CAN STORE IT IN THE DATABASE
        hashed_utf8 = hashed.decode("utf8")
        new_user = cls(
            username=username,
            password=hashed_utf8,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user
        # return instance of user w/username and hashed pwd
        # return cls(username=username, password=hashed_utf8)

# In [3]: User.register('mrmonkey1', 'bananaslol')
# Out[3]: <User (transient 4356035344)>

# In [4]: u= User.register('mrmonkey1', 'bananaslol')

# In [5]: db.session.add(u)

# In [6]: db.session.commit()
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """
                #TRYTING TO FIND A USER WITH THAT USERNAME
        u = User.query.filter_by(username=username).first()
                #IF USER NAME IS FOUND CALL THE BELOW AND COMPARES THE BCRIPT PASSWORD TO THE ONE FROM THE DATABASE
        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
        

# In [1]: from flask_bcrypt import Bcrypt

# In [2]: bcrypt =Bcrypt()

# In [3]: user_pwd = 'jimmy'

# In [4]: bcrypt.generate_password_hash(user_pwd)
# Out[4]: b'$2b$12$.a3n8tcbpcQycMZCjytBseOs4iUUXsonrL6HMPw6qmXtF.n6gO.tC'

# In [5]: bcrypt.generate_password_hash(user_pwd) #it will be diff bc it is generating a salt
# Out[5]: b'$2b$12$3yz17UeX0C2ELhQ/GPgnHeciLDIx/pJvkndPpc06w73RBrycNmzm2'

# In [6]: h = bcrypt.generate_password_hash(user_pwd)

# In [7]: h
# Out[7]: b'$2b$12$jBR/ib87k.SGbdSPdCw00O1ZGAEhV/E8YWfn8CUiHR.IgHFhyrH3W'

# In [8]: bcrypt.check_password_hash(h, user_pwd) #checks result and compares to what we have here
# Out[8]: True


