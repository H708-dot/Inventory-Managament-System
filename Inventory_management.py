# Importing all required modules

import mysql.connector as sql
import numpy
import csv
import pandas as pd
import matplotlib.pyplot as plt
import string
import random
import time

# Define constants for file paths
CREDENTIALS_USER_FILE = 'credentials_user.csv'
CREDENTIALS_STAFF_FILE = 'credentials_staff.csv'
STOCK_FILE = 'stock.csv'
ORDER_FILE = 'order.csv'

# Create User Defined Functions
current_user_name = None
cart = []
stock_data = pd.read_csv(STOCK_FILE)
order_data = pd.read_csv(ORDER_FILE)
staff_data = pd.read_csv(CREDENTIALS_STAFF_FILE)


def main_menu():
        print()
        print('='*50)
        print('Inventory Management System'.center(50))
        print('='*50)
        print("Welcome to IMS !")
        print()

def print_section_header(txt):
    print('-' * 50)
    width = 50
    print(f'{txt.upper():^{width}}')
    print('-' * 50)
    print()

    # For User
def create_user_account():
    print_section_header('Create Account')
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    id_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    with open(CREDENTIALS_USER_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([id_number, name, email, password])
        
    print(f'Your ID number is: {id_number}')
    print("Account created successfully!")

def user_sign_in():
    print_section_header('sign in')
    global current_user_name
    while True:
        email_or_id = input("Enter your email or ID: ")
        password = input("Enter your password: ")

        with open(CREDENTIALS_USER_FILE, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if (row[2] == email_or_id or row[0] == email_or_id) and row[3] == password:
                    current_user_name = row[1]
                    print(f"Welcome Back {current_user_name}!")
                    return

        print("Incorrect email/ID or password. Please try again.")

def view_stock():
    print_section_header('View Stock')
    global stock_data
    stock_data = pd.read_csv(STOCK_FILE)
    print(stock_data)

def add_items_to_cart():
    print_section_header('Add items to cart')
    global cart, stock_data
    choice = 'yes'

    with open(r'cart.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['item_number', 'item_name', 'item_brand', 'quantity', 'total_cost'])

        while choice.lower() == 'yes':
            item_number = input("Enter the item number to add to cart: ")
            quantity = int(input("Enter the quantity: "))
            item_info = stock_data[stock_data['item_no'] == int(item_number)]
            if item_info.empty:
                print("Item not found.")
                return
            available_quantity = item_info['quantity'].values[0]
            if quantity > available_quantity:
                print(f"Quantity entered exceeds available stock ({available_quantity} units). Please enter a valid quantity.")
                return
                
            item_name = item_info['item_name'].values[0]
            item_brand = item_info['item_brand'].values[0]
            cost = item_info['cost'].values[0]

            total_cost = cost * quantity  # Calculate total cost
            # Add item to cart if quantity is available
            cart.append([item_number, item_name, item_brand, quantity, total_cost])
            writer.writerow([item_number, item_name, item_brand, quantity, total_cost])
        

            choice = input('Do you want to add more items: (yes/no) ')

            
def check_out():
    print_section_header('Check Out')
    global stock_data
    
    # Read cart items from cart.csv using pandas
    cart_df = pd.read_csv('cart.csv')
    
    if cart_df.empty:
        print("Your cart is empty. Please add items before checking out.")
        return
    
    # Loop through items in the cart to update stock quantity
    for index, row in cart_df.iterrows():
        item_number = row['item_number']
        quantity_purchased = row['quantity']
        
        # Find the item in the stock data
        item_index = stock_data.index[stock_data['item_no'] == item_number].tolist()
        
        if item_index:
            # Update stock quantity by subtracting purchased quantity
            stock_data.at[item_index[0], 'quantity'] -= quantity_purchased
    
    # Save the updated stock data back to the CSV file
    stock_data.to_csv(STOCK_FILE, index=False)

    # Calculate the total cost of items in the cart
    total_cost = cart_df['total_cost'].sum()
    
    # Calculate tax (VAT 5%) and cost after tax
    tax_rate = 0.05
    tax = total_cost * tax_rate
    cost_after_tax = total_cost + tax
    
    # Print the cart using pandas
    print("Your Cart:")
    print(cart_df)
    
    # Print the total cost, tax, and cost after tax
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Tax (VAT 5%): ${tax:.2f}")
    print(f"Cost After Tax: ${cost_after_tax:.2f}")
    
    # Generate a unique order ID
    order_id = np.random.randint(10**5, 10**6)
    
    # Check if the generated order ID already exists
    while order_id in order_data['order_id'].values:
        order_id = np.random.randint(10**5, 10**6)  # Regenerate if ID exists
    
    # Create a string representation of the order details
    order_details = "\n".join([f"{row['item_name']} (Quantity: {row['quantity']}) - Total Cost: ${row['total_cost']:.2f}" for index, row in cart_df.iterrows()])
    
    # Add the new order to the orders DataFrame
    with open(ORDER_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([order_id, order_details, 'pending'])
        
    print(f"Order placed successfully! Your Order ID is {order_id}.")
    
    # Clear the cart by overwriting cart.csv
    with open('cart.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['item_number', 'item_name', 'item_brand', 'quantity', 'cost'])

def status_of_ordered_items():
    print_section_header('Status of ordered items')
    order_id = int(input("Enter your Order ID: "))

    with open(ORDER_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if int(row[0]) == order_id:
                print("Order ID:", row[0])
                print("Order Details:", row[1])
                print("Status:", row[2])
                return
        else:
                print("Order not found")

def view_chart_of_stock(stock_data, staff_data):
    print_section_header('View Chart and Statistics')
    plt.figure(figsize=(12, 8))

    # Calculate the total cost for each category
    category_totals = stock_data.groupby('category')['cost'].sum()

    # Create a bar chart for category totals
    plt.bar(category_totals.index, category_totals.values)
    plt.xlabel('Category')
    plt.ylabel('Total Cost')
    plt.title('Total Cost in Each Category')
    plt.xticks(rotation=45)
    plt.show()

    # Create a bar chart for staff scores
    plt.figure(figsize=(8, 6))
    plt.bar(staff_data['name'], staff_data['staff_score'])
    plt.xlabel('Staff Name')
    plt.ylabel('Staff Score')
    plt.title('Staff Score')
    plt.xticks(rotation=45)
    plt.show()

    # Generate brand vs. cost chart
    plt.figure(figsize=(12, 8))
    plt.bar(stock_data['item_brand'], stock_data['cost'])
    plt.xlabel('Item Brand')
    plt.ylabel('Average Cost')
    plt.title('Average Cost by Item Brand')
    plt.xticks(rotation=45)
    plt.show()

    # Generate item vs. cost chart
    plt.figure(figsize=(12, 8))
    plt.bar(stock_data['item_name'], stock_data['cost'])
    plt.xlabel('Item Name')
    plt.ylabel('Average Cost')
    plt.title('Average Cost by Item Name')
    plt.xticks(rotation=45)
    plt.show()

    # Display additional statistics
    most_common_brand = stock_data['item_brand'].mode().values[0]
    least_common_brand = stock_data['item_brand'].value_counts().idxmin()
    top_expensive_items = stock_data.nlargest(5, 'cost')
    top_cheap_items = stock_data.nsmallest(5, 'cost')
    highest_quantity_item = stock_data.nlargest(1, 'quantity')
    lowest_quantity_item = stock_data.nsmallest(1, 'quantity')
    avg_price = stock_data['cost'].mean()
    mode_price = stock_data['cost'].mode().values[0]
    median_price = stock_data['cost'].median()
    price_variance = stock_data['cost'].var()
    price_std_dev = stock_data['cost'].std()

    print("Additional Statistics:")
    print(f"Most Common Brand: {most_common_brand}")
    print(f"Least Common Brand: {least_common_brand}")
    print("Top 5 Most Expensive Items:")
    print(top_expensive_items[['item_name', 'cost']])
    print("Top 5 Least Expensive Items:")
    print(top_cheap_items[['item_name', 'cost']])
    print("Highest Quantity Item:")
    print(highest_quantity_item[['item_name', 'quantity']])
    print("Lowest Quantity Item:")
    print(lowest_quantity_item[['item_name', 'quantity']])
    print(f"Average Price: {avg_price:.2f}")
    print(f"Mode Price: {mode_price:.2f}")
    print(f"Median Price: {median_price:.2f}")
    print(f"Price Variance: {price_variance:.2f}")
    print(f"Price Standard Deviation: {price_std_dev:.2f}")
    print("Quartiles:")
    print(f"- Q1 (lower half price median): {stock_data['cost'].quantile(0.25):.2f}")
    print(f"- Q2 (median): {stock_data['cost'].quantile(0.50):.2f}")
    print(f"- Q3 (upper half price median): {stock_data['cost'].quantile(0.75):.2f}")
    print(f"Interquartile Range (IQR): {stock_data['cost'].quantile(0.75) - stock_data['cost'].quantile(0.25):.2f}")

def collect_review():
    print_section_header('User review')
    global current_user_name
    if current_user_name:
        review = input("Enter your review: ")

        with open('reviews.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([current_user_name, review])

        print("Thank you for your review!")
    else:
        print("No user signed in. Cannot collect review.")

def user_sign_out():
    print("Signing out...")
    time.sleep(1)
    global current_user_name
    current_user_name = None
    print("Signed out successfully.")

    # For Staff
def staff_login():
    print_section_header('Staff login')
    max_attempts = 3
    while max_attempts > 0:
        staff_id = input("Enter staff ID: ")
        password = input("Enter staff password: ")
        
        with open('credentials_staff.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if staff_id == row[1] and password == row[2]:
                    print(f"Welcome staff member: {row[0]}")
                    return True  # Return True if login is successful
        
        max_attempts -= 1
        if max_attempts > 0:
            print(f"Invalid credentials. You have {max_attempts} attempts left.")
    
    print("Access denied.")
    return False  # Return False if login is unsuccessful

def add_new_item(stock_data):
    print_section_header('Add new item')
    item_no = int(input("Enter item number: "))
    item_name = input("Enter item name: ")
    item_brand = input("Enter item brand: ")
    cost = float(input("Enter cost: "))
    category = input("Enter category: ")
    status = input("Enter status: ")
    quantity = int(input("Enter quantity: "))
    
    new_item = {
        'item_no': item_no,
        'item_name': item_name,
        'item_brand': item_brand,
        'cost': cost,
        'category': category,
        'status': status,
        'quantity': quantity
    }
    
    # Append the new item to the DataFrame
    stock_data = pd.concat([stock_data, pd.DataFrame([new_item])], ignore_index=True)
    stock_data.to_csv(STOCK_FILE, index=False)
    
    print("Item added successfully!")

def add_item_status():
    print_section_header('Add item status')
    item_no = input("Enter item number to update status: ")
    status = input("Enter status: ")

    # Read the existing data
    with open(STOCK_FILE, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Update the status for the item with the specified item number
    updated_rows = []
    found = False
    for row in rows:
        if row['item_no'] == item_no:
            row['status'] = status
            found = True
        updated_rows.append(row)

    # Write the updated data back to the CSV file
    with open(STOCK_FILE, 'w', newline='') as csvfile:
        fieldnames = ['item_no', 'item_name', 'item_brand', 'cost', 'category', 'status', 'quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    if found:
        print("Status updated successfully!")
    else:
        print("Item not found.")

def search_for_item(stock_data):
    print_section_header('Search item')
    item_name = input("Enter item name to search: ")
    
    # Convert the 'item_name' and 'item_brand' columns to string type
    stock_data['item_name'] = stock_data['item_name'].astype(str)
    stock_data['item_brand'] = stock_data['item_brand'].astype(str)
    
    search_result = stock_data[stock_data['item_name'].str.contains(item_name, case=False) | stock_data['item_brand'].str.contains(item_name, case=False)]
    
    if not search_result.empty:
        print("Search Results:")
        print(search_result)
    else:
        print("Item not found.")

def remove_item(stock_data):
    print_section_header('Remove item')
    item_no = int(input("Enter item number to remove: "))
    
    stock_data = stock_data[stock_data['item_no'] != item_no]
    stock_data.to_csv('stock.csv', index=False)
    
    print("Item removed successfully!")

def show_all_items(stock_data):
    print_section_header('Show all items')
    print("All Items:")
    stock_data = pd.read_csv(STOCK_FILE)
    print(stock_data)

def show_all_item_status(stock_data):
    print_section_header('Show all item statuses')
    print("All Item Status:")
    stock_data = pd.read_csv(STOCK_FILE)
    print(stock_data[['item_no', 'item_name', 'item_brand', 'status']])

def add_new_staff(staff_data):
    print_section_header('Add new staff')
    name = input("Enter staff name: ")
    staff_id = input("Enter staff ID: ")
    password = input("Enter password: ")
    phone_number = input("Enter phone number: ")
    staff_score = int(input("Enter staff score: "))
    
    new_staff = {'name': name, 'staff_id': staff_id, 'password': password, 'phone_number': phone_number, 'staff_score': staff_score}
    staff_data = staff_data._append(new_staff, ignore_index=True)
    staff_data.to_csv('credentials_staff.csv', index=False)
    
    print("New staff added successfully!")

def search_for_staff(staff_data):
    print_section_header('Search staff details')
    staff_name = input("Enter staff name to search: ")
    staff_data['name'] = staff_data['name'].astype(str)
    search_result = staff_data[staff_data['name'].str.contains(staff_name, case=False)]
    
    if not search_result.empty:
        print("Search Results:")
        print(search_result)
    else:
        print("Staff member not found.")

def remove_staff(staff_data):
    print_section_header('Remove staff')
    staff_id = input("Enter staff ID to remove: ")
    
    staff_data = staff_data[staff_data['staff_id'] != staff_id]
    staff_data.to_csv('credentials_staff.csv', index=False)
    
    print("Staff member removed successfully!")

def show_staff_details(staff_data):
    print_section_header('Show staff details')
    print("Staff Details:")
    print(staff_data)

def sql_connectivity_backup():
    print_section_header('BACKUP DATABASE')
    print("Backing up data...")
    time.sleep(1.5)
    
    object = sql.connect(host = 'localhost', user = 'root', password = 'Ihs@10987864')
    pointer = object.cursor()
    pointer.execute("CREATE database if not exists Inventory_Management_System")
    pointer.execute("Use Inventory_Management_System")
    
    #Creating Empty Tables
    pointer.execute("""CREATE TABLE IF NOT EXISTS credentials_user (
                    id_number CHAR(10) PRIMARY KEY,
                    name VARCHAR(20),
                    email VARCHAR(50),
                    password VARCHAR(25)
                    )""")
    pointer.execute("""CREATE TABLE IF NOT EXISTS credentials_staff (
                    name VARCHAR(20),
                    staff_id INT PRIMARY KEY,
                    password VARCHAR(15),
                    phone_number BIGINT,
                    staff_score INT
                    )""")
    pointer.execute("""CREATE TABLE IF NOT EXISTS stock (
                    item_no INT PRIMARY KEY,
                    item_name VARCHAR(255),
                    item_brand VARCHAR(255),
                    cost INT,
                    category VARCHAR(30),
                    status VARCHAR(50),
                    quantity INT
                    )""")
    pointer.execute("""CREATE TABLE IF NOT EXISTS order1 (
                    order_id INT PRIMARY KEY,
                    order_details VARCHAR(255),
                    status VARCHAR(30)
                    )""")
    
    #Inserting values from csv file
    CREDENTIALS_USER_FILE = csv.reader(open('credentials_user.csv'))
    next(CREDENTIALS_USER_FILE)
    for row in CREDENTIALS_USER_FILE:
        query = ("INSERT INTO credentials_user(id_number, name, email, password) "
                 "VALUES(%s, %s, %s, %s) "
                 "ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email), password = VALUES(password)"
                 )
        pointer.execute(query, row)
        object.commit()

    CREDENTIALS_STAFF_FILE = csv.reader(open('credentials_staff.csv'))
    next(CREDENTIALS_STAFF_FILE)
    for row in CREDENTIALS_STAFF_FILE:
        query = ("INSERT INTO credentials_staff(name, staff_id, password, phone_number, staff_score) "
                 "VALUES(%s, %s, %s, %s, %s) "
                 "ON DUPLICATE KEY UPDATE name = VALUES(name), staff_id = VALUES(staff_id), password = VALUES(password),\
                 phone_number = VALUES(phone_number), staff_score = VALUES(staff_score)"
                 )
        pointer.execute(query,row)
        object.commit()

    STOCK_FILE = csv.reader(open('stock.csv'))
    next(STOCK_FILE)
    for row in STOCK_FILE:
        query = ("INSERT INTO stock(item_no, item_name, item_brand, cost, category, status, quantity) "
                 "VALUES(%s, %s, %s, %s, %s, %s, %s) "
                 "ON DUPLICATE KEY UPDATE item_no = VALUES(item_no), item_name = VALUES(item_name), item_brand = VALUES(item_brand),\
                 cost = VALUES(cost), category = VALUES(category), status = VALUES(status), quantity = VALUES(quantity)"
                 )
        pointer.execute(query,row)
        object.commit()

    ORDER_FILE = csv.reader(open('order.csv'))
    next(ORDER_FILE)
    for row in ORDER_FILE:
        query = ("INSERT INTO order1(order_id, order_details, status) "
                 "VALUES(%s, %s, %s) "
                 "ON DUPLICATE KEY UPDATE order_id = VALUES(order_id), order_details = VALUES(order_details), status = VALUES(status)"
                 )
        pointer.execute(query,row)
        object.commit()

    #Extracting data from database
    pointer.execute("Select * from credentials_user")
    print("User Credentials")
    a = pointer.fetchall()
    for i in a:
        print(i)
    print('\n')

    pointer.execute("Select * from credentials_staff")
    print("Staff Credentials")
    b = pointer.fetchall()
    for i in b:
        print(i)
    print('\n')

    pointer.execute("Select * from stock")
    print("Stock details")
    c = pointer.fetchall()
    for i in c:
        print(i)
    print('\n')
          
    pointer.execute("Select * from order1")
    print("Order details")
    d = pointer.fetchall()
    for i in d:
        print(i)
    print('\n')

    print("All data has been backed-up to your mysql database 'Inventory_Management_System'.")


def staff_functionality():
    global staff_data, stock_data
    while True:
        print("\nStaff Menu:")
        print("Press 1 - Add new item")
        print("Press 2 - Add item status")
        print("Press 3 - Search for an item")
        print("Press 4 - Remove an item")
        print("Press 5 - Show all items")
        print("Press 6 - Show all item statuses")
        print("Press 7 - Add new staff")
        print("Press 8 - Search for staff")
        print("Press 9 - Remove staff")
        print("Press 10 - Show details of staff")
        print("Press 11 - To view chart")
        print("Press 12 - To backup the database")
        print("Press 13 - To exit")
        
        staff_option = input("Enter option number: ")
        
        if staff_option == '1':
            add_new_item(stock_data)
        elif staff_option == '2':
            add_item_status()
        elif staff_option == '3':
            search_for_item(stock_data)
        elif staff_option == '4':
            remove_item(stock_data)
        elif staff_option == '5':
            show_all_items(stock_data)
        elif staff_option == '6':
            show_all_item_status(stock_data)
        elif staff_option == '7':
            add_new_staff(staff_data)
        elif staff_option == '8':
            search_for_staff(staff_data)
        elif staff_option == '9':
            remove_staff(staff_data)
        elif staff_option == '10':
            show_staff_details(staff_data)
        elif staff_option == '11':
            view_chart_of_stock(stock_data, staff_data)
        elif staff_option == '12':
            sql_connectivity_backup()
        elif staff_option == '13':
            print("Exiting staff functionality...")
            break
        else:
            print("Invalid staff option.")

# Main Code
main_menu()
user_type = input("Are you a user or staff? ").lower()

if user_type == 'user':
    print('''Choice:
          1. Create Account
          2. Sign In''')
    user_choice = input("Enter choice as (1/2) ")
    
    if user_choice == '1':
        create_user_account()
        user_sign_in()
    elif user_choice == '2':
        user_sign_in()
    else:
        print("Invalid choice.")
    
    # After successful sign-in, show the menu
    while True:
        print("\nMenu:")
        print("1. View Stock")
        print("2. Add Items to Cart")
        print("3. Check Out")
        print("4. Status of Ordered Items")
        print("5. View Chart of Stock")
        print("6. Exit")
        
        option = input("Enter option number: ")
        
        if option == '1':
            view_stock()
        elif option == '2':
            add_items_to_cart()
        elif option == '3':
            check_out()
        elif option == '4':
            status_of_ordered_items()
        elif option == '5':
            view_chart_of_stock(stock_data, staff_data)
        elif option == '6':
            collect_review()
            user_sign_out()
            cart = []
            print("Exiting...")
            break
        else:
            print("Invalid option.")

elif user_type == 'staff':
    staff_logged_in = staff_login()
    
    if staff_logged_in:
        staff_data = pd.read_csv(CREDENTIALS_STAFF_FILE)
        staff_functionality()
else:
    print("Invalid user type.")