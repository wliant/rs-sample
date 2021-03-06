import csv
import json

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



#['PALADIN', 'NEUTRAL', 'HUNTER', 'WARLOCK', 'ROGUE', 'PRIEST', 'DRUID', 'SHAMAN', 'WARRIOR', 'MAGE']
# class as key, list of card id as value
classCards = { c["class"]: [a["id"] for a in myCardList if a["class"] == c["class"]] for c in myCardList}


#target class
targetClass = "MAGE"

cardRarityDict = {a["id"]: a["rarity"] for a in myCardList if a["class"] == targetClass or a["class"] == "NEUTRAL"}
cardNameDict = {a["id"]: a["name"] for a in myCardList if a["class"] == targetClass or a["class"] == "NEUTRAL"}

#list of cards
cardPool = [a for a in classCards[targetClass]] + [a for a in classCards["NEUTRAL"]]

preselect = []

import random

from deap import base
from deap import creator
from deap import tools

creator.create("FitnessMax", base.Fitness, weights=(1.0,-0.7))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, 0, len(cardPool) - 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 30 - len(preselect))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# the goal ('fitness') function to be maximized
def evalFct(individual):
    deck = set()
    for i in preselect:
        deck.add(i)
    for index in individual:
        deck.add(cardPool[index])
    return random.randint(0, 15), len(deck)

def feasible(individual):
    deck = {}
    for i in preselect:
        if i in deck:
            deck[i] += 1
        else:
            deck[i] = 1

    for index in individual:
        card = cardPool[index]
        if card in deck:
            deck[card] += 1
        else:
            deck[card] = 1
    
    for card in deck.keys():
        cardRarity = cardRarityDict[card]

        if cardRarity == "LEGENDARY" and deck[card] > 1 or deck[card] > 2:
            return False
    return True

#----------
# Operator registration
#----------
# register the goal / fitness function
toolbox.register("evaluate", evalFct)
toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, -100))

# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(cardPool) - 1, indpb=0.05)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selTournament, tournsize=3)

#----------

def main():
    random.seed(64)

    # create an initial population of 300 individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(n=300)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    CXPB, MUTPB = 0.5, 0.2
    
    print("Start of evolution")
    
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of 
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0
    
    # Begin the evolution
    while max(fits) < 100 and g < 1000:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        print("offspring length: {0}".format(len(offspring)))
    
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
    
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        print("  Evaluated %i individuals" % len(invalid_ind))
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[1] for ind in pop]
        
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        
        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)
    
    print("-- End of (successful) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

    al = sorted(best_ind)
    for index in al:
        print(cardNameDict[cardPool[index]])
if __name__ == "__main__":
    main()