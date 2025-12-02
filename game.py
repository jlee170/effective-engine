from gametools import write, write_md, get_input, get_choice, clear, pause, spin

game_state = []
inventory = []

################################################################################
# SHOW_INVENTORY
def show_inventory():
    """
    Print the player's inventory as a bulleted list using hyphens.
    If inventory is empty, show a special empty message.
    """
    print()  # spacing
    print("PLAYER INVENTORY")
    print()
    if inventory:
        for item in inventory:
            print(" -", item)
    else:
        print("*** EMPTY ***")
    print()  # spacing


################################################################################
# INTRO
def intro():
    clear()
    write_md(
"""
# OUTBREAK: RED FACILITY

You wake to the taste of metal in your mouth and a ceiling that hums with
emergency power. Fluorescent lights above flicker between sickly green and
dark. You're on a cold metal slab inside a quarantine holding cell marked
**RF-13**.

A faint, wet shuffling echoes in the distance. The smell of antiseptic is
overwhelmed by something far worse.. rot, blood, and old smoke.

At your side a battered **flashlight** rests, its button scuffed but functional.
You have minutes (maybe hours) to get out before whatever's in the vents finds
you. Somewhere deeper in the facility, a hulking infected subject known as
**B-0B** holds the module that will open the exit gate.

Pull yourself together. Survive long enough to get it back.
"""
    )
    write()
    pause("Press any key to find your feet and stand up.")
    return cell


################################################################################
# CELL (holding cell)
def cell():
    clear()

    write_md(
"""
# HOLDING CELL -RF-13

You are inside a cramped metal cell. The walls are scored with shallow claw
marks and a smear of dried blood leads to the door. The air tastes stale.
"""
    )
    write()

    if "flashlight_on" not in game_state:
        write_md(
"""
The flashlight beside you is mostly dead but could be enough to see for a
short time. The cell door is slightly ajar, obvious that whoever or whatever left last 
didn't care to shut it.

What do you do?
"""
        )
        write()
        choices = [
            "Turn on the flashlight",
            "Call out to see if anyone is alive",
            "Examine your inventory"
        ]
        user_choice = get_choice(choices)

        if user_choice == 0:
            game_state.append("flashlight_on")
            write()
            write("The flashlight sputters to life with a weak, jittery beam.")
            write("Shadows dance. In the beam you can see the corridor beyond.")
            write()
            pause()
            return cell

        elif user_choice == 1:
            write()
            write("You shout. Your voice sounds small. Wet scratching replies from somewhere beyond the door. Probably nothing friendly.")
            write()
            pause()
            return cell

        else:
            write()
            show_inventory()
            write()
            pause()
            return cell

    else:  # flashlight is on
        write_md(
"""
The corridor beyond your cell yawns darkly. The door to the SOUTH sits
slightly open. The flashlight casts a narrow cone; beyond it the hallway
is a dim, rotting tunnel lined with ruined cells.
"""
        )
        write()
        write("What will you do?")
        choices = [
            "Go South through the cell door",
            "Examine your inventory"
        ]
        user_choice = get_choice(choices)
        if user_choice == 0:
            return hall
        else:
            write()
            show_inventory()
            write()
            pause()
            return cell


################################################################################
# HALL (main corridor)
def hall():
    clear()

    # door to B-0B's lair state
    door_open = "b0b_door_open" in game_state
    door_state = "open" if door_open else "sealed"

    has_keycard = "Level-1 Keycard" in inventory

    write_md(
f"""
# MAIN CORRIDOR -SECURITY WING

You step into a long corridor of cells. The glass is spiderwebbed, and the
doors are ajar or torn off their frames. A faint red emergency strip light
pulses somewhere in the distance.

To the EAST a heavy security door is {door_state}.
To the NORTH is the way back to your cell.
"""
    )
    write()

    if not has_keycard:
        write_md(
"""
A security guard lies slumped against the wall. He is long dead, flies crowding around as his chest torn
open in places, but you notice a Level-1 security keycard still clipped
to his chest rig.
"""
        )

    write()
    choices = [
        "Go North (back to cell)",
        "Go East (toward the big door)",
        "Take the Level-1 Keycard",
        "View Inventory"
    ]

    hidden_choices = []
    if has_keycard:
        hidden_choices.append(2)  # hide "Take the Level-1 Keycard"

    user_choice = get_choice(choices, hidden_choices)

    if user_choice == 0:  # North
        return cell

    elif user_choice == 1:  # East
        if door_open:
            return attack_bob
        else:
            if has_keycard:
                game_state.append("b0b_door_open")
                write()
                write("You swipe the Level-1 Keycard. The heavy door grinds and unlocks.")
                write()
                pause("Press any key to push through the now-open door")
                return attack_bob
            else:
                write()
                write("The door is sealed tight. The keypad reads: LEVEL-1 REQUIRED.")
                write()
                pause()
                return hall

    elif user_choice == 2:  # Take Keycard
        inventory.append("Level-1 Keycard")
        write()
        write(
"""
You carefully remove the Level-1 Keycard from the guard's rig. It's sticky
with gore, but it looks functional.
"""
        )
        write()
        pause()
        return hall

    else:  # View Inventory
        write()
        show_inventory()
        write()
        pause()
        return hall


