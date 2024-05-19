SELECT u.username AS hostname, u.id AS host_id
FROM users u
JOIN rooms r ON u.id = r.host_id
JOIN reservations res ON r.id = res.room_id
WHERE u.user_type = 'Host' AND strftime('%Y-%m', res.check_in) = strftime('%Y-%m', 'now', 'start of month', '-1 month')
GROUP BY u.username, u.id
ORDER BY SUM(r.price * (julianday(res.check_out) - julianday(res.check_in))) DESC
LIMIT 1;