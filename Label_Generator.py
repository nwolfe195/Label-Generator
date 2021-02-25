import sqlite3
import itertools
import pandas as pd
import numpy as np
import datetime
import os


class LabelGenerator:
    def __init__(self, database, path):
        self.path = path
        self.database = database
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()