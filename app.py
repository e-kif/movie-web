from flask import Flask, render_template, redirect, request
import os
from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
database_filename = os.path.join(os.getcwd(), 'storage', 'movies.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_filename}'

# with app.app_context():
#     db.create_all()

data = SQLiteDataManager()
data.db.init_app(app)


@app.route('/', methods=['GET'])
def home():
    return 'Welcome to the MovieWeb App!'


@app.route('/users', methods=['GET'])
def list_users():
    users = data.get_all_users()
    print(users)
    return render_template('users.html', users=users)


@app.route('/user/<int:user_id>', methods=['GET'])
def user(user_id):
    return f'list of movies for user with id {user_id}'


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        # TODO write the from
        return render_template('add_user.html')

    name = request.form.get('user')
    data.add_user(name)
    return redirect('/users?message=User was added successfully.', 302)


@app.route('/users/<int:user_id>/add_movie', methods=['GET'])
def add_movie(user_id):
    return f'adds a movie for user with id={user_id}'


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET'])
def update_movie(user_id, movie_id):
    return f'updates a movie with id {movie_id} for user # {user_id}'


@app.route('/users/<int:user>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    return f"deletes movie {movie_id} from user's {user_id} favorites"


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
