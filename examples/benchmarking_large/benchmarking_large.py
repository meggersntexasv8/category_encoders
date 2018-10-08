"""
Run a large scale benchmark.

We measure: {dataset, encoder, model, train and test accuracy measures, train and test runtimes, feature count}.

Note: A reasonably recent version of sklearn is required to run GradientBoostingClassifier and MLPClassifier.
"""
import os
import warnings

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import category_encoders
from examples.benchmarking_large import arff_loader
from examples.benchmarking_large.util import train_model, train_encoder

# The settings are taken from:
#   Data-driven advice for applying machine learning to bioinformatics problems, Olson et al.
# Following models have high variance of results: SGD, SVC and DecisionTree. That is not a big deal.
# Just be careful during result interpretation.
# Also, following models are slow because of their configuration: GradientBoosting and RandomForest.
# SGD and DecisionTree benefit from stronger regularization.
models = [SGDClassifier(loss='modified_huber', max_iter=50, tol=1e-3),
          LogisticRegression(C=1.5, penalty='l1', fit_intercept=True),
          SVC(kernel='poly', probability=True, C=0.01, gamma=0.1, degree=3, coef0=10.0),
          KNeighborsClassifier(),
          GaussianNB(),
          DecisionTreeClassifier(max_depth=4),
          GradientBoostingClassifier(loss='deviance', learning_rate=0.1, n_estimators=500, max_depth=3, max_features='log2'),
          RandomForestClassifier(n_estimators=500, max_features=0.25, criterion='entropy'),
          MLPClassifier()]

# We use Arff datasets on GitHub. But once OpenML loader will be part of scikit-learn:
#   https://github.com/scikit-learn/scikit-learn/pull/11419
# the plan is to move on OpenML.
# We ignore datasets without any polynomial feature.
# We also ignore 'splice.arff', 'anneal.arff', 'anneal.orig.arff' due to high runtime.
# Datasets sensitive to amount of regularization are:
#     breast.cancer.arff                Medium impact
#     bridges.version1.arff
#     bridges.version2.arff
#     car.arff
#     colic.arff
#     cylinder.bands.arff               Medium impact
#     flags.arff                        Large impact
#     heart.c.arff
#     hepatitis.arff
#     hypothyroid.arff
#     kr.vs.kp.arff
#     labor.arff                        Large impact
#     lymph.arff
#     nursery.arff
#     postoperative.patient.data.arff   Large impact
#     primary.tumor.arff
#     solar.flare1.arff                 Medium impact
#     solar.flare2.arff                 Medium impact
#     soybean.arff                      Large impact
#     sick.arff
#     spectrometer.arff                 Large impact
#     sponge.arff                       Large impact
#     tic-tac-toe.arff
#     trains.arff                       Medium impact (note that this is a tiny dataset -> with high variance)
datasets = [#'audiology.arff', 'autos.arff', 'breast.cancer.arff', 'bridges.version1.arff', 'bridges.version2.arff', 'car.arff',
            # 'colic.arff',
    'credit.a.arff', 'credit.g.arff', 'cylinder.bands.arff', 'flags.arff', 'heart.c.arff', 'heart.h.arff',
            'hepatitis.arff', 'hypothyroid.arff', 'kr.vs.kp.arff', 'labor.arff', 'lymph.arff', 'mushroom.arff', 'nursery.arff',
            'postoperative.patient.data.arff', 'primary.tumor.arff', 'sick.arff', 'solar.flare1.arff', 'solar.flare2.arff',
            'soybean.arff', 'spectrometer.arff', 'sponge.arff', 'tic-tac-toe.arff', 'trains.arff', 'vote.arff', 'vowel.arff']
# datasets = ['postoperative.patient.data.arff']
# datasets = ['amazon.csv', 'carvana.csv', 'erasmus.csv', 'internetusage.csv', 'ipumsla97small.csv', 'kobe.csv', 'pbcseq.csv', 'phpvcoG8S.csv', 'westnile.csv']

# We ignore encoders {BackwardDifferenceEncoder, HelmertEncoder, PolynomialEncoder and SumEncoder} because of:
#   https://github.com/scikit-learn-contrib/categorical-encoding/issues/91
encoders = [ category_encoders.TargetEncoderV2()]

# Initialization
if os.path.isfile('./output/result.csv'):
    os.remove('./output/result.csv')

# Ok...
warnings.filterwarnings('ignore')

# Loop over datasets, then over encoders, and finally, over the models
for dataset_name in datasets:
    X, y, fold_count = arff_loader.load(dataset_name)
    non_numeric = list(X.select_dtypes(exclude=[np.number]).columns.values)
    for encoder in encoders:
        print("Encoding:", dataset_name, y.name, encoder.__class__.__name__)
        folds, fit_encoder_time, score_encoder_time = train_encoder(X, y, fold_count, encoder)
        for model in models:
            print('Evaluating:', dataset_name, encoder.__class__.__name__, model.__class__.__name__)
            scores, fit_model_time, score_model_time = train_model(folds, model)

            # Log into csv
            result = pd.DataFrame([dataset_name, y.name, encoder.__class__.__name__, model.__class__.__name__, X.shape[1],
                                   folds[0][0].shape[1], fit_encoder_time, score_encoder_time, fit_model_time, score_model_time]
                                  + list(scores)).T
            if not os.path.isfile('./output/result.csv'):
                result.to_csv('./output/result.csv',
                              header=['dataset', 'target', 'encoder', 'model', 'input_features', 'output_features', 'fit_encoder_time',
                                      'score_encoder_time', 'fit_model_time', 'score_model_time', 'test_matthews', 'train_matthews',
                                      'test_auc', 'train_auc', 'test_brier', 'train_brier'], index=False)
            else:
                result.to_csv('./output/result.csv', mode='a', header=False, index=False)

print('Finished. The result was stored into ./output/result.csv.')
