# ----------------------------
# GUI Libraries
# ----------------------------

import tkinter as tk                  # Main Tkinter library for building the GUI window and widgets
from tkinter import ttk               # Themed Tkinter widgets (modern styling)
from tkinter import colorchooser      # Allows user to pick custom colors
from tkinter import simpledialog      # Used for pop-up input dialogs
from tkinter import messagebox        # Used for pop-up alerts and messages

# ----------------------------
# Core Project Files
# ----------------------------

from Pet import Pet                   # Base Pet class containing core attributes and logic

# ----------------------------
# Standard Python Libraries
# ----------------------------

import os                             # Used for environment variables (e.g., API key security)
import openai                         # OpenAI API for AI-generated responses and descriptions
import random                         # Used for random events, activities, and simulation logic

# ----------------------------
# Species-Specific Activity & Training Enums
# Each species has its own set of play activities and training options
# ----------------------------

from Cat import CatActivities, CatTraining
from Bird import BirdActivities, BirdTraining
from Dog import DogActivities, DogTraining
from Fish import FishActivities, FishTraining
from Guinea_Pig import GuineaPigActivities, GuineaPigTraining
from Hamster import HamsterActivities, HamsterTraining
from Horse import HorseActivities, HorseTraining
from Lizard import LizardActivities, LizardTraining
from Rabbit import RabbitActivities, RabbitTraining
from Snake import SnakeActivities, SnakeTraining
from Turtle import TurtleActivities, TurtleTraining

# ----------------------------
# Additional Gameplay Enums which are pet type independent
# ----------------------------

from Chores import Chores             # Available chore options for earning money
from Clean import Clean               # Cleaning action options
from Sleep import SleepUpgrade        # Sleep-related upgrades or rest improvements

# Set the OpenAI API key so that requests to OpenAI can be authenticated
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define a list of standard pet types that the user can select from
# The "Other" option allows the user to input a custom species
PET_TYPES = [
    "Dog", "Cat", "Bird", "Fish", "Hamster", "Rabbit",
    "Guinea Pig", "Horse", "Lizard", "Snake", "Turtle", "Other"
]

