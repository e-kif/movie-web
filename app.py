from flask import Flask, render_template, redirect, request
import os
import sqlalchemy
from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
database_filename = os.path.join(os.getcwd(), 'storage', 'movies.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_filename}'

data = SQLiteDataManager()
data.db.init_app(app)


# with app.app_context():
#     data.db.create_all()


@app.route('/', methods=['GET'])
def home():
    data.other_users_movies(3)
    return 'Welcome to the MovieWeb App!'


@app.route('/users', methods=['GET'])
def list_users():
    users = data.get_all_users()
    message = request.args.get('message', '')
    return render_template('users.html', users=users, message=message)


@app.route('/user/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    try:
        username = data.get_user(user_id)
    except sqlalchemy.exc.NoResultFound:
        return redirect('/404')
    movies = data.get_user_movies(user_id)
    message = request.args.get('message', '')
    return render_template('user-movies.html', user=username, movies=movies, message=message)


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    if request.method == 'POST':
        name = request.form.get('user')
        data.add_user(name)
        return redirect(f'/users?message=User {name} was added successfully.', 302)


@app.route('/users/<int:user_id>/add-movie', methods=['GET', 'POST'])
def add_movie(user_id):
    username = data.get_user(user_id)
    if request.method == 'GET':
        message = request.args.get('message', '')
        other_users_movies = data.other_users_movies(user_id)
        return render_template('add-movie.html',
                               user=username,
                               message=message,
                               movies=other_users_movies)
    if request.method == 'POST':
        title = request.form.get('title').strip()
        if not title:
            return redirect(f'/users/{user_id}/add-movie?message=Movie title should not be empty')
        year = request.form.get('year')
        success, message = data.add_movie(user_id, title, year)
        if not success:
            return redirect(f'/users/{user_id}/add-movie?message={message}')
        return redirect(f'/user/{user_id}?message={message}')


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == 'GET':
        try:
            movie = data.get_movie(movie_id)
        except sqlalchemy.exc.NoResultFound:
            return redirect('/404')
        return render_template('update-movie.html', movie=movie, user_id=user_id)
    if request.method == 'POST':
        title = request.form.get('title')
        director = request.form.get('director')
        year = request.form.get('year')
        rating = request.form.get('rating')
        message = data.update_movie(movie_id, title, director, year, rating)
        return redirect(f'/user/{user_id}?message={message}')


@app.route('/users/<int:user_id>/delete-user', methods=['GET'])
def delete_user(user_id):
    username = data.delete_user(user_id)
    message = f'User {username} was deleted successfully.'
    return redirect(f'/users?message={message}')


@app.route('/users/<int:user_id>/update-user', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'GET':
        user = data.get_user(user_id)
        message = request.args.get('message', '')
        return render_template('update-user.html', user=user, message=message)
    if request.method == 'POST':
        username = request.form.get('username').strip()
        if not username:
            return redirect(f'/users/{user_id}/update-user?message=Username should not be empty.')
        message = data.update_user(user_id, username)
        return redirect(f'/users?message={message}')


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    message = data.delete_movie(user_id, movie_id)
    return redirect(f'/user/{user_id}?message={message}')


@app.route('/users/<int:user_id>/add-other-movie/<int:movie_id>', methods=['GET'])
def add_other_user_movie(user_id, movie_id):
    message = data.add_other_user_movie(user_id, movie_id)
    return redirect(f'/users/{user_id}/add-movie?message={message}')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
