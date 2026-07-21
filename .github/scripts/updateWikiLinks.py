import itertools
import json
import os
import re
import time
from typing import Any
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Constants
batchSize = 50
itemsDirectory = "items"
urlPrefix = "https://hypixelskyblock.minecraft.wiki/w/"
apiUrl = "https://hypixelskyblock.minecraft.wiki/api.php"
wikiUrlInfoType = "WIKI_URL"
suffixesToRemove = [
    "(Monster)", "(NPC)", "(Rift NPC)", "(Boss)", "(Miniboss)", "(Sea Creature)", "(Animal)",
    "(Mythological Creature)",
]
colourCodePattern = re.compile(r"§.")
hoeTierPattern = re.compile(" Mk\\. I{1,3}$")
minionLevelPattern = re.compile(r"Minion [IXVixv]+$")
perfectArmorPattern = re.compile(r"Perfect (?:Helmet|Chestplate|Leggings|Boots) - Tier [A-Z]+")
trophyPattern = re.compile("(?:[Ff](?:ish|rog)|Hopper|Jumper) (?:Diamond|Gold|Silver|Bronze)$")

# Config
recheckAllLinks = os.environ.get("SHOULD_RECHECK_ALL", "false") == "true"


class ItemFile:
    name: str
    data: dict[str, Any]
    candidate: dict[str, str | None]
    page: dict[str, str | None]

    def __init__(self, path: str):
        self._path = path
        with open(self._path, "r", encoding="utf-8") as fd:
            self.name = os.path.basename(fd.name)
            self.data = json.load(fd)
        self.candidates = []
        self.page = None

    def write(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fd:
            json.dump(self.data, fd, indent=2, ensure_ascii=False)


class WikiLinkUpdater:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist={429, 500, 502, 503, 504},
        allowed_methods={"GET", "POST"},
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({
        "user-agent": "NotEnoughUpdates-Repo-CI/1.0 (+https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO)",
    })

    attemptedLinks = {}
    modifiedCount = 0
    badModifiedCount = 0

    def __init__(self, files: list[ItemFile]):
        self.files = [f for f in files if self.shouldProcess(f)]

    def shouldProcess(self, file: ItemFile) -> bool:
        if file.name.startswith("ATTRIBUTE_"):
            return False

        if "vanilla" in file.data:
            return False

        if file.data["itemid"] == "minecraft:potion":
            return False

        existingInfo = file.data.get("info", [])
        validLinks = [
            link for link in existingInfo if link.startswith(urlPrefix)
        ]
        if validLinks and existingInfo == validLinks and len(validLinks) == 1 and not recheckAllLinks:
            return False

        return True

    def prepareWikiLinks(self) -> None:
        for file in self.files:
            formattedName = self.formatNameForSearch(file.data)
            file.candidates.append(formattedName)

    def fetchWikiLinks(self):
        done = 0
        candidate_to_files: dict[str, list[ItemFile]] = {}
        for file in self.files:
            for candidate in file.candidates:
                if candidate_to_files.get(candidate) is None:
                    candidate_to_files[candidate] = []
                candidate_to_files[candidate].append(file)
        candidates = list(candidate_to_files.keys())

        for batch in itertools.batched(candidates, batchSize):
            print(f"\rFetching wiki pages... {done}/{len(candidates)}", end="", flush=True)

            response = self.session.get(
                apiUrl,
                params={
                    "action": "query",
                    "format": "json",
                    "titles": "|".join(batch),
                    # "redirects": 1,
                    "formatversion": 2,
                }
            )

            if not response.ok:
                print(f"\nFailed to fetch batch ({response.status_code} {response.reason})")
                done += batchSize
                continue

            payload = response.json()
            for page in payload["query"]["pages"]:
                if page.get("missing"):
                    continue

                matches = {}
                candidate = page["title"]
                if files := candidate_to_files.get(candidate):
                    for file in files:
                        matches[file] = candidate
                else:
                    for transformation in payload["query"].get("normalized", []):
                        candidate = transformation["from"]
                        if files := candidate_to_files.get(candidate):
                            for file in files:
                                matches[file] = candidate

                for file, candidate in matches.items():
                    if not file.page:
                        file.page = candidate

            done += batchSize
            time.sleep(0.1)

        print()

    def processItemFiles(self) -> None:
        for file in self.files:
            print(f"Processing {file.name}...")

            formattedName = self.formatNameForSearch(file.data)

            fileModified = False

            if file.page:
                if not file.data.get("infoType"):
                    file.data["infoType"] = wikiUrlInfoType
                    fileModified = True
            else:
                print(f"Neither page exists for {file.name}, {formattedName}")

            wikiLink = self.getUrl(file.page)

            infoLinks_auto = []
            if wikiLink:
                infoLinks_auto.append(wikiLink)

            existingInfo = file.data.get("info", [])

            if len(infoLinks_auto) < len(existingInfo):
                continue

            if infoLinks_auto != existingInfo:
                file.data["info"] = infoLinks_auto

                print(f"Modified {file.name}")
                print(f"existing info: {existingInfo}")
                print(f"new info: {infoLinks_auto}")

                fileModified = True

            if fileModified:
                self.modifiedCount += 1
                file.write()

    @classmethod
    def formatNameForSearch(cls, data: dict[str, Any]) -> str:
        itemId = data["internalname"]
        name = cls.stripColor(data["displayname"])
        name = name.strip()
        if "[Lvl {LVL}] " in name:
            name = name.replace("[Lvl {LVL}] ", "") + " Pet"

        for suffix in suffixesToRemove:
            if name.endswith(suffix):
                name = name.removesuffix(suffix).strip()
                break
        name = cls.capitalizeWords(name)

        if name == "Enchanted Book":
            for line in data["lore"]:
                if not line.strip() or "Combinable in Anvil" in line:
                    continue
                ench = re.sub(r"§.", "", line)
                ench = re.sub(r" [IVXLCDM]+$", "", ench)
                return ench

        if match := hoeTierPattern.search(name):
            return name[0:match.start()]

        if name.endswith("Gemstone") and name != "Glossy Gemstone":
            return "Gemstone"

        name = name.removeprefix("◆ ")
        name = name.removeprefix(" ")

        if " Balloon Hat " in name:
            return " ".join(name.split(" ")[1:])

        if ("_GENERATOR_" in itemId and minionLevelPattern.search(name)) or " Rune " in name or trophyPattern.search(name):
            return " ".join(name.split(" ")[:-1])

        if name.endswith("Minion Xii Upgrade Stone"):
            return name.replace(" Xii ", " XII ")

        if perfectArmorPattern.fullmatch(name):
            return "Perfect Armor"

        return name

    @staticmethod
    def stripColor(string: str) -> str:
        return colourCodePattern.sub("", string)

    @staticmethod
    def capitalizeWords(string: str) -> str:
        return "".join(word.capitalize() for word in re.split(r"([ _-])", string) if word not in ["of", "the", "to"])

    @staticmethod
    def getUrl(page: str | None) -> str | None:
        if not page:
            return None
        return urlPrefix + quote(page.replace(" ", "_"), safe='"#()+,/:')


def main() -> None:
    itemFiles = [f for f in os.listdir(itemsDirectory) if os.path.isfile(os.path.join(itemsDirectory, f))]
    jsonFiles = [f for f in itemFiles if f.endswith('.json')]
    files = []
    for filename in jsonFiles:
        filePath = os.path.join(itemsDirectory, filename)
        file = ItemFile(filePath)
        files.append(file)

    updater = WikiLinkUpdater(files)

    updater.prepareWikiLinks()
    updater.fetchWikiLinks()
    updater.processItemFiles()


if __name__ == "__main__":
    main()
