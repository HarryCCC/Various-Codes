import csv
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from tkinter import messagebox
import sys
import os
import pyzipper
import json
import requests
import webbrowser



# 添加获取访问令牌的函数
def get_one_drive_access_token(client_id, client_secret, redirect_uri, authorization_code):
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    token_data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'client_secret': client_secret,
    }
    token_r = requests.post(token_url, data=token_data)
    token_json = json.loads(token_r.text)
    access_token = token_json.get('access_token')
    return access_token

client_id = "3d84670c-0820-4888-b6f2-2f1ddbef05e7"
client_secret = "wN58Q~NdBtOmNcVLSQl~lSK.4~4FMAyesI552dub"
redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
'''
访问以下URL获取authorization_code：
https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?
client_id=3d84670c-0820-4888-b6f2-2f1ddbef05e7&response_type=code&
redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&
scope=files.readwrite%20offline_access
得到authorization_code
'''
def open_auth_url():
    auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=3d84670c-0820-4888-b6f2-2f1ddbef05e7&response_type=code&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&scope=files.readwrite%20offline_access"
    webbrowser.open(auth_url)



# 添加上传文件到OneDrive的函数
def upload_to_one_drive(access_token, local_file_path, one_drive_file_path):
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{one_drive_file_path}:/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        with open(local_file_path, 'rb') as f:
            response = requests.put(upload_url, headers=headers, data=f)
        if response.status_code == 201:
            return True
        else:
            print(f"Failed to upload: {response.text}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
# 添加从OneDrive下载文件的函数
'''def download_from_one_drive(access_token, one_drive_file_path, local_file_path):
    download_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{one_drive_file_path}:/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(download_url, headers=headers)
    with open(local_file_path, 'wb') as f:
        f.write(response.content)'''



# 新的函数来创建加密的zip文件
def encrypt_with_pyzipper():
    with pyzipper.AESZipFile('数据.zip',
                             'w',
                             encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(b"210215")
        zf.write("销售.csv")
        zf.write("库存.csv")

def check_password():
    entered_password = password_entry.get()
    if entered_password == "210215":  # Replace with your actual password
        password_window.destroy()
        # Initialize the main application window here
    else:
        messagebox.showerror("错误", "密码不正确")

#强制关闭
def on_closing():
    password_window.destroy()
    sys.exit(0)  # End the program

# Create a new Tkinter window for password entry
password_window = tk.Tk()
password_window.title("输入密码")

# Set the window size to be 1/4 of the screen size
screen_width = password_window.winfo_screenwidth()
screen_height = password_window.winfo_screenheight()
window_width = screen_width // 4
window_height = screen_height // 4
position_x = (screen_width - window_width) // 2
position_y = (screen_height - window_height) // 2
password_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

# Increase the font size
large_font = ('Verdana', 16)

# Create a label and entry for password
label = ttk.Label(password_window, text="密码:")
label.grid(row=0, column=0, padx=20, pady=20)
label.config(font=large_font)
password_entry = ttk.Entry(password_window, show="*")
password_entry.grid(row=0, column=1, padx=20, pady=20)
password_entry.config(font=large_font)

# 创建用于检查密码的按钮，并使用更大的字体
check_password_button = tk.Button(password_window, text="验证", command=check_password, font=large_font)
check_password_button.grid(row=1, columnspan=2, padx=20, pady=20)




# Set close window behavior
password_window.protocol("WM_DELETE_WINDOW", on_closing)
password_window.mainloop()



# Function to load data from CSV
def load_data_from_zip():
    global sales, inventory, clerks
    try:
        with pyzipper.AESZipFile('数据.zip') as zf:
            zf.setpassword(b"210215")
            zf.extractall()
        
        with open("销售.csv", mode="r") as f:
            reader = csv.reader(f)
            sales = [row for row in reader]
            clerks = set(row[1] for row in sales[1:])
        
        with open("库存.csv", mode="r") as f:
            reader = csv.reader(f)
            inventory = {rows[0]: int(rows[1]) for rows in reader}
            
        # 删除临时CSV文件
        os.remove("销售.csv")
        os.remove("库存.csv")
        
    except FileNotFoundError:
        pass
    except RuntimeError:
        print("Incorrect password for the zip file.")
    except pyzipper.EncryptionError:
        print("Incorrect password for the zip file.")



# Function to save data to CSV
def save_data_to_zip():
    global sales_sync_status_label, inventory_sync_status_label  # 声明为全局变量以便访问
    with open("销售.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(sales)
    with open("库存.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        for key, value in inventory.items():
            writer.writerow([key, value])
    # 使用新的加密函数替换旧的zip创建过程
    encrypt_with_pyzipper()
    # 删除临时CSV文件
    os.remove("销售.csv")
    os.remove("库存.csv")

    # 上传备份到 OneDrive
    try:
        local_file_path = '数据.zip'
        one_drive_file_path = '会计系统/会计数据.zip'
        upload_success = upload_to_one_drive(access_token, local_file_path, one_drive_file_path)
        
        if upload_success:
            sales_sync_status_label.config(text="数据已同步")
            inventory_sync_status_label.config(text="数据已同步")
        else:
            sales_sync_status_label.config(text="数据未同步")
            inventory_sync_status_label.config(text="数据未同步")
            
    except Exception as e:
        print(f"Error: {e}")
        sales_sync_status_label.config(text="数据未同步")
        inventory_sync_status_label.config(text="数据未同步")
        messagebox.showerror("同步失败", f"出现错误: {e}")





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

    save_data_to_zip()
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
    
    save_data_to_zip()
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

#授权模块
auth_frame = ttk.LabelFrame(root, text="授权")
auth_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

auth_code_entry = ttk.Entry(auth_frame, width=50)  # 宽度可以根据需要调整
auth_code_entry.grid(row=0, column=0, padx=20, pady=10)

get_auth_code_button = tk.Button(auth_frame, text="获取授权码", command=open_auth_url)
get_auth_code_button.grid(row=1, column=0, padx=20, pady=50)


authorization_code = auth_code_entry.get()  # 从输入框获取
access_token = get_one_drive_access_token(client_id, client_secret, redirect_uri, authorization_code)


# 获取OneDrive的访问令牌（这一步通常只需要执行一次）
access_token = get_one_drive_access_token(client_id, client_secret, redirect_uri, authorization_code)


# Load data before creating the GUI
load_data_from_zip()


# Center the window on the screen and resize it
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width // 2
window_height = screen_height // 2
position_x = int((screen_width / 2) - (window_width / 2))
position_y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")


# Sales frame
sales_frame = ttk.LabelFrame(root, text="销售")
sales_frame.grid(row=0, column=0, padx=20, pady=0, sticky="nsew")

# 店员输入
clerk_label = ttk.Label(sales_frame, text="店员:", font=large_font)
clerk_label.grid(row=0, column=0, padx=20, pady=10)
clerk_entry = ttk.Combobox(sales_frame, width=15, values=list(clerks), font=large_font)
clerk_entry.bind('<KeyRelease>', auto_dropdown)
clerk_entry.grid(row=0, column=1, padx=20, pady=10)

# 货品输入
item_label = ttk.Label(sales_frame, text="货品:", font=large_font)
item_label.grid(row=1, column=0, padx=20, pady=10)
item_sale_entry = ttk.Combobox(sales_frame, width=15, values=list(inventory.keys()), font=large_font)
item_sale_entry.bind('<KeyRelease>', auto_dropdown)
item_sale_entry.grid(row=1, column=1, padx=20, pady=10)

# 数量输入
quantity_label = ttk.Label(sales_frame, text="数量:", font=large_font)
quantity_label.grid(row=2, column=0, padx=20, pady=10)
quantity_entry = ttk.Entry(sales_frame, width=15, font=large_font)
quantity_entry.grid(row=2, column=1, padx=20, pady=10)

# 金额输入
amount_label = ttk.Label(sales_frame, text="金额:", font=large_font)
amount_label.grid(row=3, column=0, padx=20, pady=10)
amount_entry = ttk.Entry(sales_frame, width=15, font=large_font)
amount_entry.grid(row=3, column=1, padx=20, pady=10)


# Button for Adding Sale
add_sale_button = tk.Button(sales_frame, text="添加销售", command=add_sale, font=large_font)
add_sale_button.grid(row=4, columnspan=2, padx=20, pady=20)

sales_status_label = ttk.Label(sales_frame, text="------")
sales_status_label.grid(row=5, columnspan=2)

sales_sync_status_label = ttk.Label(sales_frame, text="------")
sales_sync_status_label.grid(row=6, columnspan=2)



# 在库存模块里
inventory_frame = ttk.LabelFrame(root, text="库存")
inventory_frame.grid(row=0, column=1, padx=20, pady=0, sticky="nsew")

# 货品输入
item_inventory_label = ttk.Label(inventory_frame, text="货品:", font=large_font)
item_inventory_label.grid(row=0, column=0, padx=20, pady=20)
item_inventory_entry = ttk.Combobox(inventory_frame, width=15, values=list(inventory.keys()), font=large_font)
item_inventory_entry.bind('<KeyRelease>', auto_dropdown)
item_inventory_entry.grid(row=0, column=1, padx=20, pady=20)

# 数量输入
amount_inventory_label = ttk.Label(inventory_frame, text="数量:", font=large_font)
amount_inventory_label.grid(row=1, column=0, padx=20, pady=20)
amount_inventory_entry = ttk.Entry(inventory_frame, width=15, font=large_font)
amount_inventory_entry.grid(row=1, column=1, padx=20, pady=20)

# Button for Adding Inventory
add_inventory_button = tk.Button(inventory_frame, text="添加库存", command=add_inventory, font=large_font)
add_inventory_button.grid(row=2, columnspan=2, padx=20, pady=20)

inventory_status_label = ttk.Label(inventory_frame, text="------")
inventory_status_label.grid(row=3, columnspan=2)

inventory_sync_status_label = ttk.Label(inventory_frame, text="------")
inventory_sync_status_label.grid(row=4, columnspan=2)





# Bonus frame
bonus_frame = ttk.LabelFrame(root, text="奖金查询")
bonus_frame.grid(row=1, column=0, padx=10, pady=0)

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
load_data_from_zip()
update_comboboxes()


root.mainloop()
