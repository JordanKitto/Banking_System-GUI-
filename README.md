# The Bank of Kitto

A simple Python GUI banking application that simulates a basic banking environment. The application supports account creation, login, deposit, withdrawal, and transfer functionalities.

## Features

- **Account Management:**  
  Create an account and log in using a 4-digit account number and PIN.
  
- **Banking Operations:**  
  Deposit money, withdraw funds, and transfer money between accounts—all through an intuitive GUI built with Tkinter.

- **Persistent Data:**  
  All data is stored using SQLite, ensuring that account information is maintained between sessions.

## Getting Started

### Prerequisites

- **Python 3.x:**  
  Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).

- **Tkinter:**  
  Tkinter is typically included with Python. If not, refer to your operating system’s instructions for installation.

### Installation

1. **Clone the Repository:**
   ```bash
  git clone https://github.com/JordanKitto/banking_System_GUI.git
2. cd banking_System_GUI
3. python main.py


Usage

  Login/Sign Up:
    - On the initial screen, enter a 4-digit account number and PIN.
      - If you are a new user, click Sign Up to create your account.
      - If you already have an account, click Login.
      ![image](https://github.com/user-attachments/assets/0fa3ffc9-e14d-4a05-8564-418ddb0bdc9d)


  Home Page:
  Once logged in, you can:
      - View your current balance.
      - Deposit money by entering an amount and clicking Deposit.
      - Withdraw money (if sufficient funds exist) by entering an amount and clicking Withdraw.
      - Transfer money by entering a recipient's account number and the transfer amount, then clicking Transfer.
      ![image](https://github.com/user-attachments/assets/d75bb367-4847-4541-8866-bbc064c02464)


  Logout:
      - Click Logout to exit the home page and return to the login screen.

