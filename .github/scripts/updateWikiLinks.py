import os
import json
import urllib3
import re
from urllib.parse import urlparse, unquote

# Constants
itemsDirectory = "items"
unofficialLink = "https://hypixelskyblock.minecraft.wiki/w/"
officialLink = "https://wiki.hypixel.net/"
wikiUrlInfoType = "WIKI_URL"

httpPool = urllib3.PoolManager()
attemptedLinks = {}
modifiedCount = 0
badModifiedCount = 0

suffixesToRemove = [
    "(Monster)", "(NPC)", "(Rift NPC)", "(Boss)", "(Miniboss)", "(Sea Creature)", "(Animal)",
    "(Mythological Creature)"
]

linkTransformationUnofficial = {
    "Barn_Skin": unofficialLink + "Barn_Skins",
    "_Rune": unofficialLink + "Runes"
}

hoeTierPattern = re.compile("_Mk\\._I{1,3}$")


def getItemFiles() -> list[str]:
    itemFiles = [f for f in os.listdir(itemsDirectory
) if os.path.isfile(os.path.join(itemsDirectory
, f))]
    jsonFiles = [f for f in itemFiles if f.endswith('.json')]
    return jsonFiles


def _replace_title_case_prepositions(name: str) -> str:
    name = name.replace("_Of_", "_of_")
    name = name.replace("_The_", "_the_")
    name = name.replace("_To_", "_to_")
    return name

def _escape_wiki_links(links: list[str]) -> list[str]:
    for i, link in enumerate(links):
        links[i] = link.replace("=", "\\u003d").replace("'", "\\u0027")
    return links

def _page_title_from_url(pageUrl: str) -> tuple[str, str]:
    parsed = urlparse(pageUrl)
    apiUrl = f"https://{parsed.netloc}/api.php"
    pageTitle = unquote(parsed.path.removeprefix("/").removeprefix("w/").removeprefix("wiki/"))
    return apiUrl, pageTitle

def _batch_page_existence_requests(pageUrls: list[str]):
    processed = 0
    for i in range(0, len(pageUrls), 50):
        batch = pageUrls[i:i + 50]
        apiUrl, _ = _page_title_from_url(batch[0])
        hostname = urlparse(apiUrl).netloc
        titlesByUrl = {}
        titles = []
        print(f"Performing batch page lookup for {hostname} ({processed:,}/{len(pageUrls):,})")
        for pageUrl in batch:
            batchApiUrl, pageTitle = _page_title_from_url(pageUrl)
            if batchApiUrl != apiUrl:
                raise ValueError("Batch contains mixed wiki hosts")
            titlesByUrl[pageUrl] = pageTitle
            titles.append(pageTitle)
        processed += len(batch)

        response = httpPool.request(
            "GET",
            apiUrl,
            fields={
                "action": "query",
                "format": "json",
                "titles": "|".join(titles),
                "redirects": 1,
                "formatversion": 2,
            },
        )

        if response.status != 200:
            print(f"Failed to fetch batch from {apiUrl} ({response.status})")
            for pageUrl in batch:
                attemptedLinks[pageUrl] = False
            continue

        payload = json.loads(response.data.decode("utf-8"))
        titleStatuses = {}
        for page in payload.get("query", {}).get("pages", []):
            titleStatuses[page["title"]] = "missing" not in page

        for redirect in payload.get("query", {}).get("redirects", []):
            titleStatuses[redirect["from"]] = titleStatuses.get(redirect["to"], False)

        for normalized in payload.get("query", {}).get("normalized", []):
            titleStatuses[normalized["from"]] = titleStatuses.get(normalized["to"], False)

        for pageUrl, pageTitle in titlesByUrl.items():
            attemptedLinks[pageUrl] = titleStatuses.get(pageTitle, False)

def _prime_page_existence_cache(pageUrls: list[str]):
    uniqueUrls = list(dict.fromkeys(pageUrls))
    urlsByApiUrl = {}
    for pageUrl in uniqueUrls:
        apiUrl, _ = _page_title_from_url(pageUrl)
        urlsByApiUrl.setdefault(apiUrl, []).append(pageUrl)

    for _, urls in urlsByApiUrl.items():
        _batch_page_existence_requests(urls)

