#!/usr/bin/env python3
"""
Secure Password Generator
- Uses Python's 'secrets' for cryptographically strong randomness.
- Validates user inputs and ensures at least one char from each selected set.
- Optional: generate multiple passwords, exclude ambiguous chars, save to file.
"""

import string
import math
import secrets
from datetime import datetime
from typing import Dict, Tuple

# Character sets
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SPECIAL = "!@#$%^&*"

# Ambiguous characters to optionally exclude
AMBIGUOUS = set("0Ool1I|`'\"{}[]()/\\;:,.<>~")

def prompt_yes_no(msg: str, default: str = "y") -> bool:
    default = default.lower().strip()
    suffix = " [Y/n]: " if default == "y" else " [y/N]: "
    while True:
        ans = input(msg + suffix).strip().lower()
        if ans == "" and default in ("y", "n"):
            return default == "y"
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")

def prompt_int(msg: str, min_value: int = None, default: int = None) -> int:
    while True:
        raw = input(f"{msg}{' ['+str(default)+']' if default is not None else ''}: ").strip()
        if raw == "" and default is not None:
            return default
        if raw.isdigit():
            val = int(raw)
            if min_value is not None and val < min_value:
                print(f"Please enter an integer >= {min_value}.")
                continue
            return val
        print("Please enter a valid integer.")

def build_charset(include_lower: bool, include_upper: bool, include_digits: bool,
                  include_special: bool, exclude_ambiguous: bool) -> Dict[str, str]:
    pools = {}
    if include_lower:
        pools["lower"] = LOWER
    if include_upper:
        pools["upper"] = UPPER
    if include_digits:
        pools["digits"] = DIGITS
    if include_special:
        pools["special"] = SPECIAL

    if exclude_ambiguous:
        def filt(s: str) -> str:
            return "".join(c for c in s if c not in AMBIGUOUS)
        pools = {k: filt(v) for k, v in pools.items()}

        # Safety: if filtering removed an entire pool, drop it
        pools = {k: v for k, v in pools.items() if v}

    return pools

def generate_password(length: int, pools: Dict[str, str]) -> str:
    if not pools:
        raise ValueError("No character types available to generate password.")

    # Ensure at least one character from each selected pool (coverage)
    chosen = [secrets.choice(chars) for chars in pools.values()]

    # Fill the rest from the union
    union = "".join(pools.values())
    remaining = [secrets.choice(union) for _ in range(length - len(chosen))]
    candidates = chosen + remaining

    # Secure shuffle
    for i in range(len(candidates) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        candidates[i], candidates[j] = candidates[j], candidates[i]

    return "".join(candidates)

def estimate_entropy(length: int, pools: Dict[str, str]) -> float:
    # Entropy ~ length * log2(|alphabet|)
    alphabet_size = len(set("".join(pools.values())))
    if alphabet_size <= 1:
        return 0.0
    return length * math.log2(alphabet_size)

def strength_label(length: int, used_types: int, entropy_bits: float) -> str:
    # Heuristic thresholds considering modern guidance
    if length >= 16 and used_types >= 3 and entropy_bits >= 90:
        return "Strong"
    if length >= 12 and used_types >= 2 and entropy_bits >= 70:
        return "Medium"
    return "Weak"

def summarize_types(pools: Dict[str, str]) -> Tuple[int, str]:
    mapping = {"lower": "lowercase", "upper": "uppercase", "digits": "numbers", "special": "special"}
    keys = list(pools.keys())
    return len(keys), ", ".join(mapping[k] for k in ["lower", "upper", "digits", "special"] if k in keys)

def main():
    print("=== Password Generator ===")

    # Collect preferences
    length = prompt_int("Enter password length (minimum 8)", min_value=8, default=12)

    include_lower = prompt_yes_no("Include lowercase letters?", "y")
    include_upper = prompt_yes_no("Include uppercase letters?", "y")
    include_digits = prompt_yes_no("Include numbers?", "y")
    include_special = prompt_yes_no("Include special characters (!@#$%^&*)?", "y")

    if not any([include_lower, include_upper, include_digits, include_special]):
        print("You must include at least one character type. Exiting.")
        return

    exclude_ambiguous = prompt_yes_no("Exclude ambiguous characters (0,O,o,l,1,I,|, etc.)?", "y")
    count = prompt_int("How many passwords to generate", min_value=1, default=1)

    pools = build_charset(include_lower, include_upper, include_digits, include_special, exclude_ambiguous)
    used_types, used_types_list = summarize_types(pools)

    passwords = []
    for _ in range(count):
        pwd = generate_password(length, pools)
        ent = estimate_entropy(length, pools)
        label = strength_label(length, used_types, ent)
        passwords.append((pwd, ent, label))

    # Display results
    for idx, (pwd, ent, label) in enumerate(passwords, start=1):
        header = f"Generated Password: {pwd}" if count == 1 else f"[{idx}] {pwd}"
        print("\n" + header)
        print(f"Password Strength: {label}")
        print(f"Character types used: {used_types}/4 ({used_types_list})")
        print(f"Estimated entropy: {ent:.1f} bits")

    # Optional: save to file
    if prompt_yes_no("\nSave passwords to a file?", "n"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"passwords_{timestamp}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"# Generated on {datetime.now().isoformat(timespec='seconds')}\n")
            f.write(f"# Length: {length}, Types: {used_types_list}, Ambiguous excluded: {exclude_ambiguous}\n")
            for i, (pwd, ent, label) in enumerate(passwords, start=1):
                f.write(f"{i}. {pwd}  |  {label}  |  {ent:.1f} bits\n")
        print(f"Saved to {fname}")

if __name__ == "__main__":
    main()