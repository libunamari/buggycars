import string
import secrets
import random
import unittest

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from base_buggy_car_tests import BaseBuggyCarTests

NAME_LENGTH = 10
USERNAME_LENGTH = 50
PASSWORD_PER_CHAR_TYPE_LENGTH = 5
WAIT_TIME_FOR_ALERTS = 5

class RegisterUserTests(BaseBuggyCarTests):

    def setUp(self) -> None:
        super().setUp()
        self.driver.get("https://buggy.justtestit.org/register")

    def tearDown(self) -> None:
        super().tearDown()
        # It would be best if the test removes the user it tries to register.
        # However there doesn't seem to be a way to remove registered users.
        pass

    def test_invalid_password(self) -> None:
        password = self._generate_random_string(string.ascii_letters, 20)
        self._register_new_user(password, "InvalidPasswordException")

        
    def test_valid_password(self) -> None:
        password_unshuffled = self._generate_random_string(string.ascii_lowercase, PASSWORD_PER_CHAR_TYPE_LENGTH) + self._generate_random_string(string.ascii_uppercase, PASSWORD_PER_CHAR_TYPE_LENGTH) + self._generate_random_string(string.punctuation, PASSWORD_PER_CHAR_TYPE_LENGTH) + self._generate_random_string(string.digits, PASSWORD_PER_CHAR_TYPE_LENGTH)
        password_list = random.sample(list(password_unshuffled), len(password_unshuffled))
        self._register_new_user("".join(password_list), "Registration is successful")


    def _register_new_user(self, password: str, alert_to_check: str) -> None:
        username = self._generate_random_string(string.ascii_lowercase, USERNAME_LENGTH)
        first_name = self._generate_random_string(string.ascii_lowercase, NAME_LENGTH)
        last_name = self._generate_random_string(string.ascii_lowercase, NAME_LENGTH)
        self.set_value_in_input_box("username", username)
        self.set_value_in_input_box("firstName", first_name)
        self.set_value_in_input_box("lastName", last_name)
        self.set_value_in_input_box("password", password)
        element = self.set_value_in_input_box("confirmPassword", password)
        element.submit()

        alerts = WebDriverWait(self.driver, WAIT_TIME_FOR_ALERTS).until(self.find_active_alert_messages)
        self.assertTrue(alerts, f"Expected alert after registration form is submitted but none were found")
        self.assertIn(alert_to_check, " ".join(alerts), f"Expected alert with message: {alert_to_check} when registering using username '{username}', first name '{first_name}', last name '{last_name}', and password '{password}'' ")


    def _generate_random_string(self, chars_to_use: str, length: str) -> str:
        random_string_list = [secrets.choice(chars_to_use) for _ in range(length)]
        return "".join(random_string_list)

if __name__ == '__main__':
    unittest.main()