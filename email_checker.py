import smtplib
import socket

def smtp_check(email):
    try:
        domain = email.split('@')[1]

        server = smtplib.SMTP(domain, timeout=10)
        server.set_debuglevel(0)

        server.helo()
        server.mail('test@example.com')
        code, message = server.rcpt(email)

        server.quit()
        return code, message.decode() if isinstance(message, bytes) else message

    except (smtplib.SMTPException, socket.error) as e:
        return None, str(e)

if __name__ == "__main__":
    email = input("Enter email address to check: ").strip()

    if "@" not in email:
        print("❌ Invalid email format")
    else:
        code, message = smtp_check(email)

        if code == 250:
            print(f"✅ Email appears to exist ({code})")
        elif code == 550:
            print(f"❌ Email does NOT exist ({code})")
        elif code is None:
            print(f"⚠️ Could not verify email: {message}")
        else:
            print(f"⚠️ Unknown response ({code}): {message}")
