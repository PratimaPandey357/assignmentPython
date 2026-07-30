"""
Project 6: Inventory & Invoice Management System (IMS)
Complete Implementation
"""

from datetime import datetime
import json


# ============================================================================
# PRODUCT CLASSES
# ============================================================================

class Product:
    """Base class for all products."""

    def __init__(self, name, product_id, price, quantity):
        """
        Initialize product with validation.

        Args:
            name (str): Product name (non-empty)
            product_id (str): Unique product ID
            price (float): Price >= 0
            quantity (int): Stock quantity >= 0

        Raises:
            ValueError: If any validation fails
        """
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Price must be a non-negative number")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Quantity must be a non-negative integer")

        self.name = name
        self.product_id = product_id
        self.price = float(price)
        self.quantity = quantity

    def update_price(self, new_price):
        """Update product price with validation."""
        if not isinstance(new_price, (int, float)) or new_price < 0:
            raise ValueError("Price must be a non-negative number")
        self.price = float(new_price)

    def update_quantity(self, new_quantity):
        """Update product quantity with validation."""
        if not isinstance(new_quantity, int) or new_quantity < 0:
            raise ValueError("Quantity must be a non-negative integer")
        self.quantity = new_quantity

    def get_info(self):
        """Return product info as dictionary."""
        return {
            "name": self.name,
            "product_id": self.product_id,
            "price": self.price,
            "quantity": self.quantity,
            "type": "Product"
        }

    def __str__(self):
        return f"{self.name} (ID: {self.product_id}): ${self.price:.2f} [Stock: {self.quantity}]"

    def __repr__(self):
        return (f"Product(name={self.name!r}, product_id={self.product_id!r}, "
                f"price={self.price}, quantity={self.quantity})")


class PerishableProduct(Product):
    """Perishable product with expiry date."""

    def __init__(self, name, product_id, price, quantity, expiry_date):
        """
        Initialize perishable product.

        Args:
            expiry_date (str): Date string in YYYY-MM-DD format

        Raises:
            ValueError: If expiry_date format is invalid
        """
        super().__init__(name, product_id, price, quantity)

        try:
            datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Expiry date must be in format YYYY-MM-DD")

        self.expiry_date = expiry_date

    def is_expired(self):
        """Return True if product is past its expiry date."""
        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
        return datetime.now() > expiry

    def days_until_expiry(self):
        """Return days until expiry (negative if already expired)."""
        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
        delta = expiry - datetime.now()
        return delta.days

    def get_info(self):
        """Return product info including expiry date."""
        info = super().get_info()
        info["expiry_date"] = self.expiry_date
        info["type"] = "PerishableProduct"
        return info

    def __str__(self):
        base_str = super().__str__()
        status = "EXPIRED" if self.is_expired() else f"Expires: {self.expiry_date}"
        return f"{base_str} [{status}]"

    def __repr__(self):
        return (f"PerishableProduct(name={self.name!r}, product_id={self.product_id!r}, "
                f"price={self.price}, quantity={self.quantity}, expiry_date={self.expiry_date!r})")


class NonPerishableProduct(Product):
    """Non-perishable product with warranty."""

    def __init__(self, name, product_id, price, quantity, warranty_years):
        """
        Initialize non-perishable product.

        Args:
            warranty_years (int): Warranty duration in years (>= 0)

        Raises:
            ValueError: If warranty_years is invalid
        """
        super().__init__(name, product_id, price, quantity)

        if not isinstance(warranty_years, int) or warranty_years < 0:
            raise ValueError("Warranty years must be a non-negative integer")

        self.warranty_years = warranty_years

    def has_warranty(self):
        """Return True if product has a warranty."""
        return self.warranty_years > 0

    def get_info(self):
        """Return product info including warranty years."""
        info = super().get_info()
        info["warranty_years"] = self.warranty_years
        info["type"] = "NonPerishableProduct"
        return info

    def __str__(self):
        base_str = super().__str__()
        warranty_str = (f"{self.warranty_years} year warranty"
                        if self.has_warranty() else "No warranty")
        return f"{base_str} [{warranty_str}]"

    def __repr__(self):
        return (f"NonPerishableProduct(name={self.name!r}, product_id={self.product_id!r}, "
                f"price={self.price}, quantity={self.quantity}, "
                f"warranty_years={self.warranty_years})")


