# day07/data_structures_and_problems.py

# ==========================================
# PART 2: Stack & Queue Implementation
# ==========================================

class Node:
    """Generic Node for sequential structures."""
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    """LIFO Stack implemented using a singly linked list structure."""
    def __init__(self):
        self.top_node = None
        self._size = 0

    def push(self, data):
        new_node = Node(data)
        new_node.next = self.top_node
        self.top_node = new_node
        self._size += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        popped_data = self.top_node.data
        self.top_node = self.top_node.next
        self._size -= 1
        return popped_data

    def peek(self):
        if self.is_empty():
            return None
        return self.top_node.data

    def is_empty(self) -> bool:
        return self.top_node is None

    def size(self) -> int:
        return self._size


class Queue:
    """FIFO Queue implemented using a singly linked list with head/tail pointers."""
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def enqueue(self, data):
        new_node = Node(data)
        if not self.tail:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        dequeued_data = self.head.data
        self.head = self.head.next
        if not self.head:
            self.tail = None
        self._size -= 1
        return dequeued_data

    def is_empty(self) -> bool:
        return self.head is None

    def size(self) -> int:
        return self._size


# --- Problem 2.1: Balanced Brackets ---
def is_balanced(brackets: str) -> bool:
    """
    Checks if brackets match using our Stack implementation.
    Time Complexity: O(n), Space Complexity: O(n)
    """
    stack = Stack()
    mapping = {")": "(", "}": "{", "]": "["}
    
    for char in brackets:
        if char in mapping.values():
            stack.push(char)
        elif char in mapping:
            if stack.is_empty() or stack.pop() != mapping[char]:
                return False
    return stack.is_empty()


# --- Problem 2.2: Maximum Sliding Window ---
# (Using a helper Double-Ended Queue simulation pattern built via list to easily scan indices)
def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """
    Finds the maximum in every sliding window of size k.
    Uses a Monotonic Queue strategy (maintaining indices in decreasing order).
    Time Complexity: O(n), Space Complexity: O(k)
    """
    if not nums or k == 0:
        return []
    
    result = []
    # Monotonic queue storing indices. Indices are ordered such that 
    # their corresponding values in nums are strictly decreasing.
    deque = []  

    for i, val in enumerate(nums):
        # 1. Remove indices that are outside the current window boundary
        if deque and deque[0] < i - k + 1:
            deque.pop(0)
            
        # 2. Remove indices of elements smaller than the current element
        # (they can never be the maximum because current element is newer and larger)
        while deque and nums[deque[-1]] < val:
            deque.pop()
            
        deque.append(i)
        
        # 3. Once we reach a full window size k, append front of deque to result
        if i >= k - 1:
            result.append(nums[deque[0]])
            
    return result


# ==========================================
# PART 3: Hash Map Solutions (all O(n) Time)
# ==========================================

# --- Problem 3.1: Two Sum ---
# Big-O: Time O(n), Space O(n)
def two_sum(nums: list[int], target: int) -> list[int]:
    """
    Hash Map Strategy:
    We traverse the array once. At each step, we calculate the required 'complement' 
    (target - current_value). If the complement is already stored in our hash map, 
    we have found the pair and return their indices. Otherwise, we store the current 
    value along with its index. This allows O(1) average lookups.
    """
    seen = {}  # key: value, value: index
    for i, val in enumerate(nums):
        complement = target - val
        if complement in seen:
            return [seen[complement], i]
        seen[val] = i
    return []


# --- Problem 3.2: Is Anagram ---
# Big-O: Time O(n), Space O(k) where k is unique characters (max 26 for alphabets)
def is_anagram(s: str, t: str) -> bool:
    """
    Hash Map Strategy:
    An anagram must have the exact same character counts. First, check if string lengths match.
    Then, count frequencies of each character in string 's' using a hash map. Afterwards,
    traverse 't' and decrement those counts. If any character count drops below zero or is missing,
    they are not anagrams.
    """
    if len(s) != len(t):
        return False
        
    char_counts = {}
    for char in s:
        char_counts[char] = char_counts.get(char, 0) + 1
        
    for char in t:
        if char not in char_counts:
            return False
        char_counts[char] -= 1
        if char_counts[char] < 0:
            return False
            
    return True


# --- Problem 3.3: First Unique Character ---
# Big-O: Time O(n), Space O(k) where k is unique characters
def first_uniq_char(s: str) -> int:
    """
    Hash Map Strategy:
    We perform two linear passes. In the first pass, we record the frequency count 
    of each character in a hash map. In the second pass, we scan the string 
    left-to-right, checking each character's count in the map. The first index 
    holding a character with a frequency count of exactly 1 is returned.
    """
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
        
    for i, char in enumerate(s):
        if counts[char] == 1:
            return i
            
    return -1


# ==========================================
# COMPREHENSIVE TESTS FOR PARTS 2 & 3
# ==========================================

def run_tests():
    print("--- Running Queue/Stack/Problem Tests ---")

    # Stack Tests
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    assert s.peek() == 1
    assert s.size() == 1
    print("✅ Stack Tests Passed.")

    # Queue Tests
    q = Queue()
    q.enqueue("A")
    q.enqueue("B")
    assert q.dequeue() == "A"
    assert q.size() == 1
    print("✅ Queue Tests Passed.")

    # Balanced Brackets (3 test cases)
    assert is_balanced("{[()]}") is True
    assert is_balanced("{[(])}") is False
    assert is_balanced("((()") is False
    print("✅ Balanced Brackets Tests Passed.")

    # Sliding Window Maximum (3 test cases)
    assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert max_sliding_window([1], 1) == [1]
    assert max_sliding_window([9, 11, 8, 5, 7, 10], 4) == [11, 11, 8, 10]
    print("✅ Sliding Window Maximum Tests Passed.")

    # Two Sum (3 test cases)
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]
    assert sorted(two_sum([3, 3], 6)) == [0, 1]
    print("✅ Two Sum Hash Map Tests Passed.")

    # Is Anagram (3 test cases)
    assert is_anagram("anagram", "nagaram") is True
    assert is_anagram("rat", "car") is False
    assert is_anagram("listen", "silent") is True
    print("✅ Is Anagram Hash Map Tests Passed.")

    # First Unique Character (3 test cases)
    assert first_uniq_char("leetcode") == 0  # 'l' is first unique
    assert first_uniq_char("loveleetcode") == 2  # 'v' is first unique
    assert first_uniq_char("aabb") == -1  # no unique characters
    print("✅ First Unique Character Hash Map Tests Passed.")

    print("\n🎉 All tests for registry, data structures, and algorithms passed successfully!")


if __name__ == "__main__":
    run_tests()