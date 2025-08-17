#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>

struct Contact {
    int id;
    std::string name;
    std::string phone;
    std::string email;
};

std::vector<Contact> contacts;
const std::string DATA_FILE = "contacts.txt";

// Utility to trim whitespace
std::string trim(const std::string &s) {
    size_t start = s.find_first_not_of(" \t\n\r");
    if (start == std::string::npos) return "";
    size_t end = s.find_last_not_of(" \t\n\r");
    return s.substr(start, end - start + 1);
}

// Load contacts from file
void loadContacts() {
    contacts.clear();
    std::ifstream infile(DATA_FILE);
    if (!infile.is_open()) return; // file not exist, skip

    std::string line;
    while (std::getline(infile, line)) {
        std::stringstream ss(line);
        Contact c;
        std::getline(ss, line, '|'); c.id = std::stoi(line);
        std::getline(ss, c.name, '|');
        std::getline(ss, c.phone, '|');
        std::getline(ss, c.email, '|');
        contacts.push_back(c);
    }
}

// Save contacts to file
void saveContacts() {
    std::ofstream outfile(DATA_FILE);
    for (const auto &c : contacts) {
        outfile << c.id << "|" << c.name << "|" << c.phone << "|" << c.email << "\n";
    }
}

int nextId() {
    int maxId = 0;
    for (const auto &c : contacts) {
        if (c.id > maxId) maxId = c.id;
    }
    return maxId + 1;
}

void addContact() {
    Contact c;
    c.id = nextId();
    std::cout << "Enter name: ";
    std::getline(std::cin, c.name);
    std::cout << "Enter phone: ";
    std::getline(std::cin, c.phone);
    std::cout << "Enter email: ";
    std::getline(std::cin, c.email);
    contacts.push_back(c);
    saveContacts();
    std::cout << "[OK] Contact added with ID " << c.id << "\n";
}

void listContacts() {
    std::cout << "\nID | Name           | Phone         | Email\n";
    std::cout << "----------------------------------------------\n";
    for (const auto &c : contacts) {
        std::cout << c.id << " | " << c.name << " | " << c.phone << " | " << c.email << "\n";
    }
    if (contacts.empty()) {
        std::cout << "(no contacts)\n";
    }
}

void editContact() {
    std::cout << "Enter contact ID to edit: ";
    int id; std::cin >> id; std::cin.ignore();
    for (auto &c : contacts) {
        if (c.id == id) {
            std::string input;
            std::cout << "Enter new name (leave blank to keep: " << c.name << "): ";
            std::getline(std::cin, input);
            if (!trim(input).empty()) c.name = input;

            std::cout << "Enter new phone (leave blank to keep: " << c.phone << "): ";
            std::getline(std::cin, input);
            if (!trim(input).empty()) c.phone = input;

            std::cout << "Enter new email (leave blank to keep: " << c.email << "): ";
            std::getline(std::cin, input);
            if (!trim(input).empty()) c.email = input;

            saveContacts();
            std::cout << "[OK] Contact updated.\n";
            return;
        }
    }
    std::cout << "Contact not found.\n";
}

void deleteContact() {
    std::cout << "Enter contact ID to delete: ";
    int id; std::cin >> id; std::cin.ignore();
    auto it = std::remove_if(contacts.begin(), contacts.end(), [&](const Contact &c){ return c.id == id; });
    if (it != contacts.end()) {
        contacts.erase(it, contacts.end());
        saveContacts();
        std::cout << "[OK] Contact deleted.\n";
    } else {
        std::cout << "Contact not found.\n";
    }
}

void searchContacts() {
    std::cout << "Enter search term: ";
    std::string q; std::getline(std::cin, q);
    q = trim(q);
    bool found = false;
    for (const auto &c : contacts) {
        if (c.name.find(q) != std::string::npos ||
            c.phone.find(q) != std::string::npos ||
            c.email.find(q) != std::string::npos) {
            std::cout << c.id << " | " << c.name << " | " << c.phone << " | " << c.email << "\n";
            found = true;
        }
    }
    if (!found) std::cout << "No matching contacts.\n";
}

void menu() {
    while (true) {
        std::cout << "\n==============================\n";
        std::cout << "Contact Management System\n";
        std::cout << "==============================\n";
        std::cout << "1. Add Contact\n";
        std::cout << "2. View Contacts\n";
        std::cout << "3. Edit Contact\n";
        std::cout << "4. Delete Contact\n";
        std::cout << "5. Search Contacts\n";
        std::cout << "0. Exit\n";
        std::cout << "Choose an option: ";
        int choice; std::cin >> choice; std::cin.ignore();
        switch(choice) {
            case 1: addContact(); break;
            case 2: listContacts(); break;
            case 3: editContact(); break;
            case 4: deleteContact(); break;
            case 5: searchContacts(); break;
            case 0: std::cout << "Goodbye!\n"; return;
            default: std::cout << "Invalid choice.\n";
        }
    }
}

int main() {
    loadContacts();
    menu();
    return 0;
}