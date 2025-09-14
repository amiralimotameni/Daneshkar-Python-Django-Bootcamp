####### ChatGPT #######


from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json
import os
import sys
from getpass import getpass

# ---------- Data Models ----------

@dataclass
class Product:
    """Represents a store product."""
    name: str
    price: float
    stock: int
    category: str = "General"

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("Price cannot be negative.")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative.")
        self.name = self.name.strip()

    def __str__(self) -> str:
        return f"{self.name} - ${self.price:.2f} (Stock: {self.stock})"


@dataclass
class CartItem:
    """Represents a product entry inside a shopping cart."""
    product: Product
    quantity: int

    def subtotal(self) -> float:
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity} - ${self.subtotal():.2f}"


class Store:
    """Represents the store inventory and utilities to manage it."""
    def __init__(self) -> None:
        self.products: List[Product] = []

    # ---- Inventory management ----
    def add_product(self, name: str, price: float, stock: int, category: str = "General") -> Product:
        existing = self.find_product(name)
        if existing:
            # If product exists, update its price/stock/category
            existing.price = price
            existing.stock += stock
            existing.category = category or existing.category
            return existing
        product = Product(name=name, price=price, stock=stock, category=category or "General")
        self.products.append(product)
        return product

    def list_products(self) -> List[Product]:
        return list(self.products)

    def find_product(self, name: str) -> Optional[Product]:
        name_norm = name.strip().lower()
        for p in self.products:
            if p.name.lower() == name_norm:
                return p
        return None

    # ---- Persistence ----
    def to_json(self) -> Dict[str, Any]:
        return {"products": [asdict(p) for p in self.products]}

    def from_json(self, data: Dict[str, Any]) -> None:
        self.products = [Product(**p) for p in data.get("products", [])]

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> "Store":
        store = Store()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                store.from_json(data)
        return store