################################################################################
def bs_lair():
    clear()

    write_md(
"""
# B-0B'S NEST -SUBJECT CONTAINMENT

The chamber beyond the heavy door is vast and battered. Twisted metal and torn
lab coats have been fashioned into a nest around a single massive shape.
Every inch of the floor is caked in dark, congealed blood.

At the center of the nest lies **B-0B**, a hulking mass of corrupted flesh and
bone. The creature is breathing, deep and wet, a low rumble like a dying engine.

Something glows on a cord around its neck: an **Exit Gate Access Module**.
To the EAST is a ransacked armory. To the WEST is the hallway you came from.
To the SOUTH is a sealed exit gate.. the final way out (locked).
"""
    )
    write()
    choices = [
        "Go West (back to hallway)",
        "Go East (search the armory)",
        "Go South (toward the exit gate)",
        "Attack B-0B",
        "View Inventory"
    ]
    user_choice = get_choice(choices)

    # 0: West -> hall
    if user_choice == 0:
        return hall

    # 1: East -> armory
    elif user_choice == 1:
        return armory

    # 2: South -> try to reach exit gate
    elif user_choice == 2:
        # You can only go south if you've obtained the access module (or maybe later)
        if "Exit Gate Access Module" in inventory:
            write()
            write("With the Access Module in hand, you step to the exit gate and insert it.")
            write()
            pause("Press any key to use the module and open the gate")
            # unlock the exit (end game)
            write()
            write("The huge gate whines open. A stairwell leads up into smoke and the dawn.")
            write()
            pause("Press any key to climb out to the surface")
            write()
            write("You heave yourself up the stairwell and emerge into a world that is burning, smoking, and very much not safe. You survived... for now.")
            write()
            exit()
        else:
            write()
            write("The exit gate is locked and sealed shut. The module around B-0B's neck is the only thing that will operate it.")
            write()
            pause()
            return bs_lair

    # 3: Attack B-0B -> go to attack scene
    elif user_choice == 3:
        return attack_bob

    # 4: inventory
    else:
        write()
        show_inventory()
        write()
        pause()
        return attack_bob


################################################################################
# ARMORY (small ransacked room)
def armory():
    clear()

    has_spear = "Pipe Spear" in inventory

    write_md(
"""
# ARMORY -BROKEN STORAGE ROOM

Lockers lie open and equipment is strewn across the room. A few lockers
have been smashed beyond recognition. Blood prints lead out toward the lair.
"""
    )
    write()

    if not has_spear:
        write("Propped among the wreckage is a long reinforced metal pipe sharpened to a point.")
    else:
        write("The reinforced pipe you found earlier lies at the base of a locker, its tip stained dark.")

    write()
    write("What do you want to do?")
    choices = [
        "Go West back to B-0B's lair",
        "Pick up the Pipe Spear",
        "View Inventory"
    ]
    hidden_choices = []
    if has_spear:
        hidden_choices.append(1)  # hide "Pick up the Pipe Spear"

    user_choice = get_choice(choices, hidden_choices)

    if user_choice == 0:
        return attack_bob

    elif user_choice == 1:
        inventory.append("Pipe Spear")
        write()
        write(
"""
You pry the pipe from a locker. It feels heavy and solid -brutal but effective.
You test the balance. The tip is sharp enough to pierce flesh and bone.
"""
        )
        write()
        pause()
        return armory

    else:
        write()
        show_inventory()
        write()
        pause()
        return armory


