import urllib.parse
import time
import json

from gog import consts
import webview
import requests

# Helper function to exctract the login code from a webview
def checkURL(window, cl):
    while not window.get_current_url().startswith(consts.gogEmbedDomain):
        time.sleep(0.1)

    parsedURL = urllib.parse.urlparse(window.get_current_url())
    queries = urllib.parse.parse_qs(parsedURL.query)
    cl.loginCode = queries["code"][0]
    window.destroy()


class GOGClient:
    def __init__(self, config):
        self.configPath = config
        # Check tokens & login
        self.getValidLogin()

    # Set up the properties to read & write the auth & refresh tokens
    @property
    def authToken(self):
        if hasattr(self, "_authToken"):
            return self._authToken
        try:
            with open(self.configPath, encoding="utf-8") as json_file:
                data = json.load(json_file)
                self._authToken = data["authToken"]
                return data["authToken"]
        except:  # Anything wrong, default to none
            return None

    @authToken.setter
    def authToken(self, authToken):
        self._authToken = authToken
        # Write the new token to file
        self._writeToFile()

    @property
    def refreshToken(self):
        if hasattr(self, "_refreshToken"):
            return self._refreshToken
        try:
            with open(self.configPath, encoding="utf-8") as json_file:
                data = json.load(json_file)
                self._refreshToken = data["refreshToken"]
                return data["refreshToken"]
        except:  # Anything wrong, default to none
            return None

    @refreshToken.setter
    def refreshToken(self, refreshToken):
        self._refreshToken = refreshToken
        self._writeToFile()

    def _writeToFile(self):
        outDict = {"authToken": self.authToken, "refreshToken": self.refreshToken}
        with open(self.configPath, "w", encoding="utf-8") as outFile:
            json.dump(outDict, outFile, indent=4)

    def getValidLogin(self):
        # Check if auth token is valid. If not, try using refresh. If that fails, prompt for login
        if not self.authTokenisValid(self.authToken):
            if not self.getAuthFromRefresh(self.refreshToken):
                # TODO: Error handling if all of these fail?
                self.authToken, self.refreshToken = self.interactiveLogin()

    def authTokenisValid(self, token):
        # Load the userData json - tests for a valid auth token
        try:
            r = requests.get(
                consts.gogUserDataURL,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            return data["isLoggedIn"]
        except:
            # This can be an http error code, or timeout, or no isLoggedIn var - frankly we don't care
            return False

    def getAuthFromRefresh(self, refreshToken):
        try:
            r = requests.get(consts.gogRefreshToken + refreshToken, timeout=10)
            r.raise_for_status()
            data = r.json()
            if self.authTokenisValid(data["access_token"]):
                self.authToken = data["access_token"]
                self.refreshToken = data["refresh_token"]
                return True
            return False
        except:
            return False

    def interactiveLogin(self):
        # Create a webview
        window = webview.create_window(
            "GOG Login", consts.gogAuthURL, **consts.webviewOpts
        )
        # This returns when checkURL finishes. It sets self.loginCode
        webview.start(checkURL, [window, self])

        if not self.loginCode:
            print("Failed to sign in to GOG")
            raise

        # Get a token from the auth code
        r = requests.get(consts.gogInitialToken + self.loginCode, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data["access_token"], data["refresh_token"]

    def getGameList(self):
        try:
            r = requests.get(
                consts.gogSearchURL,
                headers={"Authorization": f"Bearer {self.authToken}"},
                timeout=10,
            )
            data = r.json()
            return data["products"]

        except:
            raise

    def search(self, term):
        data = self.getGameList()
        results = []
        for game in data:
            title = game["title"].lower()
            if term.lower() in title:
                results.append(game["title"])

        return results
