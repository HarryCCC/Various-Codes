import csv
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

# Function to load data from CSV
def load_data():
    global sales, inventory, clerks  # Declare clerks as global too
    try:
        with open("销售.csv", mode="r") as f:
            reader = csv.reader(f)
            sales = [row for row in reader]
            clerks = set(row[1] for row in sales[1:])  # Skip the header row
        with open("库存.csv", mode="r") as f:
            reader = csv.reader(f)
            inventory = {rows[0]: int(rows[1]) for rows in reader}
    except FileNotFoundError:
        pass

# Function to save data to CSV
def save_data():
    with open("销售.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(sales)
    with open("库存.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        for key, value in inventory.items():
            writer.writerow([key, value])

# Function to add sales
def add_sale():
    global clerks  # Declare clerks as global
    clerk = clerk_entry.get()
    clerks.add(clerk)  # Add clerk to the set
    item = item_sale_entry.get()
    amount = float(amount_entry.get())
    quantity = int(quantity_entry.get())
    timestamp = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

    # Append the new sale to the sales list
    sales.append([timestamp, clerk, item, quantity, amount])

    # Update the inventory based on the sale
    if item in inventory:
        inventory[item] -= quantity

    save_data()
    update_comboboxes()

    sales_status_label.config(text="数据已保存")
    root.after(2000, lambda: sales_status_label.config(text="------"))

# Function to add inventory
def add_inventory():
    item = item_inventory_entry.get()
    amount = int(amount_inventory_entry.get())
    if item not in inventory:
        inventory[item] = 0
    inventory[item] += amount
    
    save_data()
    update_comboboxes()

    inventory_status_label.config(text="数据已保存")
    root.after(2000, lambda: inventory_status_label.config(text="------"))

# Function to calculate bonus
def calculate_bonus():
    clerk = clerk_bonus_entry.get()
    rate = float(rate_entry.get()) / 100
    
    # Calculate the total sales of the clerk in the last 30 days
    last_30_days_sales = 0.0
    cutoff_date = datetime.now() - timedelta(days=30)
    for sale in sales[1:]:  # Skip the header row
        sale_date = datetime.strptime(sale[0], "%Y.%m.%d %H:%M:%S")
        if sale_date >= cutoff_date and sale[1] == clerk:
            last_30_days_sales += float(sale[4])
    
    bonus_amount = last_30_days_sales * rate
    
    bonus_output.config(state="normal")
    bonus_output.delete(1.0, tk.END)
    bonus_output.insert(tk.END, f"提成金额: {bonus_amount}")
    bonus_output.config(state="disabled")

def update_comboboxes():
    clerk_entry['values'] = list(clerks)
    item_sale_entry['values'] = list(inventory.keys())
    item_inventory_entry['values'] = list(inventory.keys())
    clerk_bonus_entry['values'] = list(clerks)



# Initialize this variable at the beginning of your script
debounce_timer = None
# Function to auto-dropdown the combobox
def auto_dropdown(event):
    global debounce_timer  # Declare it as global so we can cancel the previous timer

    widget = event.widget  # Get the combobox widget
    current_text = widget.get()

    # Cancel the previous timer if it exists
    if debounce_timer is not None:
        root.after_cancel(debounce_timer)

    # Set a new timer
    debounce_timer = root.after(2000, lambda: show_dropdown(widget, current_text))  # 300 milliseconds delay

def show_dropdown(widget, current_text):
    if widget == clerk_entry or widget == clerk_bonus_entry:
        original_values = list(clerks)
    elif widget == item_sale_entry or widget == item_inventory_entry:
        original_values = list(inventory.keys())

    matching_values = [value for value in original_values if current_text.lower() in value.lower()]

    if matching_values:
        widget['values'] = matching_values
    else:
        widget['values'] = original_values  # Reset the values to the original list if no match

    widget.event_generate("<Down>")  # Generate Down arrow key event to open the dropdown




# Initialize dictionaries and lists
sales = [["时间", "店员", "货品", "数量", "销售额"]]
inventory = {}
clerks = set()  # New set to keep track of clerks


# Initialize the root window
root = tk.Tk()
root.title("店铺管理")

# Load data before creating the GUI
load_data()


# Center the window on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 400  # You can change this
window_height = 400  # You can change this
position_x = int((screen_width / 2) - (window_width / 2))
position_y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

# Sales frame
sales_frame = ttk.LabelFrame(root, text="销售")
sales_frame.grid(row=0, column=0, padx=10, pady=10)

clerk_entry = ttk.Combobox(sales_frame, width=15, values=list(clerks))
clerk_entry.bind('<KeyRelease>', auto_dropdown)
clerk_entry.grid(row=0, column=1)
ttk.Label(sales_frame, text="店员:").grid(row=0, column=0)

item_sale_entry = ttk.Combobox(sales_frame, width=15, values=list(inventory.keys()))
item_sale_entry.bind('<KeyRelease>', auto_dropdown)
item_sale_entry.grid(row=1, column=1)
ttk.Label(sales_frame, text="货品:").grid(row=1, column=0)

amount_entry = ttk.Entry(sales_frame, width=15)
amount_entry.grid(row=3, column=1)
ttk.Label(sales_frame, text="金额:").grid(row=3, column=0)

quantity_entry = ttk.Entry(sales_frame, width=15)
quantity_entry.grid(row=2, column=1)
ttk.Label(sales_frame, text="数量:").grid(row=2, column=0)


ttk.Button(sales_frame, text="添加销售", command=add_sale).grid(row=4, columnspan=2)

sales_status_label = ttk.Label(sales_frame, text="------")
sales_status_label.grid(row=5, columnspan=2)



# Inventory frame
inventory_frame = ttk.LabelFrame(root, text="库存")
inventory_frame.grid(row=0, column=1, padx=10, pady=10)

item_inventory_entry = ttk.Combobox(inventory_frame, width=15, values=list(inventory.keys()))
item_inventory_entry.bind('<KeyRelease>', auto_dropdown)
item_inventory_entry.grid(row=0, column=1)
ttk.Label(inventory_frame, text="货品:").grid(row=0, column=0)

amount_inventory_entry = ttk.Entry(inventory_frame, width=15)
amount_inventory_entry.grid(row=1, column=1)
ttk.Label(inventory_frame, text="数量:").grid(row=1, column=0)

ttk.Button(inventory_frame, text="添加库存", command=add_inventory).grid(row=2, columnspan=2)

inventory_status_label = ttk.Label(inventory_frame, text="------")
inventory_status_label.grid(row=3, columnspan=2)

# Bonus frame
bonus_frame = ttk.LabelFrame(root, text="奖金查询")
bonus_frame.grid(row=1, columnspan=2, padx=10, pady=10)

clerk_bonus_entry = ttk.Combobox(bonus_frame, width=15, values=list(clerks))
clerk_bonus_entry.bind('<KeyRelease>', auto_dropdown)
clerk_bonus_entry.grid(row=0, column=1)
ttk.Label(bonus_frame, text="店员:").grid(row=0, column=0)

rate_entry = ttk.Entry(bonus_frame, width=15)
rate_entry.grid(row=1, column=1)
ttk.Label(bonus_frame, text="提成率(%):").grid(row=1, column=0)

ttk.Button(bonus_frame, text="计算提成", command=calculate_bonus).grid(row=2, columnspan=2)

bonus_output = tk.Text(bonus_frame, height=2, width=20)
bonus_output.grid(row=3, columnspan=2)
bonus_output.config(state="disabled")



# Load data and update comboboxes after creating the GUI
load_data()
update_comboboxes()


root.mainloop()
