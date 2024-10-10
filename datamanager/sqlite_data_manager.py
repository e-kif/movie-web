import dotenv
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import sqlalchemy
from datamanager.data_manager import DataManagerInterface


class Base(sqlalchemy.orm.DeclarativeBase):
    """Creates Base class for initializing SQLAlchemy object"""
    pass


class SQLiteDataManager(DataManagerInterface):
    """Defines data manager class for interaction with sqlite database"""

    omdb_key = dotenv.get_key(os.path.join(os.getcwd(), '.env'), 'OMDB_API')
    omdb_url = 'https://www.omdbapi.com/?apikey=' + omdb_key

    def __init__(self):
        """Instantiates the object"""
        self.db = SQLAlchemy(model_class=Base)
        # self.db = SQLAlchemy('storage/movies.sqlite')

    def get_all_users(self):
        """Returns all users registered in a database"""
        return self.db.session.query(Users).all()

    def get_user(self, user_id):
        """Returns one user from a database by his/her id"""
        return self.db.session.query(Users).filter(Users.id == user_id).one()

    def delete_user(self, user_id):
        """Deletes a user from a database. Checks if there are orphaned movies left in database after user deletion.
        If so, removes these movies from database.
        """
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
        """Updates username or returns error message if user not found"""
        the_user = self.db.session.query(Users).filter(Users.id == user_id).one()
        if not the_user:
            return f'There is no user with id {user_id}.'
        the_user.name = username
        self.db.session.commit()
        return f'User {the_user.name} was updated successfully.'

    def get_user_movies(self, user_id):
        """Returns movies, added by one user"""
        return self.db.session.query(Movies).join(UserMovies).filter(UserMovies.user_id == user_id).all()

    def get_all_movies(self):
        """Returns all movies from a database"""
        return self.db.session.query(Movies).all()

    def add_user(self, user):
        """Adds a new user to a database"""
        self.db.session.add(Users(name=user))
        self.db.session.commit()
        return f'User {user} was added successfully.'

    def add_movie(self, user_id, title, year=''):
        """Checks if the movie is already in a database, adds movie for user or returns error message"""
        try:
            movie_info = requests.get(f'{self.omdb_url}&t={title}&y={year}').json()
        except requests.exceptions.ConnectionError:
            return False, f'Error: movie "{title}" was not added. Check your internet connection and try again.'
        if movie_info['Response'] == 'False':
            return False, f'Error: movie "{title}" was not added. {movie_info["Error"]}'
        if not year:
            year = movie_info['Year']
        try:  # check if movie already in a database
            movie_exist = self.db.session.query(Movies) \
                .filter(Movies.title == movie_info['Title']) \
                .filter(Movies.year == movie_info['Year']).one()
        except sqlalchemy.exc.NoResultFound:  # if movie not in a database adds it
            movie = Movies(
                title=movie_info['Title'],
                director=movie_info['Director'],
                year=year,
                rating=None if movie_info['imdbRating'] == 'N/A' else movie_info['imdbRating'],
                poster=movie_info['Poster'],
                plot=movie_info['Plot'],
                genre=movie_info['Genre'],
                url=f'https://imdb.com/title/{movie_info["imdbID"]}',
                country=movie_info['Country']
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
        """Returns movie by its id"""
        return self.db.session.query(Movies).filter(Movies.id == movie_id).one()

    def update_movie(self, movie_id, title, director, year, rating):
        """Updates movie info in a database"""
        the_movie = self.db.session.query(Movies).filter(Movies.id == movie_id).one()
        the_movie.title = title
        the_movie.director = director
        the_movie.year = year
        the_movie.rating = rating
        self.db.session.commit()
        return f'The movie "{title}" was update successfully.'

    def delete_movie(self, user_id, movie_id):
        """Deletes connection between user and movie (if this movie was also added by another user)
        or also deletes movie from the database
        """
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
        """Returns all movies except for movies of a user with user_id"""
        user_movies_ids = self.db.session.query(UserMovies.movie_id).filter(UserMovies.user_id == user_id).subquery()
        return self.db.session.query(Movies).filter(Movies.id.not_in(user_movies_ids)).all()

    def add_other_user_movie(self, user_id, movie_id):
        """Adds movie a movie that was already added by another user to current user's collection"""
        if self.db.session.query(Users).get(user_id):
            if self.db.session.query(Movies).get(movie_id):
                title = self.db.session.query(Movies.title).filter(Movies.id == movie_id).one()[0]
                add_move = UserMovies(
                    user_id=user_id,
                    movie_id=movie_id
                )
                self.db.session.add(add_move)
                self.db.session.commit()
                return True, f'Movie "{title}" was added successfully.'
            return False, f'Movie with id {movie_id} does not exist.'
        return False, f'User with id {user_id} does not exist.'

    def get_last_users(self, number):
        """Returns a list of last registered users"""
        return self.db.session.query(Users).order_by(Users.id.desc()).limit(number).all()

    def get_last_movies(self, number):
        """Returns a list of last added movies, limited by number"""
        return self.db.session.query(Movies).order_by(Movies.id.desc()).limit(number).all()


db = SQLiteDataManager().db


class Users(db.Model):
    """Model for database's users table"""

    id: db.Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    name: db.Mapped[str] = db.mapped_column()

    def __repr__(self):
        """Representation of Users object class"""
        return f'Users(id={self.id}, name={self.name})'


class Movies(db.Model):
    """Model for database's movies table"""

    id: db.Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    title: db.Mapped[str] = db.mapped_column()
    director: db.Mapped[str] = db.mapped_column()
    year: db.Mapped[int] = db.mapped_column()
    rating: db.Mapped[float] = db.mapped_column(nullable=True)
    poster: db.Mapped[str] = db.mapped_column(nullable=True)
    plot: db.Mapped[str] = db.mapped_column(nullable=True)
    url: db.Mapped[str] = db.mapped_column()
    genre: db.Mapped[str] = db.mapped_column()
    country: db.Mapped[str] = db.mapped_column()

    def __repr__(self):
        """Representation of Movies object class"""
        return f'Movies(id={self.id}, title={self.title}, year={self.year})'

    def __srt__(self):
        """Representation of Movies object class for print statements"""
        return f'{self.id}. {self.title} ({self.year})'


class UserMovies(db.Model):
    """Model for database's user_movies table"""

    movie_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('movies.id'), primary_key=True)
    user_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('users.id'), primary_key=True)

    def __repr__(self):
        """Representation of UserMovies object class"""
        return f'user_id={self.user_id}, movie_id={self.movie_id}'
