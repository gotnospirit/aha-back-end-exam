import string
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from www.models import User


def validate_password(password):
    lowers = list(string.ascii_lowercase)
    if not any(s in password.data for s in lowers):
        raise ValidationError(
            'Field must contains at least one lower character.')

    uppers = list(string.ascii_uppercase)
    if not any(s in password.data for s in uppers):
        raise ValidationError(
            'Field must contains at least one upper character.')

    digits = list(string.digits)
    if not any(s in password.data for s in digits):
        raise ValidationError(
            'Field must contains at least one digit character.')

    specials = list(string.punctuation)
    if not any(s in password.data for s in specials):
        raise ValidationError(
            'Field must contains at least one special character.')


class SignupForm(FlaskForm):
    user = HiddenField()
    email = EmailField('Email', validators=[
                       InputRequired(), Length(max=255), Email()])
    password = PasswordField('Password', validators=[InputRequired(),
                                                     Length(min=8, max=20),
                                                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Join us')

    def validate_email(self, email):
        user = User.FindByEmail(email.data)
        if user and user.password is not None:
            raise ValidationError('User already exists.')
        self.user.data = user

    def validate_password(self, password):
        validate_password(password)


class LoginForm(FlaskForm):
    user = HiddenField()
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

    def validate_password(self, _):
        user = User.FindByEmail(self.email.data)
        if not user:
            raise ValidationError('User not found.')
        elif not user.check_password(self.password.data):
            raise ValidationError('Incorrect password.')
        self.user.data = user


class ProfileForm(FlaskForm):
    nickname = EmailField('Nickname', validators=[
        InputRequired(), Length(max=255)])
    submit = SubmitField('Change')


class ChangePasswordForm(FlaskForm):
    email = HiddenField()
    old_pwd = PasswordField('Old password', validators=[InputRequired()])
    password = PasswordField('New password', validators=[InputRequired(),
                                                         Length(min=8, max=20),
                                                         EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Re-enter new password',
                            validators=[InputRequired()])
    submit = SubmitField('Change')

    def validate_old_pwd(self, old_pwd):
        user = User.FindByEmail(self.email.data)
        if not user or not user.check_password(old_pwd.data):
            raise ValidationError('Incorrect password.')

    def validate_password(self, password):
        validate_password(password)
