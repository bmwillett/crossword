from tkinter import filedialog
import tkinter as tk
import logging

log = logging.getLogger("crossword_logger")


def open_file():
    # Make a top-level instance and hide since it is ugly and big.
    root = tk.Tk()
    root.withdraw()

    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    root.geometry('0x0+0+0')

    # Show window again and lift it to top so it can get focus,
    # otherwise dialogs will end up behind the terminal.
    root.deiconify()
    root.lift()
    root.focus_force()

    filename = filedialog.askopenfilename(parent=root)  # Or some other dialog

    # Get rid of the top-level instance once to make it actually invisible.
    root.destroy()

    return filename
