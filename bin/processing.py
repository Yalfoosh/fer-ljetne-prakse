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

import re

from bs4 import BeautifulSoup

from bin.util import bruh


# region Regular Expressions
doo_pattern = r"d\.o\.o\."
bracketed_pattern = r"\[[^\]]*\]"

whitespace_re = re.compile(r"\s+")
redundant_suffix_re = \
    re.compile(rf"\s*({doo_pattern})?\s*{bracketed_pattern}\s*$")
# endregion


def index_html_to_rows(content: str):
    """
        Method that converts the index page HTML to entry rows.


    :param content:
        A string containing the HTML content.

    :return:
        A list containing the parser rows.
    """
    soup = BeautifulSoup(content, "html.parser")

    table_head = soup.find("thead")
    columns = table_head.find_all("div",
                                  {"class": "tablesorter-header-inner"})

    column_labels = [bruh(x.text) for x in columns]

    # Add column "Poveznica"
    column_labels = column_labels[:1] + ["Poveznica"] + column_labels[1:]

    # Final columns:
    #   Tvrtka
    #   Poveznica
    #   Mjesta
    #   Prijava prvi odabir
    #   Tema
    #   Akcija

    rows = [tuple(column_labels)]
    table_body = soup.find("tbody")

    for row in table_body.find_all("tr"):
        cols = row.find_all("td")

        title = bruh(redundant_suffix_re.sub("", cols[0].text))

        anchor = cols[0].find("a")
        href = None if anchor is None else anchor.get("href")

        n_available = int(cols[1].text)
        n_prioritized = int(cols[2].text)
        subject = bruh(cols[3].text)
        action = cols[4].find("a").get("href")

        rows.append((title, href,
                     n_available, n_prioritized,
                     subject, action))

    return rows


def position_html_to_dict(content):
    """
        Method that converts the company position HTML into a dictionary.


    :param content:
        A string containing the HTML content.

    :return:
        A dictionary containing the company position data.
    """
    position_dict = dict()

    soup = BeautifulSoup(content, "html.parser")

    table_body = soup.find("tbody")

    for row in table_body.find_all("tr"):
        entries = row.find_all("td")

        if len(entries) == 2:
            position_dict[bruh(entries[0].text)] = bruh(entries[1].text)

    return position_dict
