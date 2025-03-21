import urllib.request, json, os

items_api = "https://api.hypixel.net/v2/resources/skyblock/items"
file_path = "constants/gemstonecosts.json"

with urllib.request.urlopen(items_api) as url:
    data = json.load(url)

slot_unlock_cost = {}

for item in data["items"]:
    if item.get("gemstone_slots", None):  # item have gemstone slots
        count = 0
        cost_dict = {}
        for slot in item.get("gemstone_slots"):
            slot_name = slot.get("slot_type") + "_" + str(count)  # e.g. RUBY_2

            if slot.get("costs", None):  # some slots are already unlocked
                gemstones_dict = {}
                for cost in slot.get("costs"):
                    if cost.get("coins", 0) != 0:
                        gemstones_dict["SKYBLOCK_COIN"] = cost.get("coins", 0)
                    if (cost.get("item_id", None)):
                        gemstones_dict[cost.get("item_id")] = cost.get("amount")

                while slot_name in cost_dict:  # loop for unique slots
                    count += 1
                    slot_name = slot.get("slot_type") + "_" + str(count)
                count = 0  # clear count

                cost_dict[slot_name] = gemstones_dict
                slot_unlock_cost[item["id"]] = cost_dict
            elif slot.get("slot_type", None):
                while slot_name in cost_dict:  # loop for unique slots
                    count += 1
                    slot_name = slot.get("slot_type") + "_" + str(count)
                count = 0  # clear count

                cost_dict[slot_name] = []
                slot_unlock_cost[item["id"]] = cost_dict

#print(json.dumps(slot_unlock_cost, indent=2, sort_keys=True))

pretty_slot_unlock_cost = {}

for item in slot_unlock_cost:
    slot_dict = {}
    for slot, cost in slot_unlock_cost[item].items():
        cost_list = []  # slot
        if len(cost) != 0:
            for ingredient, value in cost.items():
                cost_list.append("{}:{}".format(ingredient, value))
            slot_dict[slot] = cost_list
            pretty_slot_unlock_cost[item] = slot_dict

os.makedirs(os.path.dirname(file_path), exist_ok=True)
with open(file_path, "w") as json_file:
    json.dump(pretty_slot_unlock_cost, json_file, indent=2, sort_keys=True)