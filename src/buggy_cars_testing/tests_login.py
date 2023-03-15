"""
This contains the tests that require logging in as a user.
"""
import random
import string
from typing import Any, List, Dict
from urllib.parse import urljoin, quote

import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from buggy_cars_testing.base_buggy_car_tests import BaseBuggyCarTests
from buggy_cars_testing.constants import (
    BASE_API_URL,
    BASE_URL,
    WEB_PAGE_WAIT_TIME,
    PHONE_NUMBER_LENGTH,
    COMMENT_LENGTH,
    API_WAIT_TIME,
)

# Ideally this wouldn't be stored here, but instead in a secrets vault or a config file
# but for simplicity, this is hardcoded here.
USERNAME = "mgltest4"
PASSWORD = "Password1234!"


class LoginTests(BaseBuggyCarTests):
    """
    This class contains the tests that require logging in as a user.
    """

    all_cars: List[str] = []
    token: str

    @classmethod
    def setUpClass(cls) -> None:
        """
        This collects all the car model IDs.
        The IDs are used to test voting.
        This process is quite slow, so this is only done once when the class is setup rather than
        before each test case.
        """

        def add_cars_from_page(page_num: int) -> Dict[Any, Any]:
            """
            The car models is split across multiple pages, so add the car model IDs from the page
            specified by `page_num`.
            """
            url = urljoin(BASE_API_URL, f"models?page={page_num}")
            models = requests.get(url, timeout=API_WAIT_TIME).json()

            for model in models["models"]:
                cls.all_cars.append(model["id"])
            return models

        # Get the first page separately so we can find out what the total amount of pages are.
        models_page = add_cars_from_page(1)
        total_pages = models_page["totalPages"]

        for page in range(2, total_pages + 1):
            add_cars_from_page(page)

        # Shuffle the IDs so we don't always pick the same ones.
        random.shuffle(cls.all_cars)

    def setUp(self) -> None:
        """
        Login before each test case.
        """
        super().setUp()
        self.driver.get(BASE_URL)
        self.set_value_in_input_box("login", USERNAME, True)
        element = self.set_value_in_input_box("password", PASSWORD, True)
        element.submit()

        # Wait until successfully logged in by waiting for the logout element to appear.
        WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(lambda _: self._get_logout_element())

        # Create a token for use by API queries.
        self.token = self.generate_token(USERNAME, PASSWORD)

    def tearDown(self) -> None:
        """
        Logout after finishing the test case.
        """
        logout_element = WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
            lambda _: self._get_logout_element()
        )
        logout_element.click()

        super().tearDown()

    def test_update_profile_valid(self) -> None:
        """
        Check that a logged in user can update their profile.
        """
        self.get_element_containing_text("Profile").click()

        # Wait for the profile page to load.
        WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
            lambda _: self.driver.find_elements(By.ID, "firstName")
        )

        genders = self.driver.find_element(By.ID, "genders")
        hobbies = self.driver.find_element(By.ID, "hobby")

        # Go through and try out all of the gender and hobby options.
        for gender in genders.find_elements(By.TAG_NAME, "option"):
            for hobby in hobbies.find_elements(By.TAG_NAME, "option"):
                # Use a subtest so that multiple combinations can be tested without a failure in
                # one causing the rest to fail.
                with self.subTest(
                    gender=gender.get_attribute("value"), hobby=hobby.get_attribute("value")
                ):
                    # Randomly generate most of the profile options.
                    profile_values = {}
                    profile_values["firstName"] = self.generate_random_name()
                    profile_values["lastName"] = self.generate_random_name()
                    profile_values["age"] = random.randrange(95)
                    # Ideally the address would be randomly generated too, but it requires a
                    # third-party library (https://pypi.org/project/random-address/)
                    # so for simplicity, it is hardcoded.
                    profile_values["address"] = "123 Fake Street\nFake Suburb\nFake City\n1234"
                    profile_values["phone"] = self.generate_random_string(
                        string.digits, PHONE_NUMBER_LENGTH
                    )
                    profile_values["gender"] = gender.get_attribute("value")

                    # Update the elements to have the generated profile options.
                    for key, value in profile_values.items():
                        self.set_value_in_input_box(key, value)
                    hobby.click()
                    hobby.submit()

                    alerts = WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
                        lambda _ : self.find_active_alert_messages()
                    )
                    self.assertTrue(
                        alerts,
                        "Expected alert after profile update form is "
                        "submitted but none were found",
                    )
                    self.assertIn(
                        "The profile has been saved successful",
                        " ".join(alerts),
                        f"Did not successfully update profile with {profile_values} and "
                        f"hobby '{hobby.get_attribute('value')}'",
                    )

                    # Check that the API has the updated profile
                    profile = self.get_request_from_api_with_token(self.token, "users/profile")
                    for key, value in profile_values.items():
                        self.assertEqual(
                            str(value),
                            str(profile[key]),
                            f"{key} has not been updated in the API",
                        )
                    self.assertEqual(
                        hobby.get_attribute("value"),
                        profile["hobby"],
                        "Hobby has not been updated in the API",
                    )

    def test_vote_no_comment(self) -> None:
        """
        Check that voting with no comments works as expected.
        """
        self._vote_on_a_page(False)

    def test_vote_with_comment(self) -> None:
        """
        Check that voting with a comment works as expected.
        """
        self._vote_on_a_page(True)

    def _vote_on_a_page(self, add_comment: bool) -> None:
        """
        Helper class for voting on a page.
        If `add_comment` is True, then it will add a randomly generated comment as part of the vote.
        """
        model_id = self._find_model_with_no_vote()

        self.driver.get(urljoin(BASE_URL, quote(f"model/{model_id}")))
        WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
            lambda _: self.get_element_containing_text("Specification")
        )

        api_url = urljoin(BASE_API_URL, quote(f"models/{model_id}"))
        votes_before = requests.get(api_url, timeout=API_WAIT_TIME).json()["votes"]

        if add_comment:
            comment = self.generate_random_string(string.ascii_letters, COMMENT_LENGTH)
            self.set_value_in_input_box("comment", comment)

        self.get_element_containing_text("Vote!").click()

        WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
            lambda _: self.get_element_containing_text("Thank you for your vote!")
        )
        post_vote_result = self.get_request_from_api_with_token(
            self.token, quote(f"models/{model_id}")
        )
        self.assertGreater(
            post_vote_result["votes"],
            votes_before,
            f"The vote count should have increased for {model_id} after voting for it.",
        )
        self.assertFalse(
            post_vote_result["canVote"],
            f"The user should not be able to vote for {model_id} after voting for it already",
        )

        def found_added_comment_webpage(author: str) -> bool:
            """
            Helper function to check if the webpage has been updated with the comment.
            """
            comments_table = self.driver.find_element(By.TAG_NAME, "table")
            for row in comments_table.find_elements(By.TAG_NAME, "tr"):
                row_contents = row.find_elements(By.TAG_NAME, "td")
                if row_contents[1].text == author and row_contents[2].text == comment:
                    return True
            return False

        def found_added_comment_api(author: str) -> bool:
            """
            Helper function to check if the API has been updated with the comment.
            """
            for online_comment in post_vote_result["comments"]:
                if online_comment["user"] == author and online_comment["text"] == comment:
                    return True
            return False

        if add_comment:
            profile = self.get_request_from_api_with_token(self.token, "users/profile")
            user_name = f"{profile['firstName']} {profile['lastName']}"

            self.assertTrue(
                found_added_comment_api(user_name),
                f"The API should have returned the comment '{comment}' by '{user_name}' for "
                f"{model_id}.",
            )
            self.assertTrue(
                found_added_comment_webpage(user_name),
                f"The webpage should have the comment '{comment}' by '{user_name}' for {model_id}",
            )

    def _get_logout_element(self) -> WebElement:
        """
        Get the logout element.
        """
        return self.get_element_containing_text("Logout")

    def _find_model_with_no_vote(self) -> str:
        """
        Find a car model that has not been voted for by this user.
        Ideally, there would be a way to remove a user's vote so we don't have this problem.
        """

        for model_id in self.all_cars:
            model_info = self.get_request_from_api_with_token(
                self.token, quote(f"models/{model_id}")
            )
            if model_info["canVote"]:
                return model_id

        raise RuntimeError(f"{USERNAME} has voted for every model, need to use another user")
