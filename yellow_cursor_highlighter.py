"""
Yellow Cursor Highlighter
A small Windows 10/11 utility that displays a translucent yellow circle
around the mouse pointer, including while the pointer is over text fields.
"""

import math
import random
import struct
import sys
import tempfile
import wave
import winsound
import winreg
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QAction, QCursor
from PySide6.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QStyle
from pynput import mouse, keyboard

APP_NAME = "Yellow Cursor Highlighter"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "YellowCursorHighlighter"


def make_click_sound():
    """Create a quiet, short mechanical keyboard-style tap."""
    sound_path = Path(tempfile.gettempdir()) / "yellow_cursor_highlighter_click.wav"
    if sound_path.exists():
        return str(sound_path)

    sample_rate = 44100
    duration = 0.055
    rng = random.Random(21)
    frames = bytearray()

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        low = math.sin(2 * math.pi * 480 * t) * math.exp(-t * 62)
        tick = math.sin(2 * math.pi * 1750 * t) * math.exp(-t * 115)
        noise = (rng.random() * 2 - 1) * math.exp(-t * 165)
        sample = int(13500 * (0.48 * low + 0.18 * tick + 0.08 * noise))
        frames.extend(struct.pack("<h", max(-32768, min(32767, sample))))

    with wave.open(str(sound_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames)

    return str(sound_path)


class ClickBridge(QObject):
    clicked = Signal()
    exit_requested = Signal()


class CursorOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.circle_size = 34
        self.base_radius = self.circle_size / 2
        self.pulse = 0.0
        self.enabled = True
        self.sound_enabled = True
        self.sound_path = make_click_sound()

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.resize(self.circle_size + 12, self.circle_size + 12)

        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.follow_cursor)
        self.cursor_timer.start(16)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_pulse)

        self.show()
        self.make_click_through()
        self.follow_cursor()

    def make_click_through(self):
        """Make the overlay transparent to mouse input without taking focus."""
        if sys.platform != "win32":
            return
        try:
            import ctypes
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            get_style = user32.GetWindowLongW
            set_style = user32.SetWindowLongW
            style = get_style(hwnd, GWL_EXSTYLE)
            set_style(
                hwnd, GWL_EXSTYLE,
                style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
            )
            # Reassert topmost status without activation.
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except Exception:
            # Qt's WindowStaysOnTopHint remains as a fallback.
            pass

    def follow_cursor(self):
        # Deliberately do not inspect keyboard focus or the active control.
        # This keeps the pointer highlight visible over search boxes and text fields.
        if not self.enabled:
            return

        pos = QCursor.pos()
        self.move(pos.x() - self.width() // 2, pos.y() - self.height() // 2)

        if not self.isVisible():
            self.show()
            self.make_click_through()

        # Some applications can change topmost ordering; reassert it periodically.
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.SetWindowPos(
                    int(self.winId()), -1, 0, 0, 0, 0,
                    0x0002 | 0x0001 | 0x0010
                )
            except Exception:
                pass

    def register_click(self):
        if not self.enabled:
            return
        if self.sound_enabled:
            try:
                winsound.PlaySound(
                    self.sound_path,
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                )
            except Exception:
                pass
        self.pulse = 1.0
        if not self.animation_timer.isActive():
            self.animation_timer.start(16)
        self.update()

    def animate_pulse(self):
        self.pulse -= 0.10
        if self.pulse <= 0:
            self.pulse = 0
            self.animation_timer.stop()
        self.update()

    def paintEvent(self, event):
        if not self.enabled:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        radius = self.base_radius + self.pulse * 7
        alpha = 112 if self.pulse <= 0 else 150

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 220, 0, alpha)))
        painter.drawEllipse(
            int(cx - radius), int(cy - radius),
            int(radius * 2), int(radius * 2)
        )

        painter.setPen(QPen(QColor(205, 155, 0, 175), 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            int(cx - radius), int(cy - radius),
            int(radius * 2), int(radius * 2)
        )

    def toggle_highlight(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.show()
            self.follow_cursor()
        else:
            self.hide()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled


def startup_command():
    """Use the EXE when frozen, otherwise launch the script with pythonw."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    python_exe = Path(sys.executable)
    pythonw = python_exe.with_name("pythonw.exe")
    launcher = pythonw if pythonw.exists() else python_exe
    return f'"{launcher}" "{Path(__file__).resolve()}"'


def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, RUN_VALUE)
        return True
    except OSError:
        return False


def set_startup(enabled):
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        if enabled:
            winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, RUN_VALUE)
            except FileNotFoundError:
                pass


class YellowCursorApp:
    def __init__(self, app):
        self.app = app
        self.overlay = CursorOverlay()
        self.bridge = ClickBridge()
        self.bridge.clicked.connect(self.overlay.register_click)

        self.listener = mouse.Listener(
            on_click=self.on_mouse_click
        )
        self.listener.start()

        # Global emergency/quick-exit shortcut works even when another app is active.
        self.exit_hotkey = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+q": self.bridge.exit_requested.emit
        })
        self.exit_hotkey.start()
        self.bridge.exit_requested.connect(self.exit_app)

        self.tray = QSystemTrayIcon(
            app.style().standardIcon(QStyle.SP_ComputerIcon), app
        )
        self.tray.setToolTip(APP_NAME)
        menu = QMenu()

        self.highlight_action = QAction("Show yellow highlight", menu)
        self.highlight_action.setCheckable(True)
        self.highlight_action.setChecked(True)
        self.highlight_action.triggered.connect(self.toggle_highlight)
        menu.addAction(self.highlight_action)

        self.sound_action = QAction("Enable click sound", menu)
        self.sound_action.setCheckable(True)
        self.sound_action.setChecked(True)
        self.sound_action.triggered.connect(self.toggle_sound)
        menu.addAction(self.sound_action)

        self.startup_action = QAction("Start with Windows", menu)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(is_startup_enabled())
        self.startup_action.triggered.connect(self.toggle_startup)
        menu.addAction(self.startup_action)

        menu.addSeparator()
        exit_action = QAction("Exit / Stop Highlighter", menu)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.bridge.clicked.emit()

    def toggle_highlight(self, checked):
        self.overlay.toggle_highlight()
        self.highlight_action.setChecked(self.overlay.enabled)

    def toggle_sound(self, checked):
        self.overlay.toggle_sound()
        self.sound_action.setChecked(self.overlay.sound_enabled)

    def toggle_startup(self, checked):
        try:
            set_startup(checked)
        except OSError as exc:
            self.startup_action.setChecked(is_startup_enabled())
            self.tray.showMessage(APP_NAME, f"Could not update startup setting: {exc}")

    def exit_app(self):
        # Stop background listeners and timers before closing the application.
        for background_listener in (self.listener, self.exit_hotkey):
            try:
                background_listener.stop()
            except Exception:
                pass
        self.overlay.cursor_timer.stop()
        self.overlay.animation_timer.stop()
        self.overlay.close()
        self.tray.hide()
        self.app.quit()


def main():
    if sys.platform != "win32":
        raise SystemExit("Yellow Cursor Highlighter is designed for Windows 10/11.")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    YellowCursorApp(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
