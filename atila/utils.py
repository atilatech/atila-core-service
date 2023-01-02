import string
import random


def random_string(n=16):
    random_string_value = ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
    return random_string_value


class ModelUtils:

    @staticmethod
    def empty_list():
        return []

    @staticmethod
    def empty_dict():
        return {}
