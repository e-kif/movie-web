from flask import Flask, render_template, redirect, jsonify
import os
from data.sqlite_data_manager import SQLiteDataManager, db

app = Flask(__name__)
database_file = os.path.join(os.getcwd(), 'data', 'movies.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_file}'
db.init_app(app)
# with app.app_context():
#     db.create_all()
data = SQLiteDataManager(database_file)


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
