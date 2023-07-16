import time
import Quartz
from PIL import Image
import pytesseract
import cv2
import numpy as np
from fuzzywuzzy import fuzz
import json
import os
import select
import sys
import threading
import tkinter as tk
import re

HIDE_ON_STARTUP = ["All"]
ALL_POKEMON = ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree", "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata", "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu", "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂", "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales", "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume", "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth", "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine", "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop", "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool", "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke", "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel", "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter", "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb", "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee", "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon", "Chansey", "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", "Staryu", "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar", "Pinsir", "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee", "Vaporeon", "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto", "Kabutops", "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres", "Dratini", "Dragonair", "Dragonite", "Mewtwo", "Mew", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Sentret", "Furret", "Hoothoot", "Noctowl", "Ledyba", "Ledian", "Spinarak", "Ariados", "Crobat", "Chinchou", "Lanturn", "Pichu", "Cleffa", "Igglybuff", "Togepi", "Togetic", "Natu", "Xatu", "Mareep", "Flaaffy", "Ampharos", "Bellossom", "Marill", "Azumarill", "Sudowoodo", "Politoed", "Hoppip", "Skiploom", "Jumpluff", "Aipom", "Sunkern", "Sunflora", "Yanma", "Wooper", "Quagsire", "Espeon", "Umbreon", "Murkrow", "Slowking", "Misdreavus", "Unown", "Wobbuffet", "Girafarig", "Pineco", "Forretress", "Dunsparce", "Gligar", "Steelix", "Snubbull", "Granbull", "Qwilfish", "Scizor", "Shuckle", "Heracross", "Sneasel", "Teddiursa", "Ursaring", "Slugma", "Magcargo", "Swinub", "Piloswine", "Corsola", "Remoraid", "Octillery", "Delibird", "Mantine", "Skarmory", "Houndour", "Houndoom", "Kingdra", "Phanpy", "Donphan", "Porygon2", "Stantler", "Smeargle", "Tyrogue", "Hitmontop", "Smoochum", "Elekid", "Magby", "Miltank", "Blissey", "Raikou", "Entei", "Suicune", "Larvitar", "Pupitar", "Tyranitar", "Lugia", "Ho-Oh", "Celebi", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Poochyena", "Mightyena", "Zigzagoon", "Linoone", "Wurmple", "Silcoon", "Beautifly", "Cascoon", "Dustox", "Lotad", "Lombre", "Ludicolo", "Seedot", "Nuzleaf", "Shiftry", "Taillow", "Swellow", "Wingull", "Pelipper", "Ralts", "Kirlia", "Gardevoir", "Surskit", "Masquerain", "Shroomish", "Breloom", "Slakoth", "Vigoroth", "Slaking", "Nincada", "Ninjask", "Shedinja", "Whismur", "Loudred", "Exploud", "Makuhita", "Hariyama", "Azurill", "Nosepass", "Skitty", "Delcatty", "Sableye", "Mawile", "Aron", "Lairon", "Aggron", "Meditite", "Medicham", "Electrike", "Manectric", "Plusle", "Minun", "Volbeat", "Illumise", "Roselia", "Gulpin", "Swalot", "Carvanha", "Sharpedo", "Wailmer", "Wailord", "Numel", "Camerupt", "Torkoal", "Spoink", "Grumpig", "Spinda", "Trapinch", "Vibrava", "Flygon", "Cacnea", "Cacturne", "Swablu", "Altaria", "Zangoose", "Seviper", "Lunatone", "Solrock", "Barboach", "Whiscash", "Corphish", "Crawdaunt", "Baltoy", "Claydol", "Lileep", "Cradily", "Anorith", "Armaldo", "Feebas", "Milotic", "Castform", "Kecleon", "Shuppet", "Banette", "Duskull", "Dusclops", "Tropius", "Chimecho", "Absol", "Wynaut", "Snorunt", "Glalie", "Spheal", "Sealeo", "Walrein", "Clamperl", "Huntail", "Gorebyss", "Relicanth", "Luvdisc", "Bagon", "Shelgon", "Salamence", "Beldum", "Metang", "Metagross", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Starly", "Staravia", "Staraptor", "Bidoof", "Bibarel", "Kricketot", "Kricketune", "Shinx", "Luxio", "Luxray", "Budew", "Roserade", "Cranidos", "Rampardos", "Shieldon", "Bastiodon", "Burmy", "Wormadam", "Mothim", "Combee", "Combee", "Vespiquen", "Pachirisu", "Buizel", "Floatzel", "Cherubi", "Cherrim", "Shellos", "Gastrodon", "Ambipom", "Drifloon", "Drifblim", "Buneary", "Lopunny", "Mismagius", "Honchkrow", "Glameow", "Purugly", "Chingling", "Stunky", "Skuntank", "Bronzor", "Bronzong", "Bonsly", "Mime Jr.", "Happiny", "Chatot", "Spiritomb", "Gible", "Gabite", "Garchomp", "Munchlax", "Riolu", "Lucario", "Hippopotas", "Hippowdon", "Skorupi", "Drapion", "Croagunk", "Toxicroak", "Carnivine", "Finneon", "Lumineon", "Mantyke", "Snover", "Abomasnow", "Weavile", "Magnezone", "Lickilicky", "Rhyperior", "Tangrowth", "Electivire", "Magmortar", "Togekiss", "Yanmega", "Leafeon", "Glaceon", "Gliscor", "Mamoswine", "Porygon-Z", "Gallade", "Probopass", "Dusknoir", "Froslass", "Rotom", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Patrat", "Watchog", "Lillipup", "Herdier", "Stoutland", "Purrloin", "Liepard", "Pansage", "Simisage", "Pansear", "Simisear", "Panpour", "Simipour", "Munna", "Musharna", "Pidove", "Tranquill", "Unfezant", "Blitzle", "Zebstrika", "Roggenrola", "Boldore", "Gigalith", "Woobat", "Swoobat", "Drilbur", "Excadrill", "Audino", "Timburr", "Gurdurr", "Conkeldurr", "Tympole", "Palpitoad", "Seismitoad", "Throh", "Sawk", "Sewaddle", "Swadloon", "Leavanny", "Venipede", "Whirlipede", "Scolipede", "Cottonee", "Whimsicott", "Petilil", "Lilligant", "Basculin", "Sandile", "Krokorok", "Krookodile", "Darumaka", "Darmanitan", "Maractus", "Dwebble", "Crustle", "Scraggy", "Scrafty", "Sigilyph", "Yamask", "Cofagrigus", "Tirtouga", "Carracosta", "Archen", "Archeops", "Trubbish", "Garbodor", "Zorua", "Zoroark", "Minccino", "Cinccino", "Gothita", "Gothorita", "Gothitelle", "Solosis", "Duosion", "Reuniclus", "Ducklett", "Swanna", "Vanillite", "Vanillish", "Vanilluxe", "Deerling", "Sawsbuck", "Emolga", "Karrablast", "Escavalier", "Foongus", "Amoonguss", "Frillish", "Jellicent", "Alomomola", "Joltik", "Galvantula", "Ferroseed", "Ferrothorn", "Klink", "Klang", "Klinklang", "Tynamo", "Eelektrik", "Eelektross", "Elgyem", "Beheeyem", "Litwick", "Lampent", "Chandelure", "Axew", "Fraxure", "Haxorus", "Cubchoo", "Beartic", "Cryogonal", "Shelmet", "Accelgor", "Stunfisk", "Mienfoo", "Mienshao", "Druddigon", "Golett", "Golurk", "Pawniard", "Bisharp", "Bouffalant", "Rufflet", "Braviary", "Vullaby", "Mandibuzz", "Heatmor", "Durant", "Deino", "Zweilous", "Hydreigon", "Larvesta", "Volcarona", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem"]
dumpfile = os.path.join(os.path.dirname(sys.argv[0]), "dump2.txt")


