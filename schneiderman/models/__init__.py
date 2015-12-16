from pony.orm import *

from .db import db
from .models import Player, PlayerGame, Team


def reset_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
