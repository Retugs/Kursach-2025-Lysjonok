import json
import os

class BeamLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.profiles = self._load_profiles()

    def _load_profiles(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл {self.file_path} не найден.")
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def get_profile(self, profile_name):
        profile = self.profiles.get(profile_name)
        if profile is None:
            raise ValueError(f"Профиль '{profile_name}' не найден в файле {self.file_path}.")
        return profile