from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """Defines abstract class for Data Manager Interface"""

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_user(self, user):
        pass

    @abstractmethod
    def delete_user(self, user_id):
        pass

    @abstractmethod
    def update_user(self, user_id):
        pass

    @abstractmethod
    def add_movie(self, title, director, year, rating):
        pass

    @abstractmethod
    def update_movie(self, movie_id, title, director, year, rating):
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        pass