# ============================================================================
# INVOICE CLASSES
# ============================================================================

class Invoice:
    """Invoice containing multiple product items."""

    def __init__(self, invoice_id, tax_rate=0.08):
        """
        Initialize invoice.

        Args:
            invoice_id (str): Unique invoice ID
            tax_rate (float): Tax rate (default 8%)
        """
        self.invoice_id = invoice_id
        self.tax_rate = tax_rate
        self._items = []  # list of {"product": Product, "quantity": int}

    def add_item(self, product, quantity):
        """
        Add product to invoice.

        Args:
            product (Product): Product instance to add
            quantity (int): Quantity to purchase

        Raises:
            ValueError: If quantity is invalid or exceeds available stock
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        if quantity > product.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}'. "
                f"Requested: {quantity}, Available: {product.quantity}"
            )

        # If already in invoice, increase quantity
        for item in self._items:
            if item["product"].product_id == product.product_id:
                new_qty = item["quantity"] + quantity
                if new_qty > product.quantity:
                    raise ValueError(
                        f"Total quantity ({new_qty}) exceeds stock ({product.quantity})"
                    )
                item["quantity"] = new_qty
                return

        self._items.append({"product": product, "quantity": quantity})

    def remove_item(self, product_id):
        """Remove item from invoice by product ID."""
        before = len(self._items)
        self._items = [
            item for item in self._items
            if item["product"].product_id != product_id
        ]
        return len(self._items) < before  # True if something was removed

    def calculate_subtotal(self):
        """Calculate subtotal before tax."""
        return sum(item["product"].price * item["quantity"] for item in self._items)

    def calculate_tax(self):
        """Calculate tax amount."""
        return self.calculate_subtotal() * self.tax_rate

    def calculate_total(self):
        """Calculate total (subtotal + tax)."""
        return self.calculate_subtotal() + self.calculate_tax()

    def get_items(self):
        """Return a shallow copy of the items list."""
        return self._items.copy()

    def __str__(self):
        if not self._items:
            return f"Invoice {self.invoice_id} (empty)"

        lines = [f"\nInvoice ID : {self.invoice_id}"]
        lines.append(f"Tax Rate   : {self.tax_rate * 100:.1f}%")
        lines.append("-" * 52)
        lines.append(f"  {'Product':<22} {'Qty':>5}  {'Unit':>8}  {'Total':>9}")
        lines.append("-" * 52)

        for item in self._items:
            p = item["product"]
            qty = item["quantity"]
            line_total = p.price * qty
            lines.append(f"  {p.name:<22} {qty:>5}  ${p.price:>7.2f}  ${line_total:>8.2f}")

        lines.append("-" * 52)
        lines.append(f"  {'Subtotal':<38} ${self.calculate_subtotal():>8.2f}")
        lines.append(f"  {'Tax (' + str(round(self.tax_rate*100,1)) + '%)':<38} ${self.calculate_tax():>8.2f}")
        lines.append(f"  {'TOTAL':<38} ${self.calculate_total():>8.2f}")
        lines.append("-" * 52)

        return "\n".join(lines)

    def __repr__(self):
        return (f"Invoice(invoice_id={self.invoice_id!r}, "
                f"items={len(self._items)}, total=${self.calculate_total():.2f})")


class InvoiceManager:
    """Manages a collection of invoices."""

    def __init__(self):
        """Initialize with empty invoice list."""
        self.invoices = []

    def create_invoice(self, invoice_id, tax_rate=0.08):
        """
        Create and store a new invoice.

        Returns:
            Invoice: The newly created invoice
        """
        invoice = Invoice(invoice_id, tax_rate)
        self.invoices.append(invoice)
        return invoice

    def get_invoice(self, invoice_id):
        """
        Find invoice by ID.

        Returns:
            Invoice or None
        """
        for invoice in self.invoices:
            if invoice.invoice_id == invoice_id:
                return invoice
        return None

    def list_invoices(self):
        """Return a copy of all invoices."""
        return self.invoices.copy()

    def save_to_file(self, filename):
        """Save all invoices to a JSON file."""
        try:
            data = []
            for invoice in self.invoices:
                invoice_data = {
                    "invoice_id": invoice.invoice_id,
                    "tax_rate": invoice.tax_rate,
                    "items": [
                        {
                            "product": item["product"].get_info(),
                            "quantity": item["quantity"]
                        }
                        for item in invoice.get_items()
                    ]
                }
                data.append(invoice_data)

            with open(filename, "w") as f:
                json.dump(data, f, indent=2)

            print(f"  Invoices saved to {filename}")

        except IOError as e:
            print(f"  Error saving invoices: {e}")

    def load_from_file(self, filename, product_registry=None):
        """
        Load invoices from a JSON file.

        Args:
            filename (str): Path to JSON file
            product_registry (list): Optional list of Product instances
                                     to reconnect invoice items
        """
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            self.invoices = []

            for inv_data in data:
                invoice = Invoice(inv_data["invoice_id"], inv_data["tax_rate"])

                for item_data in inv_data.get("items", []):
                    p_info = item_data["product"]
                    qty    = item_data["quantity"]

                    # Try to find live product in registry
                    matched = None
                    if product_registry:
                        for p in product_registry:
                            if p.product_id == p_info["product_id"]:
                                matched = p
                                break

                    # Reconstruct product object if not found in registry
                    if matched is None:
                        p_type = p_info.get("type", "Product")
                        if p_type == "PerishableProduct":
                            matched = PerishableProduct(
                                p_info["name"], p_info["product_id"],
                                p_info["price"], p_info["quantity"],
                                p_info["expiry_date"]
                            )
                        elif p_type == "NonPerishableProduct":
                            matched = NonPerishableProduct(
                                p_info["name"], p_info["product_id"],
                                p_info["price"], p_info["quantity"],
                                p_info["warranty_years"]
                            )
                        else:
                            matched = Product(
                                p_info["name"], p_info["product_id"],
                                p_info["price"], p_info["quantity"]
                            )

                    invoice._items.append({"product": matched, "quantity": qty})

                self.invoices.append(invoice)

            print(f"  Loaded {len(self.invoices)} invoice(s) from {filename}")

        except FileNotFoundError:
            print(f"  File not found: {filename}")
        except json.JSONDecodeError:
            print(f"  Invalid JSON in {filename}")
        except IOError as e:
            print(f"  Error loading invoices: {e}")

    def __str__(self):
        return f"InvoiceManager: {len(self.invoices)} invoice(s)"


# ============================================================================
# GLOBAL STATE
# ============================================================================

products = []               # List of Product instances
invoice_manager = InvoiceManager()


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def find_product(product_id):
    """Return product with matching ID or None."""
    for p in products:
        if p.product_id == product_id:
            return p
    return None


def print_separator(char="=", width=44):
    print(char * width)


# ============================================================================
# MENUS
# ============================================================================

def display_main_menu():
    print("\n" + "=" * 44)
    print("      Inventory & Invoice Manager")
    print("=" * 44)
    print("  1. Product Management")
    print("  2. Invoice Management")
    print("  3. Save / Load Data")
    print("  4. Exit")
    print("=" * 44)


def display_product_menu():
    print("\n--- Product Management ---")
    print("  1. Add Product")
    print("  2. Update Product")
    print("  3. Remove Product")
    print("  4. Display All Products")
    print("  5. Search Product")
    print("  6. Back to Main Menu")


def display_invoice_menu():
    print("\n--- Invoice Management ---")
    print("  1. Create Invoice")
    print("  2. Add Item to Invoice")
    print("  3. Remove Item from Invoice")
    print("  4. Display Invoice")
    print("  5. List All Invoices")
    print("  6. Back to Main Menu")


def display_save_menu():
    print("\n--- Save / Load Data ---")
    print("  1. Save Data")
    print("  2. Load Data")
    print("  3. Back to Main Menu")


# ============================================================================
# PRODUCT MANAGEMENT
# ============================================================================

def add_product():
    """Prompt user and add a new product to inventory."""
    print("\nAdd Product Type:")
    print("  1. Perishable")
    print("  2. Non-Perishable")

    type_choice = input("Choose type (1/2): ").strip()
    if type_choice not in ("1", "2"):
        print("  Invalid type choice.")
        return

    try:
        name = input("Enter product name: ").strip()
        if not name:
            raise ValueError("Product name cannot be empty.")

        product_id = input("Enter product ID: ").strip()
        if not product_id:
            raise ValueError("Product ID cannot be empty.")

        # Check duplicate ID
        if find_product(product_id):
            print(f"  A product with ID '{product_id}' already exists.")
            return

        price    = float(input("Enter price: $"))
        quantity = int(input("Enter quantity: "))

        if type_choice == "1":
            expiry_date = input("Enter expiry date (YYYY-MM-DD): ").strip()
            product = PerishableProduct(name, product_id, price, quantity, expiry_date)

        else:
            warranty_years = int(input("Enter warranty years (0 for none): "))
            product = NonPerishableProduct(name, product_id, price, quantity, warranty_years)

        products.append(product)
        print(f"\n  Product added successfully!")
        print(f"  {product}")

    except ValueError as e:
        print(f"  Invalid input: {e}")


def update_product():
    """Update price or quantity of an existing product."""
    product_id = input("Enter product ID to update: ").strip()
    product = find_product(product_id)

    if not product:
        print(f"  Product '{product_id}' not found.")
        return

    print(f"  Found: {product}")
    print("  What to update?")
    print("    1. Price")
    print("    2. Quantity")

    choice = input("  Choose (1/2): ").strip()

    try:
        if choice == "1":
            new_price = float(input("  New price: $"))
            product.update_price(new_price)
            print(f"  Price updated. {product}")

        elif choice == "2":
            new_qty = int(input("  New quantity: "))
            product.update_quantity(new_qty)
            print(f"  Quantity updated. {product}")

        else:
            print("  Invalid choice.")

    except ValueError as e:
        print(f"  Invalid input: {e}")


def remove_product():
    """Remove a product from inventory by ID."""
    global products
    product_id = input("Enter product ID to remove: ").strip()
    product = find_product(product_id)

    if not product:
        print(f"  Product '{product_id}' not found.")
        return

    confirm = input(f"  Remove '{product.name}'? (y/n): ").strip().lower()
    if confirm == "y":
        products = [p for p in products if p.product_id != product_id]
        print(f"  Product '{product.name}' removed.")
    else:
        print("  Cancelled.")


def display_all_products():
    """Display all products currently in inventory."""
    if not products:
        print("  No products in inventory.")
        return

    print(f"\n  {'=' * 54}")
    print(f"  {'ALL PRODUCTS':^54}")
    print(f"  {'=' * 54}")
    for i, p in enumerate(products, 1):
        print(f"  {i}. {p}")
    print(f"  {'=' * 54}")
    print(f"  Total: {len(products)} product(s)")


def search_product():
    """Search products by name (case-insensitive) or exact ID."""
    term = input("Enter name or ID to search: ").strip()
    if not term:
        print("  Search term cannot be empty.")
        return

    results = [
        p for p in products
        if term.lower() in p.name.lower() or term == p.product_id
    ]

    if not results:
        print(f"  No products found matching '{term}'.")
    else:
        print(f"\n  Found {len(results)} result(s):")
        for p in results:
            print(f"    {p}")


# ============================================================================
# INVOICE MANAGEMENT
# ============================================================================

def create_invoice():
    """Create a new invoice."""
    invoice_id = input("Enter invoice ID: ").strip()
    if not invoice_id:
        print("  Invoice ID cannot be empty.")
        return

    if invoice_manager.get_invoice(invoice_id):
        print(f"  Invoice '{invoice_id}' already exists.")
        return

    tax_input = input("Enter tax rate (default 8%, press Enter to skip): ").strip()
    try:
        tax_rate = float(tax_input) / 100 if tax_input else 0.08
        if tax_rate < 0:
            raise ValueError("Tax rate cannot be negative.")
    except ValueError as e:
        print(f"  Invalid tax rate: {e}")
        return

    invoice_manager.create_invoice(invoice_id, tax_rate)
    print(f"  Invoice '{invoice_id}' created with {tax_rate*100:.1f}% tax rate.")


def add_item_to_invoice():
    """Add a product item to an existing invoice."""
    invoice_id = input("Enter invoice ID: ").strip()
    invoice = invoice_manager.get_invoice(invoice_id)

    if not invoice:
        print(f"  Invoice '{invoice_id}' not found.")
        return

    if not products:
        print("  No products available.")
        return

    display_all_products()

    product_id = input("Enter product ID to add: ").strip()
    product = find_product(product_id)

    if not product:
        print(f"  Product '{product_id}' not found.")
        return

    try:
        quantity = int(input(f"  Enter quantity (available: {product.quantity}): "))
        invoice.add_item(product, quantity)
        print(f"  Added {quantity}x '{product.name}' to invoice '{invoice_id}'.")

    except ValueError as e:
        print(f"  Error: {e}")


def remove_item_from_invoice():
    """Remove a product from an existing invoice."""
    invoice_id = input("Enter invoice ID: ").strip()
    invoice = invoice_manager.get_invoice(invoice_id)

    if not invoice:
        print(f"  Invoice '{invoice_id}' not found.")
        return

    items = invoice.get_items()
    if not items:
        print("  Invoice is empty.")
        return

    print("  Current items:")
    for item in items:
        print(f"    - {item['product'].name} (ID: {item['product'].product_id}) x{item['quantity']}")

    product_id = input("Enter product ID to remove: ").strip()
    removed = invoice.remove_item(product_id)

    if removed:
        print(f"  Item '{product_id}' removed from invoice '{invoice_id}'.")
    else:
        print(f"  Product '{product_id}' not found in invoice.")


def display_invoice():
    """Display full details of an invoice."""
    invoice_id = input("Enter invoice ID: ").strip()
    invoice = invoice_manager.get_invoice(invoice_id)

    if not invoice:
        print(f"  Invoice '{invoice_id}' not found.")
        return

    print(invoice)


def list_all_invoices():
    """List a summary of all invoices."""
    all_invoices = invoice_manager.list_invoices()

    if not all_invoices:
        print("  No invoices found.")
        return

    print(f"\n  {'=' * 52}")
    print(f"  {'ALL INVOICES':^52}")
    print(f"  {'=' * 52}")
    print(f"  {'ID':<15} {'Items':>6}  {'Subtotal':>10}  {'Total':>10}")
    print(f"  {'-' * 48}")

    for inv in all_invoices:
        print(f"  {inv.invoice_id:<15} {len(inv.get_items()):>6}  "
              f"${inv.calculate_subtotal():>9.2f}  ${inv.calculate_total():>9.2f}")

    print(f"  {'=' * 52}")
    print(f"  Total invoices: {len(all_invoices)}")


# ============================================================================
# SAVE / LOAD DATA
# ============================================================================

def save_data():
    """Save products and invoices to JSON files."""
    filename = input("Enter base filename (default: 'ims_data'): ").strip()
    if not filename:
        filename = "ims_data"

    products_file = filename + "_products.json"
    invoices_file = filename + "_invoices.json"

    # Save products
    try:
        data = [p.get_info() for p in products]
        with open(products_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Products saved to {products_file}")
    except IOError as e:
        print(f"  Error saving products: {e}")

    # Save invoices
    invoice_manager.save_to_file(invoices_file)


def load_data():
    """Load products and invoices from JSON files."""
    global products

    filename = input("Enter base filename (default: 'ims_data'): ").strip()
    if not filename:
        filename = "ims_data"

    products_file = filename + "_products.json"
    invoices_file = filename + "_invoices.json"

    # Load products
    try:
        with open(products_file, "r") as f:
            data = json.load(f)

        loaded_products = []
        for p_info in data:
            p_type = p_info.get("type", "Product")
            try:
                if p_type == "PerishableProduct":
                    p = PerishableProduct(
                        p_info["name"], p_info["product_id"],
                        p_info["price"], p_info["quantity"],
                        p_info["expiry_date"]
                    )
                elif p_type == "NonPerishableProduct":
                    p = NonPerishableProduct(
                        p_info["name"], p_info["product_id"],
                        p_info["price"], p_info["quantity"],
                        p_info["warranty_years"]
                    )
                else:
                    p = Product(
                        p_info["name"], p_info["product_id"],
                        p_info["price"], p_info["quantity"]
                    )
                loaded_products.append(p)
            except (KeyError, ValueError) as e:
                print(f"  Skipping invalid product entry: {e}")

        products = loaded_products
        print(f"  Loaded {len(products)} product(s) from {products_file}")

    except FileNotFoundError:
        print(f"  File not found: {products_file}")
    except json.JSONDecodeError:
        print(f"  Invalid JSON in {products_file}")
    except IOError as e:
        print(f"  Error loading products: {e}")

    # Load invoices (pass live products for relinking)
    invoice_manager.load_from_file(invoices_file, product_registry=products)


# ============================================================================
# SUBMENUS
# ============================================================================

def product_menu():
    """Handle the product management submenu loop."""
    while True:
        display_product_menu()
        choice = input("\n  Choose an option: ").strip()

        if   choice == "1": add_product()
        elif choice == "2": update_product()
        elif choice == "3": remove_product()
        elif choice == "4": display_all_products()
        elif choice == "5": search_product()
        elif choice == "6": break
        else:
            print("  Invalid choice. Please enter 1-6.")


def invoice_menu():
    """Handle the invoice management submenu loop."""
    while True:
        display_invoice_menu()
        choice = input("\n  Choose an option: ").strip()

        if   choice == "1": create_invoice()
        elif choice == "2": add_item_to_invoice()
        elif choice == "3": remove_item_from_invoice()
        elif choice == "4": display_invoice()
        elif choice == "5": list_all_invoices()
        elif choice == "6": break
        else:
            print("  Invalid choice. Please enter 1-6.")


def save_load_menu():
    """Handle the save/load submenu loop."""
    while True:
        display_save_menu()
        choice = input("\n  Choose an option: ").strip()

        if   choice == "1": save_data()
        elif choice == "2": load_data()
        elif choice == "3": break
        else:
            print("  Invalid choice. Please enter 1-3.")


# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main program entry point."""
    print("\n  Welcome to the Inventory & Invoice Management System!")

    while True:
        display_main_menu()

        try:
            choice = input("\n  Choose an option: ").strip()

            if   choice == "1": product_menu()
            elif choice == "2": invoice_menu()
            elif choice == "3": save_load_menu()
            elif choice == "4":
                print("\n  Goodbye! Exiting IMS.\n")
                break
            else:
                print("  Invalid choice. Please enter 1-4.")

        except KeyboardInterrupt:
            print("\n\n  Interrupted. Exiting IMS.\n")
            break


