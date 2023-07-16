import json
import uuid
import tkinter as tk
import tkinter.messagebox as messagebox
import pyperclip
from tkinter import ttk
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PIL import ImageTk, Image
import itertools

# written by Wyverst

# todo:
# add egg groups and egg group mating rules
# add breeding sim
# add important mons and their egg groups
# make a "breed" command that takes two uuids and returns a single uuid of a new mon that has the tag "ephemeral" and
#   does not save in a dump
# make just a list of all of em and can right click each name to copy uuid
# b breeds two mons holding items. if cannot breed, rejected (add must not be marked). if can breed, ask for items
# after ask for items, breed and make mon, mark ephemeral True, mark both parents marked True
# add canceling ephemeral mons, which unmarks parents
# add updating counts every time mons.remove is called

ITEMS = ["hp_brace", "atk_brace", "def_brace", "spa_brace", "spd_brace", "spe_brace", "none"]
STATS = ["hp", "atk", "def", "spa", "spd", "spe"]
NATS = ["adamant", "bashful", "bold", "brave", "calm", "careful", "docile", "gentle",
        "hardy", "hasty", "impish", "jolly", "lax", "lonely", "mild", "modest", "naive",
        "naughty", "quiet", "quirky", "rash", "relaxed", "sassy", "serious", "timid"]
egggroups = {"ditto": ["ditto"], "nidoking": ["field", "monster"], "gastly": ["chaos"], "haunter": ["chaos"]}
egggroupsrev = {"ditto": ["ditto"], "field": ["nidoking"], "monster": ["nidoking"], "chaos": ["gastly", "haunter"]}
mons = []
counts = {}
master = [counts, mons]
ephmons = []
j = 2

class Mon:

    def __init__(self, species, ivs, gender, nature, name, ephemeral, p1uuid = None, p2uuid = None):
        self.species = species
        self.egg_groups = egggroups.get(self.species)
        self.marked = False
        self.p1uuid = p1uuid
        self.p2uuid = p2uuid
        self.ephemeral = ephemeral
        self.ivs = ivs
        uuidjawn = uuid.uuid4()
        uuidstr = str(uuidjawn)
        self.uuid = uuidstr
        self.gender = gender
        self.nature = nature
        if name is None or name == "":
            self.name = "" + species
            i = 0
            while i < 6:
                if ivs[i] == 31:
                    if i == 0:
                        self.name = self.name + " HP "
                    elif i == 1:
                        self.name = self.name + " Atk "
                    elif i == 2:
                        self.name = self.name + " Def "
                    elif i == 3:
                        self.name = self.name + " SpA "
                    elif i == 4:
                        self.name = self.name + " SpD "
                    elif i == 5:
                        self.name = self.name + " Spe "
                i += 1

            self.name = ' '.join(self.name.split()).strip()

        else:
            self.name = name



    def getSpecies(self):
        return self.species


    def toggleMarked(self):
        self.marked = not self.marked


    def toString(self):
        return "Gender: " + self.gender + "\nName: " + self.name + "\nEgg groups: " + \
               "".join(egggroups.get(self.species)) + \
               "\nIVs: " + "".join(str(x) + " " for x in self.ivs) + "\nNature: " + self.nature + \
               "\nMarked: " + str(self.marked) + \
               "\nEphemeral: " + str(self.ephemeral) + \
               "\nUUID: (Internal use only - unrelated to Pokemmo) " + str(self.uuid)

    def __getitem__(self, key):
        if key == 'species':
            return self.species
        elif key == 'marked':
            return self.marked
        elif key == 'ephemeral':
            return self.ephemeral
        elif key == 'ivs':
            return self.ivs
        elif key == 'uuid':
            return str(self.uuid)
        elif key == 'name':
            return self.name
        elif key == 'egg_groups':
            return self.egg_groups
        elif key == 'gender':
            return self.gender
        elif key == 'nature':
            return self.nature
        else:
            raise KeyError(f"Invalid key: {key}")

    def to_dict(self):
        return {
            "species": self.species,
            "ephemeral": self.ephemeral,
            "ivs": self.ivs,
            "uuid": str(self.uuid),
            "name": self.name,
            "gender": self.gender,
            "nature": self.nature,
            "egg_groups": self.egg_groups
        }


class MonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Mon):
            return obj.to_dict()
        return super().default(obj)


def dump(master, filename):
    with open(filename, "w") as file:
        json.dump(master, file, cls=MonEncoder, indent=4)
    print("Data dumped to '{}'! Please use the file for future loading.".format(filename))


def load(filename):
    with open(filename, "r") as file:
        master = json.load(file)
    return master


def simulate_breeding(mons):
    generations = [[] for _ in range(6)]
    steps = [[] for _ in range(6)]

    # Generation 0: Initial parents
    for parent in mons:
        generations[0].append(parent)
        steps[0].append(f"Obtained {parent['name']} ({parent['uuid']})")

    for gen in range(1, 2):
        print(f"Begin generation {gen}")
        parents = generations[gen - 1]

        for i in range(len(parents)):
            z = 0
            for j in range(i + 1, len(parents)):
                parent1 = parents[i]
                parent2 = parents[j]

                # Check if the parents can breed based on the rules
                if can_breed(parent1, parent2, gen):
                    # Determine the child's species
                    child_species = determine_child_species(parent1, parent2)

                    # Determine the child's gender
                    child_gender = "c"

                    # Determine the child's nature
                    child_nature = determine_child_nature(parent1, parent2)

                    # Generate all possible combinations of items held by parents
                    item_combinations = generate_item_combinations(parent1, parent2)

                    # Iterate over each item combination
                    for items in item_combinations:
                        # Determine the child's IVs based on the items held by parents
                        child_ivs = determine_child_ivs(parent1["ivs"], parent2["ivs"], items)

                        cont = True
                        # Create the child mon
                        child_name = None
                        #f child_gender == "x":
                        if items[0] == "everstone":
                            child = Mon(child_species, child_ivs, child_gender, child_nature, child_name, False)
                        elif items[1] == "everstone":
                            child = Mon(child_species, child_ivs, child_gender, child_nature, child_name, False)
                        else:
                            child = Mon(child_species, child_ivs, child_gender, "", child_name, False)

                        iv1 = parent1["ivs"]
                        iv2 = parent2["ivs"]
                        ivc = child["ivs"]
                        if (sum(ivc) > sum(iv1)) or (sum(ivc) > sum(iv2)):
                            generations[gen].append(child)
                            steps[gen].append(f"Breed {parent1['name']} ({parent1['uuid']}) and {parent2['name']} ({parent2['uuid']}) with {', '.join(items)} to obtain {child['name']} ({child['uuid']})")
                        '''
                        else:
                            if items[0] == "everstone":
                                child1 = Mon(child_species, child_ivs, child_gender, child_nature, child_name)
                                child2 = Mon(child_species, child_ivs, child_gender, child_nature, child_name)
                            elif items[1] == "everstone":
                                child1 = Mon(child_species, child_ivs, child_gender, child_nature, child_name)
                                child2 = Mon(child_species, child_ivs, child_gender, child_nature, child_name)
                            else:
                                child1 = Mon(child_species, child_ivs, child_gender, "", child_name)
                                child2 = Mon(child_species, child_ivs, child_gender, child_nature, child_name)

                            iv1 = parent1["ivs"]
                            iv2 = parent2["ivs"]
                            ivc1 = child1["ivs"]
                            ivc2 = child2["ivs"]
                            if (sum(ivc) > sum(iv1)) or (sum(ivc) > sum(iv2)):
                                generations[gen].append(child1)
                                generations[gen].append(child2)
                                steps[gen].append(f"Breed {parent1['name']} ({parent1['uuid']}) and {parent2['name']} ({parent2['uuid']}) with {', '.join(items)} to obtain {child1['name']} ({child1['uuid']})")
                                steps[gen].append(f"Breed {parent1['name']} ({parent1['uuid']}) and {parent2['name']} ({parent2['uuid']}) with {', '.join(items)} to obtain {child2['name']} ({child2['uuid']})")
                                '''
                if i%100 == 0:
                    if z == 0:
                        print(f"{i}/{len(parents)}")
                        z+=1

    return generations, steps


