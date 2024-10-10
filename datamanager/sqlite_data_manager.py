import dotenv
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import sqlalchemy
from datamanager.data_manager import DataManagerInterface


class Base(sqlalchemy.orm.DeclarativeBase):
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

    def delete_user(self, user_id):
        user = self.db.session.query(Users).filter(Users.id == user_id)
        username = user.one().name
        user.delete()
        self.db.session.query(UserMovies).filter(UserMovies.user_id == user_id).delete()
        delete_movies_ids = [id[0] for id in self.db.session.query(Movies.id).join(UserMovies, isouter=True) \
            .filter(UserMovies.user_id.is_(None)).all()]
        self.db.session.query(Movies).filter(Movies.id.in_(delete_movies_ids)).delete()
        self.db.session.commit()
        return username

    def update_user(self, user_id, username):
        the_user = self.db.session.query(Users).filter(Users.id == user_id).one()
        if not the_user:
            return f'There is no user with id {user_id}.'
        the_user.name = username
        self.db.session.commit()
        return f'User {the_user.name} was updated successfully.'

    def get_user_movies(self, user_id):
        return self.db.session.query(Movies).join(UserMovies).filter(UserMovies.user_id == user_id).all()

    def get_all_movies(self):
        return self.db.session.query(Movies).all()

    def add_user(self, user):
        self.db.session.add(Users(name=user))
        self.db.session.commit()
        return f'User {user} was added successfully.'

    def add_movie(self, user_id, title, year=''):
        try:
            movie_info = requests.get(f'{self.omdb_url}&t={title}&y={year}').json()
        except requests.exceptions.ConnectionError:
            return False, f'Error: movie "{title}" was not added. Check your internet connection and try again.'
        if movie_info['Response'] == 'False':
            return False, f'Error: movie "{title}" was not added. {movie_info["Error"]}'
        if not year:
            year = movie_info['Year']
        try:
            movie_exist = self.db.session.query(Movies) \
                .filter(Movies.title == movie_info['Title'] and Movies.year == movie_info['Year']).one()
        except sqlalchemy.exc.NoResultFound:
            movie = Movies(
                title=movie_info['Title'],
                director=movie_info['Director'],
                year=year,
                rating=None if movie_info['imdbRating'] == 'N/A' else movie_info['imdbRating']
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
            return True, f'Movie "{movie_info["Title"]}" was added successfully.'
        if movie_exist:
            if (self.db.session.query(UserMovies).filter(UserMovies.user_id == user_id)
                    .filter(UserMovies.movie_id == movie_exist.id).all()):
                return False, f'Movie "{movie_exist.title}" is already in your movies.'
            user_movie = UserMovies(
                user_id=user_id,
                movie_id=movie_exist.id
            )
            self.db.session.add(user_movie)
            self.db.session.commit()
            return True, f'Movie "{movie_exist.title}" was added successfully.'

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

    def other_users_movies(self, user_id):
        user_movies_ids = self.db.session.query(UserMovies.movie_id).filter(UserMovies.user_id == user_id).subquery()
        return self.db.session.query(Movies).filter(Movies.id.not_in(user_movies_ids)).all()

    def add_other_user_movie(self, user_id, movie_id):
        title = self.db.session.query(Movies.title).filter(Movies.id == movie_id).one()[0]
        add_move = UserMovies(
            user_id=user_id,
            movie_id=movie_id
        )
        self.db.session.add(add_move)
        self.db.session.commit()
        print(title)
        return f'Movie "{title}" was added successfully.'


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
    rating: db.Mapped[float] = db.mapped_column(nullable=True)

    def __repr__(self):
        return f'Movies(id={self.id}, title={self.title}, year={self.year})'

    def __srt__(self):
        return f'{self.id}. {self.title} ({self.year})'


class UserMovies(db.Model):
    movie_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('movies.id'), primary_key=True)
    user_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('users.id'), primary_key=True)

    def __repr__(self):
        return (f'user_id={self.user_id} '
                f'movie_id={self.movie_id}')
