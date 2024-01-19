import tkinter as tk
from tkinter import font
from scripts.utils import *

root = tk.Tk()
root.title("Bold Text on Hover")

b = FancyButton(root, "CIAO", font=("Proxima Nova", 16))
b.grid(row=0, column=0)

root.mainloop()
