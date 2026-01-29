import smtplib
import socket
import dns.resolver

TIMEOUT = 8  # seconds

def get_mx_hosts(domain: str):
    """Return MX hosts sorted by priority (lowest first)."""
    answers = dns.resolver.resolve(domain, "MX")
    mx = sorted([(r.preference, str(r.exchange).rstrip(".")) for r in answers], key=lambda x: x[0])
    return [host for _, host in mx]

def smtp_rcpt_check(email: str):
    if "@" not in email or email.count("@") != 1:
        return {"status": "invalid_format", "detail": "Email must contain a single '@'."}

    local, domain = email.split("@", 1)

    try:
        mx_hosts = get_mx_hosts(domain)
    except Exception as e:
        return {"status": "no_mx_or_dns_error", "detail": f"MX/DNS lookup failed: {e}"}

    # Try each MX in order, fail fast
    last_error = None
    for mx in mx_hosts:
        try:
            # Explicit timeout prevents indefinite hangs
            with smtplib.SMTP(mx, 25, timeout=TIMEOUT) as server:
                server.set_debuglevel(0)
                server.ehlo_or_helo_if_needed()

                # Some servers require a valid MAIL FROM domain
                server.mail("verify@yourdomain.com")
                code, msg = server.rcpt(email)

                # Normalize message to string
                if isinstance(msg, bytes):
                    msg = msg.decode(errors="replace")

                return {
                    "status": "smtp_response",
                    "mx": mx,
                    "code": code,
                    "message": msg
                }

        except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected,
                smtplib.SMTPHeloError, smtplib.SMTPRecipientsRefused,
                smtplib.SMTPResponseException, OSError) as e:
            last_error = f"{type(e).__name__}: {e}"
            continue

    return {"status": "unverifiable", "detail": last_error, "mx_tried": mx_hosts}

if __name__ == "__main__":
    email = input("Enter email address to check: ").strip()

    result = smtp_rcpt_check(email)

    status = result["status"]
    if status == "invalid_format":
        print("❌ Invalid email format:", result["detail"])
    elif status == "no_mx_or_dns_error":
        print("❌ Domain cannot receive mail:", result["detail"])
    elif status == "smtp_response":
        code = result["code"]
        print(f"MX used: {result['mx']}")
        if code == 250:
            print(f"✅ Likely deliverable (SMTP {code})") 
        elif code in (550, 551, 552, 553, 554):
            print(f"❌ Rejected (SMTP {code}): {result['message']}")
        else:
            print(f"⚠️ Inconclusive (SMTP {code}): {result['message']}")
    else:
        print("⚠️ Could not verify via SMTP (common for Gmail/Yahoo/Outlook).")
        print("Reason:", result.get("detail"))
        print("MX tried:", ", ".join(result.get("mx_tried", [])))
