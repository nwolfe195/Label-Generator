from tkinter import *
import pandas as pd
from Label_Generator import *


class LabelGeneratorGUI:
    def __init__(self, root, path, database, protocols, sample_types):
        self.root = root
        self.path = path
        self.database = path+database
        self.protocols = path+protocols
        self.sample_types = path+sample_types

        self.root.title('VA LIMS Label Generator')
        self.label_generator = LabelGenerator(self.path, self.database, self.protocols, self.sample_types)

        self.protocol = StringVar(self.root)
        self.sample_type = StringVar(self.root)
        self.page_count = IntVar(self.root)

        self.create_components()

    def create_components(self):
        # Create GUI Title
        Label(self.root, text='VA SHIELD Label Generator', width=30, anchor='w').grid(row=0, column=0)

        # Create GUI Protocol Selection
        protocols = pd.read_csv(self.protocols, sep='\t')['Protocols']
        Label(self.root, text='Protocol', width=30, anchor='w').grid(row=1, column=0)
        self.protocol.set(protocols[0])
        OptionMenu(self.root, self.protocol, *protocols).grid(row=1, column=1)

        # Create GUI Sample Type Selection
        sample_types = pd.read_csv(self.sample_types, sep='\t')['Sample_Types']
        Label(self.root, text='Sample Type', width=30, anchor='w').grid(row=2, column=0)
        self.sample_type.set(sample_types[0])
        OptionMenu(self.root, self.sample_type, *sample_types).grid(row=2, column=1)

        # Create GUI Label Number Entry
        Label(self.root, text='Number of Sheets (85 labels each)', width=30, anchor='w').grid(row=3, column=0)
        Entry(self.root, textvariable=self.page_count).grid(row=3, column=1)

        # Create GUI Get Labels Button
        Button(self.root, text='Get Labels', command=self.create_labels).grid(row=4, column=1)

        # Create GUI Exit Button
        Button(self.root, text='Exit', command=self.exit).grid(row=5, column=0)

    def create_labels(self):
        message = self.label_generator.generate_labels(self.page_count.get(), self.protocol.get(), self.sample_type.get())
        self.popup_message([message])

    def popup_message(self, message_list):
        popup = Tk()
        popup.title('!')
        for r in range(len(message_list)):
            Label(popup, text=message_list[r]).grid(row=r, column=0)
        Button(popup, text='Close', command=popup.destroy).grid(row=len(message_list), column=0)
        popup.mainloop()

    def exit(self):
        self.label_generator.disconnect()
        self.root.destroy()


root = Tk()
configuration_file = 'Configuration.txt'
configuration = pd.read_csv(configuration_file, sep='\t')

interface = LabelGeneratorGUI(root, configuration['path'][0], configuration['database_file'][0],
                              configuration['protocol_file'][0], configuration['sample_types_file'][0])
root.mainloop()
