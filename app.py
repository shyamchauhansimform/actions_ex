"""
Demo application with intentional code quality issues for SonarQube to detect.
"""

import os
import subprocess

# --- Code Smell: Magic numbers ---
def calculate_discount(price):
    if price > 100:
        return price * 0.10
    elif price > 50:
        return price * 0.05
    else:
        return 0

# --- Code Smell: Duplicate code block ---
def process_order(order_id, amount):
    print("Processing order")
    print(f"Order ID: {order_id}")
    print(f"Amount: {amount}")
    discount = calculate_discount(amount)
    total = amount - discount
    print(f"Total: {total}")
    return total

def process_refund(order_id, amount):
    print("Processing refund")
    print(f"Order ID: {order_id}")
    print(f"Amount: {amount}")
    discount = calculate_discount(amount)
    total = amount - discount
    print(f"Total: {total}")
    return total

# --- Bug: Function always returns None when condition is false ---
def get_user_role(user_id):
    if user_id == 1:
        return "admin"
    # Missing return for other cases → returns None implicitly

# --- Vulnerability: Command injection risk ---
def run_report(report_name):
    cmd = "generate_report " + report_name  # Unsanitized input
    subprocess.call(cmd, shell=True)

# --- Code Smell: Deeply nested logic (cognitive complexity) ---
def evaluate(a, b, c, d):
    if a:
        if b:
            if c:
                if d:
                    return "all true"
                else:
                    return "d is false"
            else:
                return "c is false"
        else:
            return "b is false"
    else:
        return "a is false"

# --- Code Smell: Unused variable ---
def compute_total(items):
    unused_var = "I am never used"
    total = sum(items)
    return total


if __name__ == "__main__":
    print(process_order(42, 120))
    print(process_refund(42, 120))
    print(get_user_role(2))
    print(evaluate(True, True, True, False))
    print(compute_total([10, 20, 30]))