################################################################################
# ATTACK_BOB (final encounter)
def attack_bob():
    clear()

    write_md(
"""
# ASSAULT ON B-0B

You creep into the center of the nest. The beast's breath fogs the air.
Every second you hesitate risks it turning and noticing you.

Make your attack count.
"""
    )
    write()
    # If player doesn't have spear, it's an instant death
    if "Pipe Spear" not in inventory:
        write_md(
"""
Desperate, you lunge with bare hands. It's a terrible idea.

B-0B's head snaps toward you with impossible speed. Its maw clamps down
around your shoulder and arm like a steel trap. You scream as pain flares —
bone crunches under its jaw. You try to pull free, but the weight and
strength are too much.

Hot, acidic blood pours into your face. The world tilts. You lose the
sensation in your limbs as the monster tightens its grip.

Everything goes dark.

*** YOU DIED ***
"""
        )
        write()
        pause("Press any key to accept the end.")
        exit()

    # Player has spear -> detailed fight
    else:
        write_md(
"""
You plant your feet and jab the Pipe Spear with everything you have directly
into one of B-0B's eyes. The shaft punches through flesh and bone. The creature
howls -a wet, ungodly sound. It lashes out wildly, sweeping an arm and smashing
metal tables. The nest collapses into a storm of scrap metal and cloth.

You keep driving the spear, again and again, targeting its neck and exposed
gaps where bone shows through the rotted skin. Finally, with a grinding
rattle, B-0B's legs give out. It collapses with an earthquake-sized thud,
claws scrabbling uselessly at the floor.

The module around its neck, cracked and sparking, hangs within reach.
"""
        )
        write()
        # take module
        inventory.append("Exit Gate Access Module")
        write("You tear the glowing Access Module free from the cord around its neck.")
        write()
        pause("Press any key to catch your breath as alarms flare back to life.")

        # After taking it, alarms reactivate -> short dramatic countdown
        write()
        write_md(
"""
A blaring alarm shrieks somewhere in the facility: **FACILITY PURGE INITIATED**.
Red lights strobe. Somewhere above, mechanisms begin the process of
sealing and sterilizing entire wings.

You have only moments before automatic systems lock down the exit or worse.
"""
        )
        write()
        pause("Press any key to run for the exit gate")
        return surface_scene()


################################################################################
# SURFACE SCENE 
def surface_scene():
    clear()
    write_md(
    """
    # THE SURFACE


    The locks disengage and the gate rises. A long streak of white light cuts
    across the bunker floor. You step outside for the first time since the
    collapse.


    The sky is gray and swollen with smoke. Buildings stand like broken ribs.
    Not a sound moves except the dry wind.


    You walk forward. The ground cracks under your boots. Something soft
    squishes beneath your heel. You do not look down.


    A corpse in the distance twitches once. Not a natural twitch. A sudden
    sharp jerk as if yanked by an invisible string.


    Far ahead, three figures stand in the smoke. Still. Unmoving. Their faces
    are hidden. Their heads tilt toward you in the exact same second.

    You blink. They are closer.
    Your pulse starts to pound.
    You cannot stay here.
    """
    )


    pause("Press any key to flee the area...")
    return surface_hub()
################################################################################
# OPEN WORLD HUB #
def surface_hub():
    clear()
    write_md(
"""
# OUTSIDE THE BUNKER

The air outside is thick and gritty. Ash falls like slow snow.
The world feels completely wrong.

You take a step into the ruins, trying to steady your breath.
"""
    )
    write()

    write("1. Explore the ruined street")
    write("2. Approach the collapsed pharmacy")
    write("3. Climb the hill toward the radio tower")
    write("4. Return inside the bunker (not recommended)")

    choice = get_choice(["Street", "Pharmacy", "Tower", "Bunker"])

    if choice == 1:
        return ruined_street()
    if choice == 2:
        return collapsed_pharmacy()
    if choice == 3:
        return radio_tower()
    if choice == 4:
        write("Something slams the bunker door shut behind you.")
        write("You are not alone in the dark.")
        pause("Press any key...")
        return surface_hub()


################################################################################
# RUINED STREET
def ruined_street():
    clear()
    write_md(
    """
    # RUINED STREET


    Cars stand melted into the asphalt. Faces are fused into broken windows.
    One corpse whispers as you pass even though its throat is torn open.


    You search the area.
    """
    )


    if "Respirator Mask" not in inventory:
        inventory.append("Respirator Mask")
    write("You find a damaged but functional respirator mask on a skeleton.")


    pause("Press any key to return.")
    return surface_hub()


