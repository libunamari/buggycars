"""
This contains the base class for the tests for the Buggy Car testing.
"""
import os
import secrets
import string
from typing import Any, Dict
import unittest
from urllib.parse import urljoin

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from buggy_cars_testing.constants import (
    API_WAIT_TIME,
    BASE_API_URL,
    NAME_LENGTH,
    BROWSER_TYPE_ENV_VAR,
)


class BaseBuggyCarTests(unittest.TestCase):
    """
    This is the base class for all of the tests for the Buggy Car testing.
    It contains common methods that is shared across the tests.
    """

    driver: webdriver.remote.webdriver.WebDriver

    def setUp(self) -> None:
        """
        Start up a new browser per test case.
        The browser type can be changed based on an environment variable.
        """
        # Chrome is the default
        chosen_browser = webdriver.Chrome

        if BROWSER_TYPE_ENV_VAR in os.environ:
            browser_type = os.environ[BROWSER_TYPE_ENV_VAR]
            if browser_type == "firefox":
                chosen_browser = webdriver.Firefox

        self.driver = chosen_browser()

    def tearDown(self) -> None:
        """
        Close the browser after each test case.
        """
        self.driver.close()

    def set_value_in_input_box(
        self, element_id: str, value: str, use_name: bool = False
    ) -> WebElement:
        """
        Sets the `value` into the element that that matches the `element_id`.
        If `use_name` is True, the element name will be checked against the `element_id`.
        Otherwise the element id will be checked.

        Returns the element that was updated.
        """
        elem = self.driver.find_element(By.NAME if use_name else By.ID, element_id)
        elem.clear()
        elem.send_keys(value)

        return elem

    def find_active_alert_messages(self) -> None:
        """
        Check for any displayed alerts.
        """
        return [
            alert.text
            for alert in self.driver.find_elements(By.XPATH, "//div[contains(@class, 'alert')]")
            if alert.is_displayed()
        ]

    def get_element_containing_text(self, text: str) -> WebElement:
        """
        Return the element which contains the specified text.
        """
        return self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")

    def generate_random_name(self) -> str:
        """
        Generate a random name that can be used as either a first or last name.
        """
        return self.generate_random_string(string.ascii_lowercase, NAME_LENGTH).capitalize()

    def generate_random_string(self, chars_to_use: str, length: str) -> str:
        """
        Generate a random string using characters from `chars_to_use` and make the string of length
        `length`.
        """
        random_string_list = [secrets.choice(chars_to_use) for _ in range(length)]
        return "".join(random_string_list)

    def generate_token(self, username: str, password: str) -> str:
        """
        Generate a token to use for API calls.
        """
        url = urljoin(BASE_API_URL, "oauth/token")
        token_contents = requests.post(
            url,
            data={"grant_type": "password", "username": username, "password": password},
            timeout=API_WAIT_TIME,
        ).json()
        return f"{token_contents['token_type']} {token_contents['access_token']}"

    def get_request_from_api_with_token(self, token: str, url: str) -> Dict[Any, Any]:
        """
        Send a GET request to the API with the provided token.
        Returns the JSON response.
        """
        return requests.get(
            urljoin(BASE_API_URL, url), headers={"authorization": token}, timeout=API_WAIT_TIME
        ).json()
