import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import configparser
import datetime
import csv
from tkinter import messagebox

def save_credentials():
    config = configparser.ConfigParser()
    config['Credentials'] = {'Name': name_var.get(), 'BattleTag': battletag_var.get()}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def load_credentials():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'Credentials' in config:
        name_var.set(config['Credentials']['Name'])
        battletag_var.set(config['Credentials']['BattleTag'])

def fetch_stats():
    name = name_var.get()
    battletag = battletag_var.get()

    url = f"https://overwatch.blizzard.com/en-gb/career/{name}-{battletag}/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        stats_text.delete(1.0, tk.END)  # Clear previous stats

        stats = {}
        categories = soup.find_all('div', class_='category')
        for category in categories:
            category_name = category.find('div', class_='header').find('p').text
            stats_in_category = {}
            stat_items = category.find_all('div', class_='stat-item')
            for stat_item in stat_items:
                stat_name = stat_item.find('p', class_='name').text
                stat_value = stat_item.find('p', class_='value').text
                stats_in_category[stat_name] = stat_value
            stats[category_name] = stats_in_category

        for category, stats_in_category in stats.items():
            stats_text.insert(tk.END, f"### {category}\n")
            for stat, value in stats_in_category.items():
                stats_text.insert(tk.END, f"{stat}: {value}\n")
            stats_text.insert(tk.END, "\n")  # Add a newline between categories

    except requests.exceptions.RequestException as e:
        stats_text.delete(1.0, tk.END)  # Clear previous stats
        stats_text.insert(tk.END, f"Error: {str(e)}\n")

def save_stats():
    now = datetime.datetime.now()
    date_str = now.strftime("%d-%m")
    file_name = f"stats-{date_str}.txt"

    stats_to_save = stats_text.get(1.0, tk.END)
    with open(file_name, 'w') as statsfile:
        statsfile.write(stats_to_save)

def clear_stats():
    stats_text.delete(1.0, tk.END)

def reset_fields():
    name_var.set("")
    battletag_var.set("")

def export_to_csv():
    stats_to_export = stats_text.get(1.0, tk.END)
    with open('stats.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Category', 'Stat', 'Value'])
        current_category = ""
        for line in stats_to_export.split('\n'):
            if line.startswith("###"):
                current_category = line[4:]
            elif line.strip():
                stat_name, stat_value = line.split(": ")
                writer.writerow([current_category, stat_name, stat_value])

def create_user_profile():
    name = name_var.get()
    battletag = battletag_var.get()

    profile_name = f"{name}-{battletag}"

    config = configparser.ConfigParser()
    config[profile_name] = {'Name': name, 'BattleTag': battletag}

    with open('profiles.ini', 'a') as configfile:
        config.write(configfile)
        load_user_profiles()  # Reload user profiles in the menu

def load_user_profiles():
    profiles_menu.delete(0, tk.END)
    config = configparser.ConfigParser()
    config.read('profiles.ini')
    for section in config.sections():
        name = config[section]['Name']
        battletag = config[section]['BattleTag']
        profile_name = f"{name}-{battletag}"
        profiles_menu.add_command(label=profile_name, command=lambda name=name, battletag=battletag: select_user_profile(name, battletag))

def select_user_profile(name, battletag):
    name_var.set(name)
    battletag_var.set(battletag)

# Create the main window
root = tk.Tk()
root.title("Overwatch Stats Viewer")

# Create StringVar objects for name and BattleTag
name_var = tk.StringVar()
battletag_var = tk.StringVar()

# Create labels and entry fields for name and BattleTag
name_label = ttk.Label(root, text="Name:")
name_label.grid(row=0, column=0, padx=10, pady=5)
name_entry = ttk.Entry(root, textvariable=name_var)
name_entry.grid(row=0, column=1, padx=10, pady=5)

battletag_label = ttk.Label(root, text="BattleTag:")
battletag_label.grid(row=1, column=0, padx=10, pady=5)
battletag_entry = ttk.Entry(root, textvariable=battletag_var)
battletag_entry.grid(row=1, column=1, padx=10, pady=5)

# Create a "Remember Me" checkbox
remember_me_var = tk.BooleanVar()
remember_me_checkbox = ttk.Checkbutton(root, text="Remember Me", variable=remember_me_var)
remember_me_checkbox.grid(row=2, columnspan=2, pady=5)

# Load saved credentials if "Remember Me" is checked
load_credentials()

# Create a button to fetch stats
fetch_button = ttk.Button(root, text="Fetch Stats", command=fetch_stats)
fetch_button.grid(row=3, columnspan=2, pady=10)

# Create a "Save Stats" button
save_stats_button = ttk.Button(root, text="Save Stats", command=save_stats)
save_stats_button.grid(row=5, column=0, padx=0, pady=0)  # Remove padx and pady

# Create a "Clear Stats" button
clear_stats_button = ttk.Button(root, text="Clear Stats", command=clear_stats)
clear_stats_button.grid(row=5, column=1, padx=0, pady=0)  # Remove padx and pady

# Create a "Reset Fields" button
reset_fields_button = ttk.Button(root, text="Reset Fields", command=reset_fields)
reset_fields_button.grid(row=6, column=0, padx=0, pady=0)  # Remove padx and pady

# Create an "Export to CSV" button
export_csv_button = ttk.Button(root, text="Export to CSV", command=export_to_csv)
export_csv_button.grid(row=6, column=1, padx=0, pady=0)  # Remove padx and pady

# Create a "Create Profile" button
create_profile_button = ttk.Button(root, text="Create Profile", command=create_user_profile)
create_profile_button.grid(row=7, columnspan=2, padx=0, pady=0)  # Remove padx and pady


# Create a user profiles menu
profiles_menu = tk.Menu(root)
root.config(menu=profiles_menu)

# Load user profiles into the menu
load_user_profiles()

# Create a text widget to display the stats
stats_text = tk.Text(root, wrap=tk.WORD, width=60, height=20)
stats_text.grid(row=4, columnspan=2, padx=10, pady=5)

root.mainloop()

# Save credentials if "Remember Me" is checked
if remember_me_var.get():
    save_credentials()
