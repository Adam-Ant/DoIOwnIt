import json
import sys

import requests
from steam.webapi import WebAPI


class SteamClient:
    def __init__(self, config):

        self.configPath = config
        # Check tokens & login
        self.initCount = 0
        self.initAPI()
        self.checkSteamID()

    def checkSteamID(self):
        if not self.steamID:
            # If nil, prompt for SteamID
            self.promptForSteamID()

        id = self.steamID

        # Check to see if its a private profile
        resp = self.api.ISteamUser.GetPlayerSummaries(steamids=id)
        try:
            if resp["response"]["players"][0]["communityvisibilitystate"] == 3:
                self.steamID = id
            else:
                print(
                    "Error: Steam profile set to private. Cannot continue with private profile due to API limitations."
                )
                sys.exit(1)

        except IndexError:
            # If its not a valid ID, go again.
            self.steamID = None
            if self.initCount < 5:
                self.initCount += 1
                self.checkSteamID()
            else:
                raise

    def promptForSteamID(self):
        print(
            "Enter a valid 17 character SteamID. Can be found at https://steamdb.info/calculator/"
        )
        self.steamID = input("SteamID: ")

    def initAPI(self):
        try:
            self.api = WebAPI(key=self.apiKey)
        except requests.HTTPError:
            self.initCount += 1

            # Recursion is fun!
            if self.initCount < 5:
                self.promptForKey()
                self.initAPI()
            else:
                print("Error setting up Steam!")
                return False
        return True

    # Set up the properties to read & write the api key & SteamID
    @property
    def apiKey(self):
        if hasattr(self, "_apiKey"):
            return self._apiKey
        try:
            with open(self.configPath, encoding="utf-8") as json_file:
                data = json.load(json_file)
                self._apiKey = data["apiKey"]
                return data["apiKey"]
        except:  # Anything wrong, default to a dummy val that will prompt for manual auth.
            return "XXXXNONEXXXX"

    @apiKey.setter
    def apiKey(self, apiKey):
        self._apiKey = apiKey
        # Write the new token to file
        self._writeToFile()

    @property
    def steamID(self):
        if hasattr(self, "_steamID"):
            return self._steamID
        try:
            with open(self.configPath, encoding="utf-8") as json_file:
                data = json.load(json_file)
                self._steamID = data["steamID"]
                return self._steamID
        except:  # Anything wrong, default to none
            return None

    @steamID.setter
    def steamID(self, steamID):
        self._steamID = steamID
        self._writeToFile()

    def _writeToFile(self):
        outDict = {"apiKey": self.apiKey, "steamID": self.steamID}
        with open(self.configPath, "w", encoding="utf-8") as outFile:
            json.dump(outDict, outFile, indent=4)

    def promptForKey(self):
        print(
            "Enter a valid Steam API key.\nCan be obtained for free from https://steamcommunity.com/dev/apikey"
        )
        self.apiKey = input("API Key: ")

    def getOwnedGames(self, id):
        resp = self.api.IPlayerService.GetOwnedGames(
            steamid=id,
            include_appinfo=True,
            include_played_free_games=True,
            appids_filter="",
            include_free_sub=True,
            language="en",
            include_extended_appinfo=False,
        )
        return resp["response"]

    def search(self, term):
        try:
            data = self.getOwnedGames(self.steamID)
            results = []

            for game in data["games"]:
                title = game["name"].lower()
                if term.lower() in title:
                    results.append(game["name"])

            return results

        except:
            raise
