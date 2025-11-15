# autoClick_Python_MultiplePosition

A simple GUI auto-clicker built with Python and Tkinter. This application allows you to record a sequence of mouse clicks and keyboard presses and play them back in a loop with a customizable interval.

## Features

* **Preset Management:** Save and load different action sequences as named presets.
* **Multiple Action Types:** Record both mouse clicks and keyboard presses.
* **Customizable Interval:** Set a precise time interval between each action, from milliseconds up to hours.
* **Global Hotkeys:**
    * **Start/Stop (F6):** Easily start or stop the action loop.
    * **Add Position (F8):** Quickly add your current mouse cursor's (X, Y) coordinates to the action list.
* **Action List Editing:** Right-click an action in the list to edit its coordinates/key, or select and remove it.
* **Multi-threaded:** The clicking loop runs in a separate thread, so the GUI never freezes.
* **DirectInput:** Uses `pydirectinput` for more reliable clicks in games and other applications.

## Requirements

The application requires the following Python libraries.

```
keyboard
pyautogui
pydirectinput
```

You can install them all by running:
```bash
pip install keyboard pyautogui pydirectinput
```

## How to Use

1.  **Install Dependencies:**
    ```bash
    pip install keyboard pyautogui pydirectinput
    ```

2.  **Run the Application:**
    ```bash
    python app.py
    ```

3.  **Add Actions:**
    * Move your mouse to the desired location and press **F8** to add a click action.
    * Click the **"Add Key"** button to add a keyboard press (e.g., "e", "space", "enter").

4.  **Manage Presets:**
    * Click **"Save As..."** to save your current action list as a new preset.
    * The preset will be saved in the `presets.json` file.
    * You can select, save over, or delete presets using the dropdown and buttons.

5.  **Set Interval:**
    * Adjust the time *between* each action using the "Click Interval" fields.

6.  **Run:**
    * Press **F6** or click the **"Start (F6)"** button.
    * The app will now execute your action list, one by one, with the specified interval.
    * Press **F6** or click **"Stop (F6)"** at any time.

## Building from Source (EXE)

You can bundle this application into a single `.exe` file using **PyInstaller**.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Build the Executable:**
    Run this command from your project's directory:
    ```bash
    pyinstaller --onefile --windowed app.py
    ```
    * `--onefile`: Bundles everything into a single `.exe`.
    * `--windowed`: Prevents a black console window from opening when you run the app.

3.  **Find Your App:**
    Your finished `app.exe` will be located in the newly created `dist` folder.