class UserLogin():
    def fromDB(self, user_id, db):
        self.__user = {'id': 1, 'name': "Ivan"} # from DB
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return str(self.__user['id'])