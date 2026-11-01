from decimal import Decimal

from django.test import TestCase

from .models import Item
from .tools import add_item, calculate_cost, check_stock, set_price


class PriceToolTests(TestCase):
    def setUp(self):
        Item.objects.create(name="Chocolate Bar", quantity=20, price=Decimal("2.50"))

    def test_check_stock_includes_price(self):
        self.assertEqual(check_stock("chocolate bar")["price"], 2.5)

    def test_add_item_with_price(self):
        result = add_item("Hammer", 5, price=12.99)
        self.assertTrue(result["created"])
        self.assertEqual(Item.objects.get(name="Hammer").price, Decimal("12.99"))

    def test_restock_keeps_price_when_omitted(self):
        add_item("Chocolate Bar", 10)
        item = Item.objects.get(name="Chocolate Bar")
        self.assertEqual(item.quantity, 30)
        self.assertEqual(item.price, Decimal("2.50"))

    def test_set_price(self):
        set_price("Chocolate Bar", 3)
        self.assertEqual(Item.objects.get(name="Chocolate Bar").price, Decimal("3.00"))

    def test_set_price_rejects_negative(self):
        self.assertIn("error", set_price("Chocolate Bar", -1))

    def test_cost_of_3_chocolate_bars_with_10_percent_vat(self):
        result = calculate_cost("Chocolate Bar", 3, vat_percent=10)
        self.assertEqual(result["subtotal"], 7.5)
        self.assertEqual(result["vat_amount"], 0.75)
        self.assertEqual(result["total"], 8.25)

    def test_cost_without_vat(self):
        self.assertEqual(calculate_cost("Chocolate Bar", 3)["total"], 7.5)

    def test_cost_unknown_item(self):
        self.assertIn("error", calculate_cost("Unicorn", 1))

    def test_cost_warns_when_not_enough_stock(self):
        self.assertIn("warning", calculate_cost("Chocolate Bar", 100))
