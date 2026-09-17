
from abc import ABC, abstractmethod
from enum import Enum


# ============================================================
# ORDER STATUS
# ============================================================

class OrderStatus(Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# ============================================================
# PAYMENT  (abstraction + polymorphism)
# ============================================================

class Payment(ABC):
    """Acts as the IPayment interface. main app only ever calls
    payment.pay() / payment.refund() — never knows which subclass it has."""

    def __init__(self, amount):
        self._amount = amount
        self._status = False  # True once successfully paid

    @property
    def amount(self):
        return self._amount

    @property
    def is_successful(self):
        return self._status

    @abstractmethod
    def get_payment_method(self):
        pass

    @abstractmethod
    def pay(self):
        pass

    @abstractmethod
    def refund(self):
        pass


class UPI(Payment):
    def get_payment_method(self):
        return "UPI"

    def pay(self):
        self._status = True
        print(f"\u20b9{self._amount:.2f} paid using UPI")
        return True

    def refund(self):
        self._status = False
        print(f"\u20b9{self._amount:.2f} refunded through UPI")


class CreditCard(Payment):
    def get_payment_method(self):
        return "Credit Card"

    def pay(self):
        self._status = True
        print(f"\u20b9{self._amount:.2f} paid using Credit Card")
        return True

    def refund(self):
        self._status = False
        print(f"\u20b9{self._amount:.2f} refunded to Credit Card")


class CashOnDelivery(Payment):
    def get_payment_method(self):
        return "Cash on Delivery"

    def pay(self):
        # Cash is collected at the doorstep, so it stays PENDING, not SUCCESS
        self._status = False
        print("Payment marked PENDING — to be collected as Cash on Delivery")
        return True

    def refund(self):
        print("Cash payments are settled on delivery; nothing to refund before then")


class WalletPayment(Payment):
    """New payment method added WITHOUT touching Payment, Order or Customer
    (beyond Customer already exposing add_funds/deduct_funds)."""

    def __init__(self, amount, customer):
        super().__init__(amount)
        self._customer = customer

    def get_payment_method(self):
        return "Wallet"

    def pay(self):
        try:
            self._customer.deduct_funds(self._amount)
            self._status = True
            print(f"\u20b9{self._amount:.2f} paid using Wallet balance")
            return True
        except ValueError as e:
            print(f"Wallet payment failed: {e}")
            return False

    def refund(self):
        self._customer.add_funds(self._amount)
        self._status = False
        print(f"\u20b9{self._amount:.2f} refunded to Wallet")


# ============================================================
# VEHICLE  (delivery-charge strategy, per spec: charge depends
# on vehicle/distance — this was hard-coded to a flat 40 before)
# ============================================================

class Vehicle(ABC):
    @abstractmethod
    def get_vehicle_type(self):
        pass

    @abstractmethod
    def calculate_delivery_charge(self, distance_km):
        pass


class Bike(Vehicle):
    BASE_FARE = 20
    RATE_PER_KM = 6

    def get_vehicle_type(self):
        return "Bike"

    def calculate_delivery_charge(self, distance_km):
        return self.BASE_FARE + self.RATE_PER_KM * distance_km


class Scooter(Vehicle):
    BASE_FARE = 15
    RATE_PER_KM = 5

    def get_vehicle_type(self):
        return "Scooter"

    def calculate_delivery_charge(self, distance_km):
        return self.BASE_FARE + self.RATE_PER_KM * distance_km


class Cycle(Vehicle):
    BASE_FARE = 10
    RATE_PER_KM = 3

    def get_vehicle_type(self):
        return "Cycle"

    def calculate_delivery_charge(self, distance_km):
        return self.BASE_FARE + self.RATE_PER_KM * distance_km


# ============================================================
# DISCOUNT
# ============================================================

class Discount(ABC):
    @abstractmethod
    def calculate_discount(self, amount):
        pass


class PercentageDiscount(Discount):
    def __init__(self, percentage):
        self._percentage = percentage

    def calculate_discount(self, amount):
        return amount * self._percentage / 100


class FlatDiscount(Discount):
    def __init__(self, flat_amount):
        self._flat_amount = flat_amount

    def calculate_discount(self, amount):
        return min(self._flat_amount, amount)


class NoDiscount(Discount):
    def calculate_discount(self, amount):
        return 0


class FestivalDiscount(Discount):
    """New discount type added without touching Discount or Order."""

    def __init__(self, festival_name, percentage):
        self._festival_name = festival_name
        self._percentage = percentage

    def calculate_discount(self, amount):
        return amount * self._percentage / 100

    @property
    def festival_name(self):
        return self._festival_name


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(ABC):
    @abstractmethod
    def send(self, message):
        pass


class EmailNotification(Notification):
    def send(self, message):
        print(f"[Email] {message}")


class SMSNotification(Notification):
    def send(self, message):
        print(f"[SMS] {message}")


class PushNotification(Notification):
    def send(self, message):
        print(f"[Push] {message}")


# ============================================================
# FOOD ITEM
# ============================================================

class FoodItem:
    def __init__(self, item_id, name, price, category, is_available=True):
        self._id = item_id
        self._name = name
        self._price = price
        self._category = category
        self._is_available = is_available

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @property
    def category(self):
        return self._category

    @property
    def is_available(self):
        return self._is_available

    @is_available.setter
    def is_available(self, value):
        self._is_available = bool(value)

    def __str__(self):
        status = "Available" if self._is_available else "Not Available"
        return f"{self._name} - \u20b9{self._price:.2f} - {self._category} - {status}"


# ============================================================
# ORDER ITEM  (composition building block for Order)
# ============================================================

class OrderItem:
    def __init__(self, food_item, quantity):
        self._food_item = food_item
        self._quantity = quantity

    @property
    def food_item(self):
        return self._food_item

    @property
    def quantity(self):
        return self._quantity

    def total_amount(self):
        return self._food_item.price * self._quantity


# ============================================================
# CART
# ============================================================

class Cart:
    def __init__(self):
        self._items = []

    @property
    def items(self):
        return list(self._items)  # copy — caller can't mutate internals directly

    def add_item(self, food_item, quantity):
        if not food_item.is_available:
            print(f"{food_item.name} is not available")
            return
        self._items.append(OrderItem(food_item, quantity))
        print(f"{quantity} x {food_item.name} added to cart")

    def remove_item(self, food_item):
        for item in self._items:
            if item.food_item.id == food_item.id:
                self._items.remove(item)
                print(f"{food_item.name} removed from cart")
                return
        print("Food item not found in cart")

    def calculate_subtotal(self):
        return sum(item.total_amount() for item in self._items)

    def display(self):
        if self.is_empty():
            print("Cart is empty")
            return
        print("\n----- CART -----")
        for item in self._items:
            print(f"{item.food_item.name} x {item.quantity} = \u20b9{item.total_amount():.2f}")
        print(f"Subtotal: \u20b9{self.calculate_subtotal():.2f}")

    def clear(self):
        self._items.clear()

    def is_empty(self):
        return len(self._items) == 0


# ============================================================
# USER  (inheritance root + method overriding via login())
# ============================================================

class User(ABC):
    def __init__(self, user_id, name, email, phone):
        self._id = user_id
        self._name = name
        self._email = email
        self._phone = phone

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def phone(self):
        return self._phone

    @abstractmethod
    def get_user_type(self):
        pass

    def login(self):
        """Default login. Overridden below by each role."""
        print(f"{self.get_user_type()} '{self._name}' logged in.")
        return True


class Customer(User):
    def __init__(self, user_id, name, email, phone, wallet_balance=0.0):
        super().__init__(user_id, name, email, phone)
        self.cart = Cart()
        self._orders = []
        self._wallet_balance = wallet_balance  # encapsulated: no external setter

    def get_user_type(self):
        return "Customer"

    def login(self):
        print(f"Customer '{self._name}' logged in. Wallet balance: \u20b9{self._wallet_balance:.2f}")
        return True

    @property
    def wallet_balance(self):
        return self._wallet_balance

    def add_funds(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._wallet_balance += amount

    def deduct_funds(self, amount):
        if amount > self._wallet_balance:
            raise ValueError("Insufficient wallet balance")
        self._wallet_balance -= amount

    @property
    def orders(self):
        return list(self._orders)

    def place_order(self, restaurant, discount, delivery_vehicle, distance_km,
                     payment_class, **payment_kwargs):
        if self.cart.is_empty():
            print("Cart is empty")
            return None

        order = Order(
            order_id=len(self._orders) + 1,
            customer=self,
            restaurant=restaurant,
            order_items=self.cart.items,
            discount=discount,
            delivery_vehicle=delivery_vehicle,
            distance_km=distance_km,
        )

        # Payment amount comes from the order itself — one source of truth.
        payment = payment_class(order.total_amount, **payment_kwargs)
        order.attach_payment(payment)

        self._orders.append(order)
        self.cart.clear()
        return order


class Admin(User):
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email, phone)
        self._restaurants = []

    def get_user_type(self):
        return "Admin"

    def login(self):
        print(f"Admin '{self._name}' logged in with full system access.")
        return True

    def add_restaurant(self, restaurant, directory):
        self._restaurants.append(restaurant)
        directory.add_restaurant(restaurant)
        print(f"{restaurant.name} added successfully")

    def remove_restaurant(self, restaurant, directory):
        if restaurant in self._restaurants:
            self._restaurants.remove(restaurant)
            directory.remove_restaurant(restaurant)
            print(f"{restaurant.name} removed successfully")
        else:
            print("Restaurant not found")


class RestaurantOwner(User):
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email, phone)
        self._restaurant = None

    def get_user_type(self):
        return "Restaurant Owner"

    def login(self):
        print(f"Restaurant Owner '{self._name}' logged in.")
        return True

    def assign_restaurant(self, restaurant):
        self._restaurant = restaurant

    def add_food_item(self, food_item):
        if self._restaurant:
            self._restaurant.add_food_item(food_item)

    def remove_food_item(self, food_item):
        if self._restaurant:
            self._restaurant.remove_food_item(food_item)

    def update_price(self, food_item, new_price):
        if self._restaurant:
            self._restaurant.update_price(food_item, new_price)