class Virtual_Pet:
    def __init__(self, root):
        # Store the root Tkinter window for use throughout the GUI
        self.root = root

        # Set the window title that appears at the top of the GUI
        self.root.title("Virtual Pet")

        # Set the background color of the main window
        self.root.configure(bg="#C0C0C0")

        # Set the default window size: 900 pixels wide, 600 pixels tall
        self.root.geometry("900x600")

        # Initialize the pet object and color
        self.pet = None
        self.color = None

        # --- Frames ---
        self.left_frame = tk.Frame(root, bg="#C0C0C0")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.right_frame = tk.Frame(root, bg="#C0C0C0")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Help/Tutorial Button Top-Right ---
        self.help_btn = tk.Button(
            self.right_frame,
            text="Help/Tutorial",
            command=self.show_tutorial,
            bg="#A9A9A9", fg="black"
        )
        self.help_btn.pack(anchor="ne", padx=10, pady=10)

        # --- Console Title ---
        title_frame = tk.Frame(self.right_frame, bg="#C0C0C0")
        title_frame.pack(fill=tk.X, pady=(1, 0))  # smaller top padding to move higher

        self.console_title_label = tk.Label( # Title above console that adjusts based on the name and species of the pet
            title_frame,
            text="Life of —",
            fg="black",
            bg="#C0C0C0",
            font=("Consolas", 25, "bold")
        )
        self.console_title_label.pack(anchor="n")  # top center

        # --- Console Frame ---
        console_frame = tk.Frame(self.right_frame, bg="#C0C0C0")
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.console = tk.Text( # Setting up the console
            console_frame,
            bg="#121212",
            fg="#00b3ff",
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=("Consolas", 14)
        )
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(console_frame, command=self.console.yview) # Add a scrollbar for the console
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)

        # --- Pet Info Section ---
        self.info_frame = tk.Frame(self.left_frame, bg="#C0C0C0")
        self.info_frame.pack(pady=10)

        tk.Label(self.info_frame, text="Name", fg="black", bg="#C0C0C0").pack()
        self.name_entry = tk.Entry(self.info_frame, bg="#333333", fg="white")
        self.name_entry.pack()

        tk.Label(self.info_frame, text="Species", fg="black", bg="#C0C0C0").pack()
        self.species_var = tk.StringVar(value=PET_TYPES[0])
        self.species_frame = tk.Frame(self.info_frame, bg="#C0C0C0")
        self.species_frame.pack()
        self.species_menu = ttk.OptionMenu(
            self.species_frame,
            self.species_var,
            PET_TYPES[0],
            *PET_TYPES,
            command=self.check_species_other
        )
        self.species_menu.pack()

        self.custom_species_label = None
        self.custom_species_entry = None

        tk.Label(self.info_frame, text="Color", fg="black", bg="#C0C0C0").pack()
        self.color_display = tk.Label(
            self.info_frame,
            text="Click to pick color",
            bg="#333333", fg="white", width=20
        )
        self.color_display.pack()
        self.color_display.bind("<Button-1>", self.pick_color)

        tk.Label(self.info_frame, text="Age", fg="black", bg="#C0C0C0").pack()
        self.age_entry = tk.Entry(self.info_frame, bg="#333333", fg="white")
        self.age_entry.pack()

        self.create_pet_btn = tk.Button(
            self.info_frame,
            text="Create Pet",
            command=self.create_pet,
            bg="#444", fg="white"
        )
        self.create_pet_btn.pack(pady=5)

        self.funds_label = tk.Label(
            self.info_frame,
            text="Funds: $0.00",
            fg="#000000", bg="#C0C0C0",
            font=("Consolas", 12, "bold")
        )
        self.funds_label.pack(pady=(5, 0))

        # --- Action Buttons ---
        self.methods_frame = tk.Frame(self.left_frame, bg="#1c1c1c")
        self.methods_frame.pack(pady=10)

        methods = [
            ("Play", self.play), ("Play Random", self.play_random),
            ("Rest", self.rest), ("Random Rest", self.random_rest),
            ("Feed", self.feed), ("Random Feed", self.random_feed),
            ("Clean", self.clean), ("Random Clean", self.random_clean),
            ("Train", self.train), ("Random Train", self.random_train),
            ("Do Chore", self.do_chore), ("Random Chore", self.random_chore),
            ("Health Check", self.health_check), ("Visit Vet", self.visit_vet),
            ("Reaction", self.reaction), ("Simulate", self.simulate)
        ]

        self.method_buttons = []
        for text, cmd in methods:
            btn = tk.Button(self.methods_frame, text=text, command=cmd, bg="#444", fg="white", width=15)
            btn.pack(pady=2)
            self.method_buttons.append(btn)

        # --- Status Bars ---
        self.status_frame = tk.Frame(self.left_frame, bg="#C0C0C0")
        self.status_frame.pack(pady=5)

        self.care_var = tk.DoubleVar()
        self.tired_var = tk.DoubleVar()

        # --- Care Level Bar ---
        tk.Label(self.status_frame, text="Care", fg="black", bg="#C0C0C0").pack()

        # Create the variable to track care level
        self.care_var = tk.DoubleVar()

        # Set up the styles for dynamic coloring
        style = ttk.Style()
        style.theme_use('default')  # ensures custom colors work

        style.configure("Green.Horizontal.TProgressbar",
                        troughcolor="white",
                        background="green")
        style.configure("Orange.Horizontal.TProgressbar",
                        troughcolor="white",
                        background="orange")
        style.configure("Red.Horizontal.TProgressbar",
                        troughcolor="white",
                        background="red")

        # Use map for proper dynamic coloring (optional, but works)
        style.map("Green.Horizontal.TProgressbar", background=[('!disabled', 'green')])
        style.map("Orange.Horizontal.TProgressbar", background=[('!disabled', 'orange')])
        style.map("Red.Horizontal.TProgressbar", background=[('!disabled', 'red')])

        # Create the progress bar, default style is red for low care start
        self.care_bar = ttk.Progressbar(
            self.status_frame,
            maximum=10,
            variable=self.care_var,
            length=150,
            style="Red.Horizontal.TProgressbar"  # starts low, will change dynamically
        )
        self.care_bar.pack(pady=2)

        tk.Label(self.status_frame, text="Tiredness", fg="black", bg="#C0C0C0").pack()
        style = ttk.Style()
        style.theme_use('default')  # ensures custom colors actually work

        style.configure("TProgressbar",
                        troughcolor="white",
                        background="green")  # default

        # Use map for dynamic color change
        style.map("Green.Horizontal.TProgressbar",
                background=[('!disabled', 'green')])
        style.map("Orange.Horizontal.TProgressbar",
                background=[('!disabled', 'orange')])
        style.map("Red.Horizontal.TProgressbar",
                background=[('!disabled', 'red')])
        
        self.tired_bar = ttk.Progressbar(
            self.status_frame,
            maximum=10,
            variable=self.tired_var,
            length=150,
            style="Orange.Horizontal.TProgressbar"  # will now actually show orange
        )
        self.tired_bar.pack(pady=2)

        self.mood_frame = tk.Frame(self.status_frame, bg="#C0C0C0")
        self.mood_frame.pack(fill=tk.X, pady=2)

        self.mood_label = tk.Label(
            self.mood_frame,
            text="😶",
            font=("Segoe UI Emoji", 60),
            bg="#C0C0C0", fg="yellow"
        )
        self.mood_label.pack(expand=True)

        # --- Time Tracking ---
        self.current_hour = 8
        self.current_minute = 0
        self.current_day = 1
        self.current_month = 1
        self.current_year = 1

        # Welcome message shown in console
        self.app_output(
            "Welcome to the Virtual Pet Simulator!\n"
            "Fill in your pet's name, species, color, and age.\n"
            "Then click 'Create Pet' to begin.\n"
            "Use the buttons on the left to interact with your pet!\n"
            "Open the Help/Tutorial button on the top right for more information\n"
            "Time starts at 08:00."
        )
        
    # ========================= GUI Helper Methods =========================
    def check_species_other(self, value):
        """
        Called when the species dropdown changes.
        If the user selects "Other", it shows an entry field to type a custom species.
        If any other species is selected, it hides/removes the custom species entry.
        """
    
        # Check if the selected value from the dropdown is "Other"
        if value == "Other":
            # Only create a new custom entry if it doesn't already exist
            if self.custom_species_entry is None:
                # Create a label prompting the user to enter a custom species
                self.custom_species_label = tk.Label(
                    self.species_frame,
                    text="Enter custom species:",
                    fg="white", bg="#C0C0C0"
                )
                self.custom_species_label.pack(pady=(5,0))  # small padding above and below
    
                # Create the entry widget where the user can type the custom species
                self.custom_species_entry = tk.Entry(
                    self.species_frame,
                    bg="#333333", fg="white"
                )
                self.custom_species_entry.pack(pady=(0,5))  # small padding below
    
        else:
            # If any other species is selected and a custom entry exists, remove it
            if self.custom_species_entry:
                self.custom_species_label.destroy()  # remove the label widget
                self.custom_species_entry.destroy()  # remove the entry widget
                self.custom_species_label = None     # reset reference
                self.custom_species_entry = None     # reset reference
    
    def pick_color(self, event):
        """
        Opens a color picker for the user to select the pet's color.
        Updates the color display label with the chosen color.
        """
        # Open a color chooser dialog
        color_code = colorchooser.askcolor(title="Choose your pet's color")
        
        # If a color was selected, save it and update the display
        if color_code and color_code[1]:
            self.color = color_code[1]  # store hex color code
            self.color_display.config(bg=self.color, text=self.color)  # update label

    def app_output(self, text):
        """
        Prints a message to the console with a timestamp.
        Also updates the pet's status bars after each message.
        """
        # Create a   timestamp string in YYYY-MM-DD HH:MM format
        timestamp = f"[{int(self.current_year):04d}-{int(self.current_month):02d}-{int(self.current_day):02d} " \
                    f"{int(self.current_hour):02d}:{int(self.current_minute):02d}] "

        # Enable the console so we can insert text
        self.console.config(state=tk.NORMAL)
        
        # Insert the timestamped message at the end
        self.console.insert(tk.END, timestamp + text + "\n")
        
        # Scroll to the bottom so the latest message is visible
        self.console.see(tk.END)
        
        # Disable editing again to keep console read-only
        self.console.config(state=tk.DISABLED)
        
        # Refresh the status bars (care, tiredness, mood, funds)
        self.update_status_bars()

    def gui_input(self, prompt):
        """
        Displays a simple dialog box to get text input from the user.
        Returns the input string, or None if the user cancels.
        """
        # Ask the user for input using a simple dialog box
        result = simpledialog.askstring("Input", prompt)
        
        # Return the result, or None if the user canceled
        return result if result is not None else None

    def increment_time(self, hours=0, minutes=0):
        """
        Increments the in-game time by a specified number of hours and minutes.
        Automatically updates minutes, hours, days, months, and years as needed.
        """
        # Add minutes to current minute count
        self.current_minute += minutes
        
        # Convert excess minutes to hours and add to current hour
        self.current_hour += hours + self.current_minute // 60
        
        # Keep minutes in range 0-59
        self.current_minute %= 60
        
        # Handle hour overflow and increment day/month/year accordingly
        while self.current_hour >= 24:
            self.current_hour -= 24  # Reset hours after 24
            self.current_day += 1     # Increment day
            if self.current_day > 30:  # Simplified: assume 30 days per month
                self.current_day = 1
                self.current_month += 1
                if self.current_month > 12:
                    self.current_month = 1
                    self.current_year += 1
    
    # ========================= Create Pet =========================
    def create_pet(self):
        """
        Creates a new Pet instance based on user input from the GUI.
        Validates name, species, color, and age.
        Uses AI to strictly validate custom species and estimate max lifespan if needed.
        Disables input fields after creation.
        """
        # --- Get user inputs ---
        name = self.name_entry.get().strip()
        species = self.species_var.get()
        color = self.color or "Unknown"
        age_str = self.age_entry.get().strip()
    
        # --- Handle custom species ---
        if species == "Other" and self.custom_species_entry:
            species = self.custom_species_entry.get().strip()
    
        # Normalize species casing for lifespan and emoji lookup
        species = species.capitalize()
    
        # --- Check for missing info ---
        if not (name and species and color and age_str):
            self.app_output("Please fill in all pet information!")
            return
    
        # --- Validate custom species with AI ---
        standard_species = [
            "Dog", "Cat", "Bird", "Fish", "Hamster", "Rabbit",
            "Guinea pig", "Horse", "Lizard", "Snake", "Turtle"
        ]
    
        if species not in standard_species:
            valid = self.ai_validate_species(species)
            if not valid:
                # Show a **notification** instead of looping
                messagebox.showinfo(
                    "Invalid Species",
                    f"'{species}' is not a recognized species.\n"
                    "Please correct it in the sidebar and click 'Create Pet' again."
                )
                self.app_output(f"❌ '{species}' is invalid. Please correct it before continuing.")
                return
    
        # --- Validate age ---
        try:
            age = int(age_str)
        except ValueError:
            self.app_output("Age must be a number.")
            return
        
        # Ensure the mood label is visible
        self.mood_label.config(text="😶")   # default emoji
        self.mood_label.update_idletasks()   # force redraw

        # --- Determine max age ---
        lifespan_limits = {
            "Dog": 15, "Cat": 20, "Bird": 15, "Fish": 5, "Hamster": 3,
            "Rabbit": 12, "Guinea pig": 8, "Horse": 25, "Lizard": 10,
            "Snake": 20, "Turtle": 100
        }
    
        if species in lifespan_limits:
            max_age = lifespan_limits[species]
        else:
            # Estimate AI lifespan for custom species
            self.app_output(f"Estimating lifespan for custom species '{species}'...")
            max_age = self.ai_max_age(species) or 20
            self.app_output(f"Estimated maximum lifespan for a {species} is {int(max_age)} years.")
    
        if age > max_age:
            self.app_output(f"Invalid age: {species}s rarely live past {int(max_age)} years.")
            return
    
        # --- Create the Pet ---
        self.pet = Pet(
            name, species, color, age,
            output_func=self.app_output,
            input_func=self.gui_input
        )
        self.pet.on_death = self.handle_pet_death
    
        self.app_output(f"✅ {name} the {species} has been created!")
        self.update_funds_label()
    
        # --- Update GUI widgets ---
        self.name_entry.config(state="disabled")
        self.species_menu.config(state="disabled")
        if self.custom_species_entry:
            self.custom_species_entry.config(state="disabled")
        self.color_display.unbind("<Button-1>")
        self.age_entry.config(state="disabled")
        self.create_pet_btn.config(state="disabled")

        self.console_title_label.config(text=f"Life of {self.pet.name} the {self.pet.species}")

    # ========================= AI Helpers =========================
    def ai_validate_species(self, species):
        """
        Uses OpenAI GPT to strictly check if a species is real.
        Returns True if the species is valid, False otherwise.
        """
        # Construct strict prompt for AI: only answer 'yes' or 'no'
        prompt = f"Is '{species}' a real animal species? Answer ONLY 'yes' or 'no'. Be strict; do not accept misspellings or fictional names."
        try:
            # Call OpenAI Chat API with GPT-4
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0  # deterministic response
            )
            # Extract and normalize the AI's response
            answer = response.choices[0].message.content.strip().lower()
            # Return True if the response starts with 'yes'
            return answer.startswith("yes")
        except Exception as e:
            # On error, log it to the GUI console and reject species
            self.app_output(f"AI species validation error: {e}")
            return False

    def ai_max_age(self, species):
        """
        Uses OpenAI GPT to estimate the typical maximum lifespan of a species.
        Returns a number representing the lifespan in years.
        If AI fails or cannot parse a number, defaults to 20 years.
        """
        try:
            # Construct prompt asking AI for max lifespan
            prompt = f"What is the typical maximum lifespan (in years) of a {species}? Reply with a single number or a short phrase containing a number."
            
            # Call OpenAI Chat API with GPT-4
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0  # deterministic response
            )
            
            # Get AI's text response
            text = response.choices[0].message.content
            
            # Attempt to find a number in the response
            for token in text.replace(",", " ").split():
                try:
                    v = float(token)  # convert token to float
                    return v  # return first number found
                except:
                    continue  # skip tokens that aren't numbers
            
            # Default if no number found
            return 20
        except Exception as e:
            # On error, log it and return default
            self.app_output(f"AI max-age error: {e}")
            return 20

    def ai_validate_action(self, action, context, species=None):
        """
        Validates a user-entered action using the OpenAI API.

        The validation rules depend on the context:
        - 'chore'  → Action must be a plausible human chore.
        - 'feed'   → Must be safe and realistic food for the given species.
        - 'clean'  → Must be a realistic cleaning/grooming action performed by a human.
        - default  → Must be a plausible action the pet itself can perform (play/train/etc).

        Returns:
            True  → If the AI determines the action is valid.
            False → If the action is empty or AI responds negatively.
        """

        # Prevent empty or whitespace-only input from being validated
        if not action or action.strip() == "":
            return False

        # Remove leading/trailing whitespace for consistent validation
        cleaned_action = action.strip()

        # -----------------------------
        # Context-Specific Prompt Logic
        # -----------------------------

        # Validate human chores (pet is NOT performing the action)
        if context == "chore":
            prompt = (
                f"You are a strict validator. Answer ONLY 'yes' or 'no'.\n"
                f"Context: '{context}'\n"
                f"Question: Is this a plausible chore a human can perform?\n"
                f"Chore: '{cleaned_action}'\n"
                f"Do not allow nonsense or impossible chores."
            )

        # Validate feeding (species-specific safety check)
        elif context == "feed":
            prompt = (
                f"You are a validator. Answer ONLY 'yes' or 'no'.\n"
                f"Species: '{species or 'unknown'}'\n"
                f"Question: Is this a suitable food for this species?\n"
                f"Food: '{cleaned_action}'\n"
                f"Only consider realistic, safe, commonly eaten foods."
            )

        # Validate cleaning (human performs care on the pet)
        elif context == "clean":
            prompt = (
                f"You are a validator. Answer ONLY 'yes' or 'no'.\n"
                f"Species: '{species or 'unknown'}'\n"
                f"Question: Is this a valid cleaning, grooming, hygiene, or maintenance action "
                f"that a human can perform on this species?\n"
                f"Action: '{cleaned_action}'\n"
                f"Only allow realistic pet care actions."
            )

        # Default: Pet performs the action (play, train, etc.)
        else:
            prompt = (
                f"You are a validator. Answer ONLY 'yes' or 'no'.\n"
                f"Context: '{context}'\n"
                f"Species: '{species or 'unknown'}'\n"
                f"Question: Is it plausible for this pet to perform this action?\n"
                f"Action: '{cleaned_action}'\n"
                f"Do not allow nonsense or impossible actions."
            )

        # -----------------------------
        # Call OpenAI API for validation
        # -----------------------------
        try:
            response = openai.chat.completions.create(
                model="gpt-4",      # Deterministic, high-accuracy model
                messages=[{"role": "user", "content": prompt}],
                temperature=0      # 0 = deterministic output (reduces randomness in validation)
            )

            # Normalize response to lowercase for consistent comparison
            answer = response.choices[0].message.content.strip().lower()

            # Return True only if AI explicitly includes "yes"
            return "yes" in answer

        # -----------------------------
        # Error Handling
        # -----------------------------
        except Exception as e:
            # Print error to GUI console for debugging
            self.app_output(f"AI action validation error: {e}")

            # Fail-safe: return True so gameplay is not blocked
            # (Prevents API outages from breaking the game)
            return True
    
    def ai_action_description(self, action, context="play", species=None):
        """
        Returns a short AI-generated description of a custom action.
        Only for custom inputs; not for enums.

        Parameters:
            action (str): The user-entered action to describe.
            context (str): The type of action ('play', 'clean', 'chore', etc.).
            species (str): The species of the pet, used for descriptive accuracy.

        Returns:
            str: A short, fun, 1-sentence description of the action.
        """

        # -----------------------------
        # Build context-specific prompts
        # -----------------------------
        
        if context == "clean":
            # Human is performing hygiene or grooming on the pet
            prompt = (
                f"A person is performing a cleaning or grooming action on their {species}: "
                f"'{action}'. Write a short, fun, 1-sentence description of this moment."
            )

        elif context == "chore":
            # Human performing a chore (not the pet)
            prompt = (
                f"A person is doing this chore: '{action}'. "
                f"Write a short, fun, 1-sentence description of it."
            )

        elif context == "feed":
            # Feeding the pet
            prompt = (
                f"A person is feeding their {species}: '{action}'. "
                f"Write a short, fun, 1-sentence description of the pet enjoying the food."
            )

        elif context == "play":
            # Pet performing a playful action
            prompt = (
                f"A {species} is performing a fun play action: '{action}'. "
                f"Write a short, engaging, 1-sentence description of the pet playing."
            )

        else:
            # Default: general pet action (train, explore, etc.)
            prompt = (
                f"A {species} is performing a {context} action: '{action}'. "
                f"Write a short, fun, 1-sentence description of this action."
            )

        # -----------------------------
        # Call OpenAI API
        # -----------------------------
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7  # Allows for playful, varied responses
            )
            # Return the AI-generated description
            return response.choices[0].message.content.strip()

        except Exception as e:
            # Print error to console but return fallback
            self.app_output(f"AI description error: {e}")
            return f"{self.pet.name} {action}."
        
    def ai_generate_food(self, species=None):
        """
        Uses AI to generate a plausible food for the pet based on its species.
        Returns the food as a string.
        """
        prompt = (
            f"Suggest a single plausible food for a pet.\n"
            f"Species: '{species or 'unknown'}'\n"
            f"Return only the name of the food, no extra text, punctuation, or explanations.\n"
            f"Make it something a real {species or 'pet'} could eat."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            # Grab AI's response and strip whitespace
            food = response.choices[0].message.content.strip()
            return food
        except Exception as e:
            self.app_output(f"AI food generation error: {e}")
            # Fallback if AI fails
            return "some food"

    # ========================= Pet Actions =========================
    def update_tired_bar_color(self):
        if self.pet.tired_level < 4:
            style_name = "Green.Horizontal.TProgressbar"
        elif self.pet.tired_level < 7:
            style_name = "Orange.Horizontal.TProgressbar"
        else:
            style_name = "Red.Horizontal.TProgressbar"

        self.tired_bar.configure(style=style_name)
        self.tired_bar.update_idletasks()  # forces redraw
    
    def update_care_bar_color(self):
        if not self.pet:
            return

        care = self.pet.care_level

        if care >= 8:
            self.care_bar.configure(style="Green.Horizontal.TProgressbar")
        elif care >= 5:
            self.care_bar.configure(style="Orange.Horizontal.TProgressbar")
        else:
            self.care_bar.configure(style="Red.Horizontal.TProgressbar")
    
    def update_status_bars(self):
        """
        Updates the GUI status bars for care and tiredness.
        Also updates funds label and the pet's mood emoji.
        """
        if self.pet:
            # Update care and tiredness progress bars
            self.care_var.set(self.pet.care_level)
            self.tired_var.set(self.pet.tired_level)

            # Update bar colors
            self.update_care_bar_color()
            self.update_tired_bar_color()

            # Update funds display
            self.update_funds_label()

            # Update mood emoji based on pet's current state
            self.mood_label.config(text=self.get_mood_emoji())
    
    def update_funds_label(self):
        """
        Updates the funds label in the GUI to reflect the pet's current funds.
        """
        if self.pet:
            self.funds_label.config(text=f"Funds: ${self.pet.funds:.2f}")
    
    def get_mood_emoji(self):
        """
        Returns an emoji representing the pet's current mood.
        Based on care level and tiredness, or dead/alive status.
        """
        if not self.pet: 
            return "😶"  # Default neutral face if no pet exists
        if not self.pet._alive: 
            return "💀"  # Dead pet emoji
        care = self.pet.care_level
        tired = self.pet.tired_level
        # Determine emoji based on care and tiredness
        if tired > 8: 
            return "🥱"  # Very tired
        if care < 3: 
            return "😢"  # Very unhappy
        if care >= 8 and tired <= 4: 
            return "😄"  # Happy and rested
        if 4 <= care < 8: 
            return "🙂"  # Okay mood
        return "😐"  # Neutral
    
    def handle_pet_death(self):
        """
        Handles the pet's death in the game.
        Prompts the user to replay or exit.
        """
        self.app_output("\n💀 GAME OVER 💀")

        # Disable all method buttons to prevent further actions
        for btn in self.method_buttons:
            btn.config(state=tk.DISABLED)

        replay = messagebox.askyesno("Replay?", "Do you want to create a new pet and play again?")
        if replay:
            self.reset_game()
        else:
            self.app_output("Thanks for playing! Closing in 5 seconds...")
            self.root.after(5000, self.root.destroy)


    def reset_game(self):
        """
        Fully resets the GUI and game state so the player can create a new pet.
        """
        # --- Reset pet-related variables ---
        self.pet = None
        self.color = None

        # Reset in-game time
        self.current_hour = 8
        self.current_minute = 0
        self.current_day = 1
        self.current_month = 1
        self.current_year = 1

        # --- Reset console ---
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)

        # Reset console title and funds display
        self.console_title_label.config(text="Life of —")
        self.funds_label.config(text="Funds: $0.00")

        # --- Reset pet creation fields ---
        self.name_entry.config(state="normal")
        self.name_entry.delete(0, tk.END)

        self.species_var.set(PET_TYPES[0])
        self.species_menu.config(state="normal")

        # Remove custom species entry if it exists
        if self.custom_species_entry:
            self.custom_species_label.destroy()
            self.custom_species_entry.destroy()
            self.custom_species_label = None
            self.custom_species_entry = None

        self.age_entry.config(state="normal")
        self.age_entry.delete(0, tk.END)

        # Reset color picker display
        self.color_display.config(bg="#333333", text="Click to pick color")
        self.color_display.bind("<Button-1>", self.pick_color)

        # Reset create pet button
        self.create_pet_btn.config(state="normal")

        # --- Reset all action/method buttons ---
        for btn in self.method_buttons:
            btn.config(state=tk.NORMAL)

        # --- Reset status bars ---
        self.care_var.set(0)
        self.tired_var.set(0)
        self.mood_label.config(text="😶")  # Default neutral face

        # --- Display final welcome message ---
        self.app_output(
            "🎉 Welcome back! Fill in your pet's Name, Species, Color, and Age, "
            "then click 'Create Pet' to start a new adventure!"
        )
    
    def show_tutorial(self):
        """
        Opens a new window with instructions on how to play the Virtual Pet Simulator.
        """
        win = tk.Toplevel(self.root)
        win.title("Help / Tutorial")
        win.configure(bg="#C0C0C0")
        win.geometry("500x500")
        
        # Add a text box for tutorial content
        text = tk.Text(win, bg="#121212", fg="#00b3ff")
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END,
                    "Virtual Pet Simulator Tutorial\n\n"
                    "1. Fill in your pet's Name, Species, Color, and Age.\n"
                    "2. Click 'Create Pet' to start.\n\n"
                    "Buttons on left:\n"
                    "- Play / Play Random: Interact with your pet\n"
                    "- Rest / Random Rest: Sleep to reduce tiredness\n"
                    "- Feed / Random Feed: Feed pet and increase care\n"
                    "- Clean: Clean pet to improve care\n"
                    "- Train / Random Train: Train your pet\n"
                    "- Do Chore / Random Chore: Earn money\n"
                    "- Health Check: Show pet status\n"
                    "- Visit Vet: Heal pet\n"
                    "- Reaction: Show pet's mood\n"
                    "- Simulate: Fast-forward time\n\n"
                    "Time progresses automatically with every action starting at 08:00.\n"
                    "If your pet dies, you can choose to replay.\n")
        text.config(state="disabled")  # Make tutorial text read-only

    # ---------------- Action Buttons ----------------
    def format_action_console(self, action_desc, subject="pet"):
        """
        Formats an action description for console output, customizing the phrasing 
        based on whether the action is performed by the player or the pet.

        Adjusts action description for proper grammatical structure and tense, 
        handling verbs ending in "-ing" and converting them as needed based on the subject.

        Paramters:
            action_desc (str): The raw description of the action to format.
            subject (str): The subject performing the action, either "player" or "pet".
                        Defaults to "pet".

        Returns:
            str: A formatted string combining the subject with the action description,
                ensuring proper grammar.
        """
        
        prefix = "You" if subject == "player" else self.pet.name
        action_desc = action_desc.strip()

        words = action_desc.split()
        first_word = words[0].lower()
        rest = " ".join(words[1:])

        # Handle "ing" verbs for player
        if first_word.endswith("ing"):
            stem = first_word[:-3]

            # Fix common cases
            if stem.endswith(("at", "iz")):  # e.g., "organizing" → "organize"
                stem += "e"
            elif len(stem) >= 2 and stem[-1] == stem[-2] and stem[-3] not in "aeiou":  # e.g., "running" → "run"
                stem = stem[:-1]
            elif first_word in ("making", "taking", "baking", "shaking", "writing"):
                stem += "e"  # add 'e' for known dropped-e verbs

            first_word = stem

        if subject == "pet":
            # Convert to 3rd person singular for pet
            if first_word == "go":
                first_word = "goes"
            elif first_word == "play":
                first_word = "plays"
            elif first_word.endswith("y"):
                first_word = first_word[:-1] + "ies"
            elif first_word.endswith(("s", "sh", "ch", "x", "z")):
                first_word += "es"
            else:
                first_word += "s"

        return f"{prefix} {first_word} {rest}.".strip()

    def get_species_enum(self, species, action_type):
        """
        Returns the Enum class corresponding to a species and action type.
        action_type can be 'play', 'train', 'clean', etc.
        """
        species = species.lower()

        if action_type == "chore":
            return Chores
        if species == "dog":
            if action_type == "play":
                return DogActivities
            elif action_type == "train":
                return DogTraining
        elif species == "cat":
            if action_type == "play":
                return CatActivities
            elif action_type == "train":
                return CatTraining
        elif species == "bird":
            if action_type == "play":
                return BirdActivities
            elif action_type == "train":
                return BirdTraining
        elif species == "fish":
            if action_type == "play":
                return FishActivities
            elif action_type == "train":
                return FishTraining
        elif species == "hamster":
            if action_type == "play":
                return HamsterActivities
            elif action_type == "train":
                return HamsterTraining
        elif species == "rabbit":
            if action_type == "play":
                return RabbitActivities
            elif action_type == "train":
                return RabbitTraining
        elif species == "guinea pig":
            if action_type == "play":
                return GuineaPigActivities
            elif action_type == "train":
                return GuineaPigTraining
        elif species == "horse":
            if action_type == "play":
                return HorseActivities
            elif action_type == "train":
                return HorseTraining
        elif species == "lizard":
            if action_type == "play":
                return LizardActivities
            elif action_type == "train":
                return LizardTraining
        elif species == "snake":
            if action_type == "play":
                return SnakeActivities
            elif action_type == "train":
                return SnakeTraining
        elif species == "turtle":
            if action_type == "play":
                return TurtleActivities
            elif action_type == "train":
                return TurtleTraining
        elif species == "clean":
            return Clean  # for cleaning actions
        return None  # fallback if species/action unknown

    def play(self):
        """
        Lets the pet perform a play action. 
        Prompts the user to choose a predefined or custom action, 
        validates it with AI, performs the action, outputs a description, 
        advances time, updates status bars, and checks life status.
        """
        if not self.pet:
            return

        # Get predefined play actions for this species
        enum_class = self.get_species_enum(self.pet.species, "play")
        options = [c.value for c in enum_class] if enum_class else []

        # Build prompt for user
        prompt = "What do you want your pet to play?\n"
        for i, option in enumerate(options, start=1):
            prompt += f"{i}. {option}\n"
        prompt += "Or type your own custom action:"

        is_enum_choice = False

        while True:
            choice = self.gui_input(prompt)
            if choice is None:  # User canceled
                return

            # If user enters a number corresponding to predefined options
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    choice = options[idx]
                    is_enum_choice = True

            # Validate action
            if self.ai_validate_action(choice, context="play", species=self.pet.species):
                break
            else:
                messagebox.showinfo(
                    "Invalid action",
                    f"'{choice}' is not a valid play action. Try again."
                )

        # Perform the play action
        self.pet.act_play(choice=choice)

        if is_enum_choice:
            # Fast hard-coded output for predefined actions
            self.app_output(self.format_action_console(choice, subject="pet"))
        else:
            # AI-generated description for custom actions
            desc = self.ai_action_description(choice, context="play", species=self.pet.species)
            self.app_output(desc)

        # Advance time and update status
        self.increment_time(minutes=30)
        self.update_status_bars()
        self.pet.check_life_status()
    
    def play_random(self):
        """
        Performs a random play action for the pet without user input.
        Advances time by 30 minutes and updates status bars.
        """
        if not self.pet:
            return

        # Get the action the pet performs
        choice = self.pet.act_play()

        # Advance time
        self.increment_time(minutes=30)
        self.update_status_bars()

        # Print to console
        if choice:
            self.app_output(self.format_action_console(choice, subject="pet"))
        
        self.pet.check_life_status()
    
    def rest(self):
        """
        Prompts the user to input a rest action for the pet.
        Shows predefined rest actions from SleepUpgrade with upgrade costs.
        Allows the player to choose how many hours the pet will rest.
        Skips AI validation for predefined options, only validates custom input.
        Updates time/status bars based on chosen duration.
        """
        if not self.pet:
            return

        # Build options from SleepUpgrade enum
        options = []
        for c in SleepUpgrade:
            # Each enum value is a tuple (description, cost)
            if isinstance(c.value, tuple):
                desc, cost = c.value
                options.append(f"{desc} — Upgrade for ${cost}")
            else:
                options.append(str(c.value))

        # Build prompt message
        prompt = "How do you want your pet to rest?\n"
        for i, option in enumerate(options, start=1):
            prompt += f"{i}. {option}\n"
        prompt += "Or type your own custom action:"

        while True:
            choice = self.gui_input(prompt)
            if choice is None:
                return

            # Convert number choice to the corresponding enum string
            is_custom = False
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    choice = options[idx]  # pre-defined option
            else:
                is_custom = True  # user typed a custom action

            # Only validate custom input with AI
            if not is_custom or self.ai_validate_action(choice, context="rest", species=self.pet.species):
                break
            else:
                messagebox.showinfo(
                    "Invalid action",
                    f"'{choice}' is not a valid rest action. Try again."
                )

        # Delay the next dialog slightly to prevent accidental click
        self.root.after(500, lambda: self._ask_rest_hours(choice))

        self.pet.check_life_status()

    def _ask_rest_hours(self, choice):
        """
        Prompts the user for how long the pet should rest, applies any SleepUpgrade cost, 
        performs the rest, updates time and status bars, and prints a formatted description.
        """
        # Ask for duration in hours
        while True:
            duration_str = self.gui_input("How many hours should your pet rest for? (1-12)")
            if duration_str is None:
                duration = 1
                break
            try:
                duration = float(duration_str)
                if duration <= 0:
                    raise ValueError
                break
            except ValueError:
                messagebox.showinfo("Invalid input", "Please enter a positive number of hours.")

        # Determine cost from SleepUpgrade
        cost = 0.0
        for upgrade in SleepUpgrade:
            if upgrade.description.lower() in choice.lower():
                cost = upgrade.cost
                break

        # Let Pet handle spending (even if it goes into debt)
        if cost > 0:
            self.pet.spend(cost)

        # Perform rest
        self.pet.act_rest(choice=choice)
        self.increment_time(hours=duration)
        self.update_status_bars()

        # --- CLEAN OUTPUT LOGIC ---
        name = self.pet.name
        hour_text = "hour" if duration == 1 else "hours"

        if "normal" in choice.lower() or cost == 0:
            message = f"{name} sleeps normally for {duration} {hour_text}."
        else:
            # Extract upgrade description (remove price text if present)
            upgrade_text = choice.split("—")[0].strip()
            message = f"{name} sleeps with {upgrade_text[0].lower() + upgrade_text[1:]} for {duration} {hour_text}. (-${cost})"

        self.app_output(message)
    
    def random_rest(self):
        """
        Performs a random rest for the pet by selecting a SleepUpgrade. 
        Applies any associated cost, updates the pet's tiredness and time, 
        refreshes status bars, and prints a descriptive message including duration and cost.
        """
        if not self.pet:
            return

        selected = random.choice(list(SleepUpgrade))
        desc = selected.description
        cost = selected.cost

        # Let the Pet class handle spending (even if it goes into debt)
        self.pet.spend(cost)

        self.pet.act_rest(choice=desc)

        duration = random.randint(1, 12)
        self.increment_time(hours=duration)
        self.update_status_bars()

        name = self.pet.name
        hour_text = "hour" if duration == 1 else "hours"

        if selected == SleepUpgrade.SLEEP_NORMALLY:
            message = f"{name} sleeps normally for {duration} {hour_text}."
        else:
            message = f"{name} sleeps with {desc[0].lower() + desc[1:]} for {duration} {hour_text}."

        if cost > 0:
            message += f" (-${cost})"

        self.app_output(message)
        self.pet.check_life_status()
    
    def feed(self):
        """
        Prompts the user to input what the pet should eat.
        Uses AI to validate and generate dynamic messages.
        Advances time by 20 minutes, updates status bars, and prints a console message.
        """
        if not self.pet:
            return

        while True:
            choice = self.gui_input("What should your pet eat? (e.g. kibble)")
            if choice is None:
                return

            if self.ai_validate_action(choice, context="feed", species=self.pet.species):
                self.pet.act_feed(choice=choice)
                break
            else:
                messagebox.showinfo("Invalid food", "That doesn't look like a valid food for this pet. Try again.")

        # Increment time and update status
        self.increment_time(minutes=20)
        self.update_status_bars()

        # Use AI to generate a dynamic console message
        message = self.ai_action_description(choice, context="feed", species=self.pet.species)
        self.app_output(message)

        self.pet.check_life_status()

    def random_feed(self):
        """
        Feeds the pet with AI-generated food appropriate for its species, 
        updates hunger/tiredness, advances time, refreshes status bars, 
        and prints a short AI-generated description if feeding succeeds.
        """
        if not self.pet:
            return

        # Generate food using your AI method
        food = self.ai_generate_food(species=self.pet.species)

        # Feed the pet
        result = self.pet.act_feed(food)

        # Advance time
        self.increment_time(minutes=15)
        self.update_status_bars()

        # Only print if feeding succeeded
        if result:
            desc = self.ai_action_description(
                food,
                context="feed",
                species=self.pet.species
            )
            self.app_output(desc)

        self.pet.check_life_status()
    
    def clean(self):
        """
        Prompts the user to clean the pet using a predefined Clean action or custom input,
        validates the action with AI, performs the cleaning via Pet.act_clean, 
        prints either a formatted console message or AI-generated description, 
        advances time, and updates status bars.
        """
        if not self.pet:
            return

        # Get predefined cleaning actions from Clean enum
        options = [c.value for c in Clean]

        # Build prompt for user
        prompt = "How do you want to clean your pet?\n"
        for i, option in enumerate(options, start=1):
            prompt += f"{i}. {option}\n"
        prompt += "Or type your own custom cleaning action:"

        is_enum_choice = False

        while True:
            choice = self.gui_input(prompt)
            if choice is None:  # User canceled
                return

            # If user enters a number corresponding to predefined options
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    choice = options[idx]
                    is_enum_choice = True

            # Validate action
            if self.ai_validate_action(choice, context="clean", species=self.pet.species):
                break
            else:
                messagebox.showinfo(
                    "Invalid cleaning",
                    f"'{choice}' is not a valid cleaning action. Try again."
                )

        # Perform the cleaning action
        self.pet.act_clean(choice=choice)

        if is_enum_choice:
            # Fast hard-coded output for predefined actions
            self.app_output(self.format_action_console(choice, subject="pet"))
        else:
            # AI-generated description for custom actions
            desc = self.ai_action_description(choice, context="clean", species=self.pet.species)
            self.app_output(desc)

        # Advance time and update status
        self.increment_time(minutes=20)
        self.update_status_bars()
        self.pet.check_life_status()
    
    def random_clean(self):
        """
        Performs a random cleaning action for the pet.
        Advances time by 20 minutes and updates status bars.
        """
        if not self.pet:
            return

        # Perform the clean action and capture what happened
        choice = self.pet.act_clean()

        # Advance time
        self.increment_time(minutes=20)
        self.update_status_bars()

        # Print to console with proper grammar
        if choice:
            self.app_output(self.format_action_console(f"{choice.lower()}",subject="player"))
        self.pet.check_life_status()
    
    def train(self):
        """
        Prompts the user to train the pet using a predefined skill or custom input,
        validates custom training actions with AI, performs training via Pet.act_train,
        prints either a formatted message or AI-generated description, 
        advances time, and updates status bars.
        """
        if not self.pet:
            return

        # Get predefined training actions
        enum_class = self.get_species_enum(self.pet.species, "train")
        options = [c.value for c in enum_class] if enum_class else []

        # Build prompt string
        prompt_lines = ["What skill should your pet learn?"]
        for i, option in enumerate(options, start=1):
            prompt_lines.append(f"{i}. {option}")
        prompt_lines.append("Or type your own custom training action:")
        prompt = "\n".join(prompt_lines)

        while True:
            choice = self.gui_input(prompt)
            if choice is None:
                return

            is_custom = True

            # Check if the user picked a predefined option
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    choice = options[idx]
                    is_custom = False  # enum choice, no AI needed
                else:
                    continue  # invalid number, reprompt

            normalized_choice = choice.strip()

            # Only validate custom input
            if not is_custom or self.ai_validate_action(
                normalized_choice,
                context="train",
                species=self.pet.species
            ):
                break
            else:
                messagebox.showinfo(
                    "Invalid training",
                    f"'{normalized_choice}' doesn't seem valid. Try again."
                )

        # Perform the training
        self.pet.act_train(choice=normalized_choice)
        self.increment_time(minutes=40)
        self.update_status_bars()

        # --- Output ---
        if is_custom:
            # Generate AI description for custom action
            desc = self.ai_action_description(normalized_choice, context="train", species=self.pet.species)
            self.app_output(desc)
        else:
            # Predefined action → simple formatting
            self.app_output(self.format_action_console(choice, subject="pet"))

        self.pet.check_life_status()
    
    def random_train(self):
        """
        Performs a random training action for the pet.
        Advances time by 40 minutes and updates status bars.
        """
        if not self.pet:
            return

        # Perform the training action and capture what happened
        choice = self.pet.act_train()

        # Advance time
        self.increment_time(minutes=40)
        self.update_status_bars()

        # Print to console with proper grammar
        if choice:
            self.app_output(self.format_action_console(f"{self.pet.name} practices {choice.lower()}", subject="pet"))
        self.pet.check_life_status()
    
    def do_chore(self):
        """
        Prompts the user to perform a chore (predefined or custom), validates it with AI,
        performs the chore via Pet.act_chore (earning funds), prints either a formatted
        message or AI-generated description, advances time, and updates status bars.
        """
        if not self.pet:
            return

        # Get predefined chores
        enum_class = self.get_species_enum("human", "chore")  # Chores are human actions
        options = [c.value for c in enum_class] if enum_class else []

        # Build prompt for user
        prompt = "What chore do you want to perform?\n"
        for i, option in enumerate(options, start=1):
            prompt += f"{i}. {option}\n"
        prompt += "Or type your own custom chore:"

        is_enum_choice = False

        while True:
            choice = self.gui_input(prompt)
            if choice is None:  # User canceled
                return

            # If user enters a number corresponding to predefined options
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    choice = options[idx]
                    is_enum_choice = True

            # Validate action
            if self.ai_validate_action(choice, context="chore"):
                break
            else:
                messagebox.showinfo(
                    "Invalid chore",
                    f"'{choice}' is not a valid chore. Try again."
                )

        # Perform the chore, updating pet funds
        earned = self.pet.act_chore(choice=choice)

        # Output
        if is_enum_choice:
            # Predefined chore: use format_action_console
            self.app_output(self.format_action_console(choice, subject="player") + f" (+$10)")
        else:
            # Custom chore: use AI-generated description
            desc = self.ai_action_description(choice, context="chore")
            self.app_output(desc + f" (+$10)")

        # Advance time and update status
        self.increment_time(minutes=30)
        self.update_status_bars()
        self.pet.check_life_status()
    
    def random_chore(self):
        """
        Performs a random chore for the player via Pet.act_chore,
        prints a formatted message including earnings, advances time,
        updates status bars, and checks the pet's life status.
        """
        if not self.pet:
            return

        # Perform the chore
        choice = self.pet.act_chore()

        # Advance time
        self.increment_time(minutes=30)
        self.update_status_bars()

        # Output formatted console message
        if choice:
            self.app_output(self.format_action_console(choice, subject="player") + " (+$10)")

        self.pet.check_life_status()
    
    def health_check(self):
        """
        Checks the pet's health status.
        Advances time by 5 minutes and updates status bars.
        """
        if self.pet:
            self.pet.health_check()
            self.increment_time(minutes=5)
            self.update_status_bars()
        self.pet.check_life_status()
    
    def visit_vet(self):
        """
        Prompts the user for a reason to visit the vet.
        Calls act_vet to perform the visit (updates pet stats, etc.).
        Generates a 1-2 sentence AI-style vet report for display.
        Advances time by 1 hour and updates status bars.
        """
        if not self.pet:
            return

        while True:
            choice = self.gui_input("Why is your pet visiting the vet? (brief reason)")
            if choice is None:
                return

            if self.ai_validate_action(choice, context="visit_vet", species=self.pet.species):
                # Perform the visit and update pet stats
                self.pet.act_vet(choice=choice)
                break
            else:
                messagebox.showinfo("Invalid reason", "That isn't a valid vet visit reason. Try again.")

        # Generate AI-style vet report for display
        prompt = (
            f"The pet {self.pet.name} visited the vet for: '{choice}'. "
            f"Write a short, 1-2 sentence report in the style of instructions from a doctor, "
            f"describing what happened during the visit."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            report = response.choices[0].message.content.strip()
        except Exception as e:
            # fallback: generic report if AI fails
            report = f"{self.pet.name} visited the vet for {choice}."

        self.app_output(report)

        # Advance time and update status
        self.increment_time(hours=1)
        self.update_status_bars()
        self.pet.check_life_status()
    
    def reaction(self):
        """
        Shows the pet's reaction or mood.
        Advances time by 5 minutes and updates status bars.
        """
        if self.pet:
            self.pet.get_reaction()
            self.increment_time(minutes=5)
            self.update_status_bars()
        self.pet.check_life_status()
    
    def simulate(self):
        """
        Simulates a period of time for the pet based on user input (day, week, month, year, ten years).
        Updates the pet's status bars after simulation.
        """
        if self.pet:
            duration = simpledialog.askstring("Simulate", "Duration (day, week, month, year, ten years)")
            if duration:
                days = self.pet.simulate(duration)
                if days is not None:
                    self.increment_time(hours=days * 24)
                if self.pet._alive:
                    self.app_output(f"Final health check after {duration}:")
                    self.health_check()
                self.update_status_bars()
            self.pet.check_life_status()

    def choose_action(self, context, enum_class=None):
        """
        Allows the user to pick an action from a predefined list (enum_class) or type a custom action.
        AI validates the custom action.
        Returns the validated action string, or None if canceled.
        """
        # Auto-select enum if not provided
        if not enum_class and self.pet:
            enum_class = self.get_species_enum(self.pet.species, context)
        options = [item.value for item in enum_class] if enum_class else []

        # Ask user to choose or type
        prompt = "Choose an action:\n"
        for i, option in enumerate(options, start=1):
            prompt += f"{i}. {option}\n"
        prompt += "Or type your own custom action."

        while True:
            choice = self.gui_input(prompt)
            if choice is None:
                return None  # user canceled

            # If the input is a number and corresponds to a predefined action
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]  # return the selected enum description

            # Otherwise treat as custom, validate via AI
            if self.ai_validate_action(choice, context=context, species=self.pet.species):
                return choice
            else:
                messagebox.showinfo("Invalid action", f"'{choice}' is not a valid {context} action. Try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Virtual_Pet(root)
    root.mainloop()