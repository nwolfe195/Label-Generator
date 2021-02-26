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
        self.sample_type_file = sample_types
        self.sample_types = pd.read_csv(self.sample_type_file, sep='\t', dtype=str)

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

    def add_new_sample_type(self, new_sample_type):
        print('Creating a new sample type: %s' % new_sample_type)
        current_protocols = self.get_current_protocols()
        print('Current protocols: %s' % current_protocols)
        current_sample_types = self.get_current_sample_types()
        print('Current sample types: %s' % current_sample_types)
        last_sampletype = current_sample_types[-2]
        print('Last sample type: %s' % last_sampletype)
        next_sample_type = self.get_next_sample_type(last_sampletype)
        print('Next sample type: %s' % next_sample_type)
        digit_count = self.get_digit_count()
        print('Digit count: %d' % digit_count)
        max_number = 10 ** digit_count
        print('Max number: %d' % max_number)

        print(self.sample_types)
        self.sample_types = self.sample_types.append({'Sample_Types':new_sample_type, 'Index':next_sample_type},
                                                     ignore_index=True).sort_values(by=['Index'])
        self.sample_types.to_csv(self.sample_type_file, sep='\t', index=False)
        print(self.sample_types)

        digits = list(range(0, max_number))
        zeroed_digits = [str(item).zfill(digit_count) for item in digits]
        label_ids = list(itertools.product(current_protocols, [next_sample_type], zeroed_digits))
        label_ids_merged = list(map(lambda x: ''.join(x), label_ids))
        labels_df = pd.DataFrame(label_ids_merged, columns=['LabelID'])
        labels_df['Used'] = 0
        labels_df['UseDate'] = np.NaN
        labels_df.to_sql('Labels', self.connection, if_exists='append', index=False)
        
        return ['Added new sample code %s for sample type %s' % (next_sample_type, new_sample_type)]

    def get_current_protocols(self):
        current_studies_query = 'SELECT DISTINCT SUBSTR(LabelID, 1, 3) AS Studies FROM Labels'
        current_studies = pd.read_sql_query(current_studies_query, self.connection)['Studies'].tolist()
        return current_studies

    def get_current_sample_types(self):
        current_sample_types_query = 'SELECT DISTINCT SUBSTR(LabelID, 4, 2) AS SampleTypes FROM Labels ORDER BY SampleTypes'
        current_sample_types = pd.read_sql_query(current_sample_types_query, self.connection)['SampleTypes'].tolist()
        return current_sample_types

    def get_next_sample_type(self, last_sampletype):
        next_sampletype_int = int(last_sampletype)+1
        if len(str(next_sampletype_int)) == 1:
            next_sampletype_string = '0%d' % next_sampletype_int
        else:
            next_sampletype_string = str(next_sampletype_int)
        return next_sampletype_string

    def get_digit_count(self):
        example_query = 'SELECT LabelID FROM Labels LIMIT 1'
        example = pd.read_sql_query(example_query, self.connection)['LabelID'].tolist()[0]
        digits = len(example)-5
        return digits