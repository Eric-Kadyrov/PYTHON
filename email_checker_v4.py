import sys
import smtplib
import socket
import dns.resolver
import dns.exception

TIMEOUT = 6  # seconds (keep small; avoids tarpit)
VERIFY_MODE = "smart"  # "smart" (recommended), "rcpt", "handshake"


def get_mx_hosts(domain: str, timeout: int = TIMEOUT):
    resolver = dns.resolver.Resolver(configure=True)
    resolver.timeout = min(2.0, float(timeout))
    resolver.lifetime = float(timeout)

    try:
        answers = resolver.resolve(domain, "MX")
        mx = sorted([(r.preference, str(r.exchange).rstrip(".")) for r in answers], key=lambda x: x[0])
        hosts = [host for _, host in mx]
        if hosts:
            return hosts
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        pass
    except (dns.resolver.NoNameservers, dns.exception.Timeout) as e:
        raise RuntimeError(f"DNS lookup timed out / no nameservers: {e}")
    except Exception as e:
        raise RuntimeError(f"DNS lookup failed: {e}")

    return [domain]


def is_google_mx(mx_host: str) -> bool:
    mx_host = mx_host.lower()
    return (
        mx_host.endswith(".google.com")
        or mx_host.endswith(".googlemail.com")
        or "aspmx" in mx_host
    )


def smtp_handshake(mx: str):
    """Check connect + banner + EHLO, no RCPT."""
    with smtplib.SMTP(host=mx, port=25, timeout=TIMEOUT) as server:
        if server.sock:
            server.sock.settimeout(TIMEOUT)
        code, banner = server.connect(mx, 25)  # ensures banner read
        server.ehlo_or_helo_if_needed()
        # NOOP confirms server is still responsive
        server.noop()
        return code, banner


def smtp_rcpt(mx: str, email: str):
    """Attempt RCPT TO (often blocked/tarpitted on big providers)."""
    with smtplib.SMTP(host=mx, port=25, timeout=TIMEOUT) as server:
        if server.sock:
            server.sock.settimeout(TIMEOUT)
        server.ehlo_or_helo_if_needed()

        # If STARTTLS is offered, try it (some servers behave better)
        try:
            if server.has_extn("starttls"):
                server.starttls()
                server.ehlo()
        except Exception:
            # ignore TLS failures; continue without TLS
            pass

        server.mail("verify@example.com")
        code, msg = server.rcpt(email)
        if isinstance(msg, bytes):
            msg = msg.decode(errors="replace")
        return code, msg


def check_email(email: str, mode: str = VERIFY_MODE):
    if "@" not in email or email.count("@") != 1:
        return {"status": "invalid_format", "detail": "Email must contain a single '@'."}

    _, domain = email.split("@", 1)
    domain = domain.strip().lower()

    try:
        mx_hosts = get_mx_hosts(domain)
    except Exception as e:
        return {"status": "dns_error", "detail": str(e)}

    last_error = None

    for mx in mx_hosts:
        try:
            google = is_google_mx(mx)

            # SMART mode: avoid RCPT for Google MX because it's usually pointless
            if mode == "smart" and google:
                code, banner = smtp_handshake(mx)
                return {
                    "status": "domain_ok_google_mx",
                    "mx": mx,
                    "code": code,
                    "detail": "Google-hosted domain detected; mailbox-level verification via RCPT is typically blocked.",
                }

            if mode == "handshake":
                code, banner = smtp_handshake(mx)
                return {"status": "handshake_ok", "mx": mx, "code": code}

            # mode == "rcpt" or smart on non-google
            code, msg = smtp_rcpt(mx, email)
            return {"status": "smtp_response", "mx": mx, "code": code, "message": msg}

        except socket.timeout as e:
            last_error = f"timeout talking to {mx}: {e}"
            continue
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError,
                smtplib.SMTPHeloError, smtplib.SMTPResponseException, OSError) as e:
            last_error = f"{type(e).__name__} from {mx}: {e}"
            continue

    return {"status": "unverifiable", "detail": last_error, "mx_tried": mx_hosts}


def main():
    email = sys.argv[1].strip() if len(sys.argv) > 1 else input("Enter email address to check: ").strip()
    result = check_email(email)

    st = result["status"]
    if st == "invalid_format":
        print("❌ Invalid email format:", result["detail"])
    elif st == "dns_error":
        print("❌ DNS error:", result["detail"])
    elif st in ("handshake_ok", "domain_ok_google_mx"):
        print(f"✅ Domain can receive mail (MX responsive): {result['mx']}")
        print("Note:", result.get("detail", "Handshake OK"))
    elif st == "smtp_response":
        print(f"MX used: {result['mx']}")
        code = result["code"]
        if code == 250:
            print(f"✅ RCPT accepted (SMTP {code})")
        elif code in (550, 551, 552, 553, 554):
            print(f"❌ Rejected (SMTP {code}): {result.get('message')}")
        else:
            print(f"⚠️ Inconclusive (SMTP {code}): {result.get('message')}")
    else:
        print("⚠️ Could not verify.")
        print("Reason:", result.get("detail"))
        print("MX tried:", ", ".join(result.get("mx_tried", [])))


if __name__ == "__main__":
    main()