class Cart:
    """Represents a shopping cart with typical cart operations."""
    def __init__(self) -> None:
        self.items: List[CartItem] = []

    def _find_item(self, product_name: str) -> Optional[CartItem]:
        name_norm = product_name.strip().lower()
        for it in self.items:
            if it.product.name.lower() == name_norm:
                return it
        return None

    def add_to_cart(self, product: Product, quantity: int) -> bool:
        """Add product to cart if enough stock is available. Decrements stock on success."""
        if quantity <= 0:
            print("Quantity must be positive.")
            return False
        if product.stock < quantity:
            print("Not enough stock available.")
            return False

        product.stock -= quantity  # reduce stock immediately (like sample)
        existing = self._find_item(product.name)
        if existing:
            existing.quantity += quantity
        else:
            self.items.append(CartItem(product=product, quantity=quantity))
        return True

    def remove_from_cart(self, product_name: str) -> bool:
        """Remove a product from the cart entirely and restore its stock."""
        item = self._find_item(product_name)
        if not item:
            return False
        # restore stock
        item.product.stock += item.quantity
        self.items.remove(item)
        return True

    def view_cart(self) -> None:
        if not self.items:
            print("🛒 Your cart is empty.")
            return
        print("🛒 Your cart:")
        for it in self.items:
            print(f" - {it}")
        print(f"\n💰 Total: ${self.total_price():.2f}")

    def total_price(self) -> float:
        return sum(it.subtotal() for it in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def clear(self) -> None:
        self.items.clear()


# ---------- User History (Bonus) ----------

class UserDB:
    """Simple JSON-based user purchase history store."""
    def __init__(self, path: str) -> None:
        self.path = path
        self.data: Dict[str, Any] = {"users": {}}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {"users": {}}

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_purchase(self, username: str, items: List[CartItem], total: float) -> None:
        user = self.data["users"].setdefault(username, {"history": []})
        user["history"].append({
            "items": [{"name": it.product.name, "quantity": it.quantity, "price": it.product.price} for it in items],
            "total": total
        })
        self.save()

    def print_history(self, username: str) -> None:
        user = self.data["users"].get(username)
        if not user or not user.get("history"):
            print("No purchase history yet.")
            return
        print(f"📜 Purchase history for {username}:")
        for i, rec in enumerate(user["history"], start=1):
            print(f"  {i}.")
            for it in rec["items"]:
                print(f"     - {it['name']} x{it['quantity']} - ${it['price'] * it['quantity']:.2f}")
            print(f"     Total: ${rec['total']:.2f}")


# ---------- CLI Utilities ----------

STORE_DB_PATH = "store_data.json"
USERS_DB_PATH = "users.json"


def pause() -> None:
    input("\nPress Enter to continue...")


def clear_screen() -> None:
    # Best effort clear in different OS environments
    os.system("cls" if os.name == "nt" else "clear")


def header(title: str) -> None:
    print("--------------------------------")
    print(f"{title}")
    print("--------------------------------")


def format_products(store: Store) -> None:
    products = store.list_products()
    if not products:
        print("No products yet.")
        return
    # Group by category
    by_cat: Dict[str, List[Product]] = {}
    for p in products:
        by_cat.setdefault(p.category, []).append(p)
    print("Available products:")
    idx = 1
    for cat, plist in by_cat.items():
        print(f"  [{cat}]")
        for p in plist:
            print(f"   [{idx}] {p}")
            idx += 1


# ---------- Manager Flow ----------

def manager_login() -> bool:
    header("🔐 Store Manager Login")
    username = input("Username: ").strip()
    password = getpass("Password: ")
    if username == "admin" and password == "1234":
        print("\n✅ Login successful! Welcome, Manager.")
        return True
    print("\n❌ Login failed! Please try again or return to main menu.")
    return False


def manager_portal(store: Store) -> None:
    if not manager_login():
        pause()
        return

    while True:
        clear_screen()
        header("📦 Manager Portal")
        print("1. Add products")
        print("2. List products")
        print("3. Save inventory")
        print("4. Load inventory")
        print("5. Back to main menu")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_products_flow(store)
        elif choice == "2":
            clear_screen()
            header("📦 Product List")
            format_products(store)
            pause()
        elif choice == "3":
            store.save(STORE_DB_PATH)
            print(f"✅ Inventory saved to {STORE_DB_PATH}")
            pause()
        elif choice == "4":
            new_store = Store.load(STORE_DB_PATH)
            store.products = new_store.products
            print(f"✅ Inventory loaded from {STORE_DB_PATH}")
            pause()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
            pause()


def add_products_flow(store: Store) -> None:
    clear_screen()
    header("📦 Add Products")
    while True:
        name = input("Enter product name (or 'done' to finish): ").strip()
        if name.lower() == "done":
            print("Returning to manager menu...")
            pause()
            break
        try:
            price_str = input("Enter product price: ").strip()
            price = float(price_str)
            stock_str = input("Enter product stock quantity: ").strip()
            stock = int(stock_str)
            category = input("Enter category (default 'General'): ").strip() or "General"
            product = store.add_product(name=name, price=price, stock=stock, category=category)
            print(f"\n✅ Product added/updated: {product}")
        except ValueError as e:
            print(f"❌ Error: {e}")


# ---------- Customer Flow ----------

def customer_portal(store: Store, users: UserDB) -> None:
    clear_screen()
    header("🛍️ CUSTOMER PORTAL")
    username = input("Enter your name (for history): ").strip() or "guest"
    cart = Cart()

    while True:
        print("--------------------")
        print(f"Hello, {username}!")
        format_products(store)
        print("\nWhat would you like to do?")
        print("1. Add item to cart")
        print("2. Remove item from cart")
        print("3. View cart")
        print("4. Checkout")
        print("5. View my purchase history")
        print("6. Return to main menu")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            pname = input("Enter product name: ").strip()
            product = store.find_product(pname)
            if not product:
                print("Product not found.")
                continue
            try:
                qty = int(input("Enter quantity: ").strip())
            except ValueError:
                print("Invalid quantity.")
                continue
            if cart.add_to_cart(product, qty):
                print(f"✅ Added {qty} x {product.name} to cart.")
        elif choice == "2":
            pname = input("Enter product name to remove: ").strip()
            if cart.remove_from_cart(pname):
                print(f"🗑️ Removed {pname} from cart.")
            else:
                print("Item not found in cart.")
        elif choice == "3":
            clear_screen()
            cart.view_cart()
            pause()
        elif choice == "4":
            if cart.is_empty():
                print("Your cart is empty.")
                continue
            clear_screen()
            print("🧾 Final Checkout:")
            for it in cart.items:
                print(f" - {it}")
            total = cart.total_price()
            print(f"\n💳 Total amount due: ${total:.2f}")
            confirm = input("Proceed to payment? (y/n): ").strip().lower()
            if confirm == "y":
                users.record_purchase(username=username, items=cart.items, total=total)
                cart.clear()
                print("🎉 Thank you for shopping with us!")
                pause()
                break
            else:
                print("Checkout canceled.")
        elif choice == "5":
            clear_screen()
            users.print_history(username)
            pause()
        elif choice == "6":
            print("Returning to main menu...")
            pause()
            break
        else:
            print("Invalid choice.")


# ---------- Main App Loop ----------

def main() -> None:
    store = Store.load(STORE_DB_PATH)
    users = UserDB(USERS_DB_PATH)

    while True:
        clear_screen()
        print("=================================")
        print("🛍️  MINI STORE MANAGEMENT SYSTEM")
        print("=================================\n")
        print("👋 Welcome! Please select your role:")
        print("1. Store Manager")
        print("2. Customer")
        print("3. Exit Program")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            manager_portal(store)
        elif choice == "2":
            customer_portal(store, users)
        elif choice == "3":
            print("\n👋 Goodbye! See you next time.")
            break
        else:
            print("Invalid choice.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting... Bye!")


