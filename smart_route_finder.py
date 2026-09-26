import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import webbrowser


# ==========================================
# FIND LOCATION USING OPENSTREETMAP
# ==========================================

def find_location(place):

    url = "https://nominatim.openstreetmap.org/search"

    # First search normally in India.
    # We do NOT force Andhra Pradesh because the
    # destination may be in another state, e.g. Hyderabad.
    params = {
        "q": f"{place}, India",
        "format": "jsonv2",
        "limit": 5,
        "countrycodes": "in",
        "addressdetails": 1
    }

    headers = {
        "User-Agent": "SmartRouteFinder/1.0"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        place_lower = place.strip().lower()

        # ======================================
        # 1. PREFER EXACT CITY/TOWN/VILLAGE
        # ======================================

        for item in data:

            place_type = item.get(
                "type",
                ""
            ).lower()

            name = item.get(
                "name",
                ""
            ).lower()

            if place_type in [
                "city",
                "town",
                "village",
                "municipality"
            ]:

                if (
                    place_lower == name
                    or place_lower in name
                ):

                    latitude = float(
                        item["lat"]
                    )

                    longitude = float(
                        item["lon"]
                    )

                    display_name = item[
                        "display_name"
                    ]

                    return (
                        latitude,
                        longitude,
                        display_name
                    )

        # ======================================
        # 2. OTHERWISE PREFER CITY/TOWN/VILLAGE
        # ======================================

        for item in data:

            place_type = item.get(
                "type",
                ""
            ).lower()

            if place_type in [
                "city",
                "town",
                "village",
                "municipality"
            ]:

                latitude = float(
                    item["lat"]
                )

                longitude = float(
                    item["lon"]
                )

                display_name = item[
                    "display_name"
                ]

                return (
                    latitude,
                    longitude,
                    display_name
                )

        # ======================================
        # 3. FALLBACK
        # ======================================

        item = data[0]

        latitude = float(
            item["lat"]
        )

        longitude = float(
            item["lon"]
        )

        display_name = item[
            "display_name"
        ]

        return (
            latitude,
            longitude,
            display_name
        )

    except requests.RequestException:

        return None

    except (ValueError, KeyError, IndexError):

        return None


# ==========================================
# FIND ROAD ROUTE
# ==========================================

def find_route(
    start_lat,
    start_lon,
    end_lat,
    end_lon
):

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "overview": "false",
        "steps": "false",
        "alternatives": "true"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if data["code"] == "Ok":

            return data

        return None

    except requests.RequestException:

        return None


# ==========================================
# FIND ROUTE BUTTON
# ==========================================

def search_route():

    start = start_entry.get().strip()

    destination = destination_entry.get().strip()

    # Check empty fields

    if start == "" or destination == "":

        messagebox.showwarning(
            "Input Required",
            "Please enter both locations."
        )

        return

    # Clear previous result

    result_box.delete(
        "1.0",
        tk.END
    )

    result_box.insert(
        tk.END,
        "Searching for locations...\n\n"
    )

    root.update()

    # ======================================
    # FIND START LOCATION
    # ======================================

    start_location = find_location(start)

    if start_location is None:

        messagebox.showerror(
            "Location Not Found",
            f"Could not find: {start}\n\n"
            "Try village + district name."
        )

        result_box.delete(
            "1.0",
            tk.END
        )

        return

    start_lat = start_location[0]

    start_lon = start_location[1]

    start_name = start_location[2]

    result_box.insert(
        tk.END,
        "Starting Location:\n"
    )

    result_box.insert(
        tk.END,
        start_name + "\n\n"
    )

    root.update()

    # ======================================
    # FIND DESTINATION
    # ======================================

    destination_location = find_location(
        destination
    )

    if destination_location is None:

        messagebox.showerror(
            "Location Not Found",
            f"Could not find: {destination}\n\n"
            "Try village + district name."
        )

        result_box.delete(
            "1.0",
            tk.END
        )

        return

    end_lat = destination_location[0]

    end_lon = destination_location[1]

    end_name = destination_location[2]

    result_box.insert(
        tk.END,
        "Destination:\n"
    )

    result_box.insert(
        tk.END,
        end_name + "\n\n"
    )

    result_box.insert(
        tk.END,
        "Finding shortest road route...\n\n"
    )

    root.update()

    # ======================================
    # FIND ROUTE
    # ======================================

    route_data = find_route(
        start_lat,
        start_lon,
        end_lat,
        end_lon
    )

    if route_data is None:

        messagebox.showerror(
            "Route Error",
            "No road route found."
        )

        return

    # ======================================
    # BEST ROUTE
    # ======================================

    best_route = route_data["routes"][0]

    distance_km = (
        best_route["distance"] / 1000
    )

    time_minutes = (
        best_route["duration"] / 60
    )

    hours = int(
        time_minutes // 60
    )

    minutes = int(
        time_minutes % 60
    )

    # ======================================
    # FUEL CALCULATION
    # ======================================

    mileage = 18

    fuel_price = 100

    fuel_required = (
        distance_km / mileage
    )

    fuel_cost = (
        fuel_required * fuel_price
    )

    # ======================================
    # DISPLAY RESULT
    # ======================================

    result_box.delete(
        "1.0",
        tk.END
    )

    result_box.insert(
        tk.END,
        "========================================\n"
    )

    result_box.insert(
        tk.END,
        "          SHORTEST ROAD ROUTE\n"
    )

    result_box.insert(
        tk.END,
        "========================================\n\n"
    )

    result_box.insert(
        tk.END,
        f"Start:\n{start_name}\n\n"
    )

    result_box.insert(
        tk.END,
        f"Destination:\n{end_name}\n\n"
    )

    result_box.insert(
        tk.END,
        f"Route:\n{start} → {destination}\n\n"
    )

    result_box.insert(
        tk.END,
        f"Distance: {distance_km:.2f} KM\n"
    )

    if hours > 0:

        result_box.insert(
            tk.END,
            f"Travel Time: {hours} Hours "
            f"{minutes} Minutes\n"
        )

    else:

        result_box.insert(
            tk.END,
            f"Travel Time: {minutes} Minutes\n"
        )

    result_box.insert(
        tk.END,
        f"Fuel Required: "
        f"{fuel_required:.2f} Litres\n"
    )

    result_box.insert(
        tk.END,
        f"Fuel Cost: "
        f"Rs.{fuel_cost:.2f}\n"
    )

    # ======================================
    # ALTERNATIVE ROUTES
    # ======================================

    if len(route_data["routes"]) > 1:

        result_box.insert(
            tk.END,
            "\n========================================\n"
        )

        result_box.insert(
            tk.END,
            "          ALTERNATIVE ROUTES\n"
        )

        result_box.insert(
            tk.END,
            "========================================\n"
        )

        for i, route in enumerate(
            route_data["routes"][1:],
            1
        ):

            alt_distance = (
                route["distance"] / 1000
            )

            alt_time = (
                route["duration"] / 60
            )

            result_box.insert(
                tk.END,
                f"\nAlternative Route {i}\n"
            )

            result_box.insert(
                tk.END,
                f"Distance: "
                f"{alt_distance:.2f} KM\n"
            )

            result_box.insert(
                tk.END,
                f"Time: "
                f"{alt_time:.0f} Minutes\n"
            )

    result_box.insert(
        tk.END,
        "\n========================================\n"
    )

    result_box.insert(
        tk.END,
        "             SEARCH COMPLETE\n"
    )

    result_box.insert(
        tk.END,
        "========================================\n"
    )

    # ======================================
    # SAVE COORDINATES FOR MAP
    # ======================================

    global current_start_lat
    global current_start_lon
    global current_end_lat
    global current_end_lon

    current_start_lat = start_lat
    current_start_lon = start_lon

    current_end_lat = end_lat
    current_end_lon = end_lon

    map_button.config(
        state=tk.NORMAL
    )


# ==========================================
# OPEN ROUTE IN MAP
# ==========================================

def open_map():

    if current_start_lat is None:

        messagebox.showwarning(
            "Search First",
            "Please find a route first."
        )

        return

    map_url = (
        "https://www.openstreetmap.org/directions?"
        f"engine=fossgis_osrm_car&"
        f"route={current_start_lat},"
        f"{current_start_lon};"
        f"{current_end_lat},"
        f"{current_end_lon}"
    )

    webbrowser.open(map_url)


# ==========================================
# CLEAR BUTTON
# ==========================================

def clear_all():

    start_entry.delete(
        0,
        tk.END
    )

    destination_entry.delete(
        0,
        tk.END
    )

    result_box.delete(
        "1.0",
        tk.END
    )

    map_button.config(
        state=tk.DISABLED
    )


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()

root.title(
    "Smart Route Finder"
)

root.geometry(
    "850x700"
)


# ==========================================
# TITLE
# ==========================================

title_label = tk.Label(
    root,
    text="SMART ROUTE FINDER",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=20
)


subtitle_label = tk.Label(
    root,
    text="Find the shortest road route between any locations",
    font=("Arial", 12)
)

subtitle_label.pack(
    pady=5
)


# ==========================================
# START LOCATION
# ==========================================

start_frame = tk.Frame(root)

start_frame.pack(
    pady=15
)

start_label = tk.Label(
    start_frame,
    text="Starting Location:",
    font=("Arial", 13)
)

start_label.grid(
    row=0,
    column=0,
    padx=10
)

start_entry = tk.Entry(
    start_frame,
    width=35,
    font=("Arial", 13)
)

start_entry.grid(
    row=0,
    column=1,
    padx=10
)


# ==========================================
# DESTINATION
# ==========================================

destination_frame = tk.Frame(root)

destination_frame.pack(
    pady=10
)

destination_label = tk.Label(
    destination_frame,
    text="Destination:",
    font=("Arial", 13)
)

destination_label.grid(
    row=0,
    column=0,
    padx=10
)

destination_entry = tk.Entry(
    destination_frame,
    width=35,
    font=("Arial", 13)
)

destination_entry.grid(
    row=0,
    column=1,
    padx=10
)


# ==========================================
# BUTTON FRAME
# ==========================================

button_frame = tk.Frame(root)

button_frame.pack(
    pady=15
)

search_button = tk.Button(
    button_frame,
    text="FIND ROUTE",
    command=search_route,
    font=("Arial", 12, "bold"),
    padx=20,
    pady=10
)

search_button.grid(
    row=0,
    column=0,
    padx=10
)

map_button = tk.Button(
    button_frame,
    text="OPEN MAP",
    command=open_map,
    font=("Arial", 12, "bold"),
    padx=20,
    pady=10,
    state=tk.DISABLED
)

map_button.grid(
    row=0,
    column=1,
    padx=10
)

clear_button = tk.Button(
    button_frame,
    text="CLEAR",
    command=clear_all,
    font=("Arial", 12, "bold"),
    padx=20,
    pady=10
)

clear_button.grid(
    row=0,
    column=2,
    padx=10
)


# ==========================================
# RESULT BOX
# ==========================================

result_box = scrolledtext.ScrolledText(
    root,
    width=90,
    height=22,
    font=("Consolas", 11)
)

result_box.pack(
    padx=20,
    pady=15
)


# ==========================================
# GLOBAL MAP VARIABLES
# ==========================================

current_start_lat = None
current_start_lon = None

current_end_lat = None
current_end_lon = None


# ==========================================
# START APPLICATION
# ==========================================

root.mainloop()
