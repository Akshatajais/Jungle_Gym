import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# --- Tkinter root must be initialized BEFORE image loading ---
root = tk.Tk()
root.title("Jungle Gym - AR/VR Rehab Game")
root.geometry("800x600")
root.configure(bg="#dfffe0")  # Jungle leaf greenish

# --- Load images after root is created ---
def load_image(filename):
    path = os.path.join("assets", filename)
    try:
        img = Image.open(path).resize((64, 64), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Failed to load {filename}: {e}")
        return None

# Character images
ducky_img = load_image("ducky.png")
sushi_img = load_image("fox.png")
chad_img = load_image("chad.png")

char_img_map = {
    "Ducky": ducky_img,
    "Sushi": sushi_img,
    "Chad": chad_img
}

# Condition to exercises mapping
exercise_data = {
    "Post-Stroke": ["Make a Fist", "Egg Pinch", "Feather Flick", "Ladder Hop"],
    "Arthritis": ["Make a Fist", "Egg Pinch", "Magic Wand", "Feather Flick"],
    "Parkinson's": ["Make a Fist", "Egg Pinch", "Turtle Walk", "Soccer Save"],
    "Elderly Mobility": ["Turtle Walk", "Ladder Hop", "Make a Fist"],
    "Orthopedic Recovery": ["Magic Wand", "Feather Flick", "Ladder Hop", "Soccer Save"],
    "Carpal Tunnel / Hand Weak": ["Make a Fist", "Egg Pinch", "Magic Wand"],
    "Balance & Coordination": ["Soccer Save", "Turtle Walk", "Ladder Hop"]
}

# Exercise to character mapping
character_map = {
    "Make a Fist": "Ducky",
    "Egg Pinch": "Ducky",
    "Feather Flick": "Ducky",
    "Magic Wand": "Chad",
    "Wrist Curl": "Chad",
    "Bicep Curl": "Chad",
    "Turtle Walk": "Sushi",
    "Ladder Hop": "Sushi",
    "Soccer Save": "Sushi"
}

# Dummy function to simulate game launching
def launch_game(exercise):
    print(f"Launching {exercise}...")

# --- UI Components ---

tk.Label(root, text="🌿 Jungle Gym Rehab 🌿", font=("Helvetica", 24, "bold"), bg="#dfffe0").pack(pady=10)

# Dropdown menu
selected_condition = tk.StringVar()
tk.Label(root, text="Select Condition:", font=("Helvetica", 14), bg="#dfffe0").pack()
condition_dropdown = ttk.Combobox(root, textvariable=selected_condition, state="readonly", font=("Helvetica", 12))
condition_dropdown['values'] = list(exercise_data.keys())
condition_dropdown.pack(pady=5)

# Scrollable exercise display
display_frame = tk.Frame(root, bg="#dfffe0")
display_frame.pack(fill="both", expand=True, padx=10, pady=10)

canvas = tk.Canvas(display_frame, bg="#dfffe0")
scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#dfffe0")

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Exercise listing function
def update_exercises(event=None):
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    condition = selected_condition.get()
    if not condition:
        return

    exercises = exercise_data[condition]
    for ex in exercises:
        char = character_map.get(ex, "Unknown")
        img = char_img_map.get(char, None)

        frame = tk.Frame(scroll_frame, bg="#ffffff", padx=10, pady=10, bd=2, relief="ridge")
        frame.pack(fill="x", padx=5, pady=5)

        if img:
            img_label = tk.Label(frame, image=img, bg="#ffffff")
            img_label.image = img  # Keep a reference
            img_label.pack(side="left", padx=10)

        text_frame = tk.Frame(frame, bg="#ffffff")
        text_frame.pack(side="left", fill="both", expand=True)

        tk.Label(text_frame, text=f"Exercise: {ex}", font=("Helvetica", 14, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(text_frame, text=f"Character: {char}", font=("Helvetica", 12), bg="#ffffff").pack(anchor="w")

        tk.Button(frame, text="Start", command=lambda e=ex: launch_game(e)).pack(side="right", padx=10, pady=5)

# Hook dropdown to update function
condition_dropdown.bind("<<ComboboxSelected>>", update_exercises)

# Launch the GUI loop
root.mainloop()