def can_breed2(parent1, parent2):
    if hasattr(parent1, 'marked') and parent1['marked']:
        return False, False

    if hasattr(parent2, 'marked') and parent2['marked']:
        return False, False

    if parent1['species'] == "ditto" and parent2['species'] == "ditto":
        return False, False
    ditto = False
    if parent1['species'] == "ditto" or parent2['species'] == "ditto":
        ditto = True

    # Check if there is at least one overlapping egg group
    if len(set(parent1['egg_groups']) & set(parent2['egg_groups'])) == 0:
        if not ditto:
            return False, False

    # Check if the parents are gendered and have different genders
    if parent1['gender'] != "x" and parent2['gender'] != "x" and parent1['gender'] == parent2['gender']:
        return False, False

    if (parent1['gender'] == "x" and parent2['gender'] != "x" and not ditto) or (parent1['gender'] != "x" and parent2['gender'] == "x" and not ditto):
        return False, False

    gendered = True
    if parent1['gender'] == "x" and parent2['gender'] == "x":
        gendered = False

    return True, gendered


def can_breed(parent1, parent2, gen):
    # Check if both parents are dittos
    if parent1['marked'] or parent2['marked']:
        return False

    if parent1['species'] == "ditto" and parent2['species'] == "ditto":
        return False
    ditto = False
    if parent1['species'] == "ditto" or parent2['species'] == "ditto":
        ditto = True

    # Check if there is at least one overlapping egg group
    if len(set(parent1['egg_groups']) & set(parent2['egg_groups'])) == 0:
        if not ditto:
            return False

    # Check if the parents are gendered and have different genders
    if parent1['gender'] != "c" and parent2['gender'] != "c" and parent1['gender'] != "x" and parent2['gender'] != "x" and parent1['gender'] == parent2['gender']:
        return False

    iv1 = parent1["ivs"]
    iv2 = parent2["ivs"]
    overlap = 0
    i = 0
    while i < 6:
        if iv1[i] == iv2[i]:
            overlap += 1
        i+=1

    if overlap < gen:
        return False

    return True


def determine_child_species(parent1, parent2):
    # Determine the child's species based on the parent's genders and species
    if parent1['gender'] != "x" and parent2['gender'] != "x":
        if parent1['gender'] == "female":
            return parent1['species']
        elif parent2['gender'] == "female":
            return parent2['species']
    else:
        if parent1['species'] != "ditto":
            return parent1['species']
        elif parent2['species'] != "ditto":
            return parent2['species']

    # If both parents are dittos or have gender X, return the species of parent1
    return parent1['species']


def determine_child_gender(parent1, parent2):
    # Determine the child's gender based on the parent's genders
    if parent1['gender'] != "x" and parent2['gender'] != "x":
        # If the genders are different, the child will be gendered
        if parent1['gender'] != parent2['gender']:
            if parent1['gender'] == "female":
                return "male"
            else:
                return "female"

    # If both parents are dittos or have gender X, the child will also have gender X
    return "X"


def determine_child_nature(parent1, parent2):
    # Determine the child's nature based on the parent's natures
    if parent1['name'] == "everstone":
        return parent1['nature']
    elif parent2['name'] == "everstone":
        return parent2['nature']

    # If no Everstone is held, return the nature of parent1
    return parent1['nature']


def generate_item_combinations(parent1, parent2):
    # Generate all possible combinations of items held by parents
    items_combinations = []

    parent1validitems = []
    parent2validitems = []
    i = 0
    while i < 6:
        if parent1["ivs"][i] == 31:
            parent1validitems.append(ITEMS[i])
        if parent2["ivs"][i] == 31:
            parent2validitems.append(ITEMS[i])
        i+=1

    list1 = list(itertools.product(parent1validitems, parent2validitems))
    set1 = set(list1)
    list2 = list(set1)
    list3 = [combo for combo in list2 if combo[0] != combo[1]]
    return list3
    #return items_combinations


