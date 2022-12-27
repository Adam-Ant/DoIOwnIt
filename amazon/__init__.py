from amazon import consts
from amazon.auth import AuthenticationManager
from amazon.config import ConfigManager

import logging
import hashlib
import requests

# Most of this code is adapted from the wonderfile FOSS Amazon Games client Nile.
# It's saved me countless hours of work, so thanks :)
# https://github.com/imLinguin/nile/


class AmazonClient:
    def __init__(self, config):
        self.config_manager = ConfigManager(config)
        self.session_manager = requests.Session()
        self.session_manager.headers.update({"User-Agent": "AGSLauncher/1.0.0"})
        self.auth_manager = AuthenticationManager(
            self.config_manager, self.session_manager
        )
        self.logger = logging.getLogger("LIBRARY")
        self.do_login()

    def do_login(self):
        if self.auth_manager.is_logged_in():
            if self.auth_manager.is_token_expired():
                self.auth_manager.refresh_token()
        else:
            self.auth_manager.login()

    def request_sds(self, target, token, body):
        headers = {
            "X-Amz-Target": target,
            "x-amzn-token": token,
            "User-Agent": "com.amazon.agslauncher.win/2.1.7437.6",
            "UserAgent": "com.amazon.agslauncher.win/2.1.7437.6",
            "Content-Type": "application/json",
            "Content-Encoding": "amz-1.0",
        }
        response = self.session_manager.post(
            f"{consts.AMAZON_SDS}/amazon/",
            headers=headers,
            json=body,
        )

        return response

    def _get_sync_request_data(self, serial, nextToken=None):
        request_data = {
            "Operation": "GetEntitlementsV2",
            "clientId": "Sonic",
            "syncPoint": None,
            "nextToken": nextToken,
            "maxResults": 50,
            "productIdFilter": None,
            "keyId": "d5dc8b8b-86c8-4fc4-ae93-18c0def5314d",
            "hardwareHash": hashlib.sha256(serial.encode()).hexdigest().upper(),
        }

        return request_data

    def get_games_list(self):
        token, serial = self.config_manager.get(
            "user",
            [
                "tokens//bearer//access_token",
                "extensions//device_info//device_serial_number",
            ],
        )
        games = []
        nextToken = None
        while True:
            request_data = self._get_sync_request_data(serial, nextToken)

            response = self.request_sds(
                "com.amazonaws.gearbox.softwaredistribution.service.model.SoftwareDistributionService.GetEntitlementsV2",
                token,
                request_data,
            )
            json_data = response.json()
            games.extend(json_data["entitlements"])

            if "nextToken" not in json_data:
                break

            # making next request
            nextToken = json_data["nextToken"]

            if not response.ok:
                self.logger.error("There was an error syncing library")
                self.logger.debug(response.content)
                return None

        # Remove duplicates
        games_dict = {}
        for game in games:
            if not games_dict.get(game["product"]["id"]):
                games_dict[game["product"]["id"]] = game

        return games_dict.values()

    def search(self, term):
        data = self.get_games_list()
        results = []

        for game in data:
            title = game["product"]["title"].lower()
            if term.lower() in title:
                results.append(game["product"]["title"])

        return results
