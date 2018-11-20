#!/usr/bin/python3
from csv import DictReader
import re
import datetime
import pandas as PD
import numpy as NP
import matplotlib.pyplot as PLT

MONTHS = [
    "stycznia",
    "lutego",
    "marca",
    "kwietnia",
    "maja",
    "czerwca",
    "lipca",
    "sierpnia",
    "września",
    "października",
    "listopada",
    "grudnia",
]

class DaylioReader:
    """Takes the path of a Daylio CSV file and processes the data."""
    def __init__(self, filename):
        self._day_regex   = re.compile("^[0-9]+")
        self._month_regex = re.compile("|".join(MONTHS))
        self.filename = filename

    def read(self):
        """Accesses the file on disk and returns entries in chronological order."""
        with open(self.filename, 'r') as f:
            reader = DictReader(f)
            descending_days = [row for row in reader]
            self.days = descending_days[::-1]
        return self.days

    def parse_date(self, entry):
        """Extracts single datetime object from the year and date columns.

        Daylio exports date/time data in the following way:
        - "year" is simply represented as YYYY
        - "date" is the day in DD followed by the full month name
        - the month in "date" is also localised (in my case Polish)
        """
        year = int(entry["year"])

        date = entry["date"]
        day_str = self._day_regex.match(date)[0]
        day = int(day_str)

        month_name = self._month_regex.search(date)[0]
        month = MONTHS.index(month_name) + 1
        return datetime.date(year, month, day)

    def dates(self):
        return [self.parse_date(d) for d in self.days]

SCORES = {
        "okropnie": 1,
        "źle": 2,
        "tak sobie": 3,
        "dobrze": 4,
        "wspaniale": 5,
        }

score = lambda x: SCORES[x]

if __name__=="__main__":
    reader = DaylioReader('daylio_export.csv')
    days = reader.read()
    dates = reader.dates()

    # average
    moods = [score(d["mood"]) for d in days]
    avg = sum(moods) / len(moods)
    print("Average: {}".format(avg))
    print("Number of entries: {}".format(len(moods)))

    def create_time_axis():
        moods = [score(d["mood"]) for d in days]

        first = min(dates)
        last = max(dates)
        delta = last - first
        _day = datetime.timedelta(days=1)

        x = [first + i * _day for i in range(delta.days)]
        return x

    def rolling_mean(values, n):
        arr = NP.asarray(values)
        return PD.rolling_mean(arr, n)

    def plot(rolling_n=10, filename_base=None):
        # plot
        y = rolling_mean(moods, rolling_n)
        middle_line = [3 for val in y]
        x = dates

        PLT.plot(x,y)
        PLT.xticks(rotation=30, fontsize="small")
        PLT.plot(x,middle_line,"#eeeeee")
        xaxis = PLT.gca().xaxis
        xaxis.grid(True, color="#f2f2f2")
        if filename_base:
            d = datetime.datetime.now()
            directory = "{}.{}.{}".format(d.day, d.month, d.year)
            PLT.savefig("{}/{}-{}.png".format(directory, filename_base, rolling_n))
            PLT.clf()
        else:
            PLT.show()

    plot(rolling_n=1, filename_base="rough")
    for i in range(4, 30, 2):
        print("Now processing: {}", format(i))
        plot(rolling_n=i, filename_base="rolling")