def determine_child_ivs(parent1_ivs, parent2_ivs, items):
    child_ivs = [0] * 6
    item1 = items[0]
    item2 = items[1]

    for i in range(6):
        iv1 = parent1_ivs[i]
        iv2 = parent2_ivs[i]

        # Check if the corresponding brace is held by parents
        if f"{STATS[i]}_brace" == item1:
            child_ivs[i] = iv1
        elif f"{STATS[i]}_brace" == item2:
            child_ivs[i] = iv2
        else:
            child_ivs[i] = 31 if (iv1 == 31 and iv2 == 31) else 0

    return child_ivs


def delmon(ephmon1):
    ephmon1.ephemeral = False
    parent122 = get_mon_by_uuid(ephmon1['p1uuid'])
    parent222 = get_mon_by_uuid(ephmon1['p2uuid'])

    if parent122 in mons:
        mons.remove(parent122)
        if type(parent122) is Mon:
            spectmp1 = parent122.species
        else:
            spectmp1 = parent122["species"]

        counts[spectmp1] = counts[spectmp1] - 1
    else:
        delmon(parent122)

    if parent222 in mons:
        mons.remove(parent222)
        if type(parent222) is Mon:
            spectmp1 = parent222.species
        else:
            spectmp1 = parent222["species"]

        counts[spectmp1] = counts[spectmp1] - 1
    else:
        delmon(parent222)

    ephmons.remove(ephmon1)
    mons.add(ephmon1)


def printcounts(moncount, egroupcount):
    moncountkeys = []
    egroupkeys = []
    for moncounted1 in moncount:
        moncountkeys.append(moncounted1)
    for ecounted1 in egroupcount:
        egroupkeys.append(ecounted1)

    egroupkeys.sort()
    moncountkeys.sort()
    print("Species\t\tHP\tAtk\tDef\tSpA\tSpD\tSpe\t2x31\t3x31\t4x31\t5x31\t6x31")

    for moncounted in moncountkeys:
        sys.stdout.write(moncounted + "\t\t" + str(len(moncount[moncounted]["hp"])) + "\t" + str(len(moncount[moncounted]["atk"])) + "\t" + str(len(moncount[moncounted]["def"])) + "\t" + str(len(moncount[moncounted]["spa"])) + "\t" + str(len(moncount[moncounted]["spd"])) + "\t" + str(len(moncount[moncounted]["spe"])))
        for i in range(2, 7):
            sys.stdout.write("\t" + str(len(moncount[moncounted][i])))

        print("\n")

    print("\n")

    for egroupcounted in egroupkeys:
        sys.stdout.write(egroupcounted + "\t\t" + str(len(egroupcount[egroupcounted]["hp"])) + "\t" + str(len(egroupcount[egroupcounted]["atk"])) + "\t" + str(len(egroupcount[egroupcounted]["def"])) + "\t" + str(len(egroupcount[egroupcounted]["spa"])) + "\t" + str(len(egroupcount[egroupcounted]["spd"])) + "\t" + str(len(egroupcount[egroupcounted]["spe"])))
        for i in range(2, 7):
            sys.stdout.write("\t" + str(len(egroupcount[egroupcounted][i])))

        print("\n")

    print("\n")

def get_mon_by_uuid(uuid):
    for mon in mons:
        if str(mon['uuid']) == str(uuid):
            return mon

    for mon in ephmons:
        if str(mon['uuid']) == str(uuid):
            return mon
    return None

loop = True
customnames = False

print("Hi, welcome to Wyverst's Breeding Tool!\n")

