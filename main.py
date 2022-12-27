import argparse

import gog
import epic
import steamSearch as steam
import amazon

defaultConfigDir = "/tmp/DoIOwn"

enableGOG = True
enableEpic = True
enableSteam = True
enableAmazon = True

parser = argparse.ArgumentParser(description="Search various game services")
parser.add_argument(
    "-c", "--config", default=defaultConfigDir, help="Path to configuration director"
)
parser.add_argument("searchterm", help="Term to search for")
args = parser.parse_args()

if enableAmazon:
    print("Setting up Amazon client...")
    amazonclient = amazon.AmazonClient(config=f"{args.config}")

if enableGOG:
    print("Setting up GOG client...")
    gogclient = gog.GOGClient(config=f"{args.config}/gog.json")

if enableEpic:
    print("Setting up Epic Games client...")
    # Epic uses legendary - can't override config location :(
    epicclient = epic.EpicClient()

if enableSteam:
    print("Setting up Steam client...")
    steamclient = steam.SteamClient(config=f"{args.config}/steam.json")

print("\n")

results = []

if enableAmazon:
    amazonResults = amazonclient.search(args.searchterm)
    if amazonResults:
        amazonResults.sort()
        results.append({"provider": "Amazon", "results": amazonResults})

if enableEpic:
    epicResults = epicclient.search(args.searchterm)
    if epicResults:
        epicResults.sort()
        results.append({"provider": "Epic", "results": epicResults})


if enableGOG:
    gogResults = gogclient.search(args.searchterm)
    if gogResults:
        gogResults.sort()
        results.append({"provider": "GOG", "results": gogResults})

if enableSteam:
    steamResults = steamclient.search(args.searchterm)
    if steamResults:
        steamResults.sort()
        results.append({"provider": "Steam", "results": steamResults})


if results:
    print(f'Found results for "{args.searchterm}"!')
    for i in results:
        prov = i["provider"]
        for j in i["results"]:
            print(f"{prov} - {j}")
else:
    print("No owned games found :(")
