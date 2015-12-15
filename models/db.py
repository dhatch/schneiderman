import os
from pony.orm import *

__ALL__ = [
    'db'
]

if not os.path.isabs(os.environ['DB_PATH']):
    raise RuntimeError("DB_PATH environment variable should be an absolute path.")

db = Database('sqlite', os.environ['DB_PATH'], create_db=True)
