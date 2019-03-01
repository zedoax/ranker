from ranker.utils import ldap_get_member_slack


def find_match(match_list, player):
    for match in match_list:
        if player in match.players:
            return match
    return None


def csh_create_match(winner, loser, winner_score, loser_score, witness):
    winner_profile = ldap_get_member_slack(winner)
    loser_profile = ldap_get_member_slack(loser)
    witness_profile = ldap_get_member_slack(witness)

    if winner_profile is None:
        return {'error': 'winner'}, False
    if loser_profile is None:
        return {'error': 'loser'}, False
    if witness_profile is None:
        return {'error': 'witness'}, False

    return {
        'winner_uid': winner_profile.uid,
        'loser_uid': loser_profile.uid,
        'witness_uid': witness_profile.uid,
        'winner_score': winner_score,
        'loser_score': loser_score
    }, True


def slack_convert_players(string):
    user_start = string.find('<')
    user_index = string.find('@')
    user_trans = string.find('|')
    user_end = string.find('>')
    if user_start == -1 or user_index == -1 or user_trans == -1 or user_end == -1:
        return string
    return string[:user_start] + string[user_index+1:user_trans] + string[user_end+1:]
