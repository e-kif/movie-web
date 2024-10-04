from flask_sqlalchemy import SQLAlchemy
from data_manager import DataManagerInterface

db = SQLAlchemy()


class SQLiteDataManager(DataManagerInterface):

    def __init__(self, db_file_name):
        self.db = SQLAlchemy(db_file_name)

    def get_all_users(self):
        return self.db.session.query(Users).all

    def get_user_movies(self, user_id):
        pass


class Users(db.Model):

    id: db.Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    name: db.Mapped[str] = db.mapped_column()

    def __repr__(self):
        return f'Users(id={self.id}, name={self.name})'


class Movies(db.Model):

    id: db.Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    title: db.Mapped[str] = db.mapped_column()
    director: db.Mapped[str] = db.mapped_column()
    year: db.Mapped[int] = db.mapped_column()
    rating: db.Mapped[float] = db.mapped_column()

    def __repr__(self):
        return f'Movies(id={self.id}, title={self.title}, year={self.year})'

    def __srt__(self):
        return f'{self.id}. {self.title} ({self.year})'


class UserMovies(db.Model):

    movie_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('movies.id'))
    user_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('users.id'))

    def __repr__(self):
        return (f'user={db.session.query(Users).filter(Users.id == self.user_id).one().name} '
                f'movie={db.session.query(Movies).filter(Movies.id == self.movie_id).one().title}')
