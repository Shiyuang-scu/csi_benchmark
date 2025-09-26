from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FileField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    who_we_are = TextAreaField('Who we are', validators=[Length(min=0, max=256)])
    what_we_do = TextAreaField('What we do', validators=[Length(min=0, max=256)])
    best_submission = SelectField('BestSubmission')
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class UploadFileForm(FlaskForm):
    file = FileField()
    reference_file = SelectField('Reference File', choices=app.config['AVAILABLE_MODELS'].keys())
    submit = SubmitField('Upload')
