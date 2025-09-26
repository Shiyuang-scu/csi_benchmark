import urllib.parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, UploadFileForm
from app.models import User, SubmittedFile, del_sub_file
from app.benchmarklib import evaluate, tab2text
from flask import render_template, flash, redirect, url_for, request, send_file
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.utils import secure_filename
import os


@app.route('/')
@app.route('/index')
def index():
    best_submits = []
    for user in User.query.all():
        if user.best_submitted_file:
            if user.best_submitted_file != None:
                best_submits.append((user.username, SubmittedFile.query.filter_by(
                    user_id=user.id).filter_by(id=user.best_submitted_file).first()))
    return render_template('index.html', title='Home', best_submits=best_submits, users=get_all_users())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urllib.parse.urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, users=get_all_users())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user !')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, users=get_all_users())


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    sub_files = SubmittedFile.query.filter_by(user_id=user.id).all()
    if user.best_submitted_file:
        best_sub_file = SubmittedFile.query.filter_by(user_id=user.id).filter_by(
            id=user.best_submitted_file).first_or_404().filename
    else:
        best_sub_file = None
    return render_template('user.html', user=user, best_submitted_file=best_sub_file, sub_files=sub_files, users=get_all_users())


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    form.best_submission.choices = [(sf.id, sf.filename) for sf in SubmittedFile.query.filter_by(
        user_id=current_user.id).order_by('filename')]
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.who_we_are = form.who_we_are.data
        current_user.what_we_do = form.what_we_do.data
        current_user.best_submitted_file = form.best_submission.data
        db.session.commit()
        sub_files = SubmittedFile.query.filter_by(
            user_id=current_user.id).all()
        best_sub_file = SubmittedFile.query.filter_by(user_id=current_user.id).filter_by(
            id=current_user.best_submitted_file).first_or_404().filename
        flash('Your changes have been saved.')
        return render_template('user.html', user=current_user, best_submitted_file=best_sub_file, sub_files=sub_files, users=get_all_users())
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.who_we_are.data = current_user.who_we_are
        form.what_we_do.data = current_user.what_we_do
        form.best_submission.data = current_user.best_submitted_file
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form, users=get_all_users())


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        reference_file = form.reference_file.data
        if filename == '':
            flash('No selected file')
            return redirect(url_for('upload_file'))
        if filename in [s.filename for s in SubmittedFile.query.all()]:
            flash('You need to rename your file')
            return redirect(url_for('upload_file'))
        elif filename and allowed_file(filename):
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(path)
            steps, dst_list, middle_acc, middle_comp, size, declared_size = evaluate(path, reference_file)
            submittedfile = SubmittedFile(filename=filename, reference_file=reference_file, user_id=current_user.id,
                                          tab_absc=tab2text(steps), tab_hausdorff=tab2text(dst_list), tab_middle_accurracy=tab2text(middle_acc), tab_middle_completeness=tab2text(middle_comp), real_size=size, estimated_size=declared_size)
            db.session.add(submittedfile)
            db.session.commit()
            flash('Your file has been uploaded')
            if not current_user.best_submitted_file:
                current_user.best_submitted_file = submittedfile.id
                db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Wrong extension file')
            return redirect(url_for('upload_file'))
    return render_template('upload.html', form=form, users=get_all_users())


@app.route('/download')
def download():
    return render_template("download.html", models=app.config['AVAILABLE_MODELS'], users=get_all_users())


@app.route('/download_model/<model>')
def download_model(model):
    return send_file(os.path.join(app.config['OBJ_FOLDER'],app.config['AVAILABLE_MODELS'][model]['file']))
    # return send_from_directory(directory=app.config['OBJ_FOLDER'], filename=app.config['AVAILABLE_MODELS'][model]['file'],path='')


@app.route('/del_sub/<sub_file_id>')
def del_sub(sub_file_id):
    sub_file = SubmittedFile.query.filter_by(id=sub_file_id).first()
    del_sub_file(sub_file)
    flash('Your submission has been deleted')
    return redirect(url_for('user',username=current_user.username))


@app.route('/dlobja/<model>')
def dlobja(model):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'],model))
    # return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=model, as_attachment=True, path='')


@app.route('/stream/<model>')
def stream(model):
    return render_template('stream.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


def get_all_users():
    users = User.query.all()
    return users


def format_tabs(string_tab):
    str_data = string_tab.split(' ')
    float_tab = [float(strdat) for strdat in str_data]
    return float_tab
