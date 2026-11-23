# Yellow Cursor Highlighter

A lightweight Windows 10/11 utility that displays a translucent yellow circle around the mouse pointer. The highlight stays with the mouse pointer over search boxes and text fields; keyboard typing does not hide it. It highlights the **mouse pointer**, not the text insertion caret.

## Quick ways to stop the application

You can stop it at any time in either of these ways:

1. **Keyboard shortcut:** press `Ctrl + Alt + Q`. This global shortcut works while another application is active.
2. **System tray:** find the Yellow Cursor Highlighter icon near the Windows clock (click the `^` hidden-icons arrow if needed), right-click it, and choose **Exit / Stop Highlighter**.

Both methods close the app and stop its background listeners. Turning off **Show yellow highlight** only hides the circle; it does not close the application.

## 1. Download and extract

1. Download the complete ZIP package.
2. In File Explorer, right-click the ZIP file.
3. Choose **Extract All...**, then choose a folder and select **Extract**.
4. Open the extracted `Yellow Cursor Highlighter` folder.

## 2. Install Python (for running the `.py` source)

1. Visit <https://www.python.org/downloads/windows/>.
2. Download a current Python 3 release for Windows.
3. Run the installer and tick **Add python.exe to PATH** if that option appears.
4. Select **Install Now**.
5. Open Command Prompt and check the installation:

```bat
py --version
```

If Windows cannot find `py`, restart Command Prompt after installation. If it still cannot find it, rerun the Python installer and enable the launcher/PATH options.

## 3. Install the required packages

Open the extracted project folder in File Explorer. Click the address bar, type `cmd`, and press Enter. In the Command Prompt window, run:

```bat
py -m pip install -r requirements.txt
```

## 4. Run the Python file

From the same Command Prompt window, run:

```bat
py src\yellow_cursor_highlighter.py
```

The yellow circle should follow the mouse pointer. The app runs in the Windows system tray rather than showing a normal main window.

## 5. Build a standalone EXE

Python is required to build the EXE. From the project folder, run:

```bat
py -m pip install pyinstaller
```

Then build the application:

```bat
py -m PyInstaller --noconfirm --clean --onefile --windowed --name "Yellow Cursor Highlighter" --collect-all PySide6 src\yellow_cursor_highlighter.py
```

When the build finishes, find the application here:

```text
dist\Yellow Cursor Highlighter.exe
```

Double-click the EXE to start it. You can right-click it and choose **Send to > Desktop (create shortcut)** for easier access.

## 6. Optional: start with Windows

Right-click the app's system-tray icon and enable **Start with Windows**. Disable that option from the same menu if you no longer want it to launch automatically.

## Notes

- Designed for Windows 10 and Windows 11.
- The highlight is a mouse-pointer overlay, not a text-caret highlighter.
- The overlay is designed not to intercept mouse clicks or take keyboard focus.
- The application has not been runtime-tested on every Windows configuration.
- If the overlay behaves unexpectedly, exit with `Ctrl + Alt + Q`.

## Credits & License

- **Developer & Maintainer:** MTR-sec
- **GitHub:** [@mtr-sec](https://github.com/mtr-sec)
- **Project:** Yellow Cursor Highlighter
- **Purpose:** A lightweight Windows utility developed to improve mouse pointer visibility.
- **License:** [MIT License](LICENSE)

This project is developed and maintained by **MTR-sec**. It is released under the MIT License, allowing anyone to use, copy, modify, distribute, and contribute to the project under the terms of the license.

See the [LICENSE](LICENSE) file for full license details.
