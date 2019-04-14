import json
import csv

def cardToRow(card):
    #return [card["type"], card["rarity"], card["class"], card["race"], card["health"], card["attack"], card["cost"], card["durability"]]
    return [
        int(card["health"]) if card["health"] != "" else 0, 
        int(card["attack"]) if card["attack"] != "" else 0, 
        int(card["cost"]) if card["cost"] != "" else 0, 
        int(card["durability"] if card["durability"] != "" else 0
        )]
#cards will hold a list of class dictonary object 
cards = []
cards2 = []
#data processing cards data
with open("cards-in-use.json", "rb") as infile:
    #load from json file
    cards = json.load(infile)

with open("cards-wild.csv") as infile:
    reader = csv.reader(infile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
    cards2 = [r for r in reader]

# validate card names from csv file match with json file
for card in cards2:
    result = [a for a in cards if a["name"] == card[0] and ("set" not in a or a["set"] != "HERO_SKINS")]
    if len(result) != 1:
        print("{0}: found {1}".format(card[0], len(result)))

select1 = [a for a in cards if "attack" not in a and a["type"] == "MINION"]
print(len(select1))
for s in select1:
    print("{0} {1} {2}".format(s["name"], s["rarity"], s["type"]))

myCardList = []
for card in cards2:
    searchResult = [a for a in cards if a["name"] == card[0] and ("set" not in a or a["set"] != "HERO_SKINS")]
    matchedCard = searchResult[0]

    cardId = matchedCard["dbfId"]
    name = card[0]
    cardType = matchedCard["type"]
    cardRarity = matchedCard["rarity"]
    cardClass = matchedCard["cardClass"]
    cardRace = matchedCard["race"] if "race" in matchedCard else ""
    health = card[6]
    attack = card[7]
    cost = card[5]
    durability = card[8]
    myCardList.append({
        "id": cardId,
        "name": name,
        "type": cardType,
        "rarity": cardRarity,
        "class": cardClass,
        "race": cardRace,
        "health": health,
        "attack": attack,
        "cost": cost,
        "durability": durability
    })

#print(len(myCardList))
#for card in myCardList:
#    print(card)


#data processing card stats
with open("card-stats.json", "rb") as infile:
    stats = json.load(infile)

stats = stats["series"]["data"]["ALL"]

data = []
winrates = []
for card in myCardList:
    result = [a["winrate"] for a in stats if a["dbf_id"] == card["id"]]
    if len(result) == 1:
        data.append(cardToRow(card))
        winrates.append(result[0])

from sklearn import svm

clf = svm.SVR()
clf.fit(data,winrates)
#print("predicting for card {0}".format(myCardList[0]["name"]))
#print(clf.predict([cardToRow(myCardList[0])]))

