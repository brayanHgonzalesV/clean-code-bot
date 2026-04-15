"""
Checkout module for e-commerce application.

Provides functionality for calculating prices, printing receipts,
and processing payments, following the Single Responsibility Principle (SRP)
and Open/Closed Principle (OCP).

Example:
    >>> from checkout import OrderProcessor
    >>> items = [{'name': 'Item 1', 'price': 10.00, 'qty': 2}]
    >>> processor = OrderProcessor(tax_rate=0.08)
    >>> total = processor.calculate_price(items)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LineItem:
    """Represents a single line item in an order."""

    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        """Calculates the subtotal for this line item."""
        return self.price * self.quantity


@dataclass
class Receipt:
    """Represents a receipt for an order."""

    items: list[LineItem]
    discount: float
    tax_rate: float

    def __str__(self) -> str:
        """Returns a formatted string representation of the receipt."""
        lines = ["=== RECEIPT ==="]
        for item in self.items:
            lines.append(
                f"{item.name}: ${item.price:.2f} x {item.quantity} = ${item.subtotal:.2f}"
            )
        lines.append("-" * 20)
        lines.append(f"Subtotal: ${self.subtotal:.2f}")
        if self.discount > 0:
            lines.append(f"Discount: -{self.discount * 100:.0f}%")
            lines.append(f"After Discount: ${self.subtotal_after_discount:.2f}")
        lines.append(f"Tax ({self.tax_rate * 100:.0f}%): ${self.tax_amount:.2f}")
        lines.append("=" * 20)
        lines.append(f"Total: ${self.total:.2f}")
        return "\n".join(lines)

    @property
    def subtotal(self) -> float:
        """Calculates the subtotal before discounts and taxes."""
        return sum(item.subtotal for item in self.items)

    @property
    def subtotal_after_discount(self) -> float:
        """Calculates the subtotal after applying discount."""
        return self.subtotal * (1 - self.discount)

    @property
    def tax_amount(self) -> float:
        """Calculates the tax amount."""
        return self.subtotal_after_discount * self.tax_rate

    @property
    def total(self) -> float:
        """Calculates the total including taxes."""
        return self.subtotal_after_discount + self.tax_amount


class PaymentError(Exception):
    """Base exception for payment-related errors."""

    pass


class InvalidCardError(PaymentError):
    """Raised when card information is invalid."""

    pass


class PaymentProcessor:
    """
    Processes payments using credit cards.

    Implements the Strategy pattern for different payment methods,
    following the Open/Closed Principle (OCP) to allow extensible payment processing.
    """

    def process(self, amount: float, card_number: str) -> bool:
        """
        Processes a payment with the given card.

        Args:
            amount: The payment amount.
            card_number: The credit card number (16 digits).

        Returns:
            True if payment was successful.

        Raises:
            InvalidCardError: If the card number is invalid.
        """
        if not self._validate_card(card_number):
            raise InvalidCardError("Invalid card number. Must be 16 digits.")
        print(f"Processing card payment of ${amount:.2f}")
        return True

    def _validate_card(self, card_number: str) -> bool:
        """Validates the card number format."""
        return len(card_number.replace(" ", "")) == 16 and card_number.isdigit()


class OrderProcessor:
    """
    Processes orders including price calculation and receipt generation.

    This class handles the calculation of order totals and generation of receipts,
    following the Single Responsibility Principle (SRP).
    """

    def __init__(self, tax_rate: float = 0.08, discount: float = 0.0) -> None:
        """
        Initializes the OrderProcessor with tax and discount rates.

        Args:
            tax_rate: The tax rate to apply (default 0.08 for 8%).
            discount: The discount rate to apply (default 0.0).
        """
        self.tax_rate = tax_rate
        self.discount = discount

    def calculate_price(self, items: list[dict]) -> float:
        """
        Calculates the total price including discounts and taxes.

        Args:
            items: List of items with 'name', 'price', and 'qty' keys.

        Returns:
            The total price after discounts and taxes.
        """
        subtotal = sum(item["price"] * item["qty"] for item in items)
        if self.discount > 0:
            subtotal *= 1 - self.discount
        return subtotal * (1 + self.tax_rate)

    def generate_receipt(self, items: list[dict]) -> Receipt:
        """
        Generates a receipt for the given items.

        Args:
            items: List of items with 'name', 'price', and 'qty' keys.

        Returns:
            A Receipt instance.
        """
        line_items = [
            LineItem(name=item["name"], price=item["price"], quantity=item["qty"])
            for item in items
        ]
        return Receipt(items=line_items, discount=self.discount, tax_rate=self.tax_rate)


def calculate_price(
    items: list[dict], discount: float = 0, tax_rate: float = 0.08
) -> float:
    """
    Legacy function to calculate the total price.

    This function is maintained for backward compatibility.
    Consider using OrderProcessor for new code.

    Args:
        items: List of items with 'name', 'price', and 'qty' keys.
        discount: Discount rate (default 0).
        tax_rate: Tax rate (default 0.08).

    Returns:
        The total price after discounts and taxes.
    """
    processor = OrderProcessor(tax_rate=tax_rate, discount=discount)
    return processor.calculate_price(items)


def print_receipt(
    items: list[dict], discount: float = 0, tax_rate: float = 0.08
) -> None:
    """
    Legacy function to print a receipt.

    This function is maintained for backward compatibility.
    Consider using OrderProcessor for new code.

    Args:
        items: List of items with 'name', 'price', and 'qty' keys.
        discount: Discount rate (default 0).
        tax_rate: Tax rate (default 0.08).
    """
    processor = OrderProcessor(tax_rate=tax_rate, discount=discount)
    receipt = processor.generate_receipt(items)
    print(receipt)


def process_payment(amount: float, card_number: str) -> bool:
    """
    Legacy function to process a payment.

    This function is maintained for backward compatibility.
    Consider using PaymentProcessor for new code.

    Args:
        amount: The payment amount.
        card_number: The credit card number.

    Returns:
        True if payment was successful.

    Raises:
        InvalidCardError: If the card number is invalid.
    """
    processor = PaymentProcessor()
    return processor.process(amount, card_number)