class DeliveryPartner(User):
    def __init__(self, user_id, name, email, phone, vehicle):
        super().__init__(user_id, name, email, phone)
        self._vehicle = vehicle
        self._available = True
        self._current_order = None

    def get_user_type(self):
        return "Delivery Partner"

    def login(self):
        print(f"Delivery Partner '{self._name}' logged in. Vehicle: {self._vehicle.get_vehicle_type()}")
        return True

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def is_available(self):
        return self._available

    @property
    def current_order(self):
        return self._current_order

    def accept_order(self, order):
        if not self._available:
            print(f"{self._name} is not available")
            return
        if order.status != OrderStatus.PREPARING:
            print("Order is not ready for pickup yet")
            return

        self._current_order = order
        self._available = False
        order.assign_delivery_partner(self)
        order.mark_out_for_delivery()
        print(f"{self._name} accepted Order #{order.id}")

    def deliver_order(self):
        if self._current_order is None:
            print("No order assigned")
            return
        self._current_order.mark_delivered()
        self._current_order = None
        self._available = True


# ============================================================
# RESTAURANT
# ============================================================

class Restaurant:
    def __init__(self, restaurant_id, name, location, owner, cuisines=None):
        self._id = restaurant_id
        self._name = name
        self._location = location
        self._owner = owner
        self._menu = []
        self._cuisines = cuisines or []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def location(self):
        return self._location

    @property
    def owner(self):
        return self._owner

    @property
    def menu(self):
        return list(self._menu)

    @property
    def cuisines(self):
        return list(self._cuisines)

    def add_food_item(self, food_item):
        self._menu.append(food_item)
        print(f"{food_item.name} added to {self._name}")

    def remove_food_item(self, food_item):
        if food_item in self._menu:
            self._menu.remove(food_item)
            print(f"{food_item.name} removed from {self._name}")
        else:
            print("Food item not found")

    def update_price(self, food_item, new_price):
        if food_item not in self._menu:
            print("Food item not found")
            return
        food_item.price = new_price
        print(f"{food_item.name} price updated to \u20b9{new_price:.2f}")

    def display_menu(self):
        print(f"\n----- {self._name} MENU -----")
        if not self._menu:
            print("Menu is empty")
            return
        for item in self._menu:
            status = "Available" if item.is_available else "Not Available"
            print(f"ID: {item.id} | {item.name} | \u20b9{item.price:.2f} | {item.category} | {status}")


