from flask import request
from functools import wraps

def sizes(handle):
    '''Accept a "size" query parameter with a default of "large"'''

    @wraps(handle)
    def wrapper(*args, **kwargs):
        size = request.args.get('size', 'large')
        return handle(size, *args, **kwargs)
    return wrapper
