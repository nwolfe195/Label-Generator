from tkinter import *
import pandas as pd
from Label_Generator import *


class LabelGeneratorGUI:
    def __init__(self, root, path, database):
        self.root = root
        self.path = path
        self.database = path+database

        self.root.title('VA LIMS Label Generator')
        self.label_generator = LabelGenerator(database, path)


root = Tk()
configuration_file = 'Configuration.txt'
configuration = pd.read_csv(configuration_file, sep='\t')

interface = LabelGeneratorGUI(root, configuration['path'][0], configuration['database_file'][0])
root.mainloop()