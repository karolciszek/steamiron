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

DAY_REGEX = re.compile("^[0-9]+")
MONTH_REGEX = re.compile("|".join(MONTHS))

def parse_daylio_date(entry):
    year = int(entry["year"])
    day_month = entry["date"]
    day_str = DAY_REGEX.match(day_month)[0]
    day = int(day_str)
    month_name = MONTH_REGEX.search(day_month)[0]
    month = MONTHS.index(month_name) + 1

    #return datetime.timedelta(hours=0)
    #return datetime.timedelta(days=day)
    return datetime.date(year, month, day)
    #return datetime.datetime(
        #      day,
  #      month,
    #)


SCORES = {
        "okropnie": 1,
        "źle": 2,
        "tak sobie": 3,
        "dobrze": 4,
        "wspaniale": 5,
        }

score = lambda x: SCORES[x]

if __name__=="__main__":
    with open('daylio_export.csv', 'r') as f:
        reader = DictReader(f)
        days = [row for row in reader][::-1]

    # average
    moods = [score(d["mood"]) for d in days]
    avg = sum(moods) / len(moods)
    print("Average: {}".format(avg))
    print("Number of entries: {}".format(len(moods)))

    def create_time_axis():
        dates = [parse_daylio_date(d) for d in days]
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
        x = [parse_daylio_date(d) for d in days]

        PLT.plot(x,y)
        PLT.xticks(rotation=30, fontsize="small")
        PLT.plot(x,middle_line,"#eeeeee")
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
