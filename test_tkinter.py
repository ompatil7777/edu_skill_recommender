import tkinter as tk
from tkinter import ttk

def main():
    print("Creating simple Tkinter window...")
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x200")
    
    label = ttk.Label(root, text="Hello, Tkinter!")
    label.pack(pady=20)
    
    button = ttk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=10)
    
    print("Starting mainloop...")
    root.mainloop()
    print("Window closed.")

if __name__ == "__main__":
    main()