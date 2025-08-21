# 📊 Datasette Data Uploader
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/StanleyPangaruy/data-uploader-st)

A Streamlit web application for managing data in a [Datasette](https://datasette.io/) instance. This tool provides a user-friendly interface to upload data from CSV or Excel files, create new tables, insert, update, and delete rows without writing any SQL.

## Features

- **Connect to any Datasette Instance**: Works with any public or private (token-protected) Datasette URL.
- **Create Tables**: Upload a CSV or Excel file to create a new table in a selected database.
- **Insert Rows**: Append new data from a CSV or Excel file into an existing table.
- **Update Rows**: Modify existing records in a table by uploading a file containing the primary key(s) and the columns to be updated.
- **Delete Rows**: Remove specific rows from a table by providing their primary key(s).
- **Drop Tables**: Permanently delete a table and all its data from a database.
- **Data Preview**: Preview your data within the app before performing any write operation.
- **Schema Viewer**: View the schema of existing tables to ensure data compatibility.

## How to Run Locally

### Prerequisites
- Python 3.12+
- `uv` (or `pip`) package installer

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/stanleypangaruy/data-uploader-st.git
    cd data-uploader-st
    ```

2.  **Install dependencies:**
    This project uses `uv`. You can install the dependencies using:
    ```bash
    uv pip install -r requirements.txt
    # or if you have uv installed, you can sync with the lock file
    uv pip sync
    ```
    Alternatively, if you prefer `pip`:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    Your web browser should open a new tab with the application running.

## Usage

1.  **Configure Connection**:
    -   Open the application in your browser.
    -   In the sidebar, enter the full URL of your Datasette instance (e.g., `https://your-datasette.datasette.io`).
    -   If your Datasette instance requires authentication, enter the API token in the "API Token" field.

2.  **Select an Operation**:
    -   Use the main dropdown menu to choose an operation: "Create New Table", "Insert Rows to Existing Table", "Update Rows", "Delete Rows", or "Drop Table".

3.  **Follow On-Screen Instructions**:
    -   **For Create/Insert/Update**: Select the target database and table (if applicable), then upload your CSV or Excel file. The app will show a preview. Click the action button to proceed.
    -   **For Delete**: Select the database and table, specify the primary key column(s), and enter the values for the row you wish to delete.
    -   **For Drop**: Select the database and table, and check the confirmation box to enable the "Drop Table" button.

## Datasette Configuration for Write Operations

This tool requires the `datasette-write` and `datasette-auth-tokens` plugins to be installed and configured on your Datasette instance.