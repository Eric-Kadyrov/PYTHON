#insert data in users table
INSERT INTO users (id, username, email, password, user_type) VALUES
(1, 'host1', 'host1@example.com', 'password', 'Host'),
(2, 'host2', 'host2@example.com', 'password', 'Host'),
(3, 'guest1', 'guest1@example.com', 'password', 'Guest'),
(4, 'guest2', 'guest2@example.com', 'password', 'Guest'),
(5, 'guest3', 'guest3@example.com', 'password', 'Guest');

#Insert Data into Rooms Table
INSERT INTO rooms (id, host_id, name, description, residents, price, ac, refrigerator, availability) VALUES
(1, 1, 'Cozy Room', 'A cozy room with a beautiful view.', 2, 100.0, TRUE, TRUE, TRUE),
(2, 1, 'Luxury Suite', 'A luxury suite with all amenities.', 4, 250.0, TRUE, TRUE, TRUE),
(3, 2, 'Budget Room', 'A budget room for short stays.', 1, 50.0, FALSE, FALSE, TRUE);

#Insert Data into Reservations Table
INSERT INTO reservations (id, guest_id, room_id, check_in, check_out) VALUES
(1, 3, 1, '2024-05-01', '2024-05-05'),
(2, 4, 2, '2024-05-10', '2024-05-15'),
(3, 5, 3, '2024-05-20', '2024-05-22');

#Insert Data into Reviews Table
INSERT INTO reviews (id, reservation_id, rating, comment) VALUES
(1, 1, 5, 'Great stay!'),
(2, 2, 4, 'Very comfortable.'),
(3, 3, 3, 'Decent for the price.');