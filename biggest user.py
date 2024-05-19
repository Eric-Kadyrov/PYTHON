SELECT username, user_id
FROM (
    SELECT r.guest_id AS user_id, u.username, COUNT(*) AS reservation_count
    FROM reservations r
    JOIN users u ON r.guest_id = u.id
    GROUP BY r.guest_id, u.username
    ORDER BY reservation_count DESC
    LIMIT 1
) AS subquery;