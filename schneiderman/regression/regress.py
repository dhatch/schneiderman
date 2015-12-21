import os
import csv
from itertools import imap, izip

import numpy as np
from sklearn.linear_model.coordinate_descent import ElasticNetCV


class ElasticNetModel(object):
    """Train an elastic net model on the data."""

    def __init__(self, cleaned_data_directory_path, models_file_path,
                 residual_data_path):
        """Initialize the ElasticNetModel.

        :param str cleaned_data_directory_path: The location of cleaned data
                                                files.
        :param str models_file_path: The output location of the models file.
        :param str residual_data_path: The output location for residual data.
        """
        self.cleaned_data_directory_path = cleaned_data_directory_path
        self.models_file_path = models_file_path
        self.residual_data_path = residual_data_path

    def train_all(self):
        positions = ['PG.csv', 'SG.csv', 'SF.csv', 'PF.csv', 'C.csv']
        with open(self.models_file_path, 'w') as model_file:
            model_file_writer = csv.writer(model_file)
            for filename in positions:
                with open(os.path.join(self.cleaned_data_directory_path, filename),
                          'r') as cleaned_data:
                    cleaned_data_reader = csv.reader(cleaned_data)
                    lines = [map(float, line[:-1]) + line[-1:] for line in cleaned_data_reader
                             if len(line) >= 2]

                # conver lines to numpy array
                num_data = len(lines)
                num_features = len(lines[0]) - 2

                X = np.zeros((num_data, num_features))
                Y = np.zeros((num_data))

                for (i, data) in enumerate(lines):
                    for (ii, feature) in enumerate(data[:-2]):
                        X[i][ii] = feature
                    Y[i] = lines[i][-2]  # last one is name

                # create an instance of elasticnet
                net = ElasticNetCV(alphas=[0.01, 0.05, 0.1], eps=2e-3,
                                   l1_ratio=[0.5, 0.7, 1], cv=3, normalize=True)

                # create a model based on our data
                net.fit(X, Y)
                model_file_writer.writerow(net.coef_)

                with open(os.path.join(
                        self.residual_data_path,
                        '_'.join(('resid', filename))), 'w') as resid_file:
                    resid_file_writer = csv.writer(resid_file)
                    # get the residuals
                    resid = X.dot(net.coef_) - Y
                    for (name, row) in izip(imap(lambda l: l[-1], lines), resid):
                        resid_file_writer.writerow((name, row))
                    print sum(resid)
