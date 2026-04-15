def calculate_price(items, discount=0, tax_rate=0.08):
    total = 0
    for item in items:
        total = total + (item["price"] * item["qty"])
    if discount > 0:
        total = total - (total * discount)
    total = total + (total * tax_rate)
    return total


def print_receipt(items, discount=0, tax_rate=0.08):
    print("=== RECEIPT ===")
    for item in items:
        subtotal = item["price"] * item["qty"]
        print(f"{item['name']}: ${item['price']} x {item['qty']} = ${subtotal}")
    total = calculate_price(items, discount, tax_rate)
    print(f"Total: ${total}")


def process_payment(amount, card_number):
    if len(card_number) == 16:
        print(f"Processing card payment of ${amount}")
        return True
    return False
