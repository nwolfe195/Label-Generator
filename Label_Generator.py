import sqlite3
import itertools
import pandas as pd
import numpy as np
from datetime import datetime
import os
import shutil


class LabelGenerator:
    def __init__(self, path, database, protocols, sample_types):
        self.path = path
        self.database = database
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

        self.protocols = pd.read_csv(protocols, sep='\t', dtype=str)
        self.sample_types = pd.read_csv(sample_types, sep='\t', dtype=str)

    def disconnect(self):
        self.connection.close()

    def get_dictionaries(self, file, header):
        dataframe = pd.read_csv(file, sep='\t')
        values = dataframe[header].tolist()
        return values

    def generate_labels(self, page_count, protocol, sample_type):
        protocol_index = self.protocols.loc[self.protocols['Protocols'] == protocol]['Index'].tolist()[0]
        sample_type_index = self.sample_types.loc[self.sample_types['Sample_Types'] == sample_type]['Index'].tolist()[0]
        partial_label = protocol_index + sample_type_index

        # Select valid subset of labels
        query = 'SELECT * FROM Labels WHERE Used = 0 AND LabelID Like \'%s%%\'' % partial_label
        available_labels = pd.read_sql_query(query, self.connection)

        # Check if there are enough labels
        quantity = page_count*85
        available_labels_count = len(available_labels.index)
        if available_labels_count < quantity:
            message = 'There are insufficient available labels.  %d labels were requested, but only %d are available.' % \
                      (quantity, available_labels_count)
            # Tell external program it failed
            return message

        # Select quantity number of samples at random
        selected_labels = available_labels.sample(n=quantity)

        # Mark selected samples as used
        self.mark_label_used(selected_labels['LabelID'])

        # Write selected labels to a file
        filename = self.label_output(selected_labels, quantity, protocol, sample_type)

        # Tell external program it succeeded
        message = '%d labels were created, for project %s, sample type %s.  The labels are in the file %s' % \
                  (quantity, protocol, sample_type, filename)
        return message

    def mark_label_used(self, used_labels):
        # Make backup copy of the current database status
        backup_db_file = ('database_backup_%s' % datetime.now()).replace(':', '_').replace('.','_')+'.db'
        backup_db_path = self.path+'Database_Backups/'+backup_db_file
        shutil.copy(self.database, backup_db_path)

        for label in used_labels:
            label_query = 'UPDATE Labels SET Used = 1, UseDate = \'%s\' WHERE LabelID = \'%s\'' % \
                          (str(datetime.now()), label)
            self.cursor.execute(label_query)

        self.connection.commit()

    def label_output(self, selected_labels, quantity, protocol, sample_type):
        file_count = 1
        labels_path = self.path+'Labels/'

        while os.path.exists('%s%d_%s_%s_%s_%d.csv' % (labels_path, quantity, protocol, sample_type,
                                                       str(datetime.now().date()), file_count)):
            file_count += 1

        filename = '%d_%s_%s_%s_%d.csv' % (quantity, protocol, sample_type, str(datetime.now().date()),
                                           file_count)

        with open(self.path+'Labels/'+filename, 'w') as f:
            f.write(selected_labels['LabelID'].str.cat(sep='\n'))
        f.close()

        return filename
