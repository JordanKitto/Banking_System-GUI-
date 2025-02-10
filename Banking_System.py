# Import necessary libraries for GUI and database operations
from tkinter import *
from tkinter import messagebox
import sqlite3

# DatabaseManager class to handle all database-related operations
class DatabaseManager:
    def __init__(self, database_name='Account_Information.db'):
        # Initialize the database connection and create the account table if it doesn't exist
        self.con = sqlite3.connect(database_name)
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        # Creates the account table if it does not already exist
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS accountlog (
                accnum INTEGER PRIMARY KEY, 
                pin INTEGER, 
                balance INTEGER DEFAULT 0
            )
        ''')
        self.con.commit()
        
    def _check_account_exists(self, account_number):
        # Checks if an account already exists in the database
        try:
            self.cur.execute('SELECT * FROM accountlog WHERE accnum = ?', (account_number,))
            return self.cur.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Error checking account existence: {e}")
            return False

    def add_user(self, account, pin):
        # Adds a new user to the database if the account number is not already taken
        try:
            if self._check_account_exists(account):
                return False  # Account already exists
            self.cur.execute('INSERT INTO accountlog (accnum, pin) VALUES (?, ?)', (account, pin))
            self.con.commit()
            return True  # Account successfully created
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            self.con.rollback()
            return False
        
    def get_balance(self, account_number):
        # Retrieves the current balance for the given account number
        try:
            self.cur.execute('SELECT balance FROM accountlog WHERE accnum = ?', (account_number,))
            result = self.cur.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error retrieving balance: {e}")
            return None
        
    def update_balance(self, account_number, amount):
        # Updates the account balance by adding the specified amount (positive for deposit, negative for withdrawal)
        try:
            self.cur.execute('UPDATE accountlog SET balance = balance + ? WHERE accnum = ?', (amount, account_number))
            self.con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating balance: {e}")
            self.con.rollback()
            return False

    def transfer_money(self, sender_acc, receiver_acc, amount):
        # Transfers money from the sender's account to the receiver's account
        try:
            # Check that the sender has enough funds
            sender_balance = self.get_balance(sender_acc)
            if sender_balance is None or sender_balance < amount:
                return False
            # Check that the receiver account exists
            self.cur.execute('SELECT * FROM accountlog WHERE accnum = ?', (receiver_acc,))
            if self.cur.fetchone() is None:
                return False
            # Perform the transfer by updating both balances
            self.update_balance(sender_acc, -amount)
            self.update_balance(receiver_acc, amount)
            return True
        except sqlite3.Error as e:
            print(f"Error during transfer: {e}")
            self.con.rollback()
            return False
        
    def validate_login(self, account, pin):
        # Validates login credentials against the database
        try:
            self.cur.execute('SELECT * FROM accountlog WHERE accnum = ? AND pin = ?', (account, pin))
            return self.cur.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Login validation error: {e}")
            return False
        
    def close_connection(self):
        # Closes the database connection
        try:
            self.con.close()
        except sqlite3.Error as e:
            print(f"Error closing connection: {e}")

# Class to store user session state
class AccountState:
    def __init__(self):
        self.account_number = None

    def logged_in(self, account_number):
        # Store the account number when the user logs in
        self.account_number = account_number

    def logout(self):
        # Clear the account state when the user logs out
        self.account_number = None

    def get_account_number(self):
        # Return the logged-in account number
        return self.account_number

# Main Banking Application Class for the Login/Sign-Up interface
class BankingApplication:
    def __init__(self):
        # Initialize the main application window and its components
        self.root = Tk()
        self.root.title("The Bank of Kitto")
        self.root.configure(bg="#e0f7fa")
        self.db_manager = DatabaseManager()  # Initialize the database
        self.account_state = AccountState()  # Track the logged-in account state
        self.setup_interface()

    def setup_interface(self):
        # Create and arrange the login/sign-up widgets in a frame
        frame = Frame(self.root, bg="#e0f7fa")
        frame.grid(padx=20, pady=20)

        Label(frame, text="Login / Sign Up", font=("Helvetica", 15, "bold"), bg="#e0f7fa")\
            .grid(row=0, column=0, columnspan=2, pady=10)

        Label(frame, text="Account Number:", font=("Helvetica", 12), bg="#e0f7fa")\
            .grid(row=1, column=0, sticky=E, pady=5, padx=5)
        self.account_entry = Entry(frame, font=("Helvetica", 12))
        self.account_entry.grid(row=1, column=1, sticky=W, pady=5, padx=5)

        Label(frame, text="PIN:", font=("Helvetica", 12), bg="#e0f7fa")\
            .grid(row=2, column=0, sticky=E, pady=5, padx=5)
        self.pin_entry = Entry(frame, show="*", font=("Helvetica", 12))
        self.pin_entry.grid(row=2, column=1, sticky=W, pady=5, padx=5)

        Button(frame, text="Login", command=self.login, width=12, font=("Helvetica", 12))\
            .grid(row=3, column=0, pady=10, padx=5)
        Button(frame, text="Sign Up", command=self.sign_up, width=12, font=("Helvetica", 12))\
            .grid(row=3, column=1, pady=10, padx=5)
        Button(frame, text="Exit", command=self.exit_application, width=25, font=("Helvetica", 12))\
            .grid(row=4, column=0, columnspan=2, pady=5)
    
    def login(self):
        # Handles the login process by validating input and checking credentials in the database
        account = self.account_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if not account or not pin:
            messagebox.showerror("Missing Information", "Please enter both Account Number and PIN.")
            return

        if not (account.isdigit() and pin.isdigit()):
            messagebox.showerror("Error", "Digits only for Account Number and PIN.")
            return

        if len(account) != 4 or len(pin) != 4:
            messagebox.showerror("Error", "Account Number and PIN require 4 digits.")
            return

        account_int = int(account)
        pin_int = int(pin)

        if self.db_manager.validate_login(account_int, pin_int):
            self.account_state.logged_in(account_int)
            HomePage(self.root, self.account_state, self.db_manager)  # Open the home page window
            self.root.withdraw()  # Hide the login window
        else:
            messagebox.showerror("Failure", "Invalid Account Number or PIN.")
    
    def sign_up(self):
        # Handles the account creation process
        account = self.account_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if not account or not pin:
            messagebox.showerror("Missing Information", "Please enter both Account Number and PIN.")
            return

        if not (account.isdigit() and pin.isdigit()):
            messagebox.showerror("Error", "Digits only for Account Number and PIN.")
            return

        if len(account) != 4 or len(pin) != 4:
            messagebox.showerror("Error", "Account Number and PIN require 4 digits.")
            return

        account_number = int(account)
        pin_number = int(pin)

        if self.db_manager.add_user(account_number, pin_number):
            messagebox.showinfo("Account Created", f"Account '{account_number}' has been successfully created.")
        else:
            messagebox.showerror("Account Exists", "Account already exists, please login or try a different account number.")
    
    def exit_application(self):
        # Closes the application and the database connection
        self.db_manager.close_connection()
        self.root.destroy()
    
    def run(self):
        # Run the main application loop
        self.root.mainloop()

# HomePage class for logged-in users with full functionality displayed in the GUI
class HomePage:
    def __init__(self, master, account_state, db_manager):
        self.master = master
        self.db_manager = db_manager
        self.account_state = account_state
        self.home_window = Toplevel(master)
        self.home_window.title("Home Page")
        self.home_window.configure(bg="#f1f8e9")
        self.home_window.geometry("500x450")

        # Main frame for the home page contents
        self.frame = Frame(self.home_window, bg="#f1f8e9")
        self.frame.pack(padx=20, pady=20, fill=BOTH, expand=True)

        account_number = self.account_state.get_account_number()
        Label(self.frame, text=f"Account Number: {account_number}", font=("Helvetica", 14, "bold"), fg='Green', bg="#f1f8e9")\
            .grid(row=0, column=0, columnspan=3, pady=10)

        # Balance display label (updated after each operation)
        self.balance_label = Label(self.frame, text="", font=("Helvetica", 12), bg="#f1f8e9")
        self.balance_label.grid(row=1, column=0, columnspan=3, pady=5)
        self.update_balance_label()

        # Deposit Section
        Label(self.frame, text="Deposit Amount:", font=("Helvetica", 12), bg="#f1f8e9")\
            .grid(row=2, column=0, sticky=E, pady=5, padx=5)
        self.deposit_entry = Entry(self.frame, font=("Helvetica", 12))
        self.deposit_entry.grid(row=2, column=1, pady=5, padx=5)
        Button(self.frame, text="Deposit", command=self.deposit_money, width=10, font=("Helvetica", 12))\
            .grid(row=2, column=2, padx=5, pady=5)

        # Withdraw Section
        Label(self.frame, text="Withdraw Amount:", font=("Helvetica", 12), bg="#f1f8e9")\
            .grid(row=3, column=0, sticky=E, pady=5, padx=5)
        self.withdraw_entry = Entry(self.frame, font=("Helvetica", 12))
        self.withdraw_entry.grid(row=3, column=1, pady=5, padx=5)
        Button(self.frame, text="Withdraw", command=self.withdraw_money, width=10, font=("Helvetica", 12))\
            .grid(row=3, column=2, padx=5, pady=5)

        # Transfer Section
        Label(self.frame, text="Recipient Account:", font=("Helvetica", 12), bg="#f1f8e9")\
            .grid(row=4, column=0, sticky=E, pady=5, padx=5)
        self.transfer_account_entry = Entry(self.frame, font=("Helvetica", 12))
        self.transfer_account_entry.grid(row=4, column=1, pady=5, padx=5)

        Label(self.frame, text="Transfer Amount:", font=("Helvetica", 12), bg="#f1f8e9")\
            .grid(row=5, column=0, sticky=E, pady=5, padx=5)
        self.transfer_amount_entry = Entry(self.frame, font=("Helvetica", 12))
        self.transfer_amount_entry.grid(row=5, column=1, pady=5, padx=5)
        Button(self.frame, text="Transfer", command=self.transfer_money, width=10, font=("Helvetica", 12))\
            .grid(row=4, column=2, rowspan=2, padx=5, pady=5)

        # Logout Button
        Button(self.frame, text="Logout", command=self.logout, width=25, font=("Helvetica", 12))\
            .grid(row=6, column=0, columnspan=3, pady=15)

        # Status Label for showing feedback messages
        self.status_label = Label(self.frame, text="", font=("Helvetica", 12), fg="red", bg="#f1f8e9")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def update_balance_label(self):
        # Update the balance label by retrieving the current balance from the database
        account_number = self.account_state.get_account_number()
        balance = self.db_manager.get_balance(account_number)
        if balance is not None:
            self.balance_label.config(text=f"Current Balance: ${balance}")
        else:
            self.balance_label.config(text="Current Balance: Error retrieving balance")

    def deposit_money(self):
        # Perform a deposit operation using the amount entered in the GUI
        amount_str = self.deposit_entry.get().strip()
        if not amount_str.isdigit():
            self.status_label.config(text="Deposit amount must be a positive number.", fg="red")
            return
        amount = int(amount_str)
        if amount <= 0:
            self.status_label.config(text="Deposit amount must be greater than zero.", fg="red")
            return
        account_number = self.account_state.get_account_number()
        if self.db_manager.update_balance(account_number, amount):
            self.status_label.config(text="Deposit successful.", fg="green")
            self.deposit_entry.delete(0, END)
            self.update_balance_label()
        else:
            self.status_label.config(text="Deposit failed.", fg="red")

    def withdraw_money(self):
        # Perform a withdrawal operation using the amount entered in the GUI
        amount_str = self.withdraw_entry.get().strip()
        if not amount_str.isdigit():
            self.status_label.config(text="Withdrawal amount must be a positive number.", fg="red")
            return
        amount = int(amount_str)
        if amount <= 0:
            self.status_label.config(text="Withdrawal amount must be greater than zero.", fg="red")
            return
        account_number = self.account_state.get_account_number()
        current_balance = self.db_manager.get_balance(account_number)
        if current_balance is None or amount > current_balance:
            self.status_label.config(text="Insufficient funds for withdrawal.", fg="red")
            return
        if self.db_manager.update_balance(account_number, -amount):
            self.status_label.config(text="Withdrawal successful.", fg="green")
            self.withdraw_entry.delete(0, END)
            self.update_balance_label()
        else:
            self.status_label.config(text="Withdrawal failed.", fg="red")

    def transfer_money(self):
        # Perform a transfer operation using the recipient and amount entered in the GUI
        recipient_str = self.transfer_account_entry.get().strip()
        amount_str = self.transfer_amount_entry.get().strip()
        if not (recipient_str.isdigit() and amount_str.isdigit()):
            self.status_label.config(text="Recipient and amount must be digits.", fg="red")
            return
        recipient = int(recipient_str)
        amount = int(amount_str)
        if amount <= 0:
            self.status_label.config(text="Transfer amount must be greater than zero.", fg="red")
            return
        sender_account = self.account_state.get_account_number()
        current_balance = self.db_manager.get_balance(sender_account)
        if current_balance is None or amount > current_balance:
            self.status_label.config(text="Insufficient funds for transfer.", fg="red")
            return
        if self.db_manager.transfer_money(sender_account, recipient, amount):
            self.status_label.config(text="Transfer successful.", fg="green")
            self.transfer_account_entry.delete(0, END)
            self.transfer_amount_entry.delete(0, END)
            self.update_balance_label()
        else:
            self.status_label.config(text="Transfer failed: recipient not found or error occurred.", fg="red")

    def logout(self):
        # Logs out the user and returns to the main login window
        self.account_state.logout()
        self.home_window.destroy()
        self.master.deiconify()

if __name__ == "__main__":
    app = BankingApplication()
    app.run()
