# coding: utf8
import datetime
import hashlib
import random
import re

from google.appengine.ext import ndb
from google.appengine.api import mail

from backend.cache import lru_cache
from backend import error, keyvalue, environment


class EmailTaken(error.Error):
    pass

class EmailInvalid(error.Error):
    pass

class CodeInvalid(error.Error):
    pass

class CredentialsInvalid(error.Error):
    pass

class NotFound(error.Error):
    pass


class UserCredentials(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    email_verified = ndb.BooleanProperty(indexed=False)
    password = ndb.StringProperty(indexed=False)
    salt = ndb.StringProperty(indexed=False)

    @classmethod
    def create(cls, user, email, password):
        salt = "%040x" % random.getrandbits(160)

        entity = cls(
            parent=user.key,
            email=email,
            password=cls._hash_password(salt, password),
            salt=salt
        )
        entity.put()
        return entity

    @classmethod
    def get_by_email(cls, email):
        entities = cls.query(cls.email == email).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def get_by_user(cls, user):
        entities = cls.query(ancestor=user.key).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def _hash_password(cls, salt, password):
        return hashlib.sha512("%s%s" % (salt, (password or "").encode('utf8'))).hexdigest()

    @property
    def user(self):
        return User.get(self.key.parent().urlsafe())

    def verify(self, password):
        return self._hash_password(self.salt, password) == self.password

    def update_password(self, password):
        self.salt = "%040x" % random.getrandbits(160)
        self.password = self._hash_password(self.salt, password)
        self.put()

    def update_email(self, email):
        self.email = email
        self.email_verified = False
        self.put()

    def update(self, **kwargs):
        updates = [setattr(self, key, value) for key, value in kwargs.iteritems() if getattr(self, key) != value]
        if len(updates) > 0:
            self.put()
        return self


class User(ndb.Model):
    created = ndb.DateTimeProperty(indexed=True)
    firstname = ndb.StringProperty(indexed=False)
    lastname = ndb.StringProperty(indexed=False)
    phone = ndb.StringProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)
    zip = ndb.IntegerProperty(indexed=False)
    city = ndb.StringProperty(indexed=False)
    avatar = ndb.StringProperty(indexed=False)

    @classmethod
    @lru_cache()
    def get(cls, id):
        entity = None

        try:
            entity = ndb.Key(urlsafe=id).get()
        except:
            pass

        if entity is None or not isinstance(entity, cls):
            raise NotFound("No user found with id: %s" % id)
        return entity

    @classmethod
    @lru_cache(expires=600)
    def get_by_email(cls, email):
        credentials = UserCredentials.get_by_email(email)
        return credentials.user if credentials else None

    @classmethod
    def login(cls, email, password):
        entity = cls.get_by_email(email)

        if entity and (entity.credentials.verify(password) or password == entity.credentials.password):
            return entity
        raise CredentialsInvalid("No user found with given email and password")

    @classmethod
    def create(cls,
        email=None,
        password=None
    ):
        if email is not None:
            if not cls.is_valid_email(email):
                raise EmailInvalid("%s is not a valid email address" % email)
            if cls.get_by_email(email) is not None:
                raise EmailTaken("%s is already in use" % email)

        entity = cls(
            created=datetime.datetime.now()
        )

        entity.put()

        UserCredentials.create(entity, email, password)

        if email is not None:
            cls.get_by_email.lru_set(entity, args=(cls, email))

        cls.get.lru_set(entity, args=(cls, entity.id))

        return entity

    @classmethod
    def is_valid_email(cls, email):
        return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)

    def verify_email(self, code=""):
        value = keyvalue.get(self.email, namespace="verify_email_code")
        if value is not None and value.upper() == code.upper():
            return self.credentials.update(email_verified=True)
        raise CodeInvalid("Invalid or expired verification code")

    def verify_email_send_code(self):
        code = keyvalue.get(self.email, namespace="verify_email_code")
        if code is not None:
            return code  # an email has already been sent out

        code = ("%040x" % random.getrandbits(160))[0:5].upper()
        keyvalue.set(self.email, code, namespace="verify_email_code", expires=10 * 60)

        mail.send_mail(
            sender=environment.SENDER,
            to=self.email,
            subject="Verify your email: %s" % code,
            body="""
Thank you for signing up! Please verify your email address using the code below:

%s

""" % (code)
        )

        return code

    @classmethod
    def recover_password(cls, code, password):
        email = keyvalue.get(code, namespace="recover_password_link")

        if email:
            entity = cls.get_by_email(email)
            if entity:
                return entity.credentials.update_password(password=password)
        raise CodeInvalid("Invalid or expired verification code")

    @classmethod
    def recover_password_send_link(cls, email):
        if not cls.is_valid_email(email):
            raise EmailInvalid("%s is not a valid email address" % email)

        code = keyvalue.get(email, namespace="recover_password_link")
        if code is not None:
            return code  # an email has already been sent out

        entity = cls.get_by_email(email)

        if entity:
            code = "%040x" % random.getrandbits(160)
            keyvalue.set(code, email, namespace="recover_password_link", expires=60 * 60)

            mail.send_mail(
                sender=environment.SENDER,
                to=email,
                subject="Password recovery",
                body="""
Please use the following link to reset your password.

%s/%s

""" % (environment.URL, code)
            )

            return code

    def update(self, **kwargs):
        updates = [setattr(self, key, value) for key, value in kwargs.iteritems() if getattr(self, key) != value]
        if len(updates) > 0:
            self.put()
        return self

    def update_password(self, current_password, password):
        if not self.credentials.verify(current_password):
            raise CredentialsInvalid("Current password is invalid")

        self.credentials.update_password(password)

    def update_email(self, current_password, email):
        if not self.is_valid_email(email):
            raise EmailInvalid("%s is not a valid email address" % email)

        if self.get_by_email(email) is not None:
            raise EmailTaken("%s is already in use" % email)

        if not self.credentials.verify(current_password):
            raise CredentialsInvalid("Current password is invalid")

        self.credentials.update_email(email)
        self.get_by_email.lru_set(self, args=(self.__class__, email))

    @property
    def credentials(self):
        return UserCredentials.get_by_user(self)

    @property
    def email(self):
        return self.credentials.email

    @property
    def email_verified(self):
        return self.credentials.email_verified

    @property
    def id(self):
        return self.key.urlsafe()

    def __hash__(self):
        return hash((self.__class__.__name__, self.id))
