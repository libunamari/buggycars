import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By

from common import BrowserType


class BaseBuggyCarTests(unittest.TestCase):
    browser_type: BrowserType = None
    driver : webdriver.remote.webdriver.WebDriver

    # def __init__(self, browser_type: BrowserType) -> None:
    #     super().__init__()
    #     self.browser_type = browser_type

    def setUp(self) -> None:
        if self.browser_type == BrowserType.FIREFOX:
            self.driver = webdriver.Firefox()
        elif self.browser_type == BrowserType.CHROME:
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Chrome()

    def tearDown(self) -> None:
        self.driver.close()

    def set_value_in_input_box(self, element_id: str, input: str):
        elem = self.driver.find_element(By.ID, element_id)
        elem.clear()
        elem.send_keys(input)
        
        return elem

    def find_active_alert_messages(self, driver) -> None:
        return [alert.text for alert in driver.find_elements(By.XPATH, "//div[contains(@class, 'alert')]") if alert.is_displayed()]