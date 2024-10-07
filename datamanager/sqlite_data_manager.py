import dotenv
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import DeclarativeBase
from datamanager.data_manager import DataManagerInterface


class Base(DeclarativeBase):
    pass


class SQLiteDataManager(DataManagerInterface):

    omdb_key = dotenv.get_key(os.path.join(os.getcwd(), '.env'), 'OMDB_API')

    def __init__(self):
        self.db = SQLAlchemy(model_class=Base)
        # self.db = SQLAlchemy('storage/movies.sqlite')

    def get_all_users(self):
        return self.db.session.query(Users).all()

    def get_user(self, user_id):
        return self.db.session.query(Users).filter(Users.id == user_id).one()

    def get_user_movies(self, user_id):
        return self.db.session.query(Movies).join(UserMovies).filter(UserMovies.user_id == user_id).all()

    def add_user(self, user):
        self.db.session.add(Users(name=user))
        self.db.session.commit()
        return f'User {user} was added successfully.'

    def add_movie(self, title, director, year, rating):
        movie = Movies(
            title=title,
            director=director,
            year=year,
            rating=rating
        )
        self.db.session.add(movie)
        self.db.session.commit()
        return f'Movie "{title}" was added successfully.'

    def update_movie(self, movie_id, title, director, year, rating):
        the_movie = self.db.session.query(Movies).filter(Movies.id == movie_id).one()
        the_movie.title = title
        the_movie.director = director
        the_movie.year = year
        the_movie.rating = rating
        self.db.session.commit()
        return f'The movie "{title}" was update successfully.'

    def delete_movie(self, movie_id):
        the_movie = self.db.session.query(Movies).filter(Movies.id == movie_id).one()
        title = the_movie.title
        the_movie.delete()
        self.db.session.commit()
        return f'The movie "{title}" was deleted successfully.'


db = SQLiteDataManager().db


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
    movie_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('movies.id'), primary_key=True)
    user_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('users.id'), primary_key=True)

    def __repr__(self):
        return (f'user={db.session.query(self.Users).filter(self.Users.id == self.user_id).one().name} '
                f'movie={db.session.query(self.Movies).filter(self.Movies.id == self.movie_id).one().title}')
