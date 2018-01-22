import logging
import glob
import numpy as np
import random
import math
import time

import matplotlib.pyplot as plt

import global_flags_constanst as gfc
import support_functions as sf

from models import BaseModel
from models import PolynomialModel
from models import XGBRegressorModel
from models import RidgeRegressionModel
from models import KernelRidgeRegressionModel


logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(gfc.LOGGING_LEVEL)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")

handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(gfc.LOGGING_LEVEL)



if __name__ == "__main__":

    # Separate models will be fit for the
    # specimen with the following number of atoms.
    # number_of_total_atoms: rank
    # noa = 40 and noa = 80 not included
    # Simple models do not work for them.

    additional_feature_list = ["rho_data",
                               #"percentage_atom_data",
                               "unit_cell_data",
                               "nn_bond_parameters_data",
                               # "angles_and_rs_data",
                               "ewald_sum_data",
                               "preliminary_predictions_data"]

    seed = int(random.randint(1, 2**16 - 1))
    colsample_bytree = random.random()
    subsample = random.random()
    model_parameters = {"max_depth": 6,
                        "learning_rate": 0.1,
                        "n_estimators": 300,
                        "silent": True,
                        "objective": 'reg:linear',
                        "booster": 'gbtree',
                        "n_jobs": 1,
                        "nthread": None,
                        "gamma": 0.0,
                        "min_child_weight": 5,
                        "max_delta_step": 0,
                        "subsample": subsample,
                        "colsample_bytree": colsample_bytree,
                        "colsample_bylevel": 1,
                        "reg_alpha": 0,
                        "reg_lambda": 1,
                        "scale_pos_weight": 1,
                        "base_score": 0.5,
                        "random_state": seed + 1,
                        "seed": seed,
                        "missing": None}

    # model_parameters = {"alpha": 0.5,
    #                     "kernel": "chi2",
    #                       "gamma": 0.1,
    #                       "degree": 10,
    #                       "coef0": 1,
    #                       "n_features": None,
    #                       "max_features": None,
    #                       "validation_data": None}

    bg_general_model, _ = sf.get_model_for_noa(-1,
                                               additional_feature_list,
                                               model_class=XGBRegressorModel,
                                               model_parameters=model_parameters,
                                               y_type="band_gap")


    # fe_general_model = get_model_for_noa(-1,
    #                                      additional_feature_list,
    #                                      model_class=XGBRegressorModel,
    #                                      model_parameters=xgb_regressor_model_parameters,
    #                                      y_type="formation_energy")


    logger.info("-------------------------------")
    logger.info("---------Hyper tunning---------")
    logger.info("-------------------------------")

    minimal_avg = math.inf
    minimal_params = {}
    for i in range(1000):
        start = time.time()
        logger.info("Hyper tunning i: {0}".format(i))

        max_depth = random.randint(2, 40)

        lr = np.array([0.001, 0.005, 0.01, 0.03, 0.05, 0.1])
        learning_rate = np.random.choice(lr, 1)[0]

        n_estimators = random.randint(10, 1000)

        b = np.array(["gbtree", "gblinear", "dart"])
        booster = np.random.choice(b, 1)[0]

        gamma = random.uniform(0, 2)

        min_child_weight = random.randint(1, 10)
        max_delta_step = random.randint(0, 10)

        reg_alpha = random.uniform(0, 2)
        reg_lambda = random.uniform(0, 2)

        scale_pos_weight = random.uniform(0, 2)

        random_state = int(random.randint(1, 2 ** 16 - 1))
        seed = int(random.randint(1, 2 ** 16 - 1))

        model_parameters = {"max_depth": max_depth,
                            "learning_rate": learning_rate,
                            "n_estimators": n_estimators,
                            "silent": True,
                            "objective": 'reg:linear',
                            "booster": booster,
                            "n_jobs": 1,
                            "nthread": None,
                            "gamma": gamma,
                            "min_child_weight": min_child_weight,
                            "max_delta_step": max_delta_step,
                            "subsample": subsample,
                            "colsample_bytree": colsample_bytree,
                            "colsample_bylevel": 1,
                            "reg_alpha": reg_alpha,
                            "reg_lambda": reg_lambda,
                            "scale_pos_weight": scale_pos_weight,
                            "base_score": 0.5,
                            "random_state": random_state,
                            "seed": seed,
                            "missing": None}

        logger.info("--- Parameters used for model ---")

        for key, val in sorted(model_parameters.items(), key=lambda t: t[0]):
            logger.info("{0}: {1}".format(key, val))

        logger.info("--- Model selection ---")
        bg_general_model, valid_avg = sf.get_model_for_noa(-1,
                                                           additional_feature_list,
                                                           model_class=XGBRegressorModel,
                                                           model_parameters=model_parameters,
                                                           y_type="band_gap")

        if valid_avg < minimal_avg:
            minimal_avg = valid_avg
            minimal_params = model_parameters

        stop = time.time()

        logger.info("Times for one iteration: {0}".format(stop - start))

    logger.info(minimal_avg)
    logger.info(minimal_params)