"""
============================================================================
 Commute Route Optimizer
 ----------------------------------------------------------------------------
 Student  : Waleed Ahmad Khan
 Roll No  : Mtech-PY26017
 Phase 1 Algorithm : Hill Climbing (local search)   <-- do NOT change
 GUI Toolkit       : Tkinter  (built into Python, no extra install needed)
============================================================================

 REAL-WORLD PROBLEM
 ------------------
 A daily commuter leaves from a fixed START point (e.g. Home) and must reach
 a fixed END point (e.g. Office). On the way they have to visit several
 STOPS / waypoints - drop children at school, refuel the car, collect
 groceries, visit the bank, and so on.

 The ORDER in which these stops are visited changes the total distance
 travelled. A bad order wastes fuel and time. This program treats the map as
 a 2-D plane and uses the HILL CLIMBING algorithm to search for the ordering
 of stops that gives the SHORTEST total commute distance (straight-line /
 Euclidean distance between points).

 HOW HILL CLIMBING IS USED HERE
 ------------------------------
   * A "state"      = one complete ordering of the stops.
   * A "neighbour"  = the same ordering with any two stops swapped.
   * The "cost"     = total distance of the whole route.
   * Hill climbing repeatedly moves to a neighbour that LOWERS the cost and
     stops when no single swap can improve it any further (a local optimum).
   * Random restarts are added so the search is less likely to get trapped
     in a poor local optimum. This is the standard "random-restart hill
     climbing" variant and still uses the same hill-climbing move.
============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random


# ===========================================================================
#  PURE ALGORITHM SECTION  (no GUI code here, so it is easy to read and test)
# ===========================================================================
def route_distance(order, coords):
    """Return the total straight-line distance of one complete route.

    order  : list of location indices, e.g. [0, 3, 1, 2, 4]
    coords : list of (x, y) tuples for every location
    """
    total = 0.0
    for step in range(len(order) - 1):
        x1, y1 = coords[order[step]]
        x2, y2 = coords[order[step + 1]]
        total += math.hypot(x1 - x2, y1 - y2)   # Euclidean distance
    return total


def hill_climbing(start_index, end_index, waypoint_indices, coords,
                  restarts=25, rng=None):
    """Optimise the order of the waypoints using random-restart hill climbing.

    The START and END locations stay fixed; only the middle stops are moved.

    Returns: (best_order, best_distance, steps_evaluated)
    """
    if rng is None:
        rng = random.Random()

    best_order = None
    best_distance = float("inf")
    steps_evaluated = 0

    # Each restart begins from a fresh, random ordering of the waypoints.
    for _ in range(max(1, restarts)):
        current_waypoints = waypoint_indices[:]
        rng.shuffle(current_waypoints)
        current_order = [start_index] + current_waypoints + [end_index]
        current_distance = route_distance(current_order, coords)

        # Keep climbing while a better neighbour can be found.
        improved = True
        while improved:
            improved = False
            # Try swapping every pair of WAYPOINT positions.
            # Position 0 and the last position are the fixed start / end,
            # so the loops start at 1 and stop before the last index.
            for i in range(1, len(current_order) - 1):
                for j in range(i + 1, len(current_order) - 1):
                    neighbour = current_order[:]
                    neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
                    steps_evaluated += 1
                    neighbour_distance = route_distance(neighbour, coords)
                    # "Climb" only if the neighbour is strictly better.
                    if neighbour_distance < current_distance - 1e-9:
                        current_order = neighbour
                        current_distance = neighbour_distance
                        improved = True

        # Remember the best result found across all restarts.
        if current_distance < best_distance:
            best_distance = current_distance
            best_order = current_order

    return best_order, best_distance, steps_evaluated


# ===========================================================================
#  GRAPHICAL USER INTERFACE  (Tkinter)
# ===========================================================================
class CommuteRouteOptimizerApp:
    """The full Tkinter application window."""

    CANVAS_W = 640          # width  of the map area in pixels
    CANVAS_H = 460          # height of the map area in pixels

    def __init__(self, root):
        self.root = root
        self.root.title("Commute Route Optimizer  -  Hill Climbing  (Waleed Ahmad Khan)")
        self.root.geometry("1040x640")
        self.root.minsize(980, 600)

        # Each location is a dict: {"name": str, "x": int, "y": int}
        self.locations = []
        self.optimized_order = None    # last computed best route (list of indices)

        self._build_ui()
        self.load_sample()             # start with example data so it is ready to test

    # ---------------------------------------------------------------- UI build
    def _build_ui(self):
        # ---- left side: all the controls -----------------------------------
        controls = ttk.Frame(self.root, padding=10)
        controls.grid(row=0, column=0, sticky="ns")

        ttk.Label(controls, text="Add a Location",
                  font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2,
                                                    sticky="w", pady=(0, 6))

        ttk.Label(controls, text="Name:").grid(row=1, column=0, sticky="e")
        self.name_entry = ttk.Entry(controls, width=18)
        self.name_entry.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(controls, text="X (0-%d):" % self.CANVAS_W).grid(row=2, column=0, sticky="e")
        self.x_entry = ttk.Entry(controls, width=18)
        self.x_entry.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(controls, text="Y (0-%d):" % self.CANVAS_H).grid(row=3, column=0, sticky="e")
        self.y_entry = ttk.Entry(controls, width=18)
        self.y_entry.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Button(controls, text="Add Location",
                   command=self.add_location).grid(row=4, column=0, columnspan=2,
                                                    sticky="ew", pady=(4, 2))
        ttk.Label(controls, text="(Tip: you can also click on the map to add a stop)",
                  foreground="#555", wraplength=210,
                  font=("Arial", 8)).grid(row=5, column=0, columnspan=2, sticky="w")

        ttk.Separator(controls, orient="horizontal").grid(row=6, column=0, columnspan=2,
                                                           sticky="ew", pady=8)

        ttk.Label(controls, text="Locations",
                  font=("Arial", 12, "bold")).grid(row=7, column=0, columnspan=2, sticky="w")
        self.location_listbox = tk.Listbox(controls, height=8, width=32,
                                           activestyle="none")
        self.location_listbox.grid(row=8, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Button(controls, text="Delete Selected",
                   command=self.delete_selected).grid(row=9, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Clear All",
                   command=self.clear_all).grid(row=9, column=1, sticky="ew", pady=2)
        ttk.Button(controls, text="Load Sample Commute",
                   command=self.load_sample).grid(row=10, column=0, columnspan=2,
                                                   sticky="ew", pady=2)

        ttk.Separator(controls, orient="horizontal").grid(row=11, column=0, columnspan=2,
                                                           sticky="ew", pady=8)

        ttk.Label(controls, text="Route Settings",
                  font=("Arial", 12, "bold")).grid(row=12, column=0, columnspan=2, sticky="w")

        ttk.Label(controls, text="Start:").grid(row=13, column=0, sticky="e")
        self.start_combo = ttk.Combobox(controls, width=16, state="readonly")
        self.start_combo.grid(row=13, column=1, sticky="w", pady=2)

        ttk.Label(controls, text="End:").grid(row=14, column=0, sticky="e")
        self.end_combo = ttk.Combobox(controls, width=16, state="readonly")
        self.end_combo.grid(row=14, column=1, sticky="w", pady=2)

        ttk.Label(controls, text="Restarts:").grid(row=15, column=0, sticky="e")
        self.restart_var = tk.IntVar(value=25)
        ttk.Spinbox(controls, from_=1, to=200, textvariable=self.restart_var,
                    width=16).grid(row=15, column=1, sticky="w", pady=2)

        ttk.Button(controls, text="Optimize Route  (Hill Climbing)",
                   command=self.optimize).grid(row=16, column=0, columnspan=2,
                                                sticky="ew", pady=(8, 2))

        # ---- right side: the map canvas and the results box ----------------
        right = ttk.Frame(self.root, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(right, width=self.CANVAS_W, height=self.CANVAS_H,
                                bg="white", highlightthickness=1,
                                highlightbackground="#999")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        self.result_text = tk.Text(right, height=8, width=60, wrap="word",
                                   state="disabled", bg="#f7f7f7",
                                   font=("Consolas", 10))
        self.result_text.grid(row=1, column=0, sticky="ew", pady=(8, 0))

    # ---------------------------------------------------- helper: read numbers
    def _read_int(self, entry, field_name, low, high):
        """Read an integer from an entry box, validating the range.

        Returns the integer, or None (and shows a message) if it is invalid.
        """
        raw = entry.get().strip()
        try:
            value = int(float(raw))          # accept "120" or "120.0"
        except ValueError:
            messagebox.showwarning("Invalid input",
                                   "%s must be a number." % field_name)
            return None
        if not (low <= value <= high):
            messagebox.showwarning("Out of range",
                                   "%s must be between %d and %d." % (field_name, low, high))
            return None
        return value

    # ------------------------------------------------------------ add / remove
    def add_location(self, x=None, y=None, name=None):
        """Add a new location either from the entry boxes or from a map click."""
        # Coordinates: use the ones passed in (from a click) or read the boxes.
        if x is None:
            x = self._read_int(self.x_entry, "X coordinate", 0, self.CANVAS_W)
            if x is None:
                return
        if y is None:
            y = self._read_int(self.y_entry, "Y coordinate", 0, self.CANVAS_H)
            if y is None:
                return

        # Name: use the box, or auto-generate a friendly one if it is empty.
        if name is None:
            name = self.name_entry.get().strip()
        if not name:
            name = "Stop %d" % (len(self.locations) + 1)

        self.locations.append({"name": name, "x": int(x), "y": int(y)})

        # Clear the entry boxes for the next input.
        self.name_entry.delete(0, tk.END)
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)

        self.optimized_order = None        # old route is no longer valid
        self._refresh_lists()
        self._redraw()

    def delete_selected(self):
        """Remove the location currently highlighted in the list."""
        selection = self.location_listbox.curselection()
        if not selection:
            messagebox.showinfo("Nothing selected",
                                "Please click a location in the list first.")
            return
        index = selection[0]
        del self.locations[index]
        self.optimized_order = None
        self._refresh_lists()
        self._redraw()

    def clear_all(self):
        """Delete every location and reset the map."""
        self.locations = []
        self.optimized_order = None
        self._refresh_lists()
        self._redraw()
        self._show_result("All locations cleared. Add stops or load the sample.")

    def load_sample(self):
        """Fill the app with a realistic example commute for quick testing."""
        self.locations = [
            {"name": "Home",     "x": 60,  "y": 400},
            {"name": "School",   "x": 180, "y": 120},
            {"name": "Gas",      "x": 300, "y": 380},
            {"name": "Bank",     "x": 420, "y": 150},
            {"name": "Grocery",  "x": 520, "y": 340},
            {"name": "Pharmacy", "x": 360, "y": 250},
            {"name": "Office",   "x": 600, "y": 60},
        ]
        self.optimized_order = None
        self._refresh_lists()
        # Default: start = Home (first), end = Office (last).
        self.start_combo.current(0)
        self.end_combo.current(len(self.locations) - 1)
        self._redraw()
        self._show_result("Sample commute loaded: Home -> ... -> Office.\n"
                          "Press 'Optimize Route (Hill Climbing)' to find the "
                          "shortest order of stops.")

    # -------------------------------------------------- keep widgets in sync
    def _refresh_lists(self):
        """Refresh the listbox and the two start/end dropdowns."""
        self.location_listbox.delete(0, tk.END)
        for i, loc in enumerate(self.locations):
            self.location_listbox.insert(
                tk.END, "%d. %s  (%d, %d)" % (i + 1, loc["name"], loc["x"], loc["y"]))

        names = [loc["name"] for loc in self.locations]
        previous_start = self.start_combo.current()
        previous_end = self.end_combo.current()
        self.start_combo["values"] = names
        self.end_combo["values"] = names
        if names:
            # Keep the old choice if it is still valid, otherwise use defaults.
            self.start_combo.current(previous_start if 0 <= previous_start < len(names) else 0)
            self.end_combo.current(previous_end if 0 <= previous_end < len(names) else len(names) - 1)
        else:
            self.start_combo.set("")
            self.end_combo.set("")

    # ---------------------------------------------------------- map interaction
    def _on_canvas_click(self, event):
        """Add a stop where the user clicks on the map."""
        x = max(0, min(self.CANVAS_W, event.x))
        y = max(0, min(self.CANVAS_H, event.y))
        self.add_location(x=x, y=y)

    # ------------------------------------------------------------- optimization
    def optimize(self):
        """Run hill climbing and display the best commute route found."""
        # --- edge case: need at least a start and an end ---
        if len(self.locations) < 2:
            messagebox.showwarning("Not enough locations",
                                   "Please add at least 2 locations "
                                   "(a start and an end).")
            return

        start_index = self.start_combo.current()
        end_index = self.end_combo.current()
        if start_index < 0 or end_index < 0:
            messagebox.showwarning("Select start / end",
                                   "Please choose both a Start and an End location.")
            return

        # --- edge case: start and end must be different ---
        if start_index == end_index:
            messagebox.showwarning("Invalid selection",
                                   "Start and End must be two different locations.")
            return

        coords = [(loc["x"], loc["y"]) for loc in self.locations]
        waypoints = [i for i in range(len(self.locations))
                     if i not in (start_index, end_index)]

        # Distance of the "as entered" order, used to show the improvement.
        naive_order = [start_index] + waypoints + [end_index]
        naive_distance = route_distance(naive_order, coords)

        # --- run the Phase 1 algorithm: Hill Climbing ---
        best_order, best_distance, steps = hill_climbing(
            start_index, end_index, waypoints, coords,
            restarts=self.restart_var.get(), rng=random.Random())

        self.optimized_order = best_order
        self._redraw(best_order)

        # --- build a readable result report ---
        route_names = " -> ".join(self.locations[i]["name"] for i in best_order)
        if naive_distance > 0:
            saved_percent = (naive_distance - best_distance) / naive_distance * 100
        else:
            saved_percent = 0.0

        report = (
            "OPTIMIZED COMMUTE ROUTE\n"
            "------------------------------------------------------------\n"
            "%s\n\n"
            "Stops visited        : %d\n"
            "Original distance     : %.1f units\n"
            "Optimized distance    : %.1f units\n"
            "Distance saved        : %.1f units  (%.1f%% shorter)\n"
            "Neighbours evaluated  : %d   |   Restarts: %d"
            % (route_names, len(best_order), naive_distance, best_distance,
               naive_distance - best_distance, saved_percent,
               steps, self.restart_var.get())
        )
        self._show_result(report)

    # --------------------------------------------------------------- drawing
    def _redraw(self, order=None):
        """Redraw the whole map: grid, route lines and location markers."""
        canvas = self.canvas
        canvas.delete("all")

        # Light background grid to make it look like a map.
        for gx in range(0, self.CANVAS_W + 1, 40):
            canvas.create_line(gx, 0, gx, self.CANVAS_H, fill="#eeeeee")
        for gy in range(0, self.CANVAS_H + 1, 40):
            canvas.create_line(0, gy, self.CANVAS_W, gy, fill="#eeeeee")

        # Draw the route (arrows) if we have an optimized order.
        if order and len(order) >= 2:
            for step in range(len(order) - 1):
                a = self.locations[order[step]]
                b = self.locations[order[step + 1]]
                canvas.create_line(a["x"], a["y"], b["x"], b["y"],
                                   fill="#3366cc", width=3, arrow=tk.LAST,
                                   arrowshape=(14, 16, 6))

        # Figure out which locations are the start and end (for colour).
        start_index = self.start_combo.current()
        end_index = self.end_combo.current()

        # Draw each location as a coloured dot with its name.
        for index, loc in enumerate(self.locations):
            if index == start_index:
                colour = "#2e7d32"       # green = start
            elif index == end_index:
                colour = "#c62828"       # red = end
            else:
                colour = "#1565c0"       # blue = waypoint
            x, y = loc["x"], loc["y"]
            canvas.create_oval(x - 9, y - 9, x + 9, y + 9,
                               fill=colour, outline="black", width=1)
            canvas.create_text(x, y - 16, text=loc["name"],
                               font=("Arial", 9, "bold"))

    # --------------------------------------------------------- results helper
    def _show_result(self, text):
        """Write a message into the read-only results box."""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state="disabled")


# ===========================================================================
#  PROGRAM ENTRY POINT
# ===========================================================================
if __name__ == "__main__":
    window = tk.Tk()
    app = CommuteRouteOptimizerApp(window)
    window.mainloop()