def on_drag(event):
    global root
    root.geometry(f"+{event.x_root - x_clicked}+{event.y_root - y_clicked}")


def on_click(event):
    global root
    global x_clicked, y_clicked
    x_clicked = event.x
    y_clicked = event.y


def on_resize(event):
    global root
    root.geometry(f"{event.width}x{event.height}")


root = tk.Tk()
root.overrideredirect(True)
root.bind("<B1-Motion>", on_drag)
root.bind("<ButtonPress-1>", on_click)
root.bind("<Configure>", on_resize)
root.minsize(112, 20)
root.wm_attributes("-topmost", 1)
root.title("Wyverst's Counter")
sv = tk.StringVar(root)
# Make the window resizable
root.resizable(True, True)
hidden = []

#t1 = tk.Text(root, height=15, width=20)
#t1.grid(row=1, column=1)


counter = {}
j = 0
region_of_interest = (520, 260, 2350, 460)
targets = []
master = [targets, counter]


def run_game():
    global j
    global t1
    global root
    global sv
    # Initialize Tkinter
    j = 0
    #jawnthread = threading.Thread(target=jawn2)
    #jawnthread.start()

    #while True:
    #print("hi")
    #root.update_idletasks()
    #print("hi")
    #counter2 = sorted(master[1].items(), key=lambda x: x[1], reverse=True)
    #if j >= 1:
        #t1.delete("1.0", tk.END)
    #print("hi")
    label = tk.Label(root, textvariable=sv)
    #label = tk.Label(root, text="hi")
    label.pack()
    jawn2()
    root.mainloop()

    # Schedule the next update
    j += 1
    #root.after(3000, root.quit)
    #root.mainloop()


