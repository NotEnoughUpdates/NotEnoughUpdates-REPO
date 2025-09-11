import os
import json
import urllib3
import re

# Constants
itemsDirectory = "items"
fandomLink = "https://hypixel-skyblock.fandom.com/wiki/"
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

linkTransformationFandom = {
    "Barn_Skin": fandomLink + "Barn_Skins",
    "_Rune": fandomLink + "Runes"
}

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


def _update_special_case_links(filename: str, jsonData: dict, file, desired_links: list[str]) -> bool:
    global modifiedCount

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
        file.write(
            json.dumps(jsonData, indent=2, ensure_ascii=False)
            .replace("=", "\\u003d")
            .replace("'", "\\u0027")
        )
    return file_modified


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
                'https://hypixel-skyblock.fandom.com/wiki/5th_Anniversary_Balloon_Hat',
                'https://wiki.hypixel.net/5th_Anniversary_Balloon_Hat'
            ]
            if _update_special_case_links(filename, jsonData, file, desired_links):
                return

        if filename.startswith('BALLOON_HAT_2025'):
            desired_links = [
                'https://hypixel-skyblock.fandom.com/wiki/6th_Anniversary_Balloon_Hat',
                'https://wiki.hypixel.net/6th_Anniversary_Balloon_Hat'
            ]
            if _update_special_case_links(filename, jsonData, file, desired_links):
                return

        for link in existingInfo:
            if (link.startswith(fandomLink) or link.startswith(officialLink)):
                return

        print(f"Processing {filename}...")

        formattedName = formatNameForSearch(jsonData["displayname"])

        # Attempt to find Fandom and Official wiki links
        fullFandomLink = fandomLink + modifyFandomItem(formattedName)
        fullOfficialLink = officialLink + modifyOfficialItem(formattedName)

        fandomExists = doesPageExist(fullFandomLink)
        officialExists = doesPageExist(fullOfficialLink)

        # Try with lowercase prepositions if initial attempt fails
        if not fandomExists and ("_Of_" in formattedName or "_The_" in formattedName or "_To_" in formattedName):
            formattedName_lower_prepositions = _replace_title_case_prepositions(formattedName)
            fullFandomLink = fandomLink + modifyFandomItem(formattedName_lower_prepositions)
            fandomExists = doesPageExist(fullFandomLink)

        if not officialExists and ("_Of_" in formattedName or "_The_" in formattedName or "_To_" in formattedName):
            formattedName_lower_prepositions = _replace_title_case_prepositions(formattedName)
            fullOfficialLink = officialLink + modifyOfficialItem(formattedName_lower_prepositions)
            officialExists = doesPageExist(fullOfficialLink)

        fileModified = False

        if fandomExists or officialExists:
            if not "infoType" in jsonData or jsonData["infoType"] == "":
                jsonData["infoType"] = wikiUrlInfoType
                fileModified = True
        else:
            print(f"Neither page exists for {filename}, {formattedName}")

        infoLinks_auto = []
        if fandomExists:
            infoLinks_auto.append(fullFandomLink)
        if officialExists:
            infoLinks_auto.append(fullOfficialLink)

        # Apply Fandom link transformations here
        temp_infoLinks_auto = list(infoLinks_auto)
        for i, link in enumerate(temp_infoLinks_auto):
            if link.startswith(fandomLink):
                fixed = False
                for suffix, new_base_url in linkTransformationFandom.items():
                    if suffix.lower() in link.lower():
                        infoLinks_auto[i] = new_base_url
                        print(f"Fixed Fandom link: {new_base_url}")
                        fixed = True
                        break
                if fixed:
                    pass

        if (len(infoLinks_auto) < len(existingInfo)):
            return

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
            file.write(
                json.dumps(jsonData, indent=2, ensure_ascii=False)
                .replace("=", "\\u003d")
                .replace("'", "\\u0027")
            )


def formatNameForSearch(name: str) -> str:
    for suffix in suffixesToRemove:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    name = name.strip()
    name = name.replace(" ", "_")
    name = removeColourCodes(name)
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
    if pageUrl in attemptedLinks:
        return attemptedLinks[pageUrl]

    response = httpPool.request('GET', pageUrl, redirect=True)

    success = response.status == 200
    if response.status == 403:
        print('got 403 lol')
    attemptedLinks[pageUrl] = success
    return success


def capitalizeWords(string: str) -> str:
    words = re.split(r'([_-])', string)
    for i in range(len(words)):
        if words[i] not in ['-', '_']:
            words[i] = words[i].capitalize()
    return ''.join(words)


def modifyFandomItem(fandomItem: str) -> str:
    if "_Minion_" in fandomItem:
        return fandomItem.split("_Minion_")[0] + "_Minion"
    if "_Rune_" in fandomItem:
        return (fandomItem.split("_Rune_")[0] + "_Rune").removeprefix("◆_")
    if fandomItem.startswith("Perfect_"):
        split = fandomItem.split("_Tier_")
        if len(split) > 1:
            return "Perfect_Armor#Tier_" + split[1].upper()
        else:
            return fandomItem
    return fandomItem


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

    for item in jsonFiles:
        processItemFile(item)

    print(f"Total files modified: {modifiedCount}")
    print(f"Total bad modifications (skipped due to existing links): {badModifiedCount}")