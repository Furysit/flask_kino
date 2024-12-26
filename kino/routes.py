from kino import app, db, manager
from flask import  render_template, request, flash, redirect, url_for, current_app, send_from_directory, session
from flask_login import login_user, login_required
from kino.models import Title, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from functools import wraps


@login_required
@manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))  # Приведение к int

@login_required
@app.route('/register', methods = ['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    role = request.form.get('role')
    if request.method == 'POST':
        if not (login or password):
            flash(message='Ошибка, неправильные поля')
        else:
            try:
                hash_pwd = generate_password_hash(password)
                new_user = Admin(login= login, password= hash_pwd, role = role)
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




@app.route('/admin')

def admin_panel():
    # Отображение всех постов, которые может удалить админ
    if session.get('role') != 'admin':  # или проверка через текущего пользователя
        return redirect(url_for('main'))  # Или на другую страницу, если не админ
    data = Title.query.all()
    return render_template('admin.html', data = data)



@app.route('/delete_post/<int:post_id>', methods=['POST'])

def delete_post(post_id):
    post = Title.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Пост успешно удалён.')
    return redirect(url_for('admin_panel'))


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
            session['role'] = user.role
            return redirect(url_for('main'))
        else:
            flash('Ошибка: логин или пароль неверны')
    else:
        flash('Ошибка: заполните оба поля')
    return render_template('authorization.html')


@login_required
@app.route('/main')
def main():
    page = request.args.get('page', 1, type=int)  # Текущая страница, по умолчанию 1
    per_page = 10  # Количество элементов на странице
    pagination = Title.query.paginate(page=page, per_page=per_page)  # Пагинация
    return render_template('index.html', data=pagination.items, pagination=pagination)

@login_required
@app.route('/create_post', methods = ['GET', 'POST'])
def create_post():
    user = request.form.get('user')
    movie = request.form.get('movie')
    text = request.form.get('text')
    media_file = request.files.get('media')
    evan_rating = int(request.form.get('evan_rating', 0))
    fury_rating = int(request.form.get('fury_rating', 0))

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
                new_title = Title(user = user, movie = movie, text = text, img_path = relative_file_path, evan_rating = evan_rating, fury_rating=fury_rating)
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


@app.route('/movies', methods=['GET'])
def movies():
    page = request.args.get('page', 1, type=int)  # Получаем текущую страницу из запроса
    per_page = 10  # Количество фильмов на страницу
    pagination = Title.query.paginate(page=page, per_page=per_page)  # Пагинация
    
    return render_template('index.html', pagination=pagination)