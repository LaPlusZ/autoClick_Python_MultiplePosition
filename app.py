import tkinter as tk
from tkinter import messagebox, simpledialog
import keyboard

# Import our separated modules
import preset_manager
from clicker_core import ClickerThread

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("450x405")
        self.root.resizable(False, False)
        self.root.configure(bg="#F1F1F1")

        # Application State
        self.click_positions = []
        self.presets = {}
        self.clicker_thread = None

        # Build the GUI
        self.create_preset_frame()
        self.create_interval_frame()
        self.create_position_frame()
        self.create_control_frame()
        self.create_status_bar()

        # Bind right-click menu
        self.listbox.bind("<Button-3>", self.on_right_click)

        # Setup Hotkeys
        keyboard.add_hotkey("F6", self.toggle_clicking)
        keyboard.add_hotkey("F8", self.add_current_position)

        # Load initial data
        self.load_all_presets()

    # --- Preset Management ---
    def create_preset_frame(self):
        preset_frame = tk.LabelFrame(self.root, text="Preset Management")
        preset_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.current_preset_var = tk.StringVar(self.root)
        self.current_preset_var.trace("w", self.on_preset_select)

        self.preset_menu = tk.OptionMenu(preset_frame, self.current_preset_var, "")
        self.preset_menu.config(width=19)
        self.preset_menu.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(preset_frame, text="Save", command=self.save_current_preset, width=10).pack(side=tk.LEFT, padx=(0,5), pady=5)
        tk.Button(preset_frame, text="Save As...", command=self.save_preset_as, width=10).pack(side=tk.LEFT, padx=(0,5), pady=5)
        tk.Button(preset_frame, text="Delete", command=self.delete_current_preset, width=10).pack(side=tk.LEFT, pady=5)

    def load_all_presets(self):
        self.presets = preset_manager.load_presets()
        self.update_preset_menu()
        
        if self.presets:
            first_preset_name = list(self.presets.keys())[0]
            self.current_preset_var.set(first_preset_name)
        else:
            self.current_preset_var.set("")

    def update_preset_menu(self):
        menu = self.preset_menu["menu"]
        menu.delete(0, "end")
        sorted_presets = sorted(self.presets.keys())
        for name in sorted_presets:
            menu.add_command(label=name, command=lambda value=name: self.current_preset_var.set(value))

    def on_preset_select(self, *args):
        selected_preset = self.current_preset_var.get()
        if selected_preset in self.presets:
            self.click_positions = self.presets[selected_preset].copy()
            self.update_listbox()
            self.update_status(f"Loaded preset: {selected_preset}")

    def save_current_preset(self):
        preset_name = self.current_preset_var.get()
        if not preset_name:
            messagebox.showwarning("Warning", "No preset selected. Use 'Save As...' to create one.")
            return
        self.presets[preset_name] = self.click_positions
        preset_manager.save_presets(self.presets)
        self.update_status(f"Preset '{preset_name}' saved.")
        messagebox.showinfo("Success", f"Preset '{preset_name}' has been saved.")

    def save_preset_as(self):
        preset_name = simpledialog.askstring("Save As", "Enter a name for the new preset:")
        if preset_name:
            self.presets[preset_name] = self.click_positions
            preset_manager.save_presets(self.presets)
            self.update_preset_menu()
            self.current_preset_var.set(preset_name)
            self.update_status(f"Preset '{preset_name}' created.")

    def delete_current_preset(self):
        preset_name = self.current_preset_var.get()
        if not preset_name:
            messagebox.showwarning("Warning", "No preset selected to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the preset '{preset_name}'?"):
            del self.presets[preset_name]
            if not self.presets:
                self.presets["default"] = []
            preset_manager.save_presets(self.presets)
            self.update_preset_menu()
            first_preset = list(self.presets.keys())[0]
            self.current_preset_var.set(first_preset)

    # --- Click Interval ---
    def create_interval_frame(self):
        settings_frame = tk.LabelFrame(self.root, text="Click Interval")
        settings_frame.pack(fill="x", padx=10, pady=5)

        self.hours_var = tk.StringVar(value="0")
        self.mins_var = tk.StringVar(value="0")
        self.secs_var = tk.StringVar(value="0")
        self.milliseconds_var = tk.StringVar(value="300")

        vars = [self.hours_var, self.mins_var, self.secs_var, self.milliseconds_var]
        labels = ["hours", "mins", "secs", "milliseconds"]
        
        for text, var in zip(labels, vars):
            tk.Entry(settings_frame, textvariable=var, width=8, justify="right").pack(side=tk.LEFT, padx=5, pady=5)
            tk.Label(settings_frame, text=text).pack(side=tk.LEFT)

    def get_interval(self):
        try:
            h = float(self.hours_var.get())
            m = float(self.mins_var.get())
            s = float(self.secs_var.get())
            ms = float(self.milliseconds_var.get())
            return (h * 3600) + (m * 60) + s + (ms / 1000)
        except ValueError:
            self.update_status("Error: Invalid interval value.")
            return 0.3 # Default to 300ms

    # --- Position Management ---
    def create_position_frame(self):
        position_frame = tk.LabelFrame(self.root, text="Click Positions")
        position_frame.pack(fill="x", padx=10, pady=5)

        self.listbox = tk.Listbox(position_frame, width=40, height=8)
        self.listbox.pack(padx=5, pady=5, side="left")

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected)

        button_row_frame = tk.Frame(position_frame)
        button_row_frame.pack(pady=2, side=tk.LEFT, padx=5)

        tk.Button(button_row_frame, text="Add Pos (F8)", command=self.add_current_position, height=2, width=21).pack(pady=2)
        tk.Button(button_row_frame, text="Add Key", command=self.add_keypress_popup, height=2, width=21).pack(pady=2)
        tk.Button(button_row_frame, text="Remove Selected", command=self.remove_position, height=2, width=21).pack(pady=2)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for action in self.click_positions:
            if action["type"] == "click":
                move_text = " (MC)" if action.get("move_before_click", False) else ""
                self.listbox.insert(tk.END, f"Click: {action['x']}, {action['y']}{move_text}")
            elif action["type"] == "keypress":
                self.listbox.insert(tk.END, f"Key Press: {action['key']}")

    def add_current_position(self):
        # We need to import pyautogui for this one-off use
        import pyautogui 
        x, y = pyautogui.position()
        self.click_positions.append({"type": "click", "x": x, "y": y, "move_before_click": True}) # Defaulting 'move' to True
        self.update_listbox()
        self.update_status(f"Added position ({x}, {y}). Press 'Save' to keep changes.")

    def remove_position(self):
        try:
            index = self.listbox.curselection()[0]
            del self.click_positions[index]
            self.update_listbox()
            self.update_status("Removed position. Press 'Save' to keep changes.")
        except IndexError:
            messagebox.showwarning("Warning", "Select a position to remove")

    def add_keypress_popup(self):
        def confirm():
            key = entry.get().strip()
            if key:
                self.click_positions.append({"type": "keypress", "key": key})
                self.update_listbox()
                self.update_status(f"Added key press ({key}). Press 'Save' to keep changes.")
                popup.destroy()
            else:
                messagebox.showwarning("Warning", "Enter a valid key!")

        popup = tk.Toplevel(self.root)
        popup.title("Add Key Press")
        popup.geometry("250x100")
        popup.grab_set()

        tk.Label(popup, text="Enter key to press:").pack(pady=5)
        entry = tk.Entry(popup, width=20)
        entry.pack(pady=2)
        entry.focus_set()
        tk.Button(popup, text="Add", command=confirm).pack(pady=5)

    def on_right_click(self, event):
        try:
            index = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.listbox.activate(index)
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def edit_selected(self):
        try:
            index = self.listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("Warning", "No item selected to edit.")
            return

        action = self.click_positions[index]
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Action")
        edit_window.geometry("250x150")
        edit_window.grab_set()

        def save_changes():
            try:
                if action["type"] == "click":
                    new_x = int(x_entry.get())
                    new_y = int(y_entry.get())
                    move = move_var_edit.get()
                    action.update({"x": new_x, "y": new_y, "move_before_click": move})
                elif action["type"] == "keypress":
                    new_key = key_entry.get().strip()
                    if not new_key:
                        messagebox.showerror("Invalid", "Key cannot be empty.")
                        return
                    action["key"] = new_key
                
                self.click_positions[index] = action
                self.update_listbox()
                self.update_status("Action edited. Press 'Save' to keep changes.")
                edit_window.destroy()

            except ValueError:
                messagebox.showerror("Invalid", "X and Y must be integers.")

        if action["type"] == "click":
            tk.Label(edit_window, text="X:").pack()
            x_entry = tk.Entry(edit_window)
            x_entry.insert(0, str(action["x"]))
            x_entry.pack()

            tk.Label(edit_window, text="Y:").pack()
            y_entry = tk.Entry(edit_window)
            y_entry.insert(0, str(action["y"]))
            y_entry.pack()

            move_var_edit = tk.BooleanVar(value=action.get("move_before_click", False))
            tk.Checkbutton(edit_window, text="Move Before Click", variable=move_var_edit).pack()
        
        elif action["type"] == "keypress":
            tk.Label(edit_window, text="Key:").pack()
            key_entry = tk.Entry(edit_window)
            key_entry.insert(0, action["key"])
            key_entry.pack()

        tk.Button(edit_window, text="Save", command=save_changes).pack(pady=10)

    # --- Controls & Status ---
    def create_control_frame(self):
        control_frame = tk.LabelFrame(self.root, text="Controls")
        control_frame.pack(fill="x", padx=10, pady=5)

        self.start_button = tk.Button(control_frame, text="Start (F6)", command=self.toggle_clicking, height=2)
        self.start_button.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        self.stop_button = tk.Button(control_frame, text="Stop (F6)", command=self.toggle_clicking, height=2, state=tk.DISABLED)
        self.stop_button.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    def create_status_bar(self):
        self.status_label = tk.Label(self.root, text="Status: Idle", anchor=tk.CENTER)
        self.status_label.pack(side=tk.BOTTOM, fill="x")

    def update_status(self, text):
        self.status_label.config(text=f"Status: {text}")

    # --- Core Clicker Logic ---
    def toggle_clicking(self):
        if self.clicker_thread and self.clicker_thread.is_alive():
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if not self.click_positions:
            self.update_status("No actions to perform.")
            return

        interval = self.get_interval()
        if interval <= 0:
            self.update_status("Interval must be positive.")
            return

        self.update_status("Clicking...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Create and start the new clicker thread
        self.clicker_thread = ClickerThread(self.click_positions, interval)
        self.clicker_thread.start()

    def stop_clicking(self):
        if self.clicker_thread:
            self.clicker_thread.stop()
            self.clicker_thread = None
        
        self.update_status("Stopped")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()