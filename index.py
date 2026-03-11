import random
import time     
import copy
from colorama import Fore, Style, init

init(autoreset=True)


def title(text):
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.YELLOW + text.center(60))
    print(Fore.CYAN + "=" * 60)


class GridEnvironment:

    def __init__(self, size, mode):
        self.size = size
        self.grid = []

        if mode == 1:
            self.random_environment()
        else:
            self.manual_environment()

    def random_environment(self):

        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(random.choice(["D", "C"]))
            self.grid.append(row)

    def manual_environment(self):

        print(Fore.MAGENTA + "\nEnter Environment (D = Dirty, C = Clean)\n")

        for i in range(self.size):

            row = []

            for j in range(self.size):

                val = input(f"Cell ({i},{j}) [D/C]: ").upper()

                while val not in ["D", "C"]:
                    val = input("Invalid input. Enter D or C: ").upper()

                row.append(val)

            self.grid.append(row)

    def display(self, rx=None, ry=None):

        for i in range(self.size):

            print(Fore.BLUE + "+----" * self.size + "+")

            for j in range(self.size):

                if i == rx and j == ry:
                    symbol = Fore.MAGENTA + "🤖"
                else:
                    if self.grid[i][j] == "D":
                        symbol = Fore.RED + "D"
                    else:
                        symbol = Fore.GREEN + "C"

                print("|", symbol.center(4), end="")

            print("|")

        print(Fore.BLUE + "+----" * self.size + "+")

    def clean(self, x, y):

        if self.grid[x][y] == "D":
            self.grid[x][y] = "C"
            return True

        return False


class ReflexAgent:

    def __init__(self, env):
        self.env = env
        self.moves = 0
        self.cleaned = 0

    def run(self):

        title("REFLEX AGENT RUNNING")

        for i in range(self.env.size):

            for j in range(self.env.size):

                print(Fore.WHITE + "\nRobot Position:", (i, j))

                self.env.display(i, j)

                if self.env.clean(i, j):
                    print(Fore.GREEN + "Cleaned dirt at", (i, j))
                    self.cleaned += 1
                else:
                    print(Fore.YELLOW + "Already clean")

                self.moves += 1
                time.sleep(0.5)

        return self.moves, self.cleaned


class ModelBasedAgent:

    def __init__(self, env):
        self.env = env
        self.moves = 0
        self.cleaned = 0
        self.model = [[None] * env.size for _ in range(env.size)]

    def run(self):

        title("MODEL BASED AGENT RUNNING")

        # First observe the environment
        for i in range(self.env.size):
            for j in range(self.env.size):
                self.model[i][j] = self.env.grid[i][j]

        # Move only to dirty cells
        for i in range(self.env.size):
            for j in range(self.env.size):

                if self.model[i][j] == "D":

                    print(Fore.WHITE + "\nRobot Position:", (i, j))

                    self.env.display(i, j)

                    if self.env.clean(i, j):
                        print(Fore.GREEN + "Cleaned dirt at", (i, j))
                        self.cleaned += 1

                    self.moves += 1
                    time.sleep(0.5)

        return self.moves, self.cleaned


# ---------------- MAIN PROGRAM ---------------- #

title("VACUUM CLEANER AI SIMULATION")

size = int(input("Enter grid size (example 3 or 5): "))

print("\n1 → Random Environment")
print("2 → Manual Environment")

mode = int(input("Choose environment type: "))

env = GridEnvironment(size, mode)

title("INITIAL ENVIRONMENT")
env.display()

# identical environment for both agents
env_reflex = copy.deepcopy(env)
env_model = copy.deepcopy(env)

# Reflex Agent
reflex = ReflexAgent(env_reflex)
reflex_moves, reflex_clean = reflex.run()

# Model Agent
model = ModelBasedAgent(env_model)
model_moves, model_clean = model.run()

title("PERFORMANCE COMPARISON")

print(Fore.CYAN + "Reflex Agent Moves  :", reflex_moves)
print(Fore.CYAN + "Reflex Dirt Cleaned :", reflex_clean)

print(Fore.MAGENTA + "\nModel Agent Moves   :", model_moves)
print(Fore.MAGENTA + "Model Dirt Cleaned  :", model_clean)

# efficiency
total_cells = size * size

reflex_eff = (reflex_clean / reflex_moves) * 100
model_eff = (model_clean / model_moves) * 100

print("\nReflex Agent Efficiency :", round(reflex_eff,2), "%")
print("Model Agent Efficiency  :", round(model_eff,2), "%")
print(Fore.GREEN + "\nSimulation Completed ✔")