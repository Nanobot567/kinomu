import dearpygui.dearpygui as dpg
import json

dpg.create_context()
dpg.create_viewport(title="kinomu")
dpg.setup_dearpygui()


# TODO: add dots at click locations to show where arrow should go, or something like that
# it needs an indicator!

COLOR_PRESETS = {
    "Neutral / Default": [255, 255, 255, 255],
    "Acquaintence": [135, 255, 107, 255],
    "Friend": [35, 180, 0, 255],
    "Best Friend": [0, 255, 0, 255],
    "Love Interest": [190, 0, 150, 255],
    "Partner": [140, 0, 226, 255],
    "Dislikes": [255, 100, 100, 255],
    "Hates": [100, 0, 0, 255],
    "Annoyed By": [255, 0, 0, 255],
}

viewport_width = 1280
viewport_height = 800

mouse_pos_1 = [0, 0]
mouse_pos_2 = [0, 0]

click_pos = [0, 0]

drawmode = "Arrow"

arrow_ids = 0
person_ids = 0

currently_dragging = False

undo_stack = []

def convert_color(color):
    for i, v in enumerate(color):
        color[i] = v * 255
    
    return color

def set_arrow_color(uno, dos, tres):
    dpg.set_value("arrow_color", dpg.get_value(uno))

with dpg.window(label="Context Menu", modal=False, popup=True, show=False, tag="right_click_menu", no_title_bar=True):
    dpg.create_context()
    dpg.add_text("All those beautiful files will be deleted.\nThis operation cannot be undone!")
    dpg.add_separator()
    dpg.add_checkbox(label="Don't ask me next time")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("right_click_menu", show=False))
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("right_click_menu", show=False))

with dpg.window(label="Person name", modal=True, popup=True, show=False, tag="person_name_dialog", no_title_bar=True):
    dpg.add_text("Please enter a name:")
    dpg.add_input_text(tag="person_name_dialog_text")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=lambda: draw_person(dpg.get_value("person_name_dialog_text")))
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("person_name_dialog", show=False))

def draw_linking_arrow(doublesided=False):
    global currently_dragging
    if dpg.is_item_focused("kinomu_editor") and currently_dragging:
        global mouse_pos_1, arrow_ids

        arrow_ids += 1

        dpg.draw_arrow(dpg.get_mouse_pos(), mouse_pos_1, parent="kinomu_editor", thickness=4, color=dpg.get_value("arrow_color"), tag="arrow"+str(arrow_ids)) # can delete with tag!

        if doublesided:
            dpg.draw_arrow(mouse_pos_1, dpg.get_mouse_pos(), parent="kinomu_editor", thickness=4, color=dpg.get_value("arrow_color"), tag="dbarrow"+str(arrow_ids))

            undo_stack.append(["arrow"+str(arrow_ids), "dbarrow"+str(arrow_ids)])
        else:
            undo_stack.append("arrow"+str(arrow_ids))

        mouse_pos_1 = dpg.get_mouse_pos()

    currently_dragging = False

def draw_person(name="person"):
    global mouse_pos_1, person_ids

    dpg.hide_item("person_name_dialog")

    person_ids += 1

    dpg.draw_text(label=name, text=name, pos=click_pos, size=24, parent="kinomu_editor", tag="person"+str(person_ids))

    undo_stack.append("person"+str(person_ids))

    mouse_pos_1 = dpg.get_mouse_pos(local=False)

    # dpg.draw_rectangle(dpg.get_mouse_pos(), mouse_pos_1, parent="kinomu_editor")

def start_drag():
    global currently_dragging

    if dpg.is_item_focused("kinomu_editor"):
        global mouse_pos_1
        mouse_pos_1 = dpg.get_mouse_pos(local=False)

    currently_dragging = False

def set_drawmode(one, two=None, three=None):
    global drawmode

    if one and not two:
        dpg.set_value("draw_mode", one)
        drawmode = one
    else:
        drawmode = two

def draw_request():
    global drawmode, click_pos
    
    if dpg.is_item_focused("kinomu_editor"):
        if drawmode == "Arrow":
            draw_linking_arrow()
        elif drawmode == "Double-sided arrow":
            draw_linking_arrow(True)
        elif drawmode == "Person":
            click_pos = dpg.get_mouse_pos(local=False)

            dpg.set_item_pos("person_name_dialog", pos=click_pos)
            dpg.show_item("person_name_dialog")
            # draw_person()

with dpg.window(tag="kinomu_editor", width=viewport_width, height=viewport_height):
    pass

def undo():
    global arrow_ids, person_ids

    if len(undo_stack) > 0:
        item = undo_stack.pop()

        if isinstance(item, list):
            for i in item:
                if i.startswith("arrow"):
                    arrow_ids -= 1
                dpg.delete_item(i)
        else:
            if item.startswith("arrow"):
                arrow_ids -= 1
            else:
                person_ids -= 1

            dpg.delete_item(item)

