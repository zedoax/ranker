# Load Redis
from redis import StrictRedis

from ranker import app

redis = StrictRedis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"],
                    db=app.config["REDIS_DB"], password=app.config["REDIS_PASS"],
                    charset="utf-8", decode_responses=True)
