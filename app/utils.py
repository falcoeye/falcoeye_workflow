import os
import base64

TYPE_MAP = {"int": int, "str": str, "float": float, "list": list}


def check_type(variable, str_type):
    return type(variable) == TYPE_MAP[str_type]


def try_cast(variable, str_type):
    try:
        variable = TYPE_MAP[str_type](variable)
        return variable
    except:
        return False

def array_to_base64(arr):
    return base64.b64encode(arr)

def mkdir(path):
    if os.path.exists(path):
        return
    os.makedirs(path)


def message(status, message):
    response_object = {"status": status, "message": message}
    return response_object


def validation_error(status, errors):
    response_object = {"status": status, "errors": errors}

    return response_object


def err_resp(msg, reason, code):
    err = message(False, msg)
    err["error_reason"] = reason
    return err, code


def internal_err_resp():
    err = message(False, "Something went wrong during the process!")
    err["error_reason"] = "server_error"
    return err, 500
