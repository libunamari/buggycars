"""
This contains the tests that check the navigation of the overall ranking page.
"""
from urllib.parse import urljoin

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

from buggy_cars_testing.base_buggy_car_tests import BaseBuggyCarTests
from buggy_cars_testing.constants import BASE_API_URL, BASE_URL, WEB_PAGE_WAIT_TIME, API_WAIT_TIME


class ViewRankingTests(BaseBuggyCarTests):
    """
    This class contains the tests that check the navigation of the overall ranking page.
    """

    total_pages: int

    def setUp(self) -> None:
        """
        Go to the overall ranking page and wait for it to load.
        """
        super().setUp()
        self.driver.get(urljoin(BASE_URL, "overall"))
        self.total_pages = requests.get(
            urljoin(BASE_API_URL, "models"), timeout=API_WAIT_TIME
        ).json()["totalPages"]
        WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(
            lambda _: self._get_first_car_in_page()
        )

    def test_navigating_via_buttons_overall_ranking(self):
        """
        Check that each page can go to the previous and next page using the buttons.
        """
        previous_page_button = self.get_element_containing_text("«")
        next_page_button = self.get_element_containing_text("»")

        def check_page_reloaded() -> None:
            """
            The page has reloaded to another page when the first car entry in the page no longer
            matches the previous first car entry.
            """
            return first_car_in_page != self._get_first_car_in_page()

        def check_page_correctly_updated() -> None:
            """
            Check that the page has updated to the new page.
            """
            nonlocal first_car_in_page
            WebDriverWait(self.driver, WEB_PAGE_WAIT_TIME).until(lambda _: check_page_reloaded())
            first_car_in_page = self._get_first_car_in_page()

        def assert_page_change_invalid(button: WebElement, target_page_num: int) -> None:
            """
            Check that clicking the `button` will result in a failure.
            """
            with self.assertRaises(
                ElementClickInterceptedException,
                msg=f"Should not be able to go to page {target_page_num}",
            ):
                button.click()

        # This checks that we can get to the previous page, back to the original page, and to the
        # next page.
        for page_num in range(1, self.total_pages + 1):
            with self.subTest(page=page_num):
                first_car_in_page = self._get_first_car_in_page()
                if page_num == 1:
                    # You shouldn't be able to go to page 0 (since it doesn't exist)
                    assert_page_change_invalid(previous_page_button, page_num - 1)
                else:
                    previous_page_button.click()
                    check_page_correctly_updated()

                    # Get back to the original page
                    next_page_button.click()
                    check_page_correctly_updated()

                if page_num == self.total_pages:
                    # You shouldn't be able to go past the last page
                    assert_page_change_invalid(next_page_button, page_num + 1)
                else:
                    next_page_button.click()
                    check_page_correctly_updated()

    def _get_first_car_in_page(self) -> str:
        """
        Returns the first car entry in the page.
        """
        while True:
            try:
                car_table = self.driver.find_element(By.TAG_NAME, "table")
                first_entry = car_table.find_elements(By.TAG_NAME, "tr")[1]
                return first_entry.text
            except StaleElementReferenceException:
                # The page reloaded while we're trying to get the first car, so the elements
                # become stale.
                continue
