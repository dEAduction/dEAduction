"""
Data Visualization Tool Tutorial
https://doc.qt.io/qtforpython/tutorials/datavisualize/index.html
In this tutorial, you’ll learn about the data visualization capabilities of Qt
for Python. To start with, find some open data to visualize. For example, data
about the magnitude of earthquakes during the last hour published on the US
Geological Survey website. You could download the All earthquakes open data in a
CSV format for this tutorial.

main.py
"""

import argparse
import pandas

from PySide2.QtCore import QDateTime, QTimeZone


def transform_date(utc, timezone=None):
    utc_fmt = "yyyy-MM-ddTHH:mm:ss.zzzZ"
    new_date = QDateTime().fromString(utc, utc_fmt)
    if timezone:
        new_date.setTimeZone(timezone)
    return new_date


def read_data(fname):
    # Read the CSV content
    df = pandas.read_csv(fname)

    # Remove wrong magnitudes
    df = df.drop(df[df.mag < 0].index)
    magnitudes = df["mag"]

    # My local timezone
    timezone = QTimeZone(b"Europe/Berlin")

    # Get timestamp transformed to our timezone
    times = df["time"].apply(lambda x: transform_date(x, timezone))

    return times, magnitudes


if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=True)
    args = options.parse_args()
    data = read_data(args.file)
    print(data)
