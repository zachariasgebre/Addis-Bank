from abc import ABC, abstractmethod

# ==========================================
# OBSERVER PATTERN
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
# CORE DOMAIN: Account Family
# ==========================================

class Account(ABC):
    def __init__(self, owner: str, account_number: str, initial_balance: float):
        self.owner = owner
        self.account_number = account_number
        self._observers: list[Observer] = []
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

    def _push_transaction(self, action: str, amount: float):
        self._history_stack.append({
            "action": action,
            "amount": amount
        })

    def deposit(self, amount: float, record_history: bool = True):
        if amount <= 0:
            error_msg = f"❌ Transaction Rejected: Cannot deposit negative/zero amount ({amount} ETB)."
            print(error_msg)
            self._notify(error_msg)
            return False
        
        self._update_balance(self.balance + amount)
        if record_history:
            self._push_transaction("deposit", amount)
            
        success_msg = f"✅ Deposit of {amount:.2f} ETB successful. New Balance: {self.balance:.2f} ETB"
        print(success_msg)
        self._notify(success_msg)
        return True

    def undo_last(self) -> bool:
        if not self._history_stack:
            print(f"⚠️ Undo failed: No transactions in history for {self.owner}.")
            return False
            
        last_tx = self._history_stack.pop()
        action = last_tx["action"]
        amount = last_tx["amount"]
        
        print(f"↩️ Undoing last action ({action} of {amount:.2f} ETB) for {self.owner}...")
        
        if action == "deposit":
            self._update_balance(self.balance - amount)
        elif action == "withdraw":
            self._update_balance(self.balance + amount)
        elif action == "interest":
            self._update_balance(self.balance - amount)
            
        undo_msg = f"✅ Undo complete. Restored Balance: {self.balance:.2f} ETB"
        print(undo_msg)
        self._notify(undo_msg)
        return True

    # ----------------------------------------------------
    # STEP 4: Recursive total_transactions() for 1 Account
    # ----------------------------------------------------
    def total_transactions(self, index: int = 0) -> float:
        """
        Recursively calculates the total sum of all transaction amounts in history.
        Time Complexity: O(n), Space Complexity: O(n) call stack depth.
        """
        # Base Case: reached the end of the history stack
        if index >= len(self._history_stack):
            return 0.0
        
        # Recursive Case: current amount + total of the rest
        current_amount = self._history_stack[index]["amount"]
        return current_amount + self.total_transactions(index + 1)

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
        if amount <= 0 or amount > self.balance:
            error_msg = f"❌ Withdrawal Rejected for {self.owner}."
            print(error_msg)
            self._notify(error_msg)
            return False
        
        self._update_balance(self.balance - amount)
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
        if amount <= 0 or amount > (self.balance + self.overdraft_limit):
            error_msg = f"❌ Withdrawal Rejected for {self.owner}."
            print(error_msg)
            self._notify(error_msg)
            return False

        self._update_balance(self.balance - amount)
        if record_history:
            self._push_transaction("withdraw", amount)
            
        success_msg = f"✅ Withdrew {amount:.2f} ETB. New Balance: {self.balance:.2f} ETB"
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
# ACCOUNT REGISTRY (DAY 08 ENHANCEMENTS)
# ==========================================

class AccountRegistry:
    def __init__(self):
        self._registry: dict[str, Account] = {}

    def add(self, account: Account):
        if account.account_number in self._registry:
            print(f"⚠️ Warning: Account {account.account_number} already exists.")
            return
        self._registry[account.account_number] = account

    def find(self, account_number: str) -> Account | None:
        return self._registry.get(account_number)

    def list_all(self) -> list[Account]:
        return list(self._registry.values())

    # ----------------------------------------------------
    # STEP 2: Top N by Balance using sorted & key=lambda
    # ----------------------------------------------------
    def top_by_balance(self, n: int) -> list[Account]:
        """Returns the top N accounts with the highest balance."""
        all_accounts = self.list_all()
        # Sort in descending order using balance property as key
        sorted_accounts = sorted(all_accounts, key=lambda acc: acc.balance, reverse=True)
        return sorted_accounts[:n]

    # ----------------------------------------------------
    # STEP 3: O(log n) Binary Search by Account Number
    # ----------------------------------------------------
    def find_by_number(self, target_number: str) -> Account | None:
        """
        Performs a binary search on sorted account numbers.
        Time Complexity: O(log n) search time.
        """
        # Binary search requires sorted input
        sorted_accounts = sorted(self.list_all(), key=lambda acc: acc.account_number)
        
        low = 0
        high = len(sorted_accounts) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_acc = sorted_accounts[mid]

            if mid_acc.account_number == target_number:
                return mid_acc
            elif mid_acc.account_number < target_number:
                low = mid + 1
            else:
                high = mid - 1

        return None


# ==========================================
# STEP 5: TEST ALL THREE FEATURES
# ==========================================

if __name__ == "__main__":
    print("--- Running Day 08 Sort & Search Tests ---")

    registry = AccountRegistry()

    # Populate sample data
    acc1 = AccountFactory.create("savings", "Abel", "SAV-303", 1500.0)
    acc2 = AccountFactory.create("current", "Mebratu", "CUR-101", 5000.0)
    acc3 = AccountFactory.create("savings", "Kalikidan", "SAV-202", 2500.0)
    acc4 = AccountFactory.create("current", "Abenezer", "CUR-404", 800.0)

    for acc in [acc1, acc2, acc3, acc4]:
        registry.add(acc)

    # 1. Test Step 2: top_by_balance(n)
    print("\n--- Test 1: Leaderboard (Top 2 by Balance) ---")
    top_2 = registry.top_by_balance(2)
    for acc in top_2:
        print(f"🏆 {acc.owner} | Balance: {acc.balance} ETB")

    # 2. Test Step 3: find_by_number() (Binary Search O(log n))
    print("\n--- Test 2: Binary Search for 'SAV-202' ---")
    found_acc = registry.find_by_number("SAV-202")
    if found_acc:
        print(f"🔍 Found: {found_acc.owner} ({found_acc.account_number}) - Balance: {found_acc.balance} ETB")
    else:
        print("❌ Account not found.")

    # 3. Test Step 4: Recursive total_transactions()
    print("\n--- Test 3: Recursive Transaction Sum ---")
    acc1.deposit(200.0)   # tx 1: 200
    acc1.withdraw(50.0)   # tx 2: 50
    acc1.deposit(100.0)   # tx 3: 100
    
    total_val = acc1.total_transactions()
    print(f"📊 Recursive sum of all transaction amounts for {acc1.owner}: {total_val:.2f} ETB")