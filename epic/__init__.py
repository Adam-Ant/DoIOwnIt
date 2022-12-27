# I am so glad legendary does the hard work for us
from legendary.core import LegendaryCore
from legendary.models.exceptions import InvalidCredentialsError
from legendary.utils.webview_login import do_webview_login


# A lot of this logic is lifted from the Legendary CLI.
class EpicClient:
    def __init__(self):
        self.core = LegendaryCore()
        self.getValidLogin()

    def getValidLogin(self):
        # Check tokens & login
        if not self.checkValidLogin():
            if not self.interactiveLogin():
                print("Error logging into Epic Games")

    def checkValidLogin(self):
        try:
            if self.core.login():
                return True
        except ValueError:
            pass
        except InvalidCredentialsError:
            # If its invalid, nuke the creds so we can add new ones
            self.core.lgd.invalidate_userdata()
        return False

    def interactiveLogin(self):
        # Just invoke the legendary function, it's better than anything I could write!
        return do_webview_login(callback_code=self.core.auth_ex_token)

    def search(self, term):
        self.getValidLogin()

        results = []

        all_games = self.core.get_game_list()
        for game in all_games:
            # print(game.app_title)
            title = game.app_title.lower()
            if term.lower() in title:
                results.append(game.app_title)

        return results
