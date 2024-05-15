class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"Product: {self.name}, Price: ${self.price}, Quantity: {self.quantity}"

class Book(Product):
    def __init__(self, name, price, quantity, author):
        super().__init__(name, price, quantity)
        self.author = author

    def read(self):
        print(f"Reading '{self.name}' by {self.author}.")

    def __str__(self):
        return super().__str__() + f", Author: {self.author}"

class Restaurant:
    def __init__(self, name, cuisine, menu):
        self.name = name
        self.cuisine = cuisine
        self.menu = menu

    def __str__(self):
        return f"Restaurant: {self.name}, Cuisine: {self.cuisine}, Menu: {self.menu}"

class FastFood(Restaurant):
    def __init__(self, name, cuisine, menu, drive_thru):
        super().__init__(name, cuisine, menu)
        self.drive_thru = drive_thru

    def order(self, dish_name, quantity):
        if dish_name not in self.menu:
            return "Dish not available"
        dish = self.menu[dish_name]
        if quantity > dish['quantity']:
            return "Requested quantity not available"
        dish['quantity'] -= quantity
        return dish['price'] * quantity

# Example usage
menu = {
    'burger': {'price': 5, 'quantity': 10},
    'pizza': {'price': 10, 'quantity': 20},
    'drink': {'price': 1, 'quantity': 15}
}

mc = FastFood('McDonalds', 'Fast Food', menu, True)
print(mc.order('burger', 5))  # 25
print(mc.order('burger', 15))  # Requested quantity not available
print(mc.order('soup', 5))  # Dish not available