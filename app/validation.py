"""

"""

__author__ = ["Clément Besnier <admin@skilvit.fr>", ]


def validate_id(value):
    if type(value) == int:
        return str(value).isdigit()
    elif type(value) == str:
        return value.isdigit()
    return False


def validate_code_postal(value):
    return True


def validate_city(value):
    return True
