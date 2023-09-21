from flask import Flask, render_template, redirect, session, flash, abort, url_for, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, FeedbackForm, LogIn
from sqlalchemy.exc import IntegrityError #this is for excepting two users with the same name so I can generate an error

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///authentication"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
app.app_context().push()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def redirect_to_register():
    return redirect('/register')

@app.route('/register')
def show_register_form():
    form = UserForm()
    return render_template('register.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()

    if form.validate_on_submit():
        # Get user input data from the form
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # Create a new user and add to the database
        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')

        # Redirect to /secret or any other desired page after registration
        return redirect('/secret')
    
    return render_template('register.html', form=form)

@app.route('/login')
def show_login_form():
    form = LogIn()
    return render_template('login.html', form=form)

@app.route('/login', methods=['POST'])
def login_user():
    form = LogIn()

    if form.validate_on_submit():
        # Get user input data from the form
        username = form.username.data
        password = form.password.data

        # Authenticate user
        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            # Store user_id in session
            session['user_id'] = user.username

            # Redirect to /secret or any other desired page after login
            return redirect(f'/users/{user.username}')
    
    flash("Invalid username/password.", "danger")
    return render_template('login.html', form=form)

# @app.route('/secret')
# def secret():
#     # Check if the user is logged in
#     if 'user_id' not in session:
#         flash("Please login first!", "danger")
#         return redirect('/login')

#     # You made it!
#     return "You made it!"

@app.route('/users/<username>', methods=['GET', 'POST'])
def user_profile(username):
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)  # User not found, you can create a custom error page for this

    if request.method == 'POST':
        # Handle feedback submission
        text = request.form.get('text')
        if text:
            feedback = Feedback(text=text, user_id=user.id)
            db.session.add(feedback)
            db.session.commit()
            flash('Feedback added successfully!', 'success')
            return redirect(f'/users/{username}')
        else:
            flash('Please enter feedback text.', 'danger')

    return render_template('user_profile.html', user=user, feedback=user.user_feedbacks)


@app.route('/logout')
def logout_user():
    # Clear user_id from session
    session.pop('user_id', None)
    flash("Logged out successfully!", "info")
    return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'user_id' in session and session['user_id'] == username:
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            session.pop('user_id', None)
            flash("Account deleted successfully!", "info")
            return redirect('/')
    flash("Unauthorized action or user not found.", "danger")
    return redirect('/')

@app.route('/add-feedback', methods=['GET', 'POST'])
def add_feedback():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect('/login')

    feedback_form = FeedbackForm()  # Create an instance of the FeedbackForm

    if feedback_form.validate_on_submit():  # Check if the form is submitted and valid
        title = feedback_form.title.data
        content = feedback_form.content.data

        feedback = Feedback(title=title, content=content, username=session['user_id'])
        db.session.add(feedback)
        db.session.commit()

        flash('Feedback added successfully!', 'success')
        return redirect(url_for('user_profile', username=session['user_id']))
    
    user = User.query.get(session['user_id'])
    return render_template('feedback.html', feedback_form=feedback_form, user=user)  # Pass the feedback_form to the template




