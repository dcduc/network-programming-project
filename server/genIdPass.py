import random
from string import digits, ascii_letters


def genIDPassword():
    ID = "".join(random.choices(digits, k=10))
    password = "".join(random.choices(digits + ascii_letters, k=9))
    return ID, password