def _candidate_page_urls(formattedName: str) -> list[str]:
    urls = [
        unofficialLink + modifyUnofficialItem(formattedName),
        officialLink + modifyOfficialItem(formattedName),
    ]

    if "_Of_" in formattedName or "_The_" in formattedName or "_To_" in formattedName:
        formattedName_lower_prepositions = _replace_title_case_prepositions(formattedName)
        urls.extend([
            unofficialLink + modifyUnofficialItem(formattedName_lower_prepositions),
            officialLink + modifyOfficialItem(formattedName_lower_prepositions),
        ])

    return urls

def _update_special_case_links(filename: str, jsonData: dict, file, desired_links: list[str]) -> bool:
    global modifiedCount
    desired_links = _escape_wiki_links(desired_links)

    file_modified = False
    if jsonData.get("infoType") != wikiUrlInfoType:
        jsonData["infoType"] = wikiUrlInfoType
        file_modified = True
    if jsonData.get("info") != desired_links:
        jsonData["info"] = desired_links
        file_modified = True

    if file_modified:
        modifiedCount += 1
        file.seek(0)
        file.truncate()
        json.dump(jsonData, file, indent=2, ensure_ascii=False)
    return file_modified

def _has_complete_links(existingInfo: dict) -> bool:
    validLinks = [link for link in existingInfo if link.startswith(unofficialLink) or link.startswith(officialLink)]
    return validLinks and existingInfo == validLinks

def _should_skip_for_lookup(filename: str, jsonData: dict) -> bool:
    if (
            ("vanilla" in jsonData
             or jsonData["itemid"] == "minecraft:enchanted_book"
             or jsonData["itemid"] == "minecraft:potion")
    ):
        return True

    if filename.startswith('⚚_') or filename.startswith('ATTRIBUTE_'):
        return True

    if filename.startswith('BALLOON_HAT_2024') or filename.startswith('BALLOON_HAT_2025'):
        return True

    existingInfo = jsonData.get("info", [])
    if _has_complete_links(existingInfo):
        return True

    return False


def processItemFile(filename: str):
    global modifiedCount, badModifiedCount

    filePath = os.path.join(itemsDirectory, filename)
    with open(filePath, 'r+', encoding='utf-8') as file:
        jsonData = json.load(file)

        if (
                ("vanilla" in jsonData
                 or jsonData["itemid"] == "minecraft:enchanted_book"
                 or jsonData["itemid"] == "minecraft:potion")
        ):
            return

        existingInfo = jsonData.get("info", [])

        if filename.startswith('⚚_') or filename.startswith('ATTRIBUTE_'):
            return

        if filename.startswith('BALLOON_HAT_2024'):
            desired_links = [
                'https://hypixelskyblock.minecraft.wiki/w/5th_Anniversary_Balloon_Hat',
                'https://wiki.hypixel.net/5th_Anniversary_Balloon_Hat'
            ]
            if _update_special_case_links(filename, jsonData, file, desired_links):
                return

        if filename.startswith('BALLOON_HAT_2025'):
            desired_links = [
                'https://hypixelskyblock.minecraft.wiki/w/6th_Anniversary_Balloon_Hat',
                'https://wiki.hypixel.net/6th_Anniversary_Balloon_Hat'
            ]
            if _update_special_case_links(filename, jsonData, file, desired_links):
                return

        if _has_complete_links(existingInfo):
            return

        print(f"Processing {filename}...")

        formattedName = formatNameForSearch(jsonData["displayname"])
        candidateUrls = _candidate_page_urls(formattedName)

        # Attempt to find Unofficial and Official wiki links
        fullUnofficialLink = candidateUrls[0]
        fullOfficialLink = candidateUrls[1]

        unofficialExists = doesPageExist(fullUnofficialLink)
        officialExists = doesPageExist(fullOfficialLink)

        # Try with lowercase prepositions if initial attempt fails
        if not unofficialExists and len(candidateUrls) > 2:
            fullUnofficialLink = candidateUrls[2]
            unofficialExists = doesPageExist(fullUnofficialLink)

        if not officialExists and len(candidateUrls) > 3:
            fullOfficialLink = candidateUrls[3]
            officialExists = doesPageExist(fullOfficialLink)

        fileModified = False

        if unofficialExists or officialExists:
            if not "infoType" in jsonData or jsonData["infoType"] == "":
                jsonData["infoType"] = wikiUrlInfoType
                fileModified = True
        else:
            print(f"Neither page exists for {filename}, {formattedName}")

        infoLinks_auto = []
        if unofficialExists:
            infoLinks_auto.append(fullUnofficialLink)
        if officialExists:
            infoLinks_auto.append(fullOfficialLink)

        # Apply Unofficial link transformations here
        temp_infoLinks_auto = list(infoLinks_auto)
        for i, link in enumerate(temp_infoLinks_auto):
            if link.startswith(unofficialLink):
                fixed = False
                for suffix, new_base_url in linkTransformationUnofficial.items():
                    if suffix.lower() in link.lower():
                        infoLinks_auto[i] = new_base_url
                        print(f"Fixed Unofficial link: {new_base_url}")
                        fixed = True
                        break
                if fixed:
                    pass

        if len(infoLinks_auto) < len(existingInfo):
            return

        infoLinks_auto = _escape_wiki_links(infoLinks_auto)
        if infoLinks_auto != existingInfo:
            jsonData["info"] = infoLinks_auto

            print(f"Modified {filename}")
            print(f"existing info: {existingInfo}")
            print(f"new info: {infoLinks_auto}")

            fileModified = True

        if fileModified:
            modifiedCount += 1
            file.seek(0)
            file.truncate()
            json.dump(jsonData, file, indent=2, ensure_ascii=False)


