# Utils for bottle
import os

def check_pass(username, password):
    admin_pass = os.getenv("ADMIN_PWD")
    return username=="admin" and password==admin_pass
