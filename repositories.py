class ProfileRepository:
    def __init__(self, store):
        self.store = store

    def save_profile(self, player_id, player_name, best_score, total_games, last_score):
        data = [player_id, player_name, best_score, total_games, last_score]
        self.store.append_record('profile', 'player:' + player_id, data)

    def get_profile(self, player_id):
        record = self.store.get('player:' + player_id)
        if record is None:
            return None
        return record[2]                                                        


class SettingsRepository:
    def __init__(self, store):
        self.store = store

    def save_settings(self, volume, difficulty, fullscreen):
        data = [volume, difficulty, fullscreen]
        self.store.append_record('settings', 'settings:main', data)

    def get_settings(self):
        record = self.store.get('settings:main')
        if record is None:
            return None
        return record[2]


class LeaderboardRepository:
    def __init__(self, store):
        self.store = store

    def save_score(self, player_name, score):
        records = self.store.get_all_records()
        score_id = 'score:' + str(len(records) + 1)
        data = [player_name, score]
        self.store.append_record('score', score_id, data)

    def get_top_scores(self, top_n=10):
        all_records = self.store.get_all_records()
        scores = []
        for record in all_records:
            if len(record) >= 3 and record[0] == 'score':
                data = record[2]
                scores.append(data)

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_n]
