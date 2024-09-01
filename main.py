import sqlite3
import hashlib

# Connect to the database or create it
conn = sqlite3.connect('banking_app.db')
cursor = conn.cursor()

# Create tables if they do not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Admin (
        userID TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customer (
        userID TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        fullName TEXT NOT NULL,
        dateOfBirth TEXT NOT NULL,
        balance REAL DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userID TEXT,
        transactionType TEXT,
        amount REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Function to hash a password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to perform deposit
def deposit(user_id, amount):
    try:
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
        cursor.execute("UPDATE Customer SET balance = balance + ? WHERE userID = ?", (amount, user_id))
        conn.commit()
        cursor.execute("INSERT INTO Transactions (userID, transactionType, amount) VALUES (?, 'Deposit', ?)",
                       (user_id, amount))
        conn.commit()
        print(f"Deposited {amount} to account {user_id}.")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

# Function to perform withdrawal
def withdraw(user_id, amount):
    try:
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
        cursor.execute("SELECT balance FROM Customer WHERE userID = ?", (user_id,))
        current_balance = cursor.fetchone()[0]
        if current_balance >= amount:
            cursor.execute("UPDATE Customer SET balance = balance - ? WHERE userID = ?", (amount, user_id))
            conn.commit()
            cursor.execute("INSERT INTO Transactions (userID, transactionType, amount) VALUES (?, 'Withdrawal', ?)",
                           (user_id, amount))
            conn.commit()
            print(f"Withdrew {amount} from account {user_id}.")
        else:
            print("Insufficient funds.")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

# Function to perform transfer
def transfer(from_user_id, to_user_id, amount):
    try:
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
        cursor.execute("SELECT balance FROM Customer WHERE userID = ?", (from_user_id,))
        from_balance = cursor.fetchone()[0]
        if from_balance >= amount:
            cursor.execute("UPDATE Customer SET balance = balance - ? WHERE userID = ?", (amount, from_user_id))
            cursor.execute("UPDATE Customer SET balance = balance + ? WHERE userID = ?", (amount, to_user_id))
            conn.commit()
            cursor.execute("INSERT INTO Transactions (userID, transactionType, amount) VALUES (?, 'Transfer Out', ?)",
                           (from_user_id, amount))
            cursor.execute("INSERT INTO Transactions (userID, transactionType, amount) VALUES (?, 'Transfer In', ?)",
                           (to_user_id, amount))
            conn.commit()
            print(f"Transferred {amount} from account {from_user_id} to {to_user_id}.")
        else:
            print("Insufficient funds for transfer.")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

# Function to check customer balance
def check_balance(user_id):
    try:
        cursor.execute("SELECT balance FROM Customer WHERE userID = ?", (user_id,))
        balance = cursor.fetchone()
        if balance:
            print(f"Current balance for {user_id} is {balance[0]}.")
            return balance[0]
        else:
            print("User not found.")
            return None
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return None

# Function to check admin credentials
def admin_login():
    user_id = input("Enter Admin UserID: ")
    password = input("Enter Admin Password: ")
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("SELECT * FROM Admin WHERE userID = ? AND password = ?", (user_id, hashed_password))
        result = cursor.fetchone()
        
        if result:
            print("Admin login successful.")
            admin_actions()
        else:
            print("Invalid admin credentials.")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

# Admin actions
def admin_actions():
    while True:
        print("\nAdmin Menu")
        print("1. Deposit to Customer Account")
        print("2. Withdraw from Customer Account")
        print("3. Transfer Between Customer Accounts")
        print("4. Check Customer Balance")
        print("5. View Customer Transaction History")
        print("6. Reset Customer Password")
        print("7. Exit")
        choice = input("Select an option: ")
        
        if choice == '1':
            user_id = input("Enter customer UserID: ")
            try:
                amount = float(input("Enter amount to deposit: "))
                deposit(user_id, amount)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        elif choice == '2':
            user_id = input("Enter customer UserID: ")
            try:
                amount = float(input("Enter amount to withdraw: "))
                withdraw(user_id, amount)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        elif choice == '3':
            from_user_id = input("Enter source UserID: ")
            to_user_id = input("Enter destination UserID: ")
            try:
                amount = float(input("Enter amount to transfer: "))
                transfer(from_user_id, to_user_id, amount)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        elif choice == '4':
            user_id = input("Enter customer UserID: ")
            check_balance(user_id)
        elif choice == '5':
            user_id = input("Enter customer UserID to view transaction history: ")
            view_transaction_history(user_id)
        elif choice == '6':
            user_id = input("Enter customer UserID to reset password: ")
            reset_password(user_id)
        elif choice == '7':
            break
        else:
            print("Invalid option. Please choose again.")

# Function to handle customer login or registration
def customer_login_or_register():
    has_account = input("Do you already have an account? (yes/no): ").lower()
    
    if has_account == 'yes':
        user_id = input("Enter your UserID: ")
        password = input("Enter your Password: ")
        hashed_password = hash_password(password)
        
        try:
            cursor.execute("SELECT * FROM Customer WHERE userID = ? AND password = ?", (user_id, hashed_password))
            result = cursor.fetchone()
            
            if result:
                full_name = result[2]
                balance = check_balance(user_id)
                print(f"Welcome back, {full_name}! Your current balance is {balance}.")
                customer_actions(user_id)
            else:
                print("Invalid credentials.")
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
            
    elif has_account == 'no':
        user_id = input("Choose a UserID: ")
        password = input("Choose a Password: ")
        hashed_password = hash_password(password)
        full_name = input("Enter your Full Name: ")
        dob = input("Enter your Date of Birth (YYYY-MM-DD): ")
        
        try:
            cursor.execute("INSERT INTO Customer (userID, password, fullName, dateOfBirth) VALUES (?, ?, ?, ?)",
                           (user_id, hashed_password, full_name, dob))
            conn.commit()
            print("Account created successfully!")
        except sqlite3.IntegrityError:
            print("UserID already exists. Please choose a different UserID.")
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
            
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")

# Customer actions
def customer_actions(user_id):
    while True:
        print("\nCustomer Menu")
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("3. Transfer Money")
        print("4. View Transaction History")
        print("5. Reset Password")
        print("6. Exit")
        choice = input("Select an option: ")
        
        if choice == '1':
            try:
                amount = float(input("Enter amount to deposit: "))
                deposit(user_id, amount)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        elif choice == '2':
            try:
                amount = float(input("Enter amount to withdraw: "))
                withdraw(user_id, amount)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        elif choice == '3':
            to_user_id = input("Enter the UserID to transfer to: ")
            try:
                amount = float(input("Enter amount to transfer: "))
                transfer(user_id, to_user_id, amount)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        elif choice == '4':
            view_transaction_history(user_id)
        elif choice == '5':
            reset_password(user_id)
        elif choice == '6':
            break
        else:
            print("Invalid option. Please choose again.")

# Function to view transaction history
def view_transaction_history(user_id):
    try:
        cursor.execute("SELECT transactionType, amount, timestamp FROM Transactions WHERE userID = ? ORDER BY timestamp DESC", (user_id,))
        transactions = cursor.fetchall()
        if transactions:
            print(f"\nTransaction History for {user_id}:")
            for transaction in transactions:
                print(f"{transaction[0]} of {transaction[1]} on {transaction[2]}")
        else:
            print("No transaction history found.")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

# Function to reset password
def reset_password(user_id):
    new_password = input("Enter your new password: ")
    hashed_password = hash_password(new_password)
    
    try:
        cursor.execute("UPDATE Customer SET password = ? WHERE userID = ?", (hashed_password, user_id))
        conn.commit()
        print("Password reset successfully.")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

# Main function to run the banking app
def main():
    print("Welcome to the Banking App")
    
    while True:
        role = input("Are you a 'customer' or 'admin'? Type 'exit' to quit: ").lower()
        
        if role == 'admin':
            admin_login()
        elif role == 'customer':
            customer_login_or_register()
        elif role == 'exit':
            break
        else:
            print("Invalid role. Please enter 'customer' or 'admin'.")

if __name__ == "__main__":
    main()

# Close the database connection when done
conn.close()


