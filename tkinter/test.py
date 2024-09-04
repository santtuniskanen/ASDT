import tkinter as tk

window = tk.Tk()
window.geometry("300x600+500+300")

# functions

def function():
    print("Hello")

# widgets

text=tk.Label(window, text="tkinterface")
text.place(x=10,y=30)

button=tk.Button(window, text="button", command=function)
button.place(x=10,y=60)

window.mainloop()
