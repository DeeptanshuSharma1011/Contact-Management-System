from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

DATA_FILE = os.path.join(os.path.dirname(__file__), "contacts.json")
BACKUP_FILE = DATA_FILE + ".bak"

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_CLEAN = re.compile(r"[^0-9+()\-\s]")


@dataclass
class Contact:
    id: int
    name: str
    phone: str
    email: str


class ContactManager:
    def __init__(self, path: str = DATA_FILE) -> None:
        self.path = path
        self._contacts: List[Contact] = []
        self._load()

    # ----------------------------- Persistence ----------------------------- #
    def _load(self) -> None:
        if not os.path.exists(self.path):
            self._contacts = []
            self._save()  # create empty file
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._contacts = [Contact(**item) for item in raw]
        except Exception as e:
            # Backup the corrupted file and start fresh to keep app usable
            try:
                if os.path.exists(self.path):
                    os.replace(self.path, BACKUP_FILE)
                print(f"[WARN] Data file corrupted or unreadable. Backed up to {BACKUP_FILE}. Starting fresh.\nDetail: {e}")
            except Exception:
                pass
            self._contacts = []
            self._save()

    def _save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([asdict(c) for c in self._contacts], f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)

    # ------------------------------ Utilities ------------------------------ #
    def _next_id(self) -> int:
        return (max((c.id for c in self._contacts), default=0) + 1)

    @staticmethod
    def validate_name(name: str) -> bool:
        return bool(name.strip())

    @staticmethod
    def validate_email(email: str) -> bool:
        return bool(EMAIL_REGEX.match(email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        if PHONE_CLEAN.search(phone):
            return False
        digits = re.sub(r"\D", "", phone)
        # Basic sanity: allow 7-15 digits (common E.164 max=15)
        return 7 <= len(digits) <= 15

    # ------------------------------ CRUD Logic ----------------------------- #
    def add_contact(self, name: str, phone: str, email: str) -> Contact:
        contact = Contact(id=self._next_id(), name=name.strip(), phone=phone.strip(), email=email.strip())
        self._contacts.append(contact)
        self._save()
        return contact

    def list_contacts(self, sort_by: str = "name") -> List[Contact]:
        valid = {"id", "name", "phone", "email"}
        key = sort_by if sort_by in valid else "name"
        return sorted(self._contacts, key=lambda c: getattr(c, key, ""))

    def find_by_id(self, contact_id: int) -> Optional[Contact]:
        return next((c for c in self._contacts if c.id == contact_id), None)

    def update_contact(self, contact_id: int, *, name: Optional[str] = None,
                       phone: Optional[str] = None, email: Optional[str] = None) -> Optional[Contact]:
        c = self.find_by_id(contact_id)
        if not c:
            return None
        if name is not None and name.strip():
            c.name = name.strip()
        if phone is not None and phone.strip():
            c.phone = phone.strip()
        if email is not None and email.strip():
            c.email = email.strip()
        self._save()
        return c

    def delete_contact(self, contact_id: int) -> bool:
        before = len(self._contacts)
        self._contacts = [c for c in self._contacts if c.id != contact_id]
        deleted = len(self._contacts) < before
        if deleted:
            self._save()
        return deleted

    def search(self, query: str) -> List[Contact]:
        q = query.strip().lower()
        if not q:
            return []
        return [c for c in self._contacts if q in c.name.lower() or q in c.phone.lower() or q in c.email.lower()]


# ---------------------------- Console UI Helpers ---------------------------- #

def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_table(rows: List[Dict[str, Any]], headers: List[str]) -> None:
    if not rows:
        print("(no records)")
        return
    # Compute column widths
    cols = headers
    widths = [len(h) for h in cols]
    for r in rows:
        for i, c in enumerate(cols):
            widths[i] = max(widths[i], len(str(r.get(c, ""))))
    # Print header
    line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(cols))
    print(line)
    print("-+-".join("-" * w for w in widths))
    # Print rows
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[i]) for i, c in enumerate(cols)))


# ------------------------------ Input Flows -------------------------------- #

def prompt_nonempty(label: str, *, default: Optional[str] = None) -> str:
    while True:
        val = input(f"{label}{' [' + default + ']' if default else ''}: ").strip()
        if not val and default is not None:
            return default
        if val:
            return val
        print("  Value cannot be empty. Try again.")