def jawn2():
    global root
    global counter
    global sv
    #while True:
        #print("jawn2")
    counter2 = sorted(master[1].items(), key=lambda x: x[1], reverse=True)
    strjawn_list = [f"{key}: {value}" for key, value in counter2 if key not in hidden]
    strjawn_list.insert(0, "Wyverst's Counter")
    strjawn = "\n".join(strjawn_list)
    sv.set(strjawn)
    #print(strjawn)
    root.after(3000, jawn2)


def jawn():
    global root
    global counter
    while True:
        #print("jawn2")
        counter2 = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        for key, value in counter2:
            label = tk.Label(root, text=f"{key}: {value}")
            label.pack()
        time.sleep(3)

    """
    #for widget in root.winfo_children():
    #    widget.destroy()

    #t1 = tk.Text(root, height=15, width=20)
    #t1.grid(row=1, column=1)

    # Update labels from the counter dictionary
    counter2 = sorted(master[1].items(), key=lambda x: x[1], reverse=True)
    if j >= 1:
        t1.delete("1.0", tk.END)
    for key, value in counter2:
        label = tk.Label(root, text=f"{key}: {value}")
        label.pack()

    # Schedule the next update
    j += 1
    #root.update()
    #time.sleep(3)
    #root.after(1000, jawn())
    """


def capture_window(window_title):
    windows = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    #print(windows)
    for window in windows:
        window_title_value = window.get("kCGWindowOwnerName", "")
        if window_title_value == window_title:
            window_id = window["kCGWindowNumber"]
            region = Quartz.CGRectNull
            image = Quartz.CGWindowListCreateImage(region, Quartz.kCGWindowListOptionIncludingWindow, window_id, Quartz.kCGWindowImageDefault)
            width = Quartz.CGImageGetWidth(image)
            height = Quartz.CGImageGetHeight(image)
            bytes_per_row = Quartz.CGImageGetBytesPerRow(image)
            pixel_data = Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(image))
            image = Image.frombytes("RGB", (width, height), pixel_data, "raw", "RGBX", bytes_per_row, 1)
            return image
    return None


def extract_text(image, region):
    punctuation_pattern = r'[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]'
    ret = []
    cropped_image = image.crop(region)  # Crop the image to the region of interest
    cropped_image = make_non_white_black(cropped_image)
    # checkpoint1
    #cropped_image.show()
    text = pytesseract.image_to_string(cropped_image)

    return re.split(r"\s+|\W+", text)


def process_image(image):
    # Convert the image to grayscale for better OCR results
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    processed_image = Image.fromarray(gray_image)
    return processed_image


def add_to_counter(user_input2):
    user_input1 = user_input2[:1].capitalize() + user_input2[1:].lower()
    global counter
    global master
    global targets
    global hidden
    # Add user input to the counter
    if user_input1 is None or len(user_input1) == 0:
        return
    if user_input1 == "Exit" or user_input1 == "Quit":
        dump()
        os._exit(0)
    elif user_input1 == "Hideall" or user_input1 == "Hide all":
        for item in counter.keys():
            hidden.append(item)
    elif user_input1[0] == "-":
        master[1].pop(user_input1[1:2].capitalize() + user_input1[2:].lower())
        master[0].remove(user_input1[1:2].capitalize() + user_input1[2:].lower())
    elif user_input1[0] == "H":
        hidden.append(user_input1[1:2].capitalize() + user_input1[2:].lower())
    elif user_input1[0] == "U":
        if user_input1[1:2].capitalize() + user_input1[2:].lower() in hidden:
            hidden.remove(user_input1[1:2].capitalize() + user_input1[2:].lower())
    elif user_input1 == "Clear":
        hidden.clear()
    elif user_input1 == "Wipe all data":
        counter = {}
        targets = []
        master = [targets, counter]
        dump()
    else:
        if user_input1 not in counter.keys() and user_input1 in ALL_POKEMON:
            master[1][user_input1] = 0
            master[0].append(user_input1)
        elif user_input1 in counter.keys() and user_input1 in hidden:
            hidden.remove(user_input1)

    targets = master[0]
    counter = master[1]


def dump():
    global dumpfile
    with open(dumpfile, "w") as file:
        json.dump(master, file, indent=4)
    #print("Data dumped to '{}'! Please use the file for future loading.".format("dump2.txt"))


