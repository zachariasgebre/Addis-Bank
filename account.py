class Account:
    def __init__(self, owner: str, account_number: str, initial_balance: float):
        self.owner = owner
        self.account_number = account_number
        
        # 1. Define a private __balance (Encapsulation)
        if initial_balance >= 0:
            self.__balance = float(initial_balance)
        else:
            print("Warning: Initial balance cannot be negative. Setting balance to 0.0")
            self.__balance = 0.0

    # 2. Add a @property to read the balance (No direct external edits allowed)
    @property
    def balance(self) -> float:
        return self.__balance

    # 3 & 4. Write deposit() with validation guardrails
    def deposit(self, amount: float):
        if amount <= 0:
            print(f"❌ Transaction Rejected: Cannot deposit a negative or zero amount ({amount} ETB).")
            return
        
        self.__balance += amount
        print(f"✅ Successfully deposited {amount:.2f} ETB. New Balance: {self.__balance:.2f} ETB")

    # 3 & 4. Write withdraw() with validation guardrails (Reject negative and overdrafts)
    def withdraw(self, amount: float):
        if amount <= 0:
            print(f"❌ Transaction Rejected: Cannot withdraw a negative or zero amount ({amount} ETB).")
            return
        
        if amount > self.__balance:
            print(f"❌ Transaction Rejected: Insufficient funds! Attempted to withdraw {amount:.2f} ETB, but balance is only {self.__balance:.2f} ETB.")
            return
            
        self.__balance -= amount
        print(f"✅ Successfully withdrew {amount:.2f} ETB. New Balance: {self.__balance:.2f} ETB")


# 5. Create two accounts and run transactions to test the logic
if __name__ == "__main__":
    print("--- Running Addis Bank Account Simulation ---\n")

    # Creating Account 1
    acc1 = Account("Abel Endale", "ACC-1001", 500.00)
    print(f"Account Created for {acc1.owner} with balance: {acc1.balance} ETB")
    
    # Testing Transactions on Account 1
    acc1.deposit(150.50)      # Valid Deposit
    acc1.withdraw(200.00)     # Valid Withdrawal
    acc1.withdraw(600.00)     # Invalid Overdraft (Will reject!)
    acc1.deposit(-50.00)      # Invalid Deposit (Will reject!)
    
    print("\n---------------------------------------------\n")

    # Creating Account 2
    acc2 = Account("Mebratu Cheka", "ACC-1002", 1000.00)
    print(f"Account Created for {acc2.owner} with balance: {acc2.balance} ETB")
    
    # Testing Transactions on Account 2
    acc2.withdraw(450.00)     # Valid Withdrawal
    acc2.withdraw(-20.00)     # Invalid Withdrawal (Will reject!)
    
    print("\n--- Simulation Complete. Ready to push to version 1/day04! ---")