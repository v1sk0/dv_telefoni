import pystray
from PIL import Image

# Function to toggle the visibility of the console window
def toggle_console(icon, item):
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6 if item.checked else 9)

# Create a system tray menu
menu = (
    pystray.MenuItem('Show/Hide Console', toggle_console, default=True),
    pystray.MenuItem('Exit', lambda: exit())
)

# Create a system tray icon
icon = pystray.Icon('MyIcon', Image.open('dv.ico'), 'My Script', menu)

# Run the system tray icon
icon.run()