class RestaurantDirectory:
    """Holds all restaurants and demonstrates method overloading.

    Python has no native method overloading, so the three signatures
    from the spec:
        SearchRestaurant(name)
        SearchRestaurant(name, location)
        SearchRestaurant(name, location, cuisine)
    are emulated with optional keyword parameters on a single method."""

    def __init__(self):
        self._restaurants = []

    def add_restaurant(self, restaurant):
        self._restaurants.append(restaurant)

    def remove_restaurant(self, restaurant):
        if restaurant in self._restaurants:
            self._restaurants.remove(restaurant)

    def search_restaurant(self, name, location=None, cuisine=None):
        results = [r for r in self._restaurants if name.lower() in r.name.lower()]
        if location:
            results = [r for r in results if r.location.lower() == location.lower()]
        if cuisine:
            results = [r for r in results if cuisine.lower() in [c.lower() for c in r.cuisines]]
        return results


# ============================================================
# ORDER  (composition of OrderItems, encapsulated state machine)
# ============================================================

class Order:
    TAX_RATE = 0.05

    def __init__(self, order_id, customer, restaurant, order_items, discount,
                 delivery_vehicle, distance_km):
        self._id = order_id
        self._customer = customer
        self._restaurant = restaurant
        self._order_items = list(order_items)  # composition: Order owns these
        self._discount = discount
        self._delivery_partner = None
        self._status = OrderStatus.PLACED
        self._payment = None

        self._subtotal = sum(item.total_amount() for item in self._order_items)
        self._discount_amount = discount.calculate_discount(self._subtotal)
        self._delivery_charge = delivery_vehicle.calculate_delivery_charge(distance_km)
        self._tax = (self._subtotal - self._discount_amount) * self.TAX_RATE
        self._total_amount = (
            self._subtotal + self._delivery_charge + self._tax - self._discount_amount
        )

    # ---- read-only properties: no external code can corrupt these ----
    @property
    def id(self):
        return self._id

    @property
    def customer(self):
        return self._customer

    @property
    def restaurant(self):
        return self._restaurant

    @property
    def order_items(self):
        return list(self._order_items)

    @property
    def status(self):
        return self._status

    @property
    def total_amount(self):
        return self._total_amount

    @property
    def payment(self):
        return self._payment

    @property
    def delivery_partner(self):
        return self._delivery_partner

    def attach_payment(self, payment):
        self._payment = payment

    def assign_delivery_partner(self, delivery_partner):
        self._delivery_partner = delivery_partner

    # ---- controlled status transitions (replaces direct order.status = ...) ----
    def confirm(self):
        if self._status != OrderStatus.PLACED:
            print("Order cannot be confirmed")
            return
        self._status = OrderStatus.CONFIRMED
        print(f"Order #{self._id} confirmed")

    def start_preparing(self):
        if self._status != OrderStatus.CONFIRMED:
            print("Order must be confirmed first")
            return
        self._status = OrderStatus.PREPARING
        print(f"Order #{self._id} is being prepared")

    def mark_out_for_delivery(self):
        if self._status != OrderStatus.PREPARING:
            print("Order must be in preparation first")
            return
        self._status = OrderStatus.OUT_FOR_DELIVERY
        print(f"Order #{self._id} is out for delivery")

    def mark_delivered(self):
        if self._status != OrderStatus.OUT_FOR_DELIVERY:
            print("Order must be out for delivery first")
            return
        self._status = OrderStatus.DELIVERED
        print(f"Order #{self._id} delivered successfully")

    def cancel(self):
        if self._status == OrderStatus.DELIVERED:
            print("Delivered order cannot be cancelled")
            return
        self._status = OrderStatus.CANCELLED
        print(f"Order #{self._id} cancelled")

    def display(self):
        print("\n===== ORDER DETAILS =====")
        print(f"Order #{self._id}")
        print(f"Customer: {self._customer.name}")
        print(f"Restaurant: {self._restaurant.name}\n")

        print("Items:")
        for item in self._order_items:
            print(f"  {item.food_item.name:<10} x{item.quantity} = \u20b9{item.total_amount():.2f}")

        print(f"\nSubtotal:        \u20b9{self._subtotal:.2f}")
        print(f"Discount:        \u20b9{self._discount_amount:.2f}")
        print(f"Delivery:        \u20b9{self._delivery_charge:.2f}")
        print(f"Tax:             \u20b9{self._tax:.2f}")
        print(f"Final Amount:    \u20b9{self._total_amount:.2f}")

        if self._payment:
            print(f"\nPayment Method: {self._payment.get_payment_method()}")
            print(f"Payment Status: {'SUCCESS' if self._payment.is_successful else 'PENDING'}")

        print(f"\nOrder Status: {self._status.value}")

        if self._delivery_partner:
            print(f"\nDelivery Partner: {self._delivery_partner.name}")
            print(f"Vehicle: {self._delivery_partner.vehicle.get_vehicle_type()}")


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    print("===== FOOD DELIVERY SYSTEM =====")

    directory = RestaurantDirectory()

    # ---- Users ----
    customer = Customer(1, "Rahul", "rahul@gmail.com", "9876543210", wallet_balance=500)
    owner = RestaurantOwner(2, "Priya", "priya@gmail.com", "9876543211")
    admin = Admin(3, "Admin", "admin@gmail.com", "9876543212")
    rider = DeliveryPartner(4, "Arjun", "arjun@gmail.com", "9876543213", vehicle=Bike())

    # method overriding: each role's login() prints something different
    customer.login()
    owner.login()
    admin.login()
    rider.login()

    # ---- Restaurant + menu ----
    restaurant = Restaurant(201, "Pizza Palace", "Hyderabad", owner, cuisines=["Italian", "Fast Food"])
    admin.add_restaurant(restaurant, directory)
    owner.assign_restaurant(restaurant)

    pizza = FoodItem(101, "Pizza", 400, "Main Course")
    burger = FoodItem(102, "Burger", 200, "Fast Food")
    coke = FoodItem(103, "Coke", 80, "Beverage")

    owner.add_food_item(pizza)
    owner.add_food_item(burger)
    owner.add_food_item(coke)

    restaurant.display_menu()

    # method-overloading demo (name / name+location / name+location+cuisine)
    print("\nSearch 'Pizza':", [r.name for r in directory.search_restaurant("Pizza")])
    print("Search 'Pizza' in Hyderabad:",
          [r.name for r in directory.search_restaurant("Pizza", "Hyderabad")])
    print("Search 'Pizza' in Hyderabad, Italian:",
          [r.name for r in directory.search_restaurant("Pizza", "Hyderabad", "Italian")])

    # ---- Cart ----
    customer.cart.add_item(pizza, 1)
    customer.cart.add_item(burger, 1)
    customer.cart.add_item(coke, 1)
    customer.cart.display()

    # ---- Place order (discount + delivery charge computed from vehicle/distance) ----
    discount = PercentageDiscount(10)
    order = customer.place_order(
        restaurant, discount,
        delivery_vehicle=Bike(), distance_km=5,
        payment_class=UPI,
    )

    order.display()

    order.payment.pay()
    order.confirm()
    order.start_preparing()

    SMSNotification().send(f"Order #{order.id} is being prepared")

    rider.accept_order(order)
    PushNotification().send(f"Order #{order.id} is out for delivery")

    rider.deliver_order()
    EmailNotification().send(f"Order #{order.id} has been delivered!")

    order.display()

    # ============================================================
    # BONUS: proving the "add tomorrow without rewriting today" claim
    # WalletPayment and FestivalDiscount are new subclasses — nothing
    # above (Payment, Discount, Order, Customer) was modified for them.
    # ============================================================

    print("\n\n===== EXTENSIBILITY DEMO (new classes only) =====")

    customer.add_funds(300)  # top up wallet so the WalletPayment below can succeed
    customer.cart.add_item(pizza, 2)
    festival_discount = FestivalDiscount("Diwali Sale", 20)

    order2 = customer.place_order(
        restaurant, festival_discount,
        delivery_vehicle=Scooter(), distance_km=3,
        payment_class=WalletPayment, customer=customer,
    )
    order2.display()
    order2.payment.pay()
    print(f"Remaining wallet balance: \u20b9{customer.wallet_balance:.2f}")