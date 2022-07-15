from www import app, db
from www.models import save_new_user, fetch_all_users
from flask import render_template, request, url_for, redirect
from www.forms import SignupForm, LoginForm, ProfileForm, ChangePasswordForm
from flask_login import login_user, logout_user, current_user, login_required
from www.mailer import send_verification_mail


@app.route('/', methods=('GET', 'POST'))
def index():
    users = None
    form = None
    if current_user.is_authenticated and current_user.is_activated():
        users = fetch_all_users()

        form = ChangePasswordForm()
        form.email.data = current_user.email

        if form.validate_on_submit():
            current_user.update_password(form.password.data)
            return redirect(url_for('index'))

    return render_template('index.html', users=users, form=form)


@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignupForm()
    if form.validate_on_submit():
        user = save_new_user(form.email.data, form.password.data)
        if user.can_send_verification():
            send_verification_mail(form.email.data)
        login_user(user, remember=True)
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user.data, remember=True)
        current_user.on_logged_in()
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if current_user.nickname != form.nickname.data:
            current_user.nickname = form.nickname.data
            db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user, form=form)


@app.route('/resend')
@login_required
def resend():
    if current_user.can_send_verification():
        send_verification_mail(current_user.email)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
