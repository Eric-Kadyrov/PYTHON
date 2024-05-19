from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.org import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # Either 'Host' or 'Guest'
    
    # Relationships
    rooms = relationship("Room", back_populates="host")
    reservations = relationship("Reservation", back_populates="guest")

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    residents = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    ac = Column(Boolean, default=False)
    refrigerator = Column(Boolean, default=False)
    availability = Column(Boolean, default=True)
    
    # Relationships
    host = relationship("User", back_populates="rooms")
    reservations = relationship("Reservation", back_populates="room")

class Reservation(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    
    # Relationships
    guest = relationship("User", back_populates="reservations")
    room = relationship("Room", back_populates="reservations")
    reviews = relationship("Review", back_populates="reservation")

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    
    # Relationships
    reservation = relationship("Reservation", back_populates="reviews")

# Database setup
engine = create_engine('sqlite:///airbnb.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def prompt_and_store_reservation(session):
    # Prompt for user input
    username = input("Enter your username: ")
    room_id = int(input("Enter the room number (ID): "))
    check_in_date = input("Enter check-in date (YYYY-MM-DD): ")
    check_out_date = input("Enter check-out date (YYYY-MM-DD): ")
    
    # Convert input dates to datetime objects
    check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
    check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
    
    # Find the guest user
    guest = session.query(User).filter_by(username=username, user_type='Guest').first()
    if not guest:
        print(f"Guest with username '{username}' not found.")
        return
    
    # Check if the room is available
    room = session.query(Room).filter_by(id=room_id).first()
    if not room:
        print(f"Room with ID '{room_id}' not found.")
        return
    
    if not room.availability:
        print(f"Room with ID '{room_id}' is not available.")
        return
    
    # Create and store the reservation
    reservation = Reservation(guest_id=guest.id, room_id=room.id, check_in=check_in, check_out=check_out)
    session.add(reservation)
    session.commit()
    
    print("Reservation successfully created.")

# Example usage
if __name__ == "__main__":
    # Add a host
    host = User(username='host1', email='host1@example.com', password='password', user_type='Host')
    session.add(host)
    session.commit()
    
    # Add a room
    room = Room(host_id=host.id, name='Cozy Room', description='A cozy room with a beautiful view.', residents=2, price=100.0, ac=True, refrigerator=True)
    session.add(room)
    session.commit()
    
    # Add a guest
    guest = User(username='guest1', email='guest1@example.com', password='password', user_type='Guest')
    session.add(guest)
    session.commit()
    
    # Prompt for reservation details and store them
    prompt_and_store_reservation(session)
    
    # Example review (not part of the prompt function)
    reservation = session.query(Reservation).filter_by(guest_id=guest.id).first()
    review = Review(reservation_id=reservation.id, rating=5, comment='Great stay!')
    session.add(review)
    session.commit()