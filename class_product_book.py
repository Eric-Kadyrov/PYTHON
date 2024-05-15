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

# Example usage
book = Book("To Kill a Mockingbird", 19.99, 5, "Harper Lee")
print(book)
book.read()