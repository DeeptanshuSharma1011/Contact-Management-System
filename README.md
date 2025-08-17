# Contact Management System (C++ Console App)

A simple **console-based Contact Management System** written in **C++17**. This project demonstrates basic CRUD operations with persistent storage in a plain text file.

## Features

- Add a new contact (name, phone number, email)
- View all contacts in a tabular format
- Edit an existing contact
- Delete a contact
- Search contacts by name, phone, or email
- Persistent storage in contacts.txt
- Each contact has a unique numeric ID

## Installation & Usage

1. Clone this repository:
   git clone https://github.com/your-username/contact-management-system-cpp.git
   cd contact-management-system-cpp

2. Build the program:
   g++ -std=c++17 -o contact_manager main.cpp

3. Run the program:
   ./contact_manager

4. Follow the on-screen menu to manage your contacts.

## File Structure
contact-management-system-cpp/
├── main.cpp         # Console application source code
├── contacts.txt     # Data file for storing contacts (auto-created)
└── README.md        # Project documentation
