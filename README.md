# 📊 Datasette Data Uploader

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
- [`uv`](https://docs.astral.sh/uv/) package manager

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/stanleypangaruy/data-uploader-st.git
   cd data-uploader-st
   ```

2. **Install dependencies:**
   
   This project uses `uv` and includes a `pyproject.toml` file with all dependencies:
   
   ```bash
   uv sync
   ```
   
   This will create a virtual environment and install all required packages automatically.

3. **Run the Streamlit application:**
   ```bash
   uv run streamlit run app.py
   ```
   
   Your web browser should open a new tab with the application running.

## Usage

1. **Configure Connection**:
   - Open the application in your browser.
   - In the sidebar, enter the full URL of your Datasette instance (e.g., `https://your-datasette.datasette.io`).
   - If your Datasette instance requires authentication, enter the API token in the "API Token" field.

2. **Select an Operation**:
   - Use the main dropdown menu to choose an operation: "Create New Table", "Insert Rows to Existing Table", "Update Rows", "Delete Rows", or "Drop Table".

3. **Follow On-Screen Instructions**:
   - **For Create/Insert/Update**: Select the target database and table (if applicable), then upload your CSV or Excel file. The app will show a preview. Click the action button to proceed.
   - **For Delete**: Select the database and table, specify the primary key column(s), and enter the values for the row you wish to delete.
   - **For Drop**: Select the database and table, and check the confirmation box to enable the "Drop Table" button.

## Datasette Configuration for Write Operations

This tool requires the `datasette-write` and `datasette-auth-tokens` plugins to be installed and configured on your Datasette instance.

### Required Datasette Plugins

1. **datasette-write**: Enables write operations (create, insert, update, delete)
2. **datasette-auth-tokens**: Provides API token authentication

### Installation on your Datasette instance:

```bash
datasette install datasette-write datasette-auth-tokens
```

### Configuration

Add the following to your Datasette configuration file:

```yaml
plugins:
  datasette-auth-tokens:
    tokens:
      - token: "your-secret-token-here"
        actor:
          id: "your-user-id"
        permissions:
          - "create-table"
          - "insert-row" 
          - "update-row"
          - "delete-row"
          - "drop-table"
```

## Development

### Project Structure

```
data-uploader-st/
├── app.py              # Main Streamlit application
├── pyproject.toml      # Project dependencies and configuration
├── uv.lock            # Dependency lock file
└── README.md          # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit them
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Running in Development

For development with auto-reload:

```bash
uv run streamlit run app.py --server.runOnSave true
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Datasette documentation](https://docs.datasette.io/)
2. Review the [datasette-write plugin documentation](https://datasette.io/plugins/datasette-write)
3. Open an issue on this repository