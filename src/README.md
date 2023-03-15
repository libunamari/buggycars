# Buggy Cars Rating Tests

## Setup
Requires:
* Python 3 (I was using 3.10.6)
* Python PIP
* The following Python packages:
  * `requests` (I was using 2.25.1)
  * `selenium` (I was using 4.8.2)
  * Install using: `pip3 install requests selenium`

**_NOTE:_** `pylint` and `black` were used to format the Python code, but these packages are not necessary to run the tests

## Running the tests
1. Change directory to the `src` directory.
2. To run tests via Firefox, run `export BUGGY_CARS_TEST_BROWSER="firefox"`.
To run via Chrome, unset the environment variable using `unset export BUGGY_CARS_TEST_BROWSER`
3. Run `python3 -m unittest discover .`

## Expected results
There are some warnings that are output, but seem to be due to selenium.
These can be ignored. An example is shown below:
```
./usr/lib/python3.10/unittest/suite.py:107: ResourceWarning: unclosed <socket.socket fd=7, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 40664), raddr=('127.0.0.1', 33377)>
  for index, test in enumerate(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```

There are some tests that will fail due to the bugs in the website.
These tests are:
* `test_update_profile_valid` when the hobby is Knitting, due to the third point in https://github.com/libunamari/buggycars/issues/4
* `test_navigating_via_buttons_overall_ranking` when the page is 5, due to the second point in https://github.com/libunamari/buggycars/issues/5
* `test_vote_with_comment` may fail depending on the chosen model, due to https://github.com/libunamari/buggycars/issues/3.
Also this particular model https://buggy.justtestit.org/model/c4u1mqnarscc72is013g%7Cc4u1mqnarscc72is0170 does not load properly, so the test may also fail due to choosing this model.

An example of an expected result:
```
$ python3 -m unittest discover .
./usr/lib/python3.10/unittest/suite.py:107: ResourceWarning: unclosed <socket.socket fd=7, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 40664), raddr=('127.0.0.1', 33377)>
  for index, test in enumerate(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./usr/lib/python3.10/unittest/suite.py:84: ResourceWarning: unclosed <socket.socket fd=7, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 38554), raddr=('127.0.0.1', 60557)>
  return self.run(*args, **kwds)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./usr/lib/python3.10/unittest/suite.py:107: ResourceWarning: unclosed <socket.socket fd=7, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 50024), raddr=('127.0.0.1', 49059)>
  for index, test in enumerate(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./usr/lib/python3.10/unittest/suite.py:84: ResourceWarning: unclosed <socket.socket fd=7, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 33958), raddr=('127.0.0.1', 51295)>
  return self.run(*args, **kwds)
ResourceWarning: Enable tracemalloc to get the object allocation traceback

======================================================================
FAIL: test_update_profile_valid (buggy_cars_testing.tests_login.LoginTests) (gender='Male', hobby='Knitting')
Check that a logged in user can update their profile.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/maria/buggycars/src/buggy_cars_testing/tests_login.py", line 147, in test_update_profile_valid
    self.assertIn(
AssertionError: 'The profile has been saved successful' not found in 'Unknown error' : Did not successfully update profile with {'firstName': 'Ilcvrvchvj', 'lastName': 'Ahwpdgcrtt', 'age': 24, 'address': '123 Fake Street\nFake Suburb\nFake City\n1234', 'phone': '7291718519', 'gender': 'Male'} and hobby 'Knitting'

======================================================================
FAIL: test_update_profile_valid (buggy_cars_testing.tests_login.LoginTests) (gender='Female', hobby='Knitting')
Check that a logged in user can update their profile.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/maria/buggycars/src/buggy_cars_testing/tests_login.py", line 147, in test_update_profile_valid
    self.assertIn(
AssertionError: 'The profile has been saved successful' not found in 'Unknown error' : Did not successfully update profile with {'firstName': 'Opjacrcqnh', 'lastName': 'Augkmbnhse', 'age': 26, 'address': '123 Fake Street\nFake Suburb\nFake City\n1234', 'phone': '4930992519', 'gender': 'Female'} and hobby 'Knitting'

======================================================================
FAIL: test_vote_with_comment (buggy_cars_testing.tests_login.LoginTests)
Check that voting with a comment works as expected.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/maria/buggycars/src/buggy_cars_testing/tests_login.py", line 178, in test_vote_with_comment
    self._vote_on_a_page(True)
  File "/home/maria/buggycars/src/buggy_cars_testing/tests_login.py", line 241, in _vote_on_a_page
    self.assertTrue(
AssertionError: False is not true : The API should have returned the comment 'vcfCllaEgrxoZntWmdvCKoGPmwTovJykgLktKYwvMLGAuPIGrW' by 'Fljwssgxfd Qoiopdricq' for c4u1mqnarscc72is00ng|c4u1mqnarscc72is00pg.

======================================================================
FAIL: test_navigating_via_buttons_overall_ranking (buggy_cars_testing.tests_view_rankings.ViewRankingTests) (page=5)
Check that each page can go to the previous and next page using the buttons.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/maria/buggycars/src/buggy_cars_testing/tests_view_rankings.py", line 89, in test_navigating_via_buttons_overall_ranking
    assert_page_change_invalid(next_page_button, page_num + 1)
  File "/home/maria/buggycars/src/buggy_cars_testing/tests_view_rankings.py", line 65, in assert_page_change_invalid
    with self.assertRaises(
AssertionError: ElementClickInterceptedException not raised : Should not be able to go to page 6

----------------------------------------------------------------------
Ran 6 tests in 109.970s

FAILED (failures=4)

```

## Workarounds
Since a vote cannot be undone, after running the tests repeatedly, the login tests will run out of models to vote for.
You will need to register a new user and update the variables in https://github.com/libunamari/buggycars/blob/main/src/buggy_cars_testing/tests_login.py#L27

## Future work
My wishlist if there was more time:
* Collecting diagnostics when the test fails (e.g. a screenshot of the webpage, getting logs) to help debug
* More sad/rainy day test cases
* Dealing with passwords and tokens with security in mind
