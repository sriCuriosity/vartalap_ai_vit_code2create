# Bill Management System

A Python-based bill management system with a PyQt5 GUI interface.

## Features

- Generate bills for sales (Debit) and payments (Credit)
- Generate customer statements
- Fuzzy search for items
- Export bills and statements as HTML/Images
- SQLite database for data persistence

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/main.py
```

## Project Structure

```
project_root/
├── src/
│   ├── main.py                 # Application entry point
│   ├── database/
│   │   └── db_manager.py       # Database operations
│   ├── ui/
│   │   ├── bill_generator.py   # Bill generation UI
│   │   └── statement_generator.py  # Statement generation UI
│   ├── models/
│   │   └── bill.py            # Bill data models
│   └── utils/
│       └── constants.py        # Application constants
├── templates/                  # HTML templates
├── requirements.txt           # Project dependencies
└── README.md                 # This file
```

## Usage

1. **Generating Bills**
   - Select customer
   - Choose transaction type (Debit/Credit)
   - Add items (for Debit) or enter amount (for Credit)
   - Generate bill

2. **Generating Statements**
   - Select date range
   - Choose customer (optional)
   - Generate statement

## Development

The project follows a modular structure:
- `models/`: Data structures and business logic
- `ui/`: User interface components
- `database/`: Database operations
- `utils/`: Utility functions and constants

## Building the Windows Executable

To build a standalone Windows EXE:

1. Make sure you have Python and pip installed.
2. Open a command prompt in the project directory.
3. Run:
   ```
   build_exe.bat
   ```
4. The EXE will be created in the `dist` folder as `BusinessManagement.exe`.

The EXE will work on any Windows machine and will correctly handle all data files (database, templates, etc.).

## License

This project is licensed under the MIT License. 