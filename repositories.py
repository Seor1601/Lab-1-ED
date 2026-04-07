import time


class ProfileRepository:
    def __init__(self, store):
        self.store = store

    def create_user(self, username, password):
        key = "player:" + username
        record = self.store.get(key)

        if record is not None:
            return False

        # [username, password, best_score, games, last_score]
        data = [username, password, 0, 0, 0]
        self.store.append_record("profile", key, data)
        return True

    def login_user(self, username, password):
        key = "player:" + username
        record = self.store.get(key)

        if record is None:
            return None

        data = record[2]

        if data[1] == password:
            return data

        return None

    def get_profile(self, username):
        key = "player:" + username
        record = self.store.get(key)

        if record is None:
            return None

        return record[2]

    def save_profile(self, username, password, best_score, games, last_score):
        key = "player:" + username
        data = [username, password, best_score, games, last_score]
        self.store.append_record("profile", key, data)


class SettingsRepository:
    def __init__(self, store):
        self.store = store

    def get_settings(self):
        record = self.store.get("settings:game")

        if record is None:
            return None

        return record[2]

    def save_settings(self, volume, difficulty, fullscreen):
        data = [volume, difficulty, fullscreen]
        self.store.append_record("settings", "settings:game", data)


class LeaderboardRepository:
    def __init__(self, store):
        self.store = store

    def save_score(self, username, score):
        key = "score:" + username + ":" + str(time.time())
        data = [username, score]
        self.store.append_record("score", key, data)

    def get_top_scores(self, limit=5):
        records = self.store.get_all_records()
        scores = []

        for record in records:
            if record[0] == "score":
                data = record[2]
                scores.append((data[0], data[1]))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]