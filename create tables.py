CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    user_type VARCHAR(10) NOT NULL -- Either 'Host' or 'Guest'
);

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    host_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    residents INTEGER NOT NULL,
    price FLOAT NOT NULL,
    ac BOOLEAN DEFAULT FALSE,
    refrigerator BOOLEAN DEFAULT FALSE,
    availability BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (host_id) REFERENCES users(id)
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in DATETIME NOT NULL,
    check_out DATETIME NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    reservation_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);
