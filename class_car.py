class Car:
    def __init__(self, brand, model, year, speed=0):
        self.brand = brand
        self.model = model
        self.year = year
        self.speed = speed  # Initial speed is set to 0 by default

    def accelerate(self):
        self.speed += 5  # Increase speed by 5

    def brake(self):
        # Decrease speed by 5 but ensure it doesn't go below zero
        self.speed = max(0, self.speed - 5)

    def display_speed(self):
        print(f"The current speed of the {self.model} is {self.speed} km/h")

# Example usage:
car = Car('Toyota', 'Corolla', 2022)

# Accelerating the car
car.accelerate()
car.display_speed()  # Output should show speed increased by 5

# Applying brake
car.brake()
car.display_speed()  # Output should show speed decreased by 5

# Testing speed cannot go negative
car.brake()
car.display_speed()  # Speed should be 0, cannot go negative