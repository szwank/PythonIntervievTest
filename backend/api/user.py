import time

from protorpc import remote, messages, message_types

from backend import api, user
from backend.oauth2 import oauth2, Oauth2


class CreateRequest(messages.Message):
    email = messages.StringField(1, required=True)
    password = messages.StringField(2, required=True)

class TokenRequest(messages.Message):
    access_token = messages.StringField(1, required=True)
    refresh_token = messages.StringField(2, required=True)

class TokenResponse(messages.Message):
    access_token = messages.StringField(1)
    expires = messages.FloatField(2)
    refresh_token = messages.StringField(3)

class LoginRequest(messages.Message):
    email = messages.StringField(1)
    password = messages.StringField(2)

class EmailVerifiedResponse(messages.Message):
    email_verified = messages.BooleanField(1)

class MeResponse(messages.Message):
    id = messages.StringField(1)
    email = messages.StringField(2)
    email_verified = messages.BooleanField(3)
    firstname = messages.StringField(4)
    lastname = messages.StringField(5)

class UpdatePasswordRequest(messages.Message):
    current_password = messages.StringField(1, required=True)
    password = messages.StringField(2, required=True)

class UpdateEmailRequest(messages.Message):
    current_password = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)

class UpdateRequest(messages.Message):
    email = messages.StringField(1)
    firstname = messages.StringField(2)
    lastname = messages.StringField(3)

class VerifyEmailRequest(messages.Message):
    code = messages.StringField(1, required=True)

class RecoverPasswordRequest(messages.Message):
    code = messages.StringField(1, required=True)
    password = messages.StringField(2, required=True)

class RecoverPasswordSendLinkRequest(messages.Message):
    email = messages.StringField(1, required=True)


@api.endpoint(path="user", title="User API")
class User(remote.Service):
    @remote.method(CreateRequest, TokenResponse)
    def create(self, request):
        u = user.User.create(email=request.email, password=request.password)
        session = Oauth2.create(u.key)

        return TokenResponse(
            access_token=session.access_token.token,
            expires=time.mktime(session.access_token.expires.timetuple()),
            refresh_token=session.refresh_token.token
        )

    @remote.method(TokenRequest, TokenResponse)
    def token(self, request):
        session = Oauth2.renew(request.access_token, request.refresh_token)

        return TokenResponse(
            access_token=session.access_token.token,
            expires=time.mktime(session.access_token.expires.timetuple()),
            refresh_token=session.refresh_token.token
        )

    @remote.method(LoginRequest, TokenResponse)
    def login(self, request):
        user_key = user.User.login(request.email, request.password).key
        session = Oauth2.create(user_key)

        return TokenResponse(
            access_token=session.access_token.token,
            expires=time.mktime(session.access_token.expires.timetuple()),
            refresh_token=session.refresh_token.token
        )

    @oauth2.required()
    @remote.method(message_types.VoidMessage, message_types.VoidMessage)
    def logout(self, request):
        self.session.revoke()
        return message_types.VoidMessage()

    @oauth2.required()
    @remote.method(message_types.VoidMessage, EmailVerifiedResponse)
    def email_verified(self, request):
        return EmailVerifiedResponse(
            email_verified=self.session.user.email_verified
        )

    @oauth2.required()
    @remote.method(message_types.VoidMessage, MeResponse)
    def me(self, request):
        u = self.session.user
        return MeResponse(
            id=u.id,
            email=u.email,
            email_verified=u.email_verified,
            firstname=u.firstname,
            lastname=u.lastname
        )

    @oauth2.required()
    @remote.method(UpdatePasswordRequest, message_types.VoidMessage)
    def update_password(self, request):
        self.session.user.update_password(current_password=request.current_password, password=request.password)
        return message_types.VoidMessage()

    @oauth2.required()
    @remote.method(UpdateEmailRequest, message_types.VoidMessage)
    def update_email(self, request):
        self.session.user.update_email(current_password=request.current_password, email=request.email)
        return message_types.VoidMessage()

    @oauth2.required()
    @remote.method(UpdateRequest, message_types.VoidMessage)
    def update(self, request):
        self.session.user.update(**api.message_to_dict(request))
        return message_types.VoidMessage()

    @oauth2.required()
    @remote.method(VerifyEmailRequest, message_types.VoidMessage)
    def verify_email(self, request):
        self.session.user.verify_email(request.code)
        return message_types.VoidMessage()

    @oauth2.required()
    @remote.method(message_types.VoidMessage, message_types.VoidMessage)
    def verify_email_send_code(self, request):
        self.session.user.verify_email_send_code()
        return message_types.VoidMessage()

    @remote.method(RecoverPasswordRequest, message_types.VoidMessage)
    def recover_password(self, request):
        user.User.recover_password(request.code, request.password)
        return message_types.VoidMessage()

    @remote.method(RecoverPasswordSendLinkRequest, message_types.VoidMessage)
    def recover_password_send_link(self, request):
        user.User.recover_password_send_link(request.email)
        return message_types.VoidMessage()
