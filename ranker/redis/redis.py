from ranker.redis import redis


def put_challenge(challenger, challenged, season):
    if challenge_exists(challenger, challenged) or challenge_exists(challenged, challenger):
        raise ValueError('Error: {0} is already challenging {1}'.format(challenger, challenged))
    redis.hmset(','.join((challenger, challenged)), {
        "season": season,
        "challenger": challenger,
        "challenged": challenged,
        "accepted": "False"
    })


def pop_challenge(challenger, challenged):
    if not challenge_exists(challenger, challenged) and not challenge_exists(challenged, challenger):
        raise ValueError('Error: There is no challenge between {0} and {1}'.format(challenger, challenged))
    query_string = ','.join((challenger, challenged))
    challenge = redis.hgetall(query_string)
    if not challenge:
        query_string = ','.join((challenged, challenger))
        challenge = redis.hgetall(query_string)
    if not challenge["accepted"] == "True":
        raise PermissionError("Error: The challenge between {0} and {1} has not been accepted")
    redis.delete(query_string)
    return challenge["season"], challenge["challenger"]


def del_challenge(challenger, challenged):
    if not challenge_exists(challenger, challenged) and not challenge_exists(challenged, challenger):
        raise ValueError('Error: There is no challenge between {0} and {1}'.format(challenger, challenged))
    redis.delete(','.join((challenger, challenged)))
    redis.delete(','.join((challenged, challenger)))


def accept_challenge(challenger, challenged):
    if not challenge_exists(challenger, challenged):
        raise ValueError('Error: There is no challenge between {0} and {1}'.format(challenger, challenged))
    query_string = ','.join((challenger, challenged))
    challenge = redis.hgetall(query_string)
    challenge["accepted"] = "True"
    redis.hmset(query_string, challenge)


def challenge_exists(challenger, challenged):
    if redis.exists(','.join((challenger, challenged))):
        return True
    return False
