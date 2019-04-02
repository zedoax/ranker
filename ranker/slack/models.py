class SlackMatch:
    def __init__(self, player_one, player_two):
        self.players = []
        self.players.append(player_one)
        self.players.append(player_two)
        self.accepted = False

    def accept(self):
        self.accepted = True

    def get_player(self, user=None):
        if user is None:
            player = self.players[0]
            self.players.remove(player)
            return player
        for player in self.players:
            if player == user:
                self.players.remove(player)
                return player
        return None

    def contains_player(self, user):
        for player in self.players:
            if player == user:
                return player
        return None

    def add_player(self, user):
        self.players.append(user)
