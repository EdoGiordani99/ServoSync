import tkinter as tk

def change_menu():
    # Clear the existing menu
    for item in menu.winfo_children():
        item.destroy()

    # Create new menu items
    file_menu = tk.Menu(menu, tearoff=0)
    file_menu.add_command(label="New", command=lambda: print("New"))
    file_menu.add_command(label="Open", command=lambda: print("Open"))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.destroy)

    edit_menu = tk.Menu(menu, tearoff=0)
    edit_menu.add_command(label="Cut", command=lambda: print("Cut"))
    edit_menu.add_command(label="Copy", command=lambda: print("Copy"))
    edit_menu.add_command(label="Paste", command=lambda: print("Paste"))

    # Add the new menu items
    menu.add_cascade(label="File", menu=file_menu)
    menu.add_cascade(label="Edit", menu=edit_menu)

# Create the main window
root = tk.Tk()
root.title("Dynamic Menu Example")

# Create the initial menu
menu = tk.Menu(root)
root.config(menu=menu)

# Create initial menu items
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="New", command=lambda: print("New"))
file_menu.add_command(label="Open", command=lambda: print("Open"))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)

edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label="Cut", command=lambda: print("Cut"))
edit_menu.add_command(label="Copy", command=lambda: print("Copy"))
edit_menu.add_command(label="Paste", command=lambda: print("Paste"))

# Add initial menu items to the menu
menu.add_cascade(label="File", menu=file_menu)
menu.add_cascade(label="Edit", menu=edit_menu)

# Create a button to trigger menu change
change_menu_button = tk.Button(root, text="Change Menu", command=change_menu)
change_menu_button.pack(pady=10)

# Start the main loop
root.mainloop()
