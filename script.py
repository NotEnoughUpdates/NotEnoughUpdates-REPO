import json, os

parents = {}
for itemJsonFileName in os.listdir("./items"):
        with open("./items/"+itemJsonFileName, "rb") as f:
                try:
                        itemJson = json.load(f);
                except:
                        print("BROKEN JSON:"+itemJsonFileName)
                if "parent" in itemJson:
                        parent = itemJson["parent"]
                        if not parent in parents:
                                parents[parent] = []
                        parents[parent].append(itemJson["internalname"])

print(parents)

with open("./parents.json", "w") as f:
        json.dump(parents, f, indent=4, sort_keys=True)