while loop:
    print("Command? [D]ump data, [L]oad data, [R]ecord new mons, [V]iew data, \n"
          "        Toggle on/off asking for custom [N]ames (Currently: <" + str(customnames) + ">) [Q]uit    ")
    print("==> ")
    cmd = str(input()).lower()
    if cmd == "d":
        filename = input("Enter the filename to dump the data: ")
        dump(master, filename)

    elif cmd == "l":
        filename = input("Enter the filename to load the data: ")
        master = load(filename)
        mons = master[1]
        counts = master[0]

    elif cmd == "p":
        print("Command disabled.")
        #gui = PreviewBreedingGUI(mons)

    elif cmd == "v":
        egroups = []
        monjawns = []
        egroupcount = {}
        moncount = {}
        for egroup in egggroupsrev:
            egroupcount[egroup] = {}
            etmp1 = egroupcount[egroup]

            i = 2

            for stat in STATS:
                etmp1[stat] = []
                if i <= 6:
                    etmp1[i] = []
                i+=1

        for monjawn in egggroups:
            moncount[monjawn] = {}
            mtmp1 = moncount[monjawn]

            i = 2

            for stat in STATS:
                mtmp1[stat] = []
                if i <= 6:
                    mtmp1[i] = []
                i+=1

        for mon in mons:
            monegroups = egggroups.get(mon["species"])
            ivjawns = mon["ivs"]
            mcj = moncount[mon["species"]]
            iv31count = 0
            for i in range(0, 6):
                if ivjawns[i] == 31:
                    iv31count += 1

            for monegroup in monegroups:
                egc = egroupcount[monegroup]
                for i in range(0, 6):
                    if ivjawns[i] == 31:
                        statjawn = STATS[i]
                        egc[statjawn].append(mon)
                        mcj[statjawn].append(mon)

                if iv31count >= 2:
                    egc[iv31count].append(mons)
                    mcj[iv31count].append(mons)

        printcounts(moncount, egroupcount)

        viewloop = True
        while viewloop:
            sploop = True
            cont = True
            print("\nNow entering Viewloop. "
                  "Please enter a command: Specify by [E]gg group OR Specify by [S]pecies, "
                  "[B]reed two mons (requires UUIDS), See e[P]hemeral mons, "
                  "[D]elete mon (unmarks parents), Make ephemeral mon [R]eal, Re[V]iew mons, [Q]uit Viewloop\n")
            print("==> ")
            cmd = str(input()).lower()
            if cmd == "b":
                print('First mon UUID? ')
                parent2 = ""
                mon2uuid = ""
                mon1uuid = str(input()).lower()
                parent1 = get_mon_by_uuid(mon1uuid)
                if parent1 is None:
                    print("Sorry, that didn't work.")
                    cont = False
                else:
                    if type(parent1) is Mon:
                        print("Mon 1 selection: " + parent1.toString())
                    else:
                        print("Mon 1 selection: " + str(parent1))

                if cont:
                    print('Second mon UUID? ')
                    mon2uuid = str(input()).lower()
                    parent2 = get_mon_by_uuid(mon2uuid)
                    if parent1 is None or parent2 is None:
                        print("Sorry, that didn't work.")
                        cont = False

                    else:
                        if type(parent2) is Mon:
                            print("Mon 2 selection: " + parent2.toString())
                        else:
                            print("Mon 2 selection: " + str(parent2))
                        print("Do you wish to continue? [Y]/[N]")
                        tmp2 = str(input()).lower()
                        if tmp2 != "y":
                            cont = False

                if cont:
                    parent2 = get_mon_by_uuid(mon2uuid)
                    canbreed, gendered = can_breed2(parent1, parent2)
                    if canbreed:
                        itemloop = True
                        items2 = []
                        while itemloop:
                            print("Please select what items the parents should hold during breeding: "
                                  "(Must be in this list: " + str(ITEMS) + ")")
                            items1 = str(input()).lower()
                            try:
                                items2 = items1.split()
                                print(items2)
                                if items2[0] in ITEMS and items2[1] in ITEMS:
                                    itemloop = False
                            except:
                                print("Sorry, that didn't work. Please try again.")

                            if itemloop:
                                print("Sorry, that didn't work. Please try again.")
                        gender = ""
                        if gendered:
                            genderloop2 = True
                            while genderloop2:
                                print("Please select gender of child: [M]/[F]")
                                gender = str(input()).lower()
                                if gender != "m" and gender != "f":
                                    print("Sorry, that was not recognized. Please try again.")
                                else:
                                    genderloop2 = False

                        else:
                            gender = "x"
                        child_species = determine_child_species(parent1, parent2)
                        child_nature = ""
                        if items2[0] == "everstone":
                            child_nature = parent1['nature']

                        elif items2[1] == 'everstone':
                            child_nature = parent2["nature"]

                        child_ivs = determine_child_ivs(parent1['ivs'], parent2['ivs'], items2)

                        child_mon = Mon(child_species, child_ivs, gender, child_nature, None, True, mon1uuid, mon2uuid)
                        ephmons.append(child_mon)

                        if type(parent1) is Mon:
                            parent1.toggleMarked()
                        else:
                            parent1['marked'] = True

                        if type(parent2) is Mon:
                            parent2.toggleMarked()
                        else:
                            parent2['marked'] = True

                        print("Congrats: here is your resulting baby mon: \n" + child_mon.toString())

                    else:
                        print("Sorry, these two mons cannot breed. Either the mon species are incompatible, or one mon is \"marked\" (being used by another mon in a breed, or some "
                              "other reasons I don't feel like typing.")
                        cont = False

            elif cmd == "r":
                print("What is the UUID of the mon you wish to make real? [Q] to cancel. This will "
                      "delete the parent mons and all ancestors.")
                ans = str(input())
                ephmon = get_mon_by_uuid(ans)
                delmon(ephmon)

            elif cmd == "d":
                print("What is the UUID of the mon you wish to delete? [Q] to cancel. ")
                ans = str(input())
                ephmon = get_mon_by_uuid(ans)
                if ephmon in ephmons:
                    parent12 = get_mon_by_uuid(ephmon['p1uuid'])

                    parent22 = get_mon_by_uuid(ephmon['p2uuid'])

                    if type(parent12) is Mon:
                        parent12.toggleMarked()
                    else:
                        parent12['marked'] = True

                    if type(parent22) is Mon:
                        parent22.toggleMarked()
                    else:
                        parent22['marked'] = True
                    ephmons.remove(ephmon)
                else:
                    mons.remove(ephmon)
                    if type(ephmon) is Mon:
                        spectmp1 = ephmon.species
                    else:
                        spectmp1 = ephmon["species"]

                    counts[spectmp1] = counts[spectmp1] - 1


            elif cmd == "p":
                for mon1 in ephmons:
                    print(str(mon1))

            elif cmd == "s":
                while sploop:
                    print("Please type the following arguments: "
                          "<Species> <Stat/@x31>. Alternatively, type q to go back.\n")
                    print("==> ")
                    spec = str(input()).lower()
                    if spec == "q":
                        sploop = False
                        cont = False

                    if cont:
                        try:
                            spec = spec.split()
                        except:
                            print("Argument not recognized. Please try again.")
                            cont = False

                        if cont:
                            try:
                                tmp1 = moncount[spec[0]]
                            except:
                                print("Sorry, that didn't work. ")
                                cont = False

                            if cont:
                                for moncounted in tmp1[spec[1]]:
                                    print(str(moncounted))
                                    print("\n")

                                sploop = False

            elif cmd == "e":
                while sploop:
                    print("Please type the following arguments: "
                          "<Egg group> <Stat/@x31>. Alternatively, type q to go back.\n")
                    print("==> ")
                    spec = str(input()).lower()
                    if spec == "q":
                        sploop = False
                        cont = False

                    if cont:
                        try:
                            spec = spec.split()
                        except:
                            print("Argument not recognized. Please try again.")
                            cont = False

                        if cont:
                            try:
                                tmp1 = egroupcount[spec[0]]
                            except:
                                print("Sorry, that didn't work.")
                                cont = False
                            if cont:
                                for moncounted in tmp1[spec[1]]:
                                    print(str(moncounted))
                                    print("\n")

                                sploop = False

            elif cmd == "v":
                printcounts(moncount, egroupcount)

            elif cmd == "q":
                viewloop = False

            else:
                print("Command not recognized. Please try again.")


    elif cmd == "s":
        print("Disabled command. Please try again.")
        #possiblemons, steps = simulate_breeding(mons)
        #filename = input("Enter the filename to dump sims: ")
        #dump([possiblemons, steps], filename)
        #open_gui(mons)

    elif cmd == "n":
        customnames = False

    elif cmd == "q":
        loop = False

    elif cmd == "r":
        loop2 = True
        loop3 = True
        species = ""
        ivs = ""
        egg = ""
        gender = ""
        name = ""
        ivarr = ""
        while loop3:
            # sex species ivs nature
            print("\nSpecies? ")
            species = str(input()).lower()
            if species[0:3] == "adv":
                cont = True
                all = species.split(" ")
                species = all[2]
                if species not in egggroups:
                    print("Species not recognized.")
                    cont = False
                sex1 = all[1]
                if sex1 != "m" and sex1 != "f" and sex1 != "x":
                    cont = False
                    print("Gender not recognized.")
                ivarr = all[3].split(",")
                try:
                    ivarr = [int(numeric_string) for numeric_string in ivarr]
                except:
                    print("Sorry, those IVs were not recognized.")
                    cont = False

                nat = all[4]
                if nat not in NATS:
                    print("Nature not recognized")
                    cont = False


                if cont:
                    newmon = Mon(species, ivarr, sex1, nat, None, False)
                    try:
                        print(newmon.toString())
                    except:
                        print("Sorry, something went wrong with your mon.")
                        cont = False
                    print("\nIs this the mon you want to record? [Y]/[N] ")
                    rep = str(input()).lower()
                    if rep == "y":
                        loop3 = False
                    elif rep != "n":
                        loop4 = True
                        while loop4:
                            print("\nCommand not recognized. Please try again. \n")
                            rep = str(input()).lower()
                            if rep == "y":
                                loop3 = False
                                loop4 = False
                            elif rep == "n":
                                loop4 = False

                    mons.append(newmon)

                    if species in counts.keys():
                        counts[species] = counts[species] + 1
                    else:
                        counts[species] = 1



            else:

                print("\nIVs? ")
                ivs = str(input()).lower()

                genderloop = True
                if species == "ditto":
                    genderloop = False
                    gender = "x"
                while genderloop:
                    print("\nGender? [M]/[F]/[X]")
                    gender = str(input()).lower()
                    if not ((gender == "m") or (gender == "f") or (gender == "x")):
                        print("\nThat gender was not recognized.")
                    else:
                        genderloop = False

                print("\n")
                ivarr = ivs.split()
                cont = True
                try:
                    ivarr = [int(numeric_string) for numeric_string in ivarr]
                except:
                    print("Sorry, those IVs were not recognized.")
                    cont = False
                if cont:
                    print("\nNature? ")
                    nature = str(input()).lower()

                    if nature not in NATS:
                        cont = False

                        hascustomname = False
                        if customnames:
                            print("\nCustom name? [N] if no")
                            name = str(input()).lower()
                            if name != "n":
                                hascustomname = True

                        if hascustomname:
                            newmon = Mon(species, ivarr, gender, nature, name, False)
                        else:
                            newmon = Mon(species, ivarr, gender, nature, None, False)
                        try:
                            print(newmon.toString())
                        except:
                            print("Sorry, something went wrong with your mon.")
                            cont = False

                        if cont:
                            print("\nIs this the mon you want to record? [Y]/[N] ")
                            rep = str(input()).lower()
                            if rep == "y":
                                loop3 = False
                            elif rep != "n":
                                loop4 = True
                                while loop4:
                                    print("\nCommand not recognized. Please try again. \n")
                                    rep = str(input()).lower()
                                    if rep == "y":
                                        loop3 = False
                                        loop4 = False
                                    elif rep == "n":
                                        loop4 = False

                            mons.append(newmon)

                            if species in counts.keys():
                                counts[species] = counts[species] + 1
                            else:
                                counts[species] = 1

    else:
        print("\nSorry! Command not recognized.")