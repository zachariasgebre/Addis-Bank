# day07/linked_list.py

class Node:
    """A Node in a Singly Linked List."""
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """A Singly Linked List implemented from scratch."""
    def __init__(self):
        self.head = None

    def prepend(self, data):
        """Adds an element to the front of the list (O(1) time)."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def append(self, data):
        """Adds an element to the end of the list (O(n) time)."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def delete(self, data) -> bool:
        """Deletes the first node containing the matching data. Returns True if deleted."""
        if not self.head:
            return False

        if self.head.data == data:
            self.head = self.head.next
            return True

        current = self.head
        while current.next and current.next.data != data:
            current = current.next

        if current.next:
            current.next = current.next.next
            return True
        return False

    def reverse(self):
        """Reverses the linked list in-place (O(n) time, O(1) auxiliary space)."""
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev

    def has_cycle(self) -> bool:
        """Detects if a cycle exists in the list using Floyd's Tortoise and Hare (O(n) time)."""
        slow = self.head
        fast = self.head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True
        return False

    def __iter__(self):
        """Enables iteration over the list values."""
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        """Returns a string representation of the list."""
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        return " -> ".join(elements) if elements else "Empty List"


# ==========================================
# TEST SUITE: 8 Test Cases
# ==========================================

def run_linked_list_tests():
    print("--- Running Linked List Tests ---")

    # Test 1: Empty Representation
    ll = LinkedList()
    assert repr(ll) == "Empty List", "Test 1 Failed"
    print("Test 1 Passed: Empty representation is correct.")

    # Test 2: Prepend
    ll.prepend(10)
    ll.prepend(20)
    assert repr(ll) == "20 -> 10", "Test 2 Failed"
    print("Test 2 Passed: Prepend operates correctly.")

    # Test 3: Append
    ll.append(30)
    assert repr(ll) == "20 -> 10 -> 30", "Test 3 Failed"
    print("Test 3 Passed: Append operates correctly.")

    # Test 4: Delete head node
    assert ll.delete(20) is True, "Test 4 Failed to delete head"
    assert repr(ll) == "10 -> 30", "Test 4 Failed"
    print("Test 4 Passed: Deleting the head node works.")

    # Test 5: Delete middle/end node
    ll.append(40)  # 10 -> 30 -> 40
    assert ll.delete(30) is True, "Test 5 Failed to delete middle"
    assert repr(ll) == "10 -> 40", "Test 5 Failed"
    print("Test 5 Passed: Deleting non-head nodes works.")

    # Test 6: In-place Reversal
    ll.prepend(5)  # 5 -> 10 -> 40
    ll.reverse()   # 40 -> 10 -> 5
    assert list(ll) == [40, 10, 5], "Test 6 Failed"
    print("Test 6 Passed: Reversal operates correctly.")

    # Test 7: Cycle Detection (No Cycle)
    assert ll.has_cycle() is False, "Test 7 Failed (False positive cycle)"
    print("Test 7 Passed: Confirmed no cycle exists in normal list.")

    # Test 8: Cycle Detection (Cycle Present)
    # Creating a cycle manually: 40 -> 10 -> 5 -> 10 (points back to second node)
    node1 = ll.head
    node2 = node1.next
    node3 = node2.next
    node3.next = node2  # Make last node point to second node
    assert ll.has_cycle() is True, "Test 8 Failed (Undetected cycle)"
    print("Test 8 Passed: Successfully detected cycle.")

    print("🎉 All 8 Linked List tests passed successfully!\n")


if __name__ == "__main__":
    run_linked_list_tests()