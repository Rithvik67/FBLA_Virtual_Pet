import openai  # OpenAI library for AI calls
import os      # For environment variables and file system operations
import random  # For random choices in actions and simulation

# Import species-specific activity and training enums
from Cat import CatActivities, CatTraining
from Bird import BirdActivities, BirdTraining
from Chores import Chores  # Enum for human chores
from Clean import Clean    # Enum for pet cleaning actions
from Dog import DogActivities, DogTraining
from Fish import FishActivities, FishTraining
from Guinea_Pig import GuineaPigActivities, GuineaPigTraining
from Hamster import HamsterActivities, HamsterTraining
from Horse import HorseActivities, HorseTraining
from Lizard import LizardActivities, LizardTraining
from Rabbit import RabbitActivities, RabbitTraining
from Sleep import SleepUpgrade  # Enum for rest/sleep upgrades
from Snake import SnakeActivities, SnakeTraining
from Turtle import TurtleActivities, TurtleTraining

# -------------------- API CONFIGURATION --------------------
# Set OpenAI API key from environment variable to keep it secure
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------- PET CLASS --------------------
class Pet:
    """
    Virtual Pet class represents a single pet with attributes like:
    - Name, species, color, age
    - Care level (0-10), tired level (0-10)
    - Funds, cost, in-debt status
    - Alive/dead status

    The class supports actions such as playing, resting, feeding, training,
    cleaning, doing chores, and visiting the vet.

    AI integration generates dynamic textual descriptions for actions.
    """

    def __init__(self, name, species, color, age, output_func=None, input_func=None):
        """
        Initialize a new pet with attributes and optional input/output functions.

        Parameters:
            name (str): Pet's name
            species (str): Pet's species
            color (str): Pet's color
            age (float/int): Pet's age
            output_func (function, optional): Function to display messages (default print)
            input_func (function, optional): Function to get user input (for GUI or CLI)
        """
        # -------------------- BASIC ATTRIBUTES --------------------
        self._name = name
        self._species = species
        self._color = color
        self._age = age

        # -------------------- GAMEPLAY STATS --------------------
        self._care_level = 5      # 0 (neglected) to 10 (fully cared)
        self._tired_level = 5     # 0 (rested) to 10 (exhausted)
        self._funds = 0           # Current money available
        self._cost = 0            # Total money spent
        self._in_debt = False     # True if funds < 0
        self._alive = True        # True if pet is alive

        # -------------------- I/O HANDLING --------------------
        self.output = output_func if output_func else print  # Output text to console or GUI
        self.input_func = input_func                         # Input function if provided
        self.on_death = None                                 # Callback function triggered on death

    # -------------------- PROPERTIES --------------------
    # Getters and setters for private variables ensure controlled access
    @property
    def name(self): return self._name

    @name.setter
    def name(self, value): self._name = value

    @property
    def species(self): return self._species

    @species.setter
    def species(self, value): self._species = value

    @property
    def color(self): return self._color

    @color.setter
    def color(self, value): self._color = value

    @property
    def age(self): return self._age

    @age.setter
    def age(self, value): self._age = value

    @property
    def care_level(self): return self._care_level

    @care_level.setter
    def care_level(self, value): self._care_level = value

    @property
    def tired_level(self): return self._tired_level

    @tired_level.setter
    def tired_level(self, value): self._tired_level = value

    @property
    def funds(self): return self._funds

    @funds.setter
    def funds(self, value): self._funds = value

    @property
    def cost(self): return self._cost

    @cost.setter
    def cost(self, value): self._cost = value

    @property
    def in_debt(self): return self._in_debt
    
    @in_debt.setter
    def in_debt(self, value): self._in_debt = value

    # -------------------- USER INPUT --------------------
    def get_input(self, prompt):
        """
        Retrieve user input via input_func.
        Raises an error if no input function is provided.
        """
        if self.input_func:
            return self.input_func(prompt)
        else:
            raise RuntimeError("No input function provided!")

    # -------------------- MONEY MANAGEMENT --------------------
    def spend(self, amount, simulate=False):
        """
        Deducts funds for pet expenses, marks debt if negative, and optionally prints a warning.
        Parameters:
            amount (float): Amount to spend.
            simulate (bool): Suppress output if True.
        Returns:
            bool: False if pet is dead, True otherwise.
        """
        if not self._alive:
            self.output(f"{self._name} is dead. Cannot spend money.")
            return False
        self._funds -= amount
        self._cost += amount
        if self._funds < 0:
            self._in_debt = True
            if not simulate:
                self.output(f"You've gone into debt! Balance: ${self._funds:.2f}")
        return True

    def earn(self, amount):
        """
        Earn money from chores or other actions.
        Automatically adjusts in-debt status if balance >= 0.
        """
        self._funds += amount
        if self._funds >= 0:
            self._in_debt = False

    # -------------------- AI TEXT GENERATION --------------------
    def ai_text(self, prompt):
        """
        Generate a dynamic text description using OpenAI GPT-4.
        Parameters:
            prompt (str): Instructions for AI describing the pet's action
        Returns:
            str: AI-generated text describing the action
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4",  # GPT-4 model
                messages=[{"role": "user", "content": prompt}],  # User message for context
                temperature=0.7  # Creativity of response
            )
            # Get the AI message content and remove extra whitespace
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Handle any API errors gracefully
            self.output(f"AI Error: {e}")
            return "doing something fun"  # Fallback description

    # -------------------- ACTION METHODS --------------------
    # Play, Rest, Feed, Train, Clean, Chore, Vet
    # Each updates pet stats and optionally uses AI for description

# -------------------- ACTION METHODS WITH CUSTOM + AI --------------------
    def act_play(self, choice=None, custom_input=False, simulate=False):
        """
        Performs a play action for the pet.
        Updates care and tiredness levels, spends $5 (unless simulating), 
        and returns the chosen or generated action description.
        Parameters:
            choice (str|None): Predefined or custom play action.
            custom_input (bool): If True, allows user to input a custom action.
            simulate (bool): If True, suppresses spending/output effects.
        Returns:
            str: The action performed or generated description.
        """
        if not self._alive: return None
        self.spend(5, simulate)

        species_activities = {
            "cat": CatActivities,
            "dog": DogActivities,
            "bird": BirdActivities,
            "fish": FishActivities,
            "guineapig": GuineaPigActivities,
            "hamster": HamsterActivities,
            "horse": HorseActivities,
            "rabbit": RabbitActivities,
            "turtle": TurtleActivities,
            "snake": SnakeActivities
        }

        activities_enum = species_activities.get(self.species.lower())

        if choice is None:
            if custom_input and self.input_func:
                user_text = self.get_input(f"Type a custom play action for {self.name}: ")
                choice = self.ai_text(f"Make this grammatically correct and fun: '{self.name} is {user_text}'")
            elif activities_enum:
                choice = random.choice(list(activities_enum)).value
            else:
                choice = self.ai_text(f"Write a fun sentence describing {self.name} playing.")

        # Update stats
        self._care_level = min(10, self._care_level + 1)
        self._tired_level = min(10, self._tired_level + 2)

        return choice

    def act_train(self, choice=None, custom_input=False):
        """
        Perform a training action for the pet, updating care and tiredness.

        Parameters:
            choice (str|None): Predefined or custom training action.
            custom_input (bool): If True, allows user to input a custom action.

        Returns:
            str: The chosen or AI-generated training action description.
        """
        if not self._alive:
            return None

        species_training = {
            "cat": CatTraining,
            "dog": DogTraining,
            "bird": BirdTraining,
            "fish": FishTraining,
            "guineapig": GuineaPigTraining,
            "hamster": HamsterTraining,
            "horse": HorseTraining,
            "rabbit": RabbitTraining,
            "turtle": TurtleTraining,
            "snake": SnakeTraining,
            "lizard": LizardTraining
        }

        training_enum = species_training.get(self.species.lower())

        if choice is None:
            if custom_input and self.input_func:
                user_text = self.get_input(f"Type a custom training action for {self.name}: ")
                choice = self.ai_text(f"Make this grammatically correct and fun: '{self.name} {user_text}'")
            elif training_enum:
                choice = random.choice(list(training_enum)).value
            else:
                choice = self.ai_text(f"Write a fun sentence describing {self.name} learning a new skill.")

        self._care_level = min(10, self._care_level + 1)
        self._tired_level = min(10, self._tired_level + 2)

        return choice

    def act_clean(self, choice=None, custom_input=False):
        """
        Perform a cleaning action for the pet, updating care and tiredness.

        Parameters:
            choice (str|None): Predefined or custom cleaning action.
            custom_input (bool): If True, allows user to input a custom action.

        Returns:
            str: The chosen or AI-generated cleaning action description.
        """
        if not self._alive:
            return None

        if choice is None:
            if custom_input and self.input_func:
                user_text = self.get_input(f"Type a custom cleaning action for {self.name}: ")
                choice = self.ai_text(f"Make this grammatically correct and fun: '{self.name} {user_text}'")
            else:
                choice = random.choice(list(Clean)).value

        self._care_level = min(10, self._care_level + 1)
        self._tired_level = min(10, self._tired_level + 1)

        return choice
    
    def act_chore(self, choice=None, earned=10, custom_input=False):
        """
        Perform a chore for the pet, updating funds, care, and tiredness.

        Parameters:
            choice (str|None): Predefined or custom chore description.
            earned (float): Amount of money earned for this chore.
            custom_input (bool): If True, allows user to input a custom chore.

        Returns:
            str: The chosen or AI-generated chore description.
        """
        if not self._alive:
            return None

        self.earn(earned)

        if choice is None:
            if custom_input and self.input_func:
                user_text = self.get_input(f"Type a custom chore for {self.name}: ")
                choice = self.ai_text(
                    f"Make this grammatically correct: '{self.name} {user_text} and earned ${earned:.2f}'"
                )
            else:
                choice = random.choice(list(Chores)).value

        self._care_level = max(0, self._care_level - 1)
        self._tired_level = max(0, self._tired_level - 1)

        return choice

    def act_feed(self, choice=None, cost=5, custom_input=False, simulate=False):
        """
        Perform a feeding action for the pet, updating care, tiredness, and spending.

        Parameters:
            choice (str|None): Predefined or custom feeding action.
            cost (float): Cost of feeding the pet.
            custom_input (bool): If True, allows user to input a custom feeding action.
            simulate (bool): If True, suppresses spending output messages.

        Returns:
            str: The chosen or AI-generated feeding action description.
        """
        if not self._alive or not self.spend(cost, simulate):
            return None

        if choice is None:
            if custom_input and self.input_func:
                user_text = self.get_input(f"Type a custom feeding action for {self.name}: ")
                choice = self.ai_text(f"Make this grammatically correct: '{self.name} {user_text}'")
            else:
                choice = f"{self.name} eats happily."

        self._care_level = min(10, self._care_level + 1)
        self._tired_level = min(10, self._tired_level + 1)

        return choice

    def act_rest(self, choice=None, custom_input=False, cost=0, simulate=False):
        """
        Perform a resting action for the pet, optionally costing money, updating care and tiredness.

        Parameters:
            choice (str|None): Predefined or custom resting action.
            custom_input (bool): If True, allows user to input a custom rest action.
            cost (float): Optional cost for premium resting options.
            simulate (bool): If True, suppresses spending output messages.

        Returns:
            str: The chosen or user-defined resting action description.
        """
        if not self._alive:
            return None

        # Handle cost
        if cost > 0:
            if not self.spend(cost, simulate):  # spend() handles funds and debt
                self.output(f"Not enough funds for resting option costing ${cost:.2f}.")
                return None

        # Default rest choice
        if choice is None:
            choice = "normally"

        # Custom user input
        if custom_input and self.input_func:
            user_text = self.get_input(f"Type a custom resting action for {self.name}: ")
            choice = user_text.strip()

        # Update stats
        self._care_level = min(10, self._care_level + 1)
        self._tired_level = max(0, self._tired_level - 2)

        return choice

    def act_vet(self, choice=None, custom_input=False):
        """
        Perform a veterinary action for the pet, optionally using custom user input.

        Parameters:
            choice (str|None): Predefined or custom vet action.
            custom_input (bool): If True, allows user to input a custom vet action.

        Updates:
            Increases the pet's care and tiredness levels.

        Returns:
            str: The chosen or user-defined veterinary action description.
        """
        if not self._alive:
            return None

        if choice is None:
            if custom_input and self.input_func:
                user_text = self.get_input(f"Type a custom vet action for {self.name}: ")
                choice = self.ai_text(f"Make this grammatically correct: '{self.name} {user_text}'")
            else:
                choice = f"{self.name} visits the vet and feels better."

        self._care_level = min(10, self._care_level + 2)
        self._tired_level = min(10, self._tired_level + 1)

        return choice

    # -------------------- STATUS METHODS --------------------
    def get_reaction(self):
        """
        Generate and display a brief textual description of the pet's current mood and energy.

        Mood is based on care level:
            - High care → happy
            - Medium care → okay
            - Low care → sad

        Energy is based on tiredness level:
            - Low tiredness → energetic
            - Medium tiredness → tired
            - High tiredness → exhausted

        Outputs the description, or notes if the pet is dead.
        """
        if not self._alive:
            self.output(f"{self._name} is dead. No reaction.")
            return
        # Determine mood and energy level
        mood = "happy" if self._care_level > 7 else "okay" if self._care_level > 4 else "sad"
        energy = "energetic" if self._tired_level < 3 else "tired" if self._tired_level < 7 else "exhausted"
        self.output(f"{self._name} feels {mood} and {energy}.")

    def health_check(self):
        """
        Display the pet's current status including care level, tiredness, and available funds.
        Also performs a life check to see if the pet is still alive.
        """
        self.output(f"Health: Care {self._care_level}, Tired {self._tired_level}, Funds ${self._funds:.2f}")
        self.check_life_status()

    # -------------------- LIFE & DEATH --------------------
    def check_life_status(self):
        """
        Check if the pet has died from exhaustion or neglect.

        - Collapsed if tiredness reaches 10.
        - Dies from neglect if care level drops to 0 or below.
        Returns True if the pet is dead, otherwise False.
        """
        if not self._alive:
            return True

        if self._tired_level >= 10:
            self.die("collapsed from exhaustion")
            return True
        elif self._care_level <= 0:
            self.die("neglected for too long")
            return True

        return False

    def die(self, reason):
        """
        Handle pet death:
        - Mark pet as dead
        - Print reason
        - Show final summary
        """
        self._alive = False
        self.output(f"{self._name} has died ({reason}).")
        self.final_summary()

    def final_summary(self):
        """
        Print complete summary of pet stats:
        - Age, species, color, care, tiredness, funds
        - Uses AI to describe color if hex code
        - Calls optional on_death callback
        """
        display_color = self.color
        if display_color.startswith("#"):
            try:
                prompt = f"Describe the color represented by the hex code {display_color} in natural language (e.g., 'sky blue', 'forest green')."
                display_color = self.ai_text(prompt)
            except Exception:
                pass  # fallback to hex if AI fails
    
        self.output(
            f"\n{self._name}'s Summary:\n"
            f"Age: {self._age:.2f}\n"
            f"Species: {self._species}\n"
            f"Color: {display_color}\n"
            f"Care: {self._care_level}\n"
            f"Tired: {self._tired_level}\n"
            f"Funds: ${self._funds:.2f}"
        )
        if self.on_death:
            self.on_death()

    def simulate(self, duration):
        """
        Fast-forward the pet's life by a specified duration.
        Each simulated day applies species-specific actions, updates care/tiredness,
        ages the pet slightly, and checks for death conditions.
        
        Parameters:
            duration (str): "day", "week", "month", "year", or "ten years"
        """

        if not self._alive:
            self.output(f"{self.name} is dead. Simulation cannot continue.")
            return

        # Map textual duration to number of days
        duration = duration.strip().lower()
        days_map = {"day": 1, "week": 7, "month": 30, "year": 365, "ten years": 3650}
        if duration not in days_map:
            self.output("Invalid duration. Choose: day, week, month, year, or ten years.")
            return
        days = days_map[duration]

        # Approximate max age for some common pets
        max_ages = {
            "dog": 15, "cat": 20, "fish": 5, "bird": 10, "rabbit": 12, "hamster": 3,
            "guineapig": 8, "turtle": 100, "horse": 25, "snake": 20, "lizard": 10
        }
        pet_type_lower = self.species.strip().lower()
        max_age = max_ages.get(pet_type_lower, 10)

        # Mapping species to their activity and training enums
        species_activities = {
            "dog": DogActivities, "cat": CatActivities, "fish": FishActivities,
            "bird": BirdActivities, "rabbit": RabbitActivities, "hamster": HamsterActivities,
            "guineapig": GuineaPigActivities, "turtle": TurtleActivities, "horse": HorseActivities,
            "snake": SnakeActivities, "lizard": LizardActivities
        }
        species_training = {
            "dog": DogTraining, "cat": CatTraining, "fish": FishTraining,
            "bird": BirdTraining, "rabbit": RabbitTraining, "hamster": HamsterTraining,
            "guineapig": GuineaPigTraining, "turtle": TurtleTraining, "horse": HorseTraining,
            "snake": SnakeTraining, "lizard": LizardTraining
        }

        for _ in range(days):
            if not self._alive:
                break

            # Randomly pick an activity from the species-specific enum
            if pet_type_lower in species_activities:
                activity_enum = species_activities[pet_type_lower]
                activity_choice = random.choice(list(activity_enum))
                self.act_play(choice=activity_choice.value, simulate=True)

            # Rest
            for _ in range(random.randint(2, 4)):
                self.act_rest(simulate=True)

            # Chores / earn funds
            for _ in range(random.randint(3, 5)):
                self.act_chore()

            # Feed
            for _ in range(3):
                self.act_feed(simulate=True)

            # Train
            if pet_type_lower in species_training:
                training_enum = species_training[pet_type_lower]
                training_choice = random.choice(list(training_enum))
                self.act_train(choice=training_choice.value)

            # Clean
            self.act_clean()

            # Random fluctuation in care and tiredness for realism
            self.care_level = max(0, min(10, self.care_level + random.randint(-2, 2)))
            self.tired_level = max(0, min(10, self.tired_level + random.randint(-2, 2)))
            self.check_life_status()

            # Slight age increase (1 day ≈ 0.0027 years)
            self.age += 0.0027

            # Age-based chance of death
            age_factor = self.age / max_age
            if random.random() < age_factor * 0.02:
                self.die("They passed away of old age.")
                break
            # Rare sudden death event
            elif random.random() < 0.001:
                self.die("A sudden unforeseen event ended their life.")
                break

        if self._alive:
            self.output(f"Final health check after {duration}:")
            self.health_check()