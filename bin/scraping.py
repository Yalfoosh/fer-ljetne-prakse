# Copyright 2020 Miljenko Šuflaj
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bin.processing import index_html_to_rows, position_html_to_dict


# Check "selenium" directory for the webdrivers first
os.environ['PATH'] += ':' + os.path.abspath("../selenium/")

login_page_url = "https://www.fer.unizg.hr/login/?frompage=%2Fprakse%2F" + \
                 "prijava&return=%2Fprakse%2Fprijava"
index_page_url = "https://www.fer.unizg.hr/prakse/prijava"


def get_credentials(username: str = None, password: str = None):
    """
        Method that gets one's FERWeb credentials.


    :param username:
        A string containing one's FERWeb username.

    :param password:
        A string containing one's FERWeb password.

    :return:
        A tuple of strings containing the username and password.
    """
    if username is None:
        username = input("Upišite korisničko ime: ")

    if password is None:
        password = input("Upišite lozinku: ")

    return username, password


def login(driver: RemoteWebDriver, username: str = None, password: str = None):
    """
        A method that uses Selenium to log in into FERWeb.


    :param driver:
        A RemoteWebDriver object representing the webdriver.

    :param username:
        A string containing one's FERWeb username.

    :param password:
        A string containing one's FERWeb password.

    :return:
        Nothing.
    """
    username, password = get_credentials(username, password)

    driver.get(login_page_url)

    username_field = driver.find_element_by_id("username")
    password_field = driver.find_element_by_id("password")
    submit_button = driver.find_element_by_xpath("/html/body/div/div/div/div[2]"
                                                 "/div/form/div[3]/button")

    username_field.send_keys(username)
    password_field.send_keys(password)
    submit_button.click()


def get_index_html(driver: RemoteWebDriver):
    """
        Method that retrieves the index page HTML.


    :param driver:
        A RemoteWebDriver object representing the webdriver.

    :return:
        A string containing the index page HTML.
    """
    driver.get(index_page_url)

    index_html = driver.find_elements_by_tag_name("table")[1] \
                       .get_attribute("outerHTML")

    return BeautifulSoup(index_html, "html.parser").prettify()


def get_position_html(driver: RemoteWebDriver, href: str):
    """
        Method that retrieves the job position HTML.

    :param driver:
        A RemoteWebDriver object representing the webdriver.

    :param href:
        A string containing the path relative to FERWeb.

    :return:
        A string containing the job position HTML.
    """
    full_href = "https://www.fer.unizg.hr" + href

    driver.get(full_href)

    # Necessary because it just fast forwards to the end without change.
    time.sleep(2)

    table = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "tvrtka_ostalo")
        ))

    position_html = table.get_attribute("outerHTML")

    return BeautifulSoup(position_html, "html.parser").prettify()


def merge_into_list(username: str = None, password: str = None):
    """
        Method that merges index rows and position dicts into one.


    :param username:
        A string containing one's FERWeb username.

    :param password:
        A string containing one's FERWeb password.

    :return:
        A list of merged entries.
    """
    _driver = webdriver.Firefox()
    login(_driver, username, password)

    merged_list = list()

    index_html = get_index_html(_driver)
    index_rows = index_html_to_rows(index_html)

    relevant_rows = index_rows[1:]

    for row in relevant_rows:
        href = row[-1]

        position_html = get_position_html(_driver, href)
        position_dict = position_html_to_dict(position_html)

        merged_list.append((row, position_dict))

    _driver.quit()

    return merged_list


def merge_fully_into_list(username: str = None, password: str = None):
    """
        Method that metrges entries seamlessly into a list.


    :param username:
        A string containing one's FERWeb username.

    :param password:
        A string containing one's FERWeb password.

    :return:
        A list of fully merged entries.
    """
    fully_merged_list = list()

    for element in merge_into_list(username, password):
        fully_merged_list.append({
            "company": element[0][0],
            "page": element[0][1],
            "company_address": element[1]["Adresa prakse"],
            "company_desc": element[1]["Opis tvrtke"],
            "position": element[0][4],
            "position_desc": element[1]["Opis"],
            "n_available": element[0][2],
            "n_prioritized": element[0][3],
            "start": element[1]["Planirani početak"],
            "end": element[1]["Planirani završetak"],
            "compensation": element[1]["Honoriranje prakse"]
        })

    return fully_merged_list


def preprocess_fully(username: str = None, password: str = None):
    """
        Method that fully preprocesses scraped data.


    :param username:
        A string containing one's FERWeb username.

    :param password:
        A string containing one's FERWeb password.

    :return:
        A dictionary of companies and their position offerings.
    """
    full_dict = dict()
    group_by = ["company", "page", "company_address", "company_desc"]

    for element in merge_fully_into_list(username, password):
        name, page, addr, desc = [element[x] for x in group_by]

        if name not in full_dict:
            full_dict[name] = {"page": page,
                               "company_address": addr,
                               "company_desc": desc,
                               "jobs": list()}

        new_dict = dict(element)

        for key in group_by:
            del new_dict[key]

        full_dict[name]["jobs"].append(new_dict)

    return full_dict
