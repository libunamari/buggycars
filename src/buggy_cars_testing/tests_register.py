"""
This contains the tests that register as a new user.
"""
import random
import string
from urllib.parse import urljoin

from selenium.webdriver.support.wait import WebDriverWait

from buggy_cars_testing.base_buggy_car_tests import BaseBuggyCarTests
from buggy_cars_testing.constants import (
    BASE_URL,
    USERNAME_LENGTH,
    PASSWORD_PER_CHAR_TYPE_LENGTH,
    WEB_PAGE_WAIT_TIME,
)


class RegisterUserTests(BaseBuggyCarTests):
    """
    This class contains the tests that register as a new user.
    """

    def setUp(self) -> None:
        """
        Go to the register page.
        """
        super().setUp()
        self.driver.get(urljoin(BASE_URL, "register"))

    # It would be best if the test removes the user it tries to register as part of the tearDown.
    # However there doesn't seem to be a way to remove registered users.

    def test_invalid_password(self) -> None:
        """
        Check that a password with only letters will fail the registration.
        """
        password = self.generate_random_string(string.ascii_letters, 20)
        self._register_new_user(password, "InvalidPasswordException")

    def test_valid_password(self) -> None:
        """
        Check that a new user can be registered.
        """

        # Create a password using lowercase, uppercase, symbols, and numbers.
        password_unshuffled = (
            self.generate_random_string(string.ascii_lowercase, PASSWORD_PER_CHAR_TYPE_LENGTH)
            + self.generate_random_string(string.ascii_uppercase, PASSWORD_PER_CHAR_TYPE_LENGTH)
            + self.generate_random_string(string.punctuation, PASSWORD_PER_CHAR_TYPE_LENGTH)
            + self.generate_random_string(string.digits, PASSWORD_PER_CHAR_TYPE_LENGTH)
        )
        password_list = random.sample(list(password_unshuffled), len(password_unshuffled))
        password = "".join(password_list)

        username = self._register_new_user(password, "Registration is successful")

        # Check that we can login using this user by trying to create a token.
        self.generate_token(username, password)

    def _register_new_user(self, password: str, alert_to_check: str) -> str:
        """
        Register a new user using the provided `password` and randomly generating the other options.
        After attempting to register, checks the alerts for `alert_to_check`.
        """
        username = self.generate_random_string(string.ascii_lowercase, USERNAME_LENGTH)
        first_name = self.generate_random_name()
        last_name = self.generate_random_name()
        self.set_value_in_input_box("username", username)
        self.set_value_in_input_box("firstName", first_name)
        self.set_value_in_input_box("lastName", last_name)
        self.set_value_in_input_box("password", password)
        element = self.set_value_in_input_box("confirmPassword", password)
        element.submit()

        alerts = WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
            lambda _ : self.find_active_alert_messages()
        )
        self.assertTrue(
            alerts, "Expected alert after registration form is submitted but none were found"
        )
        self.assertIn(
            alert_to_check,
            " ".join(alerts),
            f"Expected alert with message: {alert_to_check} when registering using username "
            f"'{username}', first name '{first_name}', last name '{last_name}', "
            f"and password '{password}'' ",
        )
        return username