def prompt_email(label: str, *, default: Optional[str] = None) -> str:
    while True:
        email = input(f"{label}{' [' + default + ']' if default else ''}: ").strip() or (default or "")
        if ContactManager.validate_email(email):
            return email
        print("  Invalid email format. Example: user@example.com")


def prompt_phone(label: str, *, default: Optional[str] = None) -> str:
    while True:
        phone = input(f"{label}{' [' + default + ']' if default else ''}: ").strip() or (default or "")
        if ContactManager.validate_phone(phone):
            return phone
        print("  Invalid phone. Allowed: digits, + ( ), - spaces; length 7-15 digits.")


def action_add(cm: ContactManager) -> None:
    print_header("Add New Contact")
    name = prompt_nonempty("Name")
    phone = prompt_phone("Phone")
    email = prompt_email("Email")
    c = cm.add_contact(name, phone, email)
    print(f"\n[OK] Added contact with ID {c.id}.")


def action_list(cm: ContactManager) -> None:
    print_header("All Contacts")
    sort_by = input("Sort by (id/name/phone/email) [name]: ").strip().lower() or "name"
    contacts = cm.list_contacts(sort_by=sort_by)
    rows = [asdict(c) for c in contacts]
    print_table(rows, headers=["id", "name", "phone", "email"])


def action_edit(cm: ContactManager) -> None:
    print_header("Edit Contact")
    try:
        cid = int(prompt_nonempty("Enter Contact ID"))
    except ValueError:
        print("  ID must be a number.")
        return
    c = cm.find_by_id(cid)
    if not c:
        print("  Contact not found.")
        return
    print("Leave a field empty to keep the current value.")
    new_name = input(f"Name [{c.name}]: ").strip()
    new_phone = input(f"Phone [{c.phone}]: ").strip()
    new_email = input(f"Email [{c.email}]: ").strip()

    # Validate only when provided; otherwise keep old
    if new_name and not ContactManager.validate_name(new_name):
        print("  Invalid name.")
        return
    if new_phone and not ContactManager.validate_phone(new_phone):
        print("  Invalid phone.")
        return
    if new_email and not ContactManager.validate_email(new_email):
        print("  Invalid email.")
        return

    updated = cm.update_contact(cid,
                                name=new_name or None,
                                phone=new_phone or None,
                                email=new_email or None)
    if updated:
        print("  [OK] Contact updated.")
    else:
        print("  Update failed.")


def action_delete(cm: ContactManager) -> None:
    print_header("Delete Contact")
    try:
        cid = int(prompt_nonempty("Enter Contact ID"))
    except ValueError:
        print("  ID must be a number.")
        return
    c = cm.find_by_id(cid)
    if not c:
        print("  Contact not found.")
        return
    confirm = input(f"Are you sure you want to delete '{c.name}' (ID {c.id})? [y/N]: ").strip().lower()
    if confirm == 'y':
        if cm.delete_contact(cid):
            print("  [OK] Contact deleted.")
        else:
            print("  Delete failed.")
    else:
        print("  Cancelled.")


def action_search(cm: ContactManager) -> None:
    print_header("Search Contacts")
    q = prompt_nonempty("Enter search text (name/phone/email)")
    results = cm.search(q)
    if not results:
        print("  No matches.")
        return
    rows = [asdict(c) for c in results]
    print_table(rows, headers=["id", "name", "phone", "email"])


# --------------------------------- Menu ----------------------------------- #
MENU = {
    "1": ("Add contact", action_add),
    "2": ("View contacts", action_list),
    "3": ("Edit contact", action_edit),
    "4": ("Delete contact", action_delete),
    "5": ("Search contacts", action_search),  # optional convenience
    "0": ("Exit", None),
}


def main(argv: List[str] | None = None) -> int:
    cm = ContactManager()
    while True:
        print_header("Contact Management System")
        for key in sorted(MENU.keys()):
            print(f" {key}. {MENU[key][0]}")
        choice = input("\nChoose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            return 0
        action = MENU.get(choice)
        if not action:
            print("\n[!] Invalid option. Please try again.")
            continue
        try:
            func = action[1]
            if func:
                func(cm)
        except KeyboardInterrupt:
            print("\n[!] Operation cancelled by user.")
        except Exception as e:
            print(f"\n[ERROR] {e}")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
