import csv

import numpy as np


class NPCsvPredictor(object):
    """Produce predictions for data contained in a csv file.

    The data is output from the regress operation.
    """

    def __init__(self, model_file_path, salary_file_path,
                 prediction_file_output_path):
        """Initialize the predictor with its input and output locations.

        :param str prediction_path: The prediction csv containing data points.
        :param str output_path: Path to write prediction data.
        """
        self.model_file_path = model_file_path
        self.salary_file_path = salary_file_path
        self.prediction_file_output_path = prediction_file_output_path

    def predict_all(self):
        models = {}
        with open(self.model_file_path, 'r') as model_file:
            positions = {1: 'PG', 2: 'SG', 3: 'SF', 4: 'PF', 5: 'C'}
            reader = csv.reader(model_file)
            for (i, line) in enumerate(reader):
                print i
                a = np.zeros(len(line) - 1)
                for (ii, item) in a:
                    a[ii] = float(item)
                models[positions[i]] = a
                i += 1

        X = None
        with open(self.salary_file_path, 'r') as salary_file:
            # format is
            # position, name, salary, x1,x2,..
            salary_reader = csv.reader(salary_file)
            lines = [line[:2] + map(float, line[2:]) for line in salary_reader]

            # conver lines to numpy array
            num_data = len(lines)
            num_features = len(lines[0]) - 3
            X = np.zeros((num_data, num_features))

            for (i, row) in enumerate(lines):
                for (ii, feature) in enumerate(row[3:]):
                    X[i][ii] = feature

        preds = {}
        print X
        for position in positions.itervalues():
            preds[position] = X.dot(models[positions])

        with open(self.prediction_file_output_path, 'w') as prediction_file:
            prediction_file_writer = csv.writer(prediction_file)
            for i in range(num_data):
                # a,PG,40.0,20,4,10000
                prediction_file_writer.writerow(
                    [lines[i][1], lines[i][0], preds[lines[i][0]][i], 0,
                     lines[i][2]])
