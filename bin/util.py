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


from datetime import datetime
import re

whitespace_re = re.compile(r"\s+")
range_delimiter_re = re.compile(r"\-")


def bruh(text):
    """
        The bruh method. Cleans up entries.


    :param text:
        A string.

    :return:
        A cleaned up string.
    """
    return whitespace_re.sub(" ", text.strip())


def get_timestamp():
    """
        Method that returns a YYYYMMDD_hhmmss formatted timestamp.


    :return:
        A string with the current time formatted as per description.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_file(content: str, folder: str, extension):
    """
        Method that saves content in a timestamped file with the extension
        designated by extension into a folder designated in folder.


    :param content:
        A string that's going to be written into a file.

    :param folder:
        Path to a folder in which the content is going to be saved.

    :param extension:
        A string that represents the extension that's going to be given to the
        newly created file (without the "." prefix).

    :return:
        Nothing.
    """
    with open(f"{folder}/{get_timestamp()}.{extension}", mode="w+") as file:
        file.write(content)


def calculate_average(company_dict, min_wage: float = 25.39):
    """
        Method that calculated the average wage per position. For more info
        on how this is calculated, visit the Jupyter notebook.


    :param company_dict:
        A dictionary containing the companies and their position offerings.

    :param min_wage:
        A float containing the minimum wage per hour.

    :return:
        A float containing the average wage per hour.
    """
    counter = {"Da": 0, "Honorar": 0, "DaNe": 0, "Ne": 0}
    total = 0
    count = 0

    for name, company in company_dict.items():
        for job in company["jobs"]:
            comp = job["compensation"]

            if comp in counter:
                counter[comp] += 1

                if comp != "Honorar":
                    count += 1
            else:
                amount = range_delimiter_re.split(comp)

                if len(amount) > 1:
                    amount = sum(amount) / len(amount)

                total += amount
                count += 1

    return (total + counter["Da"] * min_wage)/count