def load():
    global dumpfile
    global master
    global targets
    global counter
    with open(dumpfile, "r") as file:
        master = json.load(file)
        targets = master[0]
        counter = master[1]

    allj = False
    for item in HIDE_ON_STARTUP:
        item = item[:1].capitalize() + item[1:].lower()
        if item == "All":
            allj = True
            for item2 in counter.keys():
                hidden.append(item2)
        else:
            if not allj:
                if item in ALL_POKEMON:
                    hidden.append(item)


def get_four_corner_pixels(img):
    # Get the four corner pixels
    global region_of_interest
    #img = img.crop(region_of_interest)
    width, height = img.size
    top_left = img.getpixel((0, 0))
    top_right = img.getpixel((width - 1, 0))
    bottom_left = img.getpixel((0, height - 1))
    bottom_right = img.getpixel((width - 1, height - 1))

    # Save the corner pixels to a list
    corner_pixels = [top_left, top_right, bottom_left, bottom_right]
    #print(corner_pixels)
    return corner_pixels


def is_white_pixel(pixel):
    # For grayscale images, the pixel value directly represents the intensity (0 to 255).
    # Check if the pixel intensity is greater than or equal to the threshold (e.g., 220) to consider it as white.
    return pixel >= 220


#checkpoint2
def make_non_white_black(img):
    # Create a new image with a black background (grayscale mode)
    width = img.width
    height = img.height
    black_img = Image.new("L", img.size, color=255)
    # Loop through each pixel and set it to black if it's not white
    for x in range(img.width):
        for y in range(img.height):
            pixel_color = img.getpixel((x, y))
            if x in (0, width - 1) and y in (0, height - 1):
                black_img.putpixel((x, y), pixel_color)  # Keep the original corner color
                #print(black_img.getpixel((x,y)))
            elif not is_white_pixel(pixel_color):  # Check if it's not white
                black_img.putpixel((x, y), 0)

    return black_img


def main():
    # Example usage
    global region_of_interest
    target_window_title = "java"
    i = 0
    data_detected = False
    print("Type a Pokemon species to add to counter, or -Pokemon to remove from counter, or exit/quit to save data and close program.")
    corners = []
    while True:
        # Capture the specific window
        window_image = capture_window(target_window_title)

        if window_image is not None:
            # Process the image and extract text as before
            processed_image = process_image(window_image)
            region_of_interest2 = []
            region_of_interest2.append(int(processed_image.height * float(520/2156)))
            region_of_interest2.append(int(processed_image.width * float(260/3592)))
            region_of_interest2.append(int(processed_image.height * float(2350/2156)))
            region_of_interest2.append(int(processed_image.width * float(460/3592)))
            # region_of_interest = (520, 260, 2350, 460)
            region_of_interest = tuple(region_of_interest2)
            extracted_text = extract_text(processed_image, region_of_interest)
            #print(extracted_text)

            # Check if the extracted text contains target text
            #print(extracted_text)
            #text_found = any(item in target_text for item in extracted_text)
            count = 0
            text_found = False
            for item in master[0]:
                for word in extracted_text:
                    if fuzz.ratio(word, item) > 60:
                        text_found = True

            #print(text_found)

            if text_found and not data_detected:
                # Update the counter only when data is detected for the first time

                data_detected = True
                corners = get_four_corner_pixels(make_non_white_black(processed_image.crop(region_of_interest)))
                for item in master[0]:
                    for word in extracted_text:
                        if fuzz.ratio(word, item) > 60:
                            master[1][item] = master[1].get(item, 0) + 1
                # wait for background to stop moving
                time.sleep(2)
                #processed_image.show()

            elif not text_found:
                # Reset the data detection flag when no data is found on the screen
                # if 4 corners all different
                if data_detected:
                    corners2 = get_four_corner_pixels(make_non_white_black(processed_image.crop(region_of_interest)))
                    #processed_image.show()
                    cont = True
                    v = 0
                    #print(corners)
                    #print(corners2)
                    if len(corners) == len(corners2) and len(corners) == 4:
                        while v <= 3:
                            if corners[j] == corners2[j]:
                                cont = False
                            v+=1

                        if cont:
                            data_detected = False
                            corners = []

        # Display the counter on the screen
        if i%10 == 0:
            print(f"Counter: {sorted(master[1].items(), key=lambda x: x[1], reverse=True)}")
            dump()
        i+=1

        inputs, _, _ = select.select([sys.stdin], [], [], 1)

        if inputs:
            user_input = sys.stdin.readline().rstrip()
            add_to_counter(user_input)


        # Update the counter display

        # You can add a delay here if needed

if os.path.exists(dumpfile):
    load()
    print("Data loaded!")

game_thread = threading.Thread(target=main)
game_thread.start()

#jawnthread = threading.Thread(target=run_game)
#jawnthread.start()
#run_game()
#while True:
run_game()
    #root.after(3000, root.quit)
    #root.mainloop()
#root.mainloop()