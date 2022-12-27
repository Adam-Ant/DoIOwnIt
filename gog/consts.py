webviewOpts = {"height": 800, "width": 400, "frameless": True, "on_top": True}

gogAuthDomain = "https://auth.gog.com"
gogAuthURL = f"{gogAuthDomain}/auth?client_id=46899977096215655&redirect_uri=https://embed.gog.com/on_login_success?origin=client&response_type=code&layout=client2"  # noqa: E501
gogTokenURL = f"{gogAuthDomain}/token?client_id=46899977096215655&client_secret=9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
gogInitialToken = f"{gogTokenURL}&grant_type=authorization_code&redirect_uri=https://embed.gog.com/on_login_success?origin=client&code="
gogRefreshToken = f"{gogTokenURL}&grant_type=refresh_token&refresh_token="

gogEmbedDomain = "https://embed.gog.com"
gogUserDataURL = f"{gogEmbedDomain}/userData.json"
gogSearchURL = f"{gogEmbedDomain}/account/getFilteredProducts?mediaType=1&search="
