import hashlib
import os

SECRET_KEY = "i_love_tfmc"
HASHED_KEY = hashlib.md5(SECRET_KEY.encode()).hexdigest()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
NATION_JSON_PATH = os.path.join(BASE_DIR, "input", "nation.json")