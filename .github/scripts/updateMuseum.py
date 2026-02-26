import json
import requests
import os
from collections import defaultdict

outputJson = {}

itemCategories = defaultdict(set)

armorToID = {}
children = {}
maxValues = {}
itemToXp = {}
armorSets = {}
mappedIds = {}


def fetchJson(apiUrl):
    try:
        response = requests.get(apiUrl)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Error fetching data from {apiUrl}: {e}")


def processMuseumData(internalName, data):
    itemType = data.get('category').lower()

    if 'parent' in data:
        parentData = data['parent']
        if parentData:
            for parent in parentData:
                children[parentData[parent]] = parent

    if 'mapped_item_ids' in data:
        for mappedId in data['mapped_item_ids']:
            mappedIds[mappedId] = internalName

    if 'armor_set_donation_xp' in data:
        donationXpInfo = data.get('armor_set_donation_xp', {})
        for armorSet in donationXpInfo:
            itemToXp[armorSet] = donationXpInfo[armorSet]
            itemCategories[itemType].add(armorSet)
            if armorSet in setOverride:
                addPieceToSet(setOverride[armorSet], armorSet)
                continue
            addPieceToSet(internalName, armorSet)
    else:
        donationXp = data.get('donation_xp', 0)
        itemToXp[internalName] = donationXp
        itemCategories[itemType].add(internalName)


def addPieceToSet(piece, setName):
    if setName not in armorSets:
        armorSets[setName] = set()
    if isinstance(piece, list):
        for p in piece:
            armorSets[setName].add(p)
    else:
        armorSets[setName].add(piece)


priorityExceptions = {
    "PERFECT_TIER_12": "PERFECT_HELMET_12",
    "PERFECT_TIER_13": "PERFECT_HELMET_13",
    "ARMOR_OF_THE_PACK": "HELMET_OF_THE_PACK",
    "SALMON_NEW": "SALMON_HELMET_NEW",
}

# The item type that should be prioritized when displaying the armor set (what Hypixel shows in the museum)
setPriorityList = [
    "HELMET",
    "NECKLACE",
    "HOOD",
    "HAT",
    "CAP",
    "LOCKET",
    "AMULET",
    "PENDANT",
    "CHESTPLATE",
    "CLOAK",
]

# Manually added overrides for armor sets as the Hypixel API does not provide the correct data
setOverride = {
    "BLAZE": [
        "BLAZE_BOOTS",
        "BLAZE_CHESTPLATE",
        "BLAZE_HELMET",
        "BLAZE_LEGGINGS"
    ],
    "CRIMSON_HUNTER": [
        "BLAZE_BELT",
        "GHAST_CLOAK",
        "GLOWSTONE_GAUNTLET",
        "MAGMA_NECKLACE"
    ],
    "END": [
        "ENDER_BELT",
        "ENDER_CLOAK",
        "ENDER_GAUNTLET",
        "ENDER_NECKLACE",
        "END_BOOTS",
        "END_CHESTPLATE",
        "END_HELMET",
        "END_LEGGINGS",
    ],
    "MONSTER_RAIDER": [
        "CREEPER_LEGGINGS",
        "GUARDIAN_CHESTPLATE",
        "SKELETON_HELMET",
        "TARANTULA_BOOTS"
    ],
    "SNOW_SUIT": [
        "SNOW_SUIT_BOOTS",
        "SNOW_SUIT_CHESTPLATE",
        "SNOW_SUIT_HELMET",
        "SNOW_SUIT_LEGGINGS",
        "SNOW_BELT",
        "SNOW_CLOAK",
        "SNOW_GLOVES",
        "SNOW_NECKLACE"
    ],
    "SPONGE": [
        "SPONGE_BOOTS",
        "SPONGE_CHESTPLATE",
        "SPONGE_HELMET",
        "SPONGE_LEGGINGS"
    ],
}


def findAppropriateId(setName):
    if setName in priorityExceptions:
        armorToID[setName] = priorityExceptions[setName]
        return

    partsMap = {}
    for part in armorSets[setName]:
        partsMap[part] = part.split("_")[-1]

    priorityMap = {part: index for index, part in enumerate(setPriorityList)}

    sortedParts = sorted(partsMap.keys(), key=lambda part: priorityMap.get(partsMap[part], float('inf')))

    highestPriorityPart = sortedParts[0] if sortedParts else None

    if highestPriorityPart and partsMap[highestPriorityPart] not in priorityMap:
        print(f"Highest priority part for set {setName} was not found in setPriorityList. Parts: {partsMap}")

    armorToID[setName] = highestPriorityPart


setExceptions = {
    "FLAMEBREAKER": "FLAME_BREAKER",
    "ENDER": "END",
    "SEYMOUR_SPECIAL": "SEYMOUR",
    "MAXOR": "SPEED_WITHER",
    "NECRON": "POWER_WITHER",
    "STORM": "WISE_WITHER",
    "GOLDOR": "TANK_WITHER",
    "SALMON": "SALMON_NEW",
    "ARMOR_OF_GROWTH": "GROWTH",
    "PROSPECTOR_OUTFIT": "MINER_OUTFIT",
    "MINER": "TANK_MINER",
    "PERFECT_ARMOR_TIER_XII": "PERFECT_TIER_12",
    "PERFECT_ARMOR_TIER_XIII": "PERFECT_TIER_13",
    "VANQUISHER": "VANQUISHED",
}

if __name__ == '__main__':

    url = "https://api.hypixel.net/v2/resources/skyblock/items"
    fetchedJson = fetchJson(url)
    items = fetchedJson['items']

    for item in items:
        itemId = item['id']

        if 'museum_data' in item:
            processMuseumData(itemId, item['museum_data'])
            continue

        if 'museum' in item:
            itemCategories['special'].add(itemId)

    for armorSet in armorSets:
        findAppropriateId(armorSet)

    for itemCategory in itemCategories:
        maxValues[itemCategory] = len(itemCategories[itemCategory])

    maxValues['special'] = 48
    maxValues['total'] = sum(maxValues[category] for category in itemCategories) - maxValues['special']

    outputJson = {
        "notice": "This file is automatically generated and should not be modified manually. Please edit the `updateMuseum.py` file instead.",
        "items": {k: sorted(list(v), key=lambda item: (itemToXp.get(item, 0), item)) for k, v in itemCategories.items()},
        "armor_to_id": dict(sorted(armorToID.items())),
        "children": dict(sorted(children.items())),
        "max_values": maxValues,
        "itemToXp": dict(sorted(itemToXp.items())),
        "mapped_ids": dict(sorted(mappedIds.items())),
        "sets_to_items": {k: sorted(v) for k, v in sorted(armorSets.items())},
        "set_exceptions": setExceptions,
    }

    os.makedirs(os.path.dirname("constants/museum.json"), exist_ok=True)
    with open("constants/museum.json", "w") as json_file:
        json.dump(outputJson, json_file, indent=2)

    print(f"Saved {maxValues['total']} items to museum.json")
