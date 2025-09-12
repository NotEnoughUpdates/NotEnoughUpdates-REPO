import json
from string import capwords

import requests
import os


def fetchJson(apiUrl):
    try:
        response = requests.get(apiUrl)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Error fetching data from {apiUrl}: {e}")


coinCosts = [
    0,
    0,
    0,
    10000,
    25000,
    50000,
    100_000,
    250_000,
    500_000,
    1_000_000,
    2_500_000,
    5_000_000,
    10_000_000,
    25_000_000,
    50_000_000,
]

allCosts = {}


def processItem(name, costs: list[list[dict]]):
    essenceType = None
    essenceCosts = {}
    itemCosts = {}

    tier = 1
    for cost in costs:
        for item in cost:
            costType = item['type']
            if costType == 'ESSENCE':
                foundType = item['essence_type']
                if essenceType is None:
                    essenceType = foundType
                elif essenceType != foundType:
                    raise ValueError(f"Multiple essence types found for {name}: {essenceType} and {foundType}")

                essenceCosts[tier] = item['amount']

                if tier > len(coinCosts):
                    raise ValueError(f"No coin cost defined for tier {tier} of {name}")
                coinCost = coinCosts[tier - 1]
                if coinCost > 0:
                    itemCosts.setdefault(tier, []).append(f"SKYBLOCK_COIN:{coinCost}")

            elif costType == 'ITEM':
                itemId = item['item_id']
                itemAmount = item['amount']
                recipeString = f"{itemId}:{itemAmount}"
                itemCosts.setdefault(tier, []).append(recipeString)

            else:
                raise ValueError(f"Unknown cost type {costType} for {name}")

        tier += 1

    # skip these as they break neu
    if essenceType is None:
        print(f"No essence type found for {name}")
        return

    finalData = {
        "type": capwords(essenceType)
    }
    for essenceCost in essenceCosts:
        finalData[essenceCost] = essenceCosts[essenceCost]
    finalData["items"] = itemCosts
    allCosts[name] = finalData


if __name__ == '__main__':
    url = "https://api.hypixel.net/v2/resources/skyblock/items"
    fetchedJson = fetchJson(url)
    itemsData = fetchedJson['items']

    for itemData in itemsData:
        if not 'upgrade_costs' in itemData:
            continue

        upgradeCosts = itemData['upgrade_costs']
        internalName = itemData['id']

        processItem(internalName, upgradeCosts)

    sorted_allCosts = {key: allCosts[key] for key in sorted(allCosts)}

    os.makedirs(os.path.dirname("constants/essencecosts.json"), exist_ok=True)
    with open("constants/essencecosts.json", "w") as json_file:
        json.dump(sorted_allCosts, json_file, indent=2)

    print(f"Saved essence costs for {len(allCosts)} items to essencecosts.json")
