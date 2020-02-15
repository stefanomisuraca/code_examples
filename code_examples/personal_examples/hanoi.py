"""Hanoi problem solver with recursion."""
# Use python3
import sys

moves = 0


def move(_from, _to):
    """Move a disk from a column to another."""
    global moves
    moves += 1
    print(f"Move {_from.upper()} to {_to.upper()}")


def hanoi(_disks, _from, helper, _to):
    """Solves hanoi's tower."""
    disks = int(_disks)
    if disks > 0:
        hanoi(disks - 1, _from, _to, helper)
        move(_from, _to)
        hanoi(disks - 1, helper, _from, _to)


hanoi(sys.argv[1], "A", "B", "C")
print(f"Total moves: {moves}")
