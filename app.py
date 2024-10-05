from flask import Flask, render_template, redirect, jsonify, request
import os
from data.sqlite_data_manager import SQLiteDataManager, db, Movies, Users, UserMovies

app = Flask(__name__)
database_filename = os.path.join(os.getcwd(), 'data', 'movies.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_filename}'
db.init_app(app)

# with app.app_context():
#     db.create_all()

data = SQLiteDataManager(database_filename)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', users=data.get_all_users())


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')

    name = request.form.get('user')
    data.add_user(name)
    return redirect('/?message=User was added successfully.', 302)


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
