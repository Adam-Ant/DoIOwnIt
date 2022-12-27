import os
import json
import logging


class ConfigManager:
    """
    Handles writing and reading from config with automatic in memory caching
    TODO: Make memory caching opt out in some cases
    """

    def __init__(self, configpath):
        self.config_path = configpath
        self.logger = logging.getLogger("CONFIG")
        self.cache = {}

    def _join_path_name(self, name: str) -> str:
        return os.path.join(self.config_path, f"amazon_{name}.json")

    def remove(self, store):
        """
        Remove file
        """
        path = self._join_path_name(store)
        if os.path.exists(path):
            os.remove(path)

    def write(self, store: str, data: any, raw=False):
        """
        Stringifies data to json and overrides file contents
        """
        directory, _ = os.path.split(self._join_path_name(store))
        os.makedirs(directory, exist_ok=True)
        file_path = self._join_path_name(store)
        self.cache.update({store: data})
        mode = "w"
        if raw:
            parsed = data
            mode += "b"
        else:
            parsed = json.dumps(data)
        with open(file_path, mode=mode, encoding="utf-8") as stream:
            stream.write(parsed)

    def get(self, store: str, key: str or list = None) -> any or None:
        """
        Get value of provided key from store
        Double slash separated keys can access object values
        e.g tokens//bearer//access_token
        If no key provided returns whole file
        """
        file_path = self._join_path_name(store)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            if not self.cache.get(store):
                with open(file_path, mode="r", encoding="utf-8") as stream:
                    data = stream.read()
                parsed = json.loads(data)
                self.cache.update({store: parsed})
            else:
                parsed = self.cache[store]
            if not key:
                return parsed
            if isinstance(key, str):
                keys = key.split("//")
                return self._get_value_based_on_keys(parsed, keys)
            if isinstance(key, list):
                array = []
                for option in key:
                    keys = option.split("//")
                    array.append(self._get_value_based_on_keys(parsed, keys))
                return array

        if isinstance(key, list):
            return [None for i in key]
        return None

    def _get_value_based_on_keys(self, parsed, keys):
        if len(keys) > 1:
            iterator = parsed.copy()
            for key in keys:
                iterator = iterator[key]

            return iterator
        return parsed.get(keys[0])
