from tkinter import filedialog, messagebox, simpledialog, dialog
import tkinter as tk
import logging

log = logging.getLogger("crossword_logger")


def open_file():
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()

    filename = filedialog.askopenfilename(parent=root)

    root.destroy()

    return filename

def yesno_dialog(title, message):
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()

    res = messagebox.askquestion(title, message, parent=root)

    root.destroy()

    return res == 'yes'


def dialogbox(title, message, **items):
    master = tk.Tk()
    var = tk.IntVar()
    var.set(0)

    def quit_loop():
        global selection
        selection = var.get()
        master.quit()

    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    size = tuple(int(_) for _ in master.geometry().split('+')[0].split('x'))
    x = screen_width / 2 - size[0] / 2
    y = screen_height / 2 - size[1] / 2
    master.geometry("+%d+%d" % (x, y))
    master.title(title)

    tk.Label(master, text=message).grid(row=0, sticky=tk.W)
    for i, option in enumerate(items):
        tk.Radiobutton(master, text=items[option], variable=var, value=i).grid(row=i+1, sticky=tk.W)
    tk.Button(master, text="OK", command=quit_loop).grid(row=len(items)+1, sticky=tk.W)

    master.mainloop()
    master.destroy()
    return selection