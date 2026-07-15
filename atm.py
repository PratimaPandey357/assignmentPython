# Smart ATM Simulator

balance = 1000
pin = "1234"

attempts = 0
authenticated = False

# Authentication
while attempts < 3:
    entered_pin = input("Enter your 4-digit PIN: ")

    if entered_pin == pin:
        print("Access granted!\n")
        authenticated = True
        break
    else:
        attempts += 1
        print("Incorrect PIN.")

        if attempts < 3:
            print(f"You have {3 - attempts} attempt(s) remaining.\n")

if not authenticated:
    print("Too many incorrect attempts. Your account has been locked.")
else:
    # ATM Menu
    while True:
        print("\n===== SMART ATM MENU =====")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Exit")

        choice = input("Choose an option (1-4): ")

        if choice == "1":
            print(f"Your current balance is: Rs. {balance}")

        elif choice == "2":
            amount = float(input("Enter amount to deposit: Rs. "))

            if amount > 0:
                balance += amount
                print(f"Deposit successful!")
                print(f"New balance: Rs. {balance}")
            else:
                print("Please enter a valid amount.")

        elif choice == "3":
            amount = float(input("Enter amount to withdraw: Rs. "))

            if amount <= 0:
                print("Please enter a valid amount.")
            elif amount > balance:
                print("Insufficient balance. Withdrawal denied.")
            else:
                balance -= amount
                print(f"Withdrawal successful!")
                print(f"Remaining balance: Rs. {balance}")

        elif choice == "4":
            print("Thank you for using the Smart ATM. Goodbye!")
            break

        else:
            print("Invalid option. Please choose between 1 and 4.")