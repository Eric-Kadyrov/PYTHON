class Country:
    def __init__(self, name, population):
        self.name = name
        self.population = population

    def add(self, other):
        # Combine the name of both countries with a space in between
        combined_name = f"{self.name} {other.name}"
        # Sum the population of both countries
        combined_population = self.population + other.population
        # Create a new Country object with the combined name and population
        return Country(combined_name, combined_population)

# Create instances for Bosnia and Herzegovina
bosnia = Country('Bosnia', 10_000_000)
herzegovina = Country('Herzegovina', 5_000_000)

# Add Bosnia and Herzegovina together
bosnia_herzegovina = bosnia.add(herzegovina)

# Print the properties of the new country
print("Name:", bosnia_herzegovina.name)  # Output: Bosnia Herzegovina
print("Population:", bosnia_herzegovina.population)  # Output: 15000000