with dpg.window(tag="kinomu_tools", pos=[viewport_width - 250, 30], label="Tools", width=200, height=300):
    dpg.add_radio_button(["Arrow", "Double-sided arrow", "Person"], tag="draw_mode", callback=set_drawmode)
 
    dpg.add_separator()

    dpg.add_color_edit(label="Arrow color", no_inputs=True, tag="arrow_color", default_value=[255, 255, 255])    
    with dpg.collapsing_header(label="Color Presets"):
        for k in COLOR_PRESETS.keys():
            with dpg.group(horizontal=True, indent=8):
                dpg.add_color_button(label=k, callback=set_arrow_color, default_value=COLOR_PRESETS[k])
                dpg.add_text(default_value=k)
            
    dpg.add_separator()

    dpg.add_button(label="Undo", callback=undo)

def load(sender, name):
    global arrow_ids, person_ids

    for i in range(1, arrow_ids + 1):
        if dpg.does_item_exist("arrow"+str(i)):
            dpg.delete_item("arrow"+str(i))
            if dpg.does_item_exist("dbarrow"+str(i)):
                dpg.delete_item("dbarrow"+str(i))

    for i in range(1, person_ids + 1):
        if dpg.does_item_exist("person"+str(i)):
            dpg.delete_item("person"+str(i))

    arrow_ids = 0
    person_ids = 0

    with open(name["file_path_name"], "r") as f:
        data = json.loads(f.read())

        for i, v in enumerate(data):
            if "arrow" in v[0]:
                color = convert_color(v[2])

                arrow_ids += 1

                dpg.draw_arrow(v[1][0], v[1][1], parent="kinomu_editor", thickness=4, color=color, tag="arrow"+str(arrow_ids))
                if v[0] == "dbarrow":
                    dpg.draw_arrow(v[1][1], v[1][0], parent="kinomu_editor", thickness=4, color=color, tag="dbarrow"+str(arrow_ids))

            elif v[0] == "person":
                person_ids += 1

                dpg.draw_text(label=v[1], text=v[1], pos=v[2], size=24, parent="kinomu_editor", tag="person"+str(person_ids))

def save():
    writedata = []

    for i in range(1, arrow_ids + 1): 
        objwritedata = []

        if dpg.does_item_exist("arrow"+str(i)):
            arrowcfg = dpg.get_item_configuration("arrow"+str(i))

            if dpg.does_item_exist("dbarrow"+str(i)):
                objwritedata.append("dbarrow")
            else:
                objwritedata.append("arrow")

            objwritedata.append([arrowcfg["p1"], arrowcfg["p2"]])
            objwritedata.append(arrowcfg["color"])

            writedata.append(objwritedata)

    for i in range(1, person_ids + 1):
        objwritedata = []

        if dpg.does_item_exist("person"+str(i)):
            objwritedata.append("person")
            objwritedata.append(dpg.get_item_label("person"+str(i)))
            objwritedata.append(dpg.get_item_configuration("person"+str(i))["pos"])
            
            writedata.append(objwritedata)
        
    with open("save.knm", "w+") as f:
        f.write(json.dumps(writedata))

with dpg.file_dialog(directory_selector=False, show=False, callback=load, id="filedialog_load", width=700 ,height=400, default_path="."):
    dpg.add_file_extension(".knm", color=(0, 255, 0, 255), custom_text="[kinomu save]")

def ctrl_key_handler(before_key=""):
    if dpg.is_key_down(dpg.mvKey_Control):
        if before_key == "a":
            set_drawmode("Arrow")
        elif before_key == "d":
            set_drawmode("Double-sided arrow")
        elif before_key == "o":
            dpg.show_item("filedialog_load")
        elif before_key == "p":
            set_drawmode("Person")
        elif before_key == "s":
            save()
        elif before_key == "z":
            undo()

def set_dragging_var():
    global currently_dragging

    delta = dpg.get_mouse_drag_delta()

    if abs(delta[0]) + abs(delta[1]) > 50:
        currently_dragging = True

with dpg.handler_registry():
    dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=start_drag)
    dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=set_dragging_var)
    dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=draw_request)

    dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=lambda: dpg.configure_item("right_click_menu", show=True))

    dpg.add_key_press_handler(dpg.mvKey_A, callback=lambda: ctrl_key_handler("a"))
    dpg.add_key_press_handler(dpg.mvKey_D, callback=lambda: ctrl_key_handler("d"))
    dpg.add_key_press_handler(dpg.mvKey_O, callback=lambda: ctrl_key_handler("o"))
    dpg.add_key_press_handler(dpg.mvKey_P, callback=lambda: ctrl_key_handler("p"))
    dpg.add_key_press_handler(dpg.mvKey_S, callback=lambda: ctrl_key_handler("s"))
    dpg.add_key_press_handler(dpg.mvKey_Z, callback=lambda: ctrl_key_handler("z"))

with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Load", callback=lambda: dpg.show_item("filedialog_load"))
        dpg.add_menu_item(label="Save", callback=save)
        dpg.add_menu_item(label="Save As", callback=print)

        # with dpg.menu(label="Settings"):
        #     dpg.add_menu_item(label="Setting 1", callback=print, check=True)
        #     dpg.add_menu_item(label="Setting 2", callback=print)

dpg.set_primary_window("kinomu_editor", True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
