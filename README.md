# Business Management Software

## Objective

This project is a comprehensive desktop application designed to help small to medium-sized businesses manage their daily operations. It provides tools for managing sales, customers, and products, as well as a suite of advanced analytics dashboards to offer insights into business performance. The primary goal is to provide a standalone, all-in-one solution for business management without relying on cloud-based services.

## Technology Stack

*   **Programming Language:** Python
*   **GUI Framework:** PyQt5
*   **Data Analysis and Manipulation:** pandas, numpy
*   **Data Visualization:** matplotlib, squarify
*   **Time Series Forecasting:** Prophet
*   **Database:** SQLite
*   **Fuzzy String Matching:** fuzzywuzzy
*   **Packaging:** PyInstaller

## Features

This application offers a wide range of features to cover various aspects of business management:

*   **Bill Generation:** Create and manage bills for both sales (Debit) and payments (Credit).
*   **Statement Generation:** Generate detailed financial statements for customers over a specified period.
*   **Product Master:** A central module to add, edit, and manage all products.
*   **Bill Deletion:** A secure way to delete incorrect or voided bills.
*   **Exporting:** Export bills and statements to HTML or as an image for printing or sharing.
*   **Fuzzy Search:** Quickly find customers and products with an intelligent fuzzy search.
*   **Analytics Dashboards:**
    *   **Inventory Intelligence:** Track stock levels, view product performance, and manage inventory.
    *   **Customer Profitability:** Analyze which customers are most valuable to your business.
    *   **Expense & Profit/Loss:** Track business expenses and view profit/loss statements.
    *   **Product Analysis:** Get insights into sales trends and product performance.
    *   **Customer Behavior:** Understand customer purchasing patterns and trends.
    *   **Business Overview:** A high-level dashboard summarizing the overall health of the business.
    *   **Sales Forecast:** Use historical data to forecast future sales.
    *   **Advanced Analytics:** A dashboard for custom and in-depth data analysis.

## End User

This software is intended for small to medium-sized business owners, managers, and administrative staff who need a powerful, offline tool to manage their business operations and make data-driven decisions.

## Installation Instructions

1.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python business_management/main.py
    ```

## Usage

Once the application is running, you can use the navigation buttons at the top of the window to switch between the different modules, such as the "Bill Generator," "Product Master," or any of the analytics dashboards.

## License

This project is licensed under the MIT License.
