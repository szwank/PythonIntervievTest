# coding: utf8
from backend import keyvalue, test, user, cache


class Testuser(test.TestCase):

    def test_create(self):
        obj = user.User.create(email="test@gmail.com", password="test")
        self.assertEqual(obj, user.User.get(obj.id))
        self.assertTrue(obj.email == "test@gmail.com")
        self.assertTrue(obj.credentials.password != "test")
        self.assertRaises(user.EmailInvalid, lambda: user.User.create(email="test@", password="test"))
        user.User.create(email="test2@gmail.com", password=u"åäö")

    def test_login(self):
        obj = user.User.create(email="test@gmail.com", password="test")
        self.assertRaises(user.CredentialsInvalid, lambda: user.User.login("test@gmail.com", "wrong_password"))
        self.assertEqual(obj, user.User.login("test@gmail.com", "test"))
        self.assertEqual(obj, user.User.login("test@gmail.com", u"test"))
        self.assertEqual(obj, user.User.login("test@gmail.com", obj.credentials.password))

    def test_email(self):
        self.policy.SetProbability(1)

        user.User.create(email="test@gmail.com", password="test")
        self.assertRaises(user.EmailTaken, lambda: user.User.create(email="test@gmail.com", password="test"))

        user.User.create(email="test2@gmail.com", password="test")
        cache.lru_clear_all()
        self.assertRaises(user.EmailTaken, lambda: user.User.create(email="test2@gmail.com", password="test"))

    def test_update_password(self):
        obj = user.User.create("test@gmail.com", "test")
        obj.update_password(current_password="test", password="test2")
        self.assertEqual(obj, user.User.login("test@gmail.com", "test2"))

    def test_update_email(self):
        obj = user.User.create("test@gmail.com", "test")
        obj.update_email(current_password="test", email="test2@gmail.com")
        self.assertEqual(obj, user.User.login("test2@gmail.com", "test"))

    def test_verify_email(self):
        obj = user.User.create(email="test@gmail.com", password="test")
        self.assertFalse(obj.email_verified)
        code = obj.verify_email_send_code()
        messages = self.mail_stub.get_sent_messages(to="test@gmail.com")
        self.assertEqual(1, len(messages))
        obj.verify_email(code)
        self.assertTrue(obj.email_verified)

    def test_recover_password(self):
        obj = user.User.create("test@gmail.com", "test")
        code = user.User.recover_password_send_link("test@gmail.com")
        messages = self.mail_stub.get_sent_messages(to="test@gmail.com")
        self.assertEqual(1, len(messages))
        user.User.recover_password(code, "test2")
        self.assertEqual(obj, user.User.login("test@gmail.com", "test2"))


class TestUserApi(test.TestCase):
    def test_login(self):
        resp = self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        self.assertEqual(resp.get("error"), None)
        resp = self.api_mock.post("/api/user.me")
        self.assertEqual(resp.get("email"), "test@gmail.com")

    def test_logout(self):
        resp = self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        self.assertEqual(resp.get("error"), None)
        resp = self.api_mock.post("/api/user.me")
        self.assertEqual(resp.get("email"), "test@gmail.com")
        resp = self.api_mock.post("/api/user.logout")
        self.assertEqual(resp.get("error"), None)
        resp = self.api_mock.post("/api/user.me")
        self.assertTrue(resp.get("error"))

    def test_token(self):
        session = self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        self.assertEqual(session.get("error"), None)

        resp = self.api_mock.post("/api/user.token", dict(access_token=session.get("access_token"), refresh_token=session.get("refresh_token")))
        self.assertEqual(resp.get("error"), None)
        self.assertTrue(resp.get("access_token") != session.get("access_token"))
        self.assertTrue(resp.get("refresh_token") != session.get("refresh_token"))

        # try to renew an already used refreshtoken
        resp = self.api_mock.post("/api/user.token", dict(access_token=session.get("access_token"), refresh_token=session.get("refresh_token")))
        self.assertTrue(resp.get("error"))

    def test_update_password(self):
        self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        resp = self.api_mock.post("/api/user.update_password", dict(current_password="test", password="test2"))
        self.assertEqual(resp.get("error"), None)
        resp = self.api_mock.post("/api/user.login", dict(email="test@gmail.com", password="test2"))
        self.assertEqual(resp.get("error"), None)

    def test_update_email(self):
        self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        resp = self.api_mock.post("/api/user.update_email", dict(current_password="test", email="test2@gmail.com"))
        self.assertEqual(resp.get("error"), None)
        resp = self.api_mock.post("/api/user.login", dict(email="test2@gmail.com", password="test"))
        self.assertEqual(resp.get("error"), None)

    def test_verify_email(self):
        self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        resp = self.api_mock.post("/api/user.verify_email_send_code")
        self.assertEqual(resp.get("error"), None)
        code = keyvalue.get("test@gmail.com", namespace="verify_email_code")
        messages = self.mail_stub.get_sent_messages(to="test@gmail.com")
        self.assertEqual(1, len(messages))
        resp = self.api_mock.post("/api/user.verify_email", dict(code=code))
        self.assertEqual(resp.get("error"), None)
        resp = self.api_mock.post("/api/user.me")
        self.assertEqual(resp.get("email_verified"), True)

    def test_recover_password(self):
        self.api_mock.post("/api/user.create", dict(email="test@gmail.com", password="test"))
        resp = self.api_mock.post("/api/user.recover_password_send_link", dict(email="test@gmail.com"))
        self.assertEqual(resp.get("error"), None)
        code = "test"
        keyvalue.set(code, "test@gmail.com", namespace="recover_password_link")
        messages = self.mail_stub.get_sent_messages(to="test@gmail.com")
        self.assertEqual(1, len(messages))
        resp = self.api_mock.post("/api/user.recover_password", dict(code=code, password="test2"))
        self.assertEqual(resp.get("error"), None)
