from kino import app, db, manager
from flask import  render_template, request, flash, redirect, url_for, current_app, send_from_directory
from flask_login import login_user, login_required
from kino.models import Title, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


@login_required
@manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))  # Приведение к int

@login_required
@app.route('/register', methods = ['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    if request.method == 'POST':
        if not (login or password):
            flash(message='Ошибка, неправильные поля')
        else:
            try:
                hash_pwd = generate_password_hash(password)
                new_user = Admin(login= login, password= hash_pwd)
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(message=f'Ошибка при сохранении в базу данных: {e}')
                return redirect(url_for('register'))
            flash(message='Успех')
            return redirect(url_for('authorization'))
    return render_template('register.html')


@app.route('/')
def index():
    return redirect(url_for('authorization'))

@app.route('/authorization', methods=['GET','POST'])
def authorization():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        print(f"Ищем пользователя с логином: {login}")  # Отладка
        user = db.session.execute(
            db.select(Admin).filter_by(login=login)
        ).scalar_one_or_none()
        print(f"Пользователь найден: {user}")
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main'))
        else:
            flash('Ошибка: логин или пароль неверны')
    else:
        flash('Ошибка: заполните оба поля')
    return render_template('authorization.html')


@login_required
@app.route('/main')
def main():
    data = Title.query.all()
    return render_template('index.html', data=data)

@login_required
@app.route('/create_post', methods = ['GET', 'POST'])
def create_post():
    user = request.form.get('user')
    movie = request.form.get('movie')
    text = request.form.get('text')
    media_file = request.files.get('media')

    if request.method == 'POST':
        if user and movie and text:
            if media_file and media_file.filename != '':
                # Генерируем безопасное имя файла
                filename = secure_filename(media_file.filename)
                # Определяем директорию для сохранения файла
                upload_folder = 'static/saved_images'
                file_path = os.path.join(upload_folder, filename)
                # Сохраняем файл
                media_file.save(os.path.join(current_app.root_path, file_path))
                
                # Сохраняем относительный путь без 'static/'
                relative_file_path = os.path.join('saved_images', filename)
            try:
                new_title = Title(user = user, movie = movie, text = text, img_path = relative_file_path )
                db.session.add(new_title)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(message='ERROR')
            return redirect(url_for('main'))
        else:
            flash(message='Not valid data')
        

    return render_template('create_title.html')

@login_required
@app.route('/media/<filename>')
def media(filename):
    upload_folder = 'static/saved_images'
    return send_from_directory(upload_folder, filename)


@login_required
@app.route('/delete_post/<int:post_id>', methods=['GET','POST'])
def delete_post(post_id):
    post = Title.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('main'))