# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 23:55:22 2021

@author: Reza
"""

class InternalServerError(Exception):
    pass

class SchemaValidationError(Exception):
    pass

class DataNotExistsError(Exception):
    pass

class KeyError(Exception):
    pass

class ThresholdError(Exception):
    pass

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    "DataNotExistsError": {
        "message": "Data does not exists",
        "status": 400
    },
    "KeyError": {
        "message": "Search parameter not found in data",
        "status": 400
    },
    "ThresholdError": {
        "message": "Threshold is missing",
        "status": 400
    }
}