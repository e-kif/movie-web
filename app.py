from flask import Flask, render_template, redirect, request
import os
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
    return 'Welcome to the MovieWeb App!'


@app.route('/users', methods=['GET'])
def list_users():
    users = data.get_all_users()
    return render_template('users.html', users=users)


@app.route('/user/<int:user_id>', methods=['GET'])
def user(user_id):
    username = data.get_user(user_id)
    movies = data.get_user_movies(user_id)
    return render_template('user-movies.html', user=username, movies=movies)


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    if request.method == 'POST':
        name = request.form.get('user')
        data.add_user(name)
        return redirect('/users?message=User was added successfully.', 302)


@app.route('/users/<int:user_id>/add-movie', methods=['GET', 'POST'])
def add_movie(user_id):
    username = data.get_user(user_id)
    if request.method == 'GET':
        return render_template('add-movie.html', user=username)
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        message = data.add_movie(user_id, title, year)
        return redirect(f'/user/{user_id}?message={message}')


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == 'GET':
        movie = data.get_movie(movie_id)
        return render_template('update-movie.html', movie=movie, user_id=user_id)
    if request.method == 'POST':
        title = request.form.get('title')
        director = request.form.get('director')
        year = request.form.get('year')
        rating = request.form.get('rating')
        message = data.update_movie(movie_id, title, director, year, rating)
        return redirect(f'/user/{user_id}?message={message}')


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    message = data.delete_movie(user_id, movie_id)
    return redirect(f'/user/{user_id}?message={message}')


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
