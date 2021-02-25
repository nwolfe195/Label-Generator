from tkinter import *
import pandas as pd
from Label_Generator import *


class LabelGeneratorGUI:
    def __init__(self, root, path, database, protocols, sampletypes):
        self.root = root
        self.path = path
        self.database = path+database
        self.protocols = path+protocols
        self.sample_types = path+sampletypes

        self.root.title('VA LIMS Label Generator')
        self.label_generator = LabelGenerator(database, path)

        self.protocol = StringVar(self.root)
        self.sample_type = StringVar(self.root)

        self.create_components()

    def create_components(self):
        # Create GUI Title
        Label(self.root, text='VA SHIELD Label Generator', width=30, anchor='w').grid(row=0, column=0)

        # Create GUI Protocol Selection
        protocols = pd.read_csv(self.protocols)['Protocols']
        Label(self.root, text='Protocol', width=30, anchor='w').grid(row=1, column=0)
        self.protocol.set(protocols[0])
        OptionMenu(self.root, self.protocol, *protocols).grid(row=1, column=1)

        # Create GUI Sample Type Selection
        sample_types = pd.read_csv(self.sample_types)['SampleTypes']
        Label(self.root, text='Sample Type', width=30, anchor='w').grid(row=2, column=0)
        self.sample_type.set(sample_types[0])
        OptionMenu(self.root, self.sample_type, *sample_types).grid(row=2, column=1)




root = Tk()
configuration_file = 'Configuration.txt'
configuration = pd.read_csv(configuration_file, sep='\t')

interface = LabelGeneratorGUI(root, configuration['path'][0], configuration['database_file'][0],
                              configuration['protocol_file'][0], configuration['sampletypes_file'][0])
root.mainloop()
