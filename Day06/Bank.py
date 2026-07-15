from abc import ABC, abstractmethod

# ==========================================
# 1. OBSERVER PATTERN: Interfaces & Services
# ==========================================

class Observer(ABC):
    """Abstract Observer representing any alert destination."""
    @abstractmethod
    def update(self, message: str):
        pass


class SMSAlert(Observer):
    """Concrete Observer: Sends an SMS alert (Single Responsibility Principle - Step 2/4)."""
    def __init__(self, phone_number: str):
        self.phone_number = phone_number

    def update(self, message: str):
        # Splitting alert logic into its own service class instead of having Account handle print alerts
        print(f"📱 [SMS sent to {self.phone_number}]: {message}")


# ==========================================
# 2. CORE DOMAIN: Account Family (Abstract Base & Children)
# ==========================================

class Account(ABC):
    """Abstract Base Class representing a generic bank account with Observer capability."""
    def __init__(self, owner: str, account_number: str, initial_balance: float):
        self.owner = owner
        self.account_number = account_number
        self._observers: list[Observer] = []  # List of subscribed observers
        
        if initial_balance >= 0:
            self.__balance = float(initial_balance)
        else:
            print("Warning: Initial balance cannot be negative. Setting balance to 0.0")
            self.__balance = 0.0

    @property
    def balance(self) -> float:
        return self.__balance

    def _update_balance(self, new_balance: float):
        self.__balance = new_balance

    # Step 4: Observer Pattern Support (Subscribe / Notify)
    def subscribe(self, observer: Observer):
        """Attaches an alert observer to this account."""
        if observer not in self._observers:
            self._observers.append(observer)

    def _notify(self, message: str):
        """Triggers updates on all attached observers."""
        for observer in self._observers:
            observer.update(message)

    def deposit(self, amount: float):
        if amount <= 0:
            error_msg = f"❌ Transaction Rejected: Cannot deposit negative/zero amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return
        
        self.__balance += amount
        success_msg = f"✅ Deposit of {amount:.2f} ETB successful. New Balance: {self.__balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)

    @abstractmethod
    def withdraw(self, amount: float):
        pass

    @abstractmethod
    def statement(self) -> str:
        pass


class SavingsAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, interest_rate: float = 0.05):
        super().__init__(owner, account_number, initial_balance)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self.balance * self.interest_rate
        self._update_balance(self.balance + interest)
        success_msg = f"📈 Interest of {interest:.2f} ETB applied. New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)

    def withdraw(self, amount: float):
        if amount <= 0:
            error_msg = f"❌ Withdrawal Rejected: Invalid amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return
        if amount > self.balance:
            error_msg = f"❌ Withdrawal Rejected: Insufficient funds! Balance is {self.balance:.2f} ETB."
            print(error_msg)
            self._notify(error_msg)
            return
        
        self._update_balance(self.balance - amount)
        success_msg = f"✅ Withdrew {amount:.2f} ETB. New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)

    def statement(self) -> str:
        return f"Savings Account [{self.account_number}] - Owner: {self.owner} | Balance: {self.balance:.2f} ETB (Rate: {self.interest_rate * 100}%)"


class CurrentAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, overdraft_limit: float = 1000.0):
        super().__init__(owner, account_number, initial_balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float):
        if amount <= 0:
            error_msg = f"❌ Withdrawal Rejected: Invalid amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return
        
        if amount > self.balance + self.overdraft_limit:
            error_msg = f"❌ Withdrawal Rejected: Overdraft Limit Exceeded! Max available funds: {(self.balance + self.overdraft_limit):.2f} ETB."
            print(error_msg)
            self._notify(error_msg)
            return

        self._update_balance(self.balance - amount)
        success_msg = f"✅ Withdrew {amount:.2f} ETB (Overdraft active). New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)

    def statement(self) -> str:
        return f"Current Account [{self.account_number}] - Owner: {self.owner} | Balance: {self.balance:.2f} ETB (Overdraft Limit: {self.overdraft_limit:.2f} ETB)"


# ==========================================
# 3. FACTORY PATTERN: Account Creation
# ==========================================

class AccountFactory:
    """Factory Class to instantiate specific bank account types (Step 3)."""
    @staticmethod
    def create(kind: str, owner: str, account_number: str, initial_balance: float, **kwargs) -> Account:
        """Instantiates and returns the requested concrete Account subclass."""
        kind_clean = kind.strip().lower()
        if kind_clean == "savings":
            # Safely grab interest rate if provided in kwargs, default to 5%
            rate = kwargs.get("interest_rate", 0.05)
            return SavingsAccount(owner, account_number, initial_balance, interest_rate=rate)
        elif kind_clean == "current":
            # Safely grab overdraft limit if provided, default to 1000 ETB
            overdraft = kwargs.get("overdraft_limit", 1000.0)
            return CurrentAccount(owner, account_number, initial_balance, overdraft_limit=overdraft)
        else:
            raise ValueError(f"Unknown account type: '{kind}'. Only 'savings' or 'current' are supported.")


# ==========================================
# 4. RUNNING & TESTING PATTERNS (Step 5)
# ==========================================

if __name__ == "__main__":
    print("--- Running Pattern-Refactored Addis Bank Simulation ---\n")

    # Step 5: Open accounts via the Factory Pattern
    acc1 = AccountFactory.create("savings", "Abel Endale", "SAV-9001", 1000.0, interest_rate=0.06)
    acc2 = AccountFactory.create("current", "Mebratu Cheka", "CUR-9002", 500.0, overdraft_limit=300.0)

    # Step 5: Write and attach SMS observers
    abel_sms = SMSAlert("+251-911-111111")
    mebratu_sms = SMSAlert("+251-922-222222")

    acc1.subscribe(abel_sms)
    acc2.subscribe(mebratu_sms)

    print("\n--- Executing Transactions with Observer Alerts ---")
    
    # Trigger deposit update on Abel's Savings account
    acc1.deposit(500.00)
    
    # Trigger interest accrual with SMS notification
    acc1.add_interest()

    print("-" * 65)

    # Trigger Mebratu's normal withdrawal
    acc2.withdraw(600.00)  # Uses 100 ETB of his 300 ETB overdraft
    
    # Trigger Mebratu's failed transaction
    acc2.withdraw(500.00)  # Attempts to exceed overdraft, SMS alert notifies transaction failure!

    print("-" * 65)
    print("\n--- Running Step 5 Polymorphic Loop ---")
    
    # Driving the factory-created accounts polymorphically
    accounts_list = [acc1, acc2]
    for acc in accounts_list:
        print(acc.statement())

    print("\n--- Simulation Complete. Ready to push to day06! ---")