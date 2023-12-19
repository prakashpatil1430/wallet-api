from django.contrib.auth.backends import ModelBackend
import hashlib
import base64
import uuid
import random
import string
from rest_framework.authtoken.models import Token

from wallet_service.models import *


def generate_random_reference_id():
    return str(uuid.uuid4())


# geeting detailed error response
def get_json_errors(error_list_data):
    __field_errors = {}

    field_errors = [(k, v[0]) for k, v in error_list_data.items()]

    for key, error_list in field_errors:
        __field_errors[key] = error_list

    return __field_errors
