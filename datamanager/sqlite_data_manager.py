import dotenv
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from sqlalchemy.orm import DeclarativeBase
from datamanager.data_manager import DataManagerInterface


class Base(DeclarativeBase):
    pass


class SQLiteDataManager(DataManagerInterface):
    omdb_key = dotenv.get_key(os.path.join(os.getcwd(), '.env'), 'OMDB_API')
    omdb_url = 'https://www.omdbapi.com/?apikey=' + omdb_key

    def __init__(self):
        self.db = SQLAlchemy(model_class=Base)
        # self.db = SQLAlchemy('storage/movies.sqlite')

    def get_all_users(self):
        return self.db.session.query(Users).all()

    def get_user(self, user_id):
        return self.db.session.query(Users).filter(Users.id == user_id).one()

    def get_user_movies(self, user_id):
        return self.db.session.query(Movies).join(UserMovies).filter(UserMovies.user_id == user_id).all()

    def get_all_movies(self):
        return self.db.session.query(Movies).all()

    def add_user(self, user):
        self.db.session.add(Users(name=user))
        self.db.session.commit()
        return f'User {user} was added successfully.'

    def add_movie(self, user_id, title, year=''):
        movie_info = requests.get(f'{self.omdb_url}&t={title}&y={year}').json()
        if not year:
            year = movie_info['Year']
        movie = Movies(
            title=movie_info['Title'],
            director=movie_info['Director'],
            year=year,
            rating=movie_info['imdbRating']
        )
        self.db.session.add(movie)
        self.db.session.flush()
        user_movie = UserMovies(
            user_id=user_id,
            movie_id=movie.id
        )
        self.db.session.add(movie)
        self.db.session.add(user_movie)
        self.db.session.commit()
        return f'Movie "{movie_info["Title"]}" was added successfully.'

    def get_movie(self, movie_id):
        return self.db.session.query(Movies).filter(Movies.id == movie_id).one()

    def update_movie(self, movie_id, title, director, year, rating):
        the_movie = self.db.session.query(Movies).filter(Movies.id == movie_id).one()
        the_movie.title = title
        the_movie.director = director
        the_movie.year = year
        the_movie.rating = rating
        self.db.session.commit()
        return f'The movie "{title}" was update successfully.'

    def delete_movie(self, user_id, movie_id):
        self.db.session.query(UserMovies) \
            .filter(UserMovies.user_id == user_id) \
            .filter(UserMovies.movie_id == movie_id) \
            .delete()
        if not self.db.session.query(UserMovies).filter(UserMovies.movie_id == movie_id).count():
            the_movie = self.db.session.query(Movies).filter(Movies.id == movie_id)
            title = the_movie.one().title
            the_movie.delete()
        else:
            title = self.db.session.query(Movies.title).filter(Movies.id == movie_id).one()
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