def formatNameForSearch(name: str) -> str:
    for suffix in suffixesToRemove:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    name = name.strip()
    name = name.replace(" ", "_")
    name = removeColourCodes(name)

    if match := hoeTierPattern.search(name):
        name = name[0:match.start()]

    if "[Lvl_{LVL}]_" in name:
        name = name.replace("[Lvl_{LVL}]_", "") + "_Pet"
    if name.endswith("Gemstone") and name != "Glossy Gemstone":
        name = "Gemstone"
    name = capitalizeWords(name)
    name = name.replace("'", "%27")
    return name


def removeColourCodes(string: str) -> str:
    output = ""
    skipNext = False
    for char in string:
        if skipNext:
            skipNext = False
        elif char == "§":
            skipNext = True
        else:
            output += char
    return output


def doesPageExist(pageUrl: str) -> bool:
    return attemptedLinks.get(pageUrl, False)


def capitalizeWords(string: str) -> str:
    words = re.split(r'([_-])', string)
    for i in range(len(words)):
        if words[i] not in ['-', '_']:
            words[i] = words[i].capitalize()
    return ''.join(words)


def modifyUnofficialItem(unofficialItem: str) -> str:
    if "_Minion_" in unofficialItem:
        return unofficialItem.split("_Minion_")[0] + "_Minion"
    if "_Rune_" in unofficialItem:
        return (unofficialItem.split("_Rune_")[0] + "_Rune").removeprefix("◆_")
    if unofficialItem.startswith("Perfect_"):
        split = unofficialItem.split("_Tier_")
        if len(split) > 1:
            return "Perfect_Armor#Tier_" + split[1].upper()
        else:
            return unofficialItem
    return unofficialItem


def modifyOfficialItem(officialItem: str) -> str:
    if "_Minion_" in officialItem:
        split = officialItem.split("_Minion_")
        return split[0] + "_Minion_" + split[1].upper()
    if "_Rune_" in officialItem:
        return "Runes"
    if officialItem.startswith("Perfect_"):
        split = officialItem.split("_Tier_")
        if len(split) > 1:
            return split[0] + "_Tier_" + split[1].upper()
        else:
            return officialItem
    return officialItem


if __name__ == '__main__':
    print("Starting item file processing...")
    jsonFiles = getItemFiles()

    lookupUrls = []
    for item in jsonFiles:
        filePath = os.path.join(itemsDirectory, item)
        with open(filePath, 'r', encoding='utf-8') as file:
            jsonData = json.load(file)
            if _should_skip_for_lookup(item, jsonData):
                continue

            formattedName = formatNameForSearch(jsonData["displayname"])
            lookupUrls.extend(_candidate_page_urls(formattedName))

    _prime_page_existence_cache(lookupUrls)

    for item in jsonFiles:
        processItemFile(item)

    print(f"Total files modified: {modifiedCount}")
    print(f"Total bad modifications (skipped due to existing links): {badModifiedCount}")
