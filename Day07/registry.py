from abc import ABC, abstractmethod

# ==========================================
# OBSERVER PATTERN: Interfaces & Services
# ==========================================

class Observer(ABC):
    @abstractmethod
    def update(self, message: str):
        pass


class SMSAlert(Observer):
    def __init__(self, phone_number: str):
        self.phone_number = phone_number

    def update(self, message: str):
        print(f"📱 [SMS sent to {self.phone_number}]: {message}")


# ==========================================
# CORE DOMAIN: Account Family with Transaction Stack
# ==========================================

class Account(ABC):
    def __init__(self, owner: str, account_number: str, initial_balance: float):
        self.owner = owner
        self.account_number = account_number
        self._observers: list[Observer] = []
        
        # Step 4: Give each account a history stack (using a Python list as a stack)
        self._history_stack: list[dict] = []
        
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

    def subscribe(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def _notify(self, message: str):
        for observer in self._observers:
            observer.update(message)

    # Helper to push transactions to the history stack
    def _push_transaction(self, action: str, amount: float):
        """Pushes a successful transaction onto the history stack."""
        self._history_stack.append({
            "action": action,     # "deposit" or "withdraw" (or "interest")
            "amount": amount
        })

    def deposit(self, amount: float, record_history: bool = True):
        if amount <= 0:
            error_msg = f"❌ Transaction Rejected: Cannot deposit negative/zero amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return False
        
        self._update_balance(self.balance + amount)
        
        # Step 4: Push to stack on successful deposit
        if record_history:
            self._push_transaction("deposit", amount)
            
        success_msg = f"✅ Deposit of {amount:.2f} ETB successful. New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)
        return True

    # Step 5: Implement undo_last() using Stack Pop (LIFO)
    def undo_last(self) -> bool:
        """Pops and reverses the most recent transaction from the history stack."""
        if not self._history_stack:
            print(f"⚠️ Undo failed: No transactions in history for {self.owner}.")
            return False
            
        last_tx = self._history_stack.pop()
        action = last_tx["action"]
        amount = last_tx["amount"]
        
        print(f"↩️ Undoing last action ({action} of {amount:.2f} ETB) for {self.owner}...")
        
        if action == "deposit":
            # Reversing a deposit means subtracting money
            self._update_balance(self.balance - amount)
        elif action == "withdraw":
            # Reversing a withdrawal means adding money back
            self._update_balance(self.balance + amount)
        elif action == "interest":
            # Reversing interest addition
            self._update_balance(self.balance - amount)
            
        undo_msg = f"✅ Undo complete. Restored Balance: {self.balance:.2f} ETB"
        print(undo_msg)
        self._notify(undo_msg)
        return True

    @abstractmethod
    def withdraw(self, amount: float, record_history: bool = True) -> bool:
        pass

    @abstractmethod
    def statement(self) -> str:
        pass


class SavingsAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, interest_rate: float = 0.05):
        super().__init__(owner, account_number, initial_balance)
        self.interest_rate = interest_rate

    def add_interest(self, record_history: bool = True):
        interest = self.balance * self.interest_rate
        self._update_balance(self.balance + interest)
        
        if record_history:
            self._push_transaction("interest", interest)
            
        success_msg = f"📈 Interest of {interest:.2f} ETB applied. New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)

    def withdraw(self, amount: float, record_history: bool = True) -> bool:
        if amount <= 0:
            error_msg = f"❌ Withdrawal Rejected: Invalid amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return False
        if amount > self.balance:
            error_msg = f"❌ Withdrawal Rejected: Insufficient funds! Balance is {self.balance:.2f} ETB."
            print(error_msg)
            self._notify(error_msg)
            return False
        
        self._update_balance(self.balance - amount)
        
        # Step 4: Push to stack on successful withdrawal
        if record_history:
            self._push_transaction("withdraw", amount)
            
        success_msg = f"✅ Withdrew {amount:.2f} ETB. New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)
        return True

    def statement(self) -> str:
        return f"Savings Account [{self.account_number}] - Owner: {self.owner} | Balance: {self.balance:.2f} ETB"


class CurrentAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, overdraft_limit: float = 1000.0):
        super().__init__(owner, account_number, initial_balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float, record_history: bool = True) -> bool:
        if amount <= 0:
            error_msg = f"❌ Withdrawal Rejected: Invalid amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return False
        
        if amount > self.balance + self.overdraft_limit:
            error_msg = f"❌ Withdrawal Rejected: Overdraft Limit Exceeded! Max available: {(self.balance + self.overdraft_limit):.2f} ETB."
            print(error_msg)
            self._notify(error_msg)
            return False

        self._update_balance(self.balance - amount)
        
        # Step 4: Push to stack on successful withdrawal
        if record_history:
            self._push_transaction("withdraw", amount)
            
        success_msg = f"✅ Withdrew {amount:.2f} ETB (Overdraft active). New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)
        return True

    def statement(self) -> str:
        return f"Current Account [{self.account_number}] - Owner: {self.owner} | Balance: {self.balance:.2f} ETB"


# ==========================================
# FACTORY PATTERN
# ==========================================

class AccountFactory:
    @staticmethod
    def create(kind: str, owner: str, account_number: str, initial_balance: float, **kwargs) -> Account:
        kind_clean = kind.strip().lower()
        if kind_clean == "savings":
            rate = kwargs.get("interest_rate", 0.05)
            return SavingsAccount(owner, account_number, initial_balance, interest_rate=rate)
        elif kind_clean == "current":
            overdraft = kwargs.get("overdraft_limit", 1000.0)
            return CurrentAccount(owner, account_number, initial_balance, overdraft_limit=overdraft)
        else:
            raise ValueError(f"Unknown account type: '{kind}'")


# ==========================================
# 3. REGISTRY PATTERN: Dict for O(1) Lookups
# ==========================================

class AccountRegistry:
    """Stores many accounts in a dictionary for O(1) lookup speed (Step 2 & 3)."""
    def __init__(self):
        # Key: account_number (str), Value: Account object
        self._registry: dict[str, Account] = {}

    def add(self, account: Account):
        """Adds an account to the registry. Time Complexity: O(1)"""
        if account.account_number in self._registry:
            print(f"⚠️ Warning: Account {account.account_number} already exists.")
            return
        self._registry[account.account_number] = account
        print(f"📂 Registered: {account.owner}'s account ({account.account_number}) saved to registry.")

    def find(self, account_number: str) -> Account | None:
        """Finds and returns an account in O(1) time complexity."""
        # Standard dictionary lookups run in O(1) constant time
        return self._registry.get(account_number)

    def list_all(self) -> list[Account]:
        """Returns accounts in the registry ordered by when they were added (Python dicts preserve order)."""
        return list(self._registry.values())


# ==========================================
# TESTING THE DATA STRUCTURES (Step 5)
# ==========================================

if __name__ == "__main__":
    print("--- Running Day 07 Account Registry & History Stack Simulation ---\n")

    # 1. Initialize Registry
    registry = AccountRegistry()

    # 2. Open Accounts using Factory
    acc1 = AccountFactory.create("savings", "Abel Endale", "SAV-001", 1000.0)
    acc2 = AccountFactory.create("current", "Mebratu Cheka", "CUR-002", 500.0, overdraft_limit=300.0)

    # Attach Alert Listeners
    acc1.subscribe(SMSAlert("+251-911-111111"))
    acc2.subscribe(SMSAlert("+251-922-222222"))

    print("\n--- Step 3: Adding accounts to Registry ---")
    registry.add(acc1)
    registry.add(acc2)

    print("\n--- Step 3: Finding an account in O(1) time ---")
    retrieved_acc = registry.find("CUR-002")
    if retrieved_acc:
        print(f"🔍 Found matching account! Owner: {retrieved_acc.owner}, Balance: {retrieved_acc.balance} ETB")

    print("\n--- Step 4: Running Transactions (Building Stack History) ---")
    # Abel makes a deposit and withdrawal
    acc1.deposit(250.00)  # History stack gets: [{"action": "deposit", "amount": 250.0}]
    acc1.withdraw(100.00) # History stack gets: [{"action": "deposit", ...}, {"action": "withdraw", "amount": 100.0}]

    print("\n--- Step 5: Testing undo_last() (LIFO Stack Action) ---")
    # Balance before undo: 1150 ETB (1000 + 250 - 100)
    print(f"Pre-undo Balance: {acc1.balance} ETB")
    
    # First undo: Should reverse the withdrawal of 100 ETB (adding it back to make 1250 ETB)
    acc1.undo_last() 
    
    # Second undo: Should reverse the deposit of 250 ETB (subtracting it to return to base 1000 ETB)
    acc1.undo_last()
    
    # Third undo: Stack is now empty, should handle gracefully
    acc1.undo_last()

    print("\n--- Final Ordered Registry Accounts List ---")
    for acc in registry.list_all():
        print(acc.statement())