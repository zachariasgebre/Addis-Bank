# Statement method added
# Polymorphism, inheritance, Overriding, Abstraction
from abc import ABC, abstractmethod

class Account(ABC):  # Made an Abstract Base Class
    def __init__(self, owner: str, account_number: str, initial_balance: float):
        self.owner = owner
        self.account_number = account_number
        
        # 1. Private __balance (Encapsulation)
        if initial_balance >= 0:
            self.__balance = float(initial_balance)
        else:
            print("Warning: Initial balance cannot be negative. Setting balance to 0.0")
            self.__balance = 0.0

    # 2. @property getter to read balance securely
    @property
    def balance(self) -> float:
        return self.__balance

    # Encapsulation Helper: Allows safe, internal balance updates by subclasses
    def _update_balance(self, new_balance: float):
        self.__balance = new_balance

    # 3 & 4. deposit() with validation guardrails
    def deposit(self, amount: float):
        if amount <= 0:
            print(f"❌ Transaction Rejected: Cannot deposit a negative or zero amount ({amount} ETB).")
            return
        
        self.__balance += amount
        print(f"✅ Successfully deposited {amount:.2f} ETB. New Balance: {self.__balance:.2f} ETB")

    # Abstract methods: Every subclass MUST implement custom logic for these
    @abstractmethod
    def withdraw(self, amount: float):
        pass

    @abstractmethod
    def statement(self) -> str:
        pass


# Step 2: Add SavingsAccount with a rate and add_interest()
class SavingsAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, interest_rate: float = 0.05):
        super().__init__(owner, account_number, initial_balance)
        self.interest_rate = interest_rate  # e.g., 0.05 for 5% interest

    def add_interest(self):
        """Calculates interest and deposits it securely."""
        interest = self.balance * self.interest_rate
        self._update_balance(self.balance + interest)
        print(f"📈 Interest of {interest:.2f} ETB applied at a rate of {self.interest_rate * 100}%. New Balance: {self.balance:.2f} ETB")

    # Overriding abstract withdraw logic for savings accounts
    def withdraw(self, amount: float):
        if amount <= 0:
            print(f"❌ Transaction Rejected: Cannot withdraw negative/zero amounts ({amount} ETB).")
            return
        if amount > self.balance:
            print(f"❌ Transaction Rejected: Insufficient funds! {self.owner}'s balance is {self.balance:.2f} ETB.")
            return
        
        self._update_balance(self.balance - amount)
        print(f"✅ Successfully withdrew {amount:.2f} ETB from Savings. New Balance: {self.balance:.2f} ETB")

    # Step 4: Custom statement label
    def statement(self) -> str:
        return f"Savings Account [{self.account_number}] - Owner: {self.owner} | Balance: {self.balance:.2f} ETB (Interest Rate: {self.interest_rate * 100}%)"


# Step 3: Add CurrentAccount with an overdraft and overridden withdraw()
class CurrentAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, overdraft_limit: float = 1000.0):
        super().__init__(owner, account_number, initial_balance)
        self.overdraft_limit = overdraft_limit

    # Overriding withdraw logic to explicitly leverage overdraft thresholds
    def withdraw(self, amount: float):
        if amount <= 0:
            print(f"❌ Transaction Rejected: Cannot withdraw negative/zero amounts ({amount} ETB).")
            return
        
        # Balance is allowed to drop negative up to the overdraft limit
        if amount > self.balance + self.overdraft_limit:
            print(f"❌ Transaction Rejected: Overdraft Limit Exceeded! Max available funds for {self.owner} are {(self.balance + self.overdraft_limit):.2f} ETB.")
            return

        self._update_balance(self.balance - amount)
        print(f"✅ Successfully withdrew {amount:.2f} ETB using overdraft facility. New Balance: {self.balance:.2f} ETB")

    # Step 4: Custom statement label
    def statement(self) -> str:
        return f"Current Account [{self.account_number}] - Owner: {self.owner} | Balance: {self.balance:.2f} ETB (Overdraft Limit: {self.overdraft_limit:.2f} ETB)"


# Step 5: Polymorphic Loop Demonstration
if __name__ == "__main__":
    print("--- Running Extended Addis Bank Polymorphic Simulation ---\n")

    # Creating a polymorphic mixed list of valid bank subclasses
    accounts_list = [
        SavingsAccount("Abel Endale", "SAV-1001", 500.00, interest_rate=0.07),
        CurrentAccount("Mebratu Cheka", "CUR-1002", 1000.00, overdraft_limit=500.0),
        SavingsAccount("Abenezer Erase", "SAV-1003", 2500.00)
    ]

    print("--- Executing Subclass Specific Operations ---")
    # Apply interest to Abel's Savings account
    accounts_list[0].add_interest()
    
    # Test Current Account Overdraft for Mebratu (Withdrawing more than balance)
    accounts_list[1].withdraw(1200.00) 
    
    # Attempting to crash Mebratu's overdraft facility entirely
    accounts_list[1].withdraw(400.00)
    print("\n" + "="*60 + "\n")

    print("--- Running Step 5 Polymorphic Loop ---")
    # Single loop treating everything as a generic 'Account' object
    for acc in accounts_list:
        # Executes the custom child statement() implementation dynamically at runtime
        print(acc.statement())

    print("\n--- Simulation Complete. Ready to push to day05! ---")