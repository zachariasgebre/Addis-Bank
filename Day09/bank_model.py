from collections import deque
from abc import ABC, abstractmethod

# ==========================================
# PREVIOUS CLASSES (Observer, Account, Registry)
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


class Account(ABC):
    def __init__(self, owner: str, account_number: str, initial_balance: float):
        self.owner = owner
        self.account_number = account_number
        self._observers: list[Observer] = []
        self._history_stack: list[dict] = []
        
        if initial_balance >= 0:
            self.__balance = float(initial_balance)
        else:
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

    def deposit(self, amount: float):
        if amount <= 0:
            return False
        self._update_balance(self.balance + amount)
        return True

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        pass

    @abstractmethod
    def statement(self) -> str:
        pass


class SavingsAccount(Account):
    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self._update_balance(self.balance - amount)
        return True

    def statement(self) -> str:
        return f"Savings [{self.account_number}] - {self.owner}: {self.balance} ETB"


class CurrentAccount(Account):
    def __init__(self, owner: str, account_number: str, initial_balance: float, overdraft_limit: float = 1000.0):
        super().__init__(owner, account_number, initial_balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > (self.balance + self.overdraft_limit):
            return False
        self._update_balance(self.balance - amount)
        return True

    def statement(self) -> str:
        return f"Current [{self.account_number}] - {self.owner}: {self.balance} ETB"


class AccountFactory:
    @staticmethod
    def create(kind: str, owner: str, account_number: str, initial_balance: float, **kwargs) -> Account:
        kind_clean = kind.strip().lower()
        if kind_clean == "savings":
            return SavingsAccount(owner, account_number, initial_balance)
        elif kind_clean == "current":
            overdraft = kwargs.get("overdraft_limit", 1000.0)
            return CurrentAccount(owner, account_number, initial_balance, overdraft_limit=overdraft)
        else:
            raise ValueError(f"Unknown account type: '{kind}'")


# ==========================================
# STEP 2 & 3: BRANCH HIERARCHY TREE
# ==========================================

class BranchNode:
    """Represents a node in the Bank Hierarchy Tree (Head Office -> Regions -> Branches)."""
    def __init__(self, name: str, direct_balance: float = 0.0):
        self.name = name
        self.direct_balance = direct_balance  # Balance held directly at this node/branch
        self.children: list['BranchNode'] = []  # Sub-regions or sub-branches

    def add_child(self, child_node: 'BranchNode'):
        """Adds a child branch or region to this node."""
        self.children.append(child_node)

    # STEP 3: Recursive total_balance()
    def total_balance(self) -> float:
        """
        Recursively calculates total balance for this branch and all sub-branches.
        Time Complexity: O(V) where V is total nodes in the subtree.
        """
        # Base case / Current node total
        total = self.direct_balance
        
        # Recursive step: Sum balances of all child subtrees
        for child in self.children:
            total += child.total_balance()
            
        return total


# ==========================================
# STEP 4: TRANSFERS GRAPH & BFS TRAVERSAL
# ==========================================

class TransferGraph:
    """Represents transfer paths between account/branch nodes as an Adjacency List."""
    def __init__(self):
        # Graph dictionary: key = account/node, value = list of connected accounts/nodes
        self.graph: dict[str, list[str]] = {}

    def add_edge(self, u: str, v: str, directed: bool = True):
        """Adds a transfer link between node u and node v."""
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
            
        self.graph[u].append(v)
        if not directed:
            self.graph[v].append(u)

    # STEP 4: Breadth-First Search (BFS) Traversal
    def bfs(self, start_node: str) -> list[str]:
        """
        Traverses the transfer graph starting from start_node using BFS.
        Returns a list of all reachable accounts/nodes.
        Time Complexity: O(V + E)
        """
        if start_node not in self.graph:
            return []

        visited = set()
        queue = deque([start_node])
        visited.add(start_node)
        reachable_nodes = []

        while queue:
            current = queue.popleft()
            reachable_nodes.append(current)

            for neighbor in self.graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return reachable_nodes


# ==========================================
# STEP 5: DEMONSTRATION & TEST CASES
# ==========================================

if __name__ == "__main__":
    print("--- Day 09: Model the Bank Simulation ---\n")

    # 1. Build the Tree Structure (Step 2)
    head_office = BranchNode("Head Office (Addis Ababa)", direct_balance=1000000.0)

    # Regions
    north_region = BranchNode("Northern Region", direct_balance=50000.0)
    central_region = BranchNode("Central Region", direct_balance=75000.0)

    head_office.add_child(north_region)
    head_office.add_child(central_region)

    # Local Branches
    mekelle_branch = BranchNode("Mekelle Branch", direct_balance=250000.0)
    addis_4kilo_branch = BranchNode("4 Kilo Branch", direct_balance=400000.0)
    addis_5kilo_branch = BranchNode("5 Kilo Branch", direct_balance=350000.0)

    north_region.add_child(mekelle_branch)
    central_region.add_child(addis_4kilo_branch)
    central_region.add_child(addis_5kilo_branch)

    # 2. Print Recursive Totals (Step 3 & Step 5)
    print("--- Step 3: Recursive Branch Balance Totals ---")
    print(f"💰 Total Central Region Balance: {central_region.total_balance():,.2f} ETB")
    print(f"🏛️ Bank's Entire Total (Head Office): {head_office.total_balance():,.2f} ETB")

    # 3. Build Transfer Graph (Step 4)
    print("\n--- Step 4: Transfer Graph & BFS Reachability ---")
    transfers = TransferGraph()

    # Transfers setup (CBE-1 can reach CBE-2, CBE-3, CBE-4 through direct/indirect transfers)
    transfers.add_edge("CBE-1", "CBE-2")
    transfers.add_edge("CBE-1", "CBE-3")
    transfers.add_edge("CBE-2", "CBE-4")
    transfers.add_edge("CBE-3", "CBE-5")
    transfers.add_edge("CBE-5", "CBE-6")
    
    # Isolated node / Unconnected network
    transfers.add_edge("CBE-99", "CBE-100")

    # 4. Perform BFS (Step 5)
    start_account = "CBE-1"
    reachable = transfers.bfs(start_account)

    print(f"🔗 Accounts reachable from '{start_account}' via transfers (BFS order):")
    print(" -> ".join(reachable))