################################################################################
# COLLAPSED PHARMACY
def collapsed_pharmacy():
    clear()
    write_md(
    """
    # COLLAPSED PHARMACY


    Shelves have collapsed under rubble. Bottles leak into sticky puddles.
    A sound comes from behind the counter. Something wet drags itself across
    the tiles.
    """
    )


    if "Adrenaline Shot" in inventory:
        write("The creature here has already been dealt with.")
    else:
        creature_fight()


    pause("Press any key to return.")
    return surface_hub()
################################################
# CREATURE FIGHT
def creature_fight():
    clear()
    write_md(
    """
    The creature rises out of the rubble, its shape wrong in every way.
    It does not breathe. It only watches.


    You have seconds to react.


    1. Run back to the street
    2. Hide behind the fallen shelves
    3. Freeze completely
    """
    )
    choice = get_choice(["Run", "Hide", "Freeze"])


    if choice == 1:
        write("You bolt for the doorway. The creature lunges but slips on glass. You escape.")
        pause("Press any key to continue...")
        return ruined_street()


    if choice == 2:
        write("You crouch behind a collapsed shelf. The creature sniffs the air and slowly drifts away. There is an opening to leave now.")
        pause("Press any key to continue...")
        return ruined_street()


    if choice == 3:
        write_md(
    """
    You freeze. Total stillness.


    The creature tilts its head, then rushes you in a blur. There is no time. Maybe next time.
    *** YOU DIED ***
    """
    )
    pause("Press any key...")
    exit()
################################################################################
# RADIO TOWER
def radio_tower():
    clear()
    write_md(
    """
    # RADIO TOWER HILL
    You climb the cracked slope. The city stretches below you like a dead sea.


    The tower at the peak hums even though its wires are torn. When you touch
    the metal, a voice crackles through the dead speakers.


    It whispers your name.
    A recently used flare lies at the base. You can see it shimmering and lighting the sky, it seems close. 
    Too close, you can taste the warm. 
    """
    )


    if "Saw the Flare" not in inventory:
        inventory.append("Saw the Flare")


    pause("Press any key to continue.")


    return final_signal()
#############################
# CALL OUT
def call_out():
    clear()
    write_md(
    """
    # THE WATCHERS


    You shout into the smoke. The figures freeze. One takes a slow step toward
    you. Another mirrors it.


    They do not answer.


    You feel eyes on your back even when you turn.
    """
    )


    pause("Press any key to return.")
    return final_signal()


################################################################################
# FINAL SIGNAL
def final_signal():
    clear()
    write_md(
    """
    # THE LAST CHOICE


    A bright orange flare rises from the far street. Someone is calling for you, they know you're here.
    Or something wants you to come closer.

    You must decide.
    """
    )


    choice = get_choice([
    "Run toward the flare",
    "Avoid it and search for another route",
    "Hide and observe"
    ])


    if choice == 1:
        return ending_survivors()
    if choice == 2:
        return ending_solo()
    if choice == 3:
        return ending_ambush()


################################################################################
# ENDINGS


def ending_survivors():
    clear()
    write_md(
    """
    # ENDING: THE SIGNAL


    You run toward the flare. Figures step out of the smoke. They hold weapons
    but lower them when they see you are alive and breathing.


    They pull you onto a truck and drive into the wasteland. You made it out.
    """
    )
    pause("Press any key to end.")
    exit()




def ending_solo():
    clear()
    write_md(
    """
    # ENDING: THE LONELY ROAD


    You ignore the flare and vanish into the ruins alone. The silence follows
    close behind you.


    Somewhere, humanity might still exist. You will find it in your own time.
    Instead, you turn, your back facing salvation or death. You'll never find out anyway.
    """
    )
    pause("Press any key to end.")
    exit()



def ending_ambush():
    clear()
    write_md(
    """
    # ENDING: THE WATCHERS


    You wait and observe. The figures drift farther without footsteps. When you
    finally move, they are already behind you.


    The world fades under pale hands.
    """
    )

################################################################################
# MAIN RUNNER
if __name__ == "__main__":
    # Start the game
    current_scene = intro
    # run scenes in a loop; scene functions return the next scene function
    while True:
        try:
            current_scene = current_scene()
        except SystemExit:
            # allow clean exit from scenes with exit()
            break