if __name__ == "__main__":
    main()


# ============================================================================
# TESTING SECTION (uncomment to test individual components)
# ============================================================================

# --- Test 1: Product base class ---
# p1 = Product("Laptop", "P001", 999.99, 10)
# print(p1)
# print(repr(p1))

# --- Test 2: Invalid Product (should raise ValueError) ---
# try:
#     p2 = Product("", "P002", 50, 5)
# except ValueError as e:
#     print(f"Caught: {e}")
# try:
#     p3 = Product("Item", "P003", -10, 5)
# except ValueError as e:
#     print(f"Caught: {e}")

# --- Test 3: PerishableProduct ---
# pp = PerishableProduct("Milk", "PP001", 4.99, 50, "2026-07-20")
# print(pp)
# print(f"Expired: {pp.is_expired()}")
# print(f"Days until expiry: {pp.days_until_expiry()}")
# print(pp.get_info())

# --- Test 4: NonPerishableProduct ---
# np = NonPerishableProduct("Keyboard", "NP001", 79.99, 20, 2)
# print(np)
# print(f"Has warranty: {np.has_warranty()}")
# print(np.get_info())

# --- Test 5: Invoice ---
# inv = Invoice("INV001", 0.08)
# p1 = Product("Mouse", "P001", 25.99, 10)
# p2 = Product("Monitor", "P002", 299.99, 5)
# inv.add_item(p1, 2)
# inv.add_item(p2, 1)
# print(inv)

# --- Test 6: Insufficient stock ---
# try:
#     inv.add_item(p2, 10)
# except ValueError as e:
#     print(f"Caught: {e}")

# --- Test 7: InvoiceManager ---
# mgr = InvoiceManager()
# i1 = mgr.create_invoice("INV001", 0.08)
# i2 = mgr.create_invoice("INV002", 0.10)
# print(mgr)
# print(mgr.get_invoice("INV001"))
# print(mgr.get_invoice("INV999"))

# --- Test 8: Save/Load ---
# mgr.save_to_file("test_invoices.json")
# mgr2 = InvoiceManager()
# mgr2.load_from_file("test_invoices.json")
