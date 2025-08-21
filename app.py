import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO
import sqlite3
from typing import Dict, List, Any, Optional
import urllib.parse

# Configure Streamlit page
st.set_page_config(
    page_title="Datasette Data Uploader",
    page_icon="📊",
    layout="wide"
)

class DatasetteUploader:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {}
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
    
    def get_databases(self) -> List[str]:
        """Get list of databases from Datasette instance"""
        try:
            response = requests.get(f"{self.base_url}/.json")
            if response.status_code == 200:
                data = response.json()
                return list(data.get('databases', {}))
            return []
        except Exception as e:
            st.error(f"Error fetching databases: {e}")
            return []
    
    def get_tables(self, database: str) -> List[str]:
        """Get list of tables from a specific database"""
        try:
            response = requests.get(f"{self.base_url}/{database}.json")
            if response.status_code == 200:
                data = response.json()
                return [table['name'] for table in data.get('tables', [])]
            return []
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            return []
    
    def get_table_schema(self, database: str, table: str) -> Dict:
        """Get table schema information"""
        try:
            response = requests.get(f"{self.base_url}/{database}/{table}.json?_=schema")
            if response.status_code == 200:
                data = response.json()
                return data.get('rows', [])
            return []
        except Exception as e:
            st.error(f"Error fetching table schema: {e}")
            return []
    
    def create_table(self, database: str, table_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a new table with data from DataFrame"""
        try:
            # Convert DataFrame to records for JSON payload
            records = df.to_dict('records')
            
            # Create table payload
            payload = {
                "table": table_name,
                "rows": records
            }
            
            # Make API call to create table
            response = requests.post(
                f"{self.base_url}/{database}/-/create",
                headers={**self.headers, 'Content-Type': 'application/json'},
                json=payload,
            )
            
            return {
                'success': response.status_code in [200, 201],
                'status_code': response.status_code,
                'response': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def insert_rows(self, database: str, table: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Insert rows into existing table"""
        try:
            records = df.to_dict('records')
            
            payload = {
                "rows": records
            }
            
            response = requests.post(
                f"{self.base_url}/{database}/{table}/-/insert",
                headers={**self.headers, 'Content-Type': 'application/json'},
                json=payload
            )
            
            return {
                'success': response.status_code in [200, 201],
                'status_code': response.status_code,
                'response': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def drop_table(self, database: str, table: str, confirm: bool = False) -> Dict[str, Any]:
        """Drop a table from the given database."""
        try:
            url = f"{self.base_url}/{database}/{table}/-/drop"
            payload = {"confirm": True} if confirm else {}

            response = requests.post(
                url,
                headers={**self.headers, 'Content-Type': 'application/json'},
                json=payload
            )

            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_rows(self, database: str, table: str, pk_values: List[str], updates: Dict[str, Any], return_row: bool = True) -> Dict[str, Any]:
        """Update a row in a table by primary key(s)."""
        try:
            # Tilde-encode PKs (Datasette requirement)
            row_pks = ",".join([urllib.parse.quote(pk, safe="") for pk in pk_values])

            url = f"{self.base_url}/{database}/{table}/{row_pks}/-/update"
            payload = {
                "update": updates
            }
            if return_row:
                payload["return"] = True

            response = requests.post(
                url,
                headers={**self.headers, 'Content-Type': 'application/json'},
                json=payload
            )

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


    def delete_rows(self, database: str, table: str, row_pks: List[Any]) -> Dict[str, Any]:
        """
        Delete a row by primary key(s) from a Datasette table.
        - database: name of the Datasette database
        - table: table name
        - row_pks: list of primary key values (single value for single PK, list for composite PK)
        """
        try:
            # Tilde-encode PKs (Datasette requirement: ~ becomes ~~ , / becomes ~s , etc.)
            def tilde_encode(value: str) -> str:
                return (
                    str(value)
                    .replace("~", "~~")
                    .replace("/", "~s")
                    .replace(",", "~c")
                    .replace("?", "~q")
                    .replace("#", "~h")
                )

            if isinstance(row_pks, (list, tuple)):
                pk_path = ",".join([tilde_encode(str(pk)) for pk in row_pks])
            else:
                pk_path = tilde_encode(str(row_pks))

            url = f"{self.base_url}/{database}/{table}/{pk_path}/-/delete"
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            resp = requests.post(url, headers=headers, json={})
            resp.raise_for_status()

            return resp.json()

        except Exception as e:
            return {"ok": False, "error": str(e)}

    
    def get_table_rows(self, database: str, table: str) -> pd.DataFrame:
        """Fetch rows from a table"""
        try:
            url = f"{self.base_url}/{database}/{table}.json?_shape=array"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data) if data else pd.DataFrame()
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching table rows: {e}")
            return pd.DataFrame()


def load_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Load data from uploaded file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def main():
    st.title("📊 Datasette Data Uploader")
    st.markdown("Upload and manage data in your Datasette instance")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Initialize session state for persistent URL
    if 'datasette_url' not in st.session_state:
        st.session_state.datasette_url = ""
    if 'token' not in st.session_state:
        st.session_state.token = ""
    
    # URL input with session state
    datasette_url = st.sidebar.text_input(
        "Datasette Instance URL",
        value=st.session_state.datasette_url,
        placeholder="https://your-datasette-instance.com",
        help="Enter the base URL of your Datasette instance"
    )
    
    # Update session state
    if datasette_url:
        st.session_state.datasette_url = datasette_url
    
    # Token input (optional)
    token = st.sidebar.text_input(
        "API Token (optional)",
        value=st.session_state.token,
        type="password",
        help="Enter your Datasette API token if authentication is required"
    )
    
    if token:
        st.session_state.token = token
    
    if not datasette_url:
        st.warning("Please enter your Datasette instance URL in the sidebar to get started.")
        return
    
    # Initialize uploader
    uploader = DatasetteUploader(datasette_url, token if token else None)
    
    # Main operation selection
    st.header("Select Operation")
    
    operation = st.selectbox(
        "What would you like to do?",
        [
            "Create New Table",
            "Insert Rows to Existing Table",
            "Update Rows",
            "Drop Table",
            "Delete Rows"
        ]
    )
    
    st.divider()
    
    if operation == "Create New Table":
        st.subheader("📋 Create New Table")
        
        # Get databases
        databases = uploader.get_databases()
        if not databases:
            st.error("Could not fetch databases. Please check your Datasette URL and connection.")
            return
        
        database = st.selectbox("Select Database", databases)
        table_name = st.text_input("Table Name", placeholder="my_new_table")
        
        uploaded_file = st.file_uploader(
            "Upload Data File",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file containing the data for your new table"
        )
        
        if uploaded_file and table_name:
            df = load_file(uploaded_file)
            if df is not None:
                st.write("**Preview of data to be uploaded:**")
                st.dataframe(df.head())
                st.write(f"Total rows: {len(df)}")
                
                if st.button("Create Table", type="primary"):
                    with st.spinner("Creating table..."):
                        result = uploader.create_table(database, table_name, df)
                    
                    if result.get('success'):
                        st.success(f"✅ Table '{table_name}' created successfully!")
                        # st.info(f"You can view your table at: {datasette_url}/{database}/{table_name}")
                    else:
                        st.error(f"❌ Failed to create table: {result.get('error', result.get('response', 'Unknown error'))}")
    
    elif operation == "Insert Rows to Existing Table":
        st.subheader("➕ Insert Rows to Existing Table")
        
        # Get databases
        databases = uploader.get_databases()
        if not databases:
            st.error("Could not fetch databases. Please check your Datasette URL and connection.")
            return
        
        database = st.selectbox("Select Database", databases)
        
        # Get tables for selected database
        tables = uploader.get_tables(database) if database else []
        if not tables:
            st.warning("No tables found in the selected database.")
            return
        
        table = st.selectbox("Select Table", tables)
        schema = uploader.get_table_schema(database, table)
        if schema:
            schema_df = pd.DataFrame(schema)
            st.write("**Table Schema:**")
            st.dataframe(schema_df)

        
        
        uploaded_file = st.file_uploader(
            "Upload Data File",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file containing the rows to insert"
        )
        
        if uploaded_file and table:
            df = load_file(uploaded_file)
            if df is not None:
                st.write("**Preview of data to be inserted:**")
                st.dataframe(df.head())
                st.write(f"Total rows to insert: {len(df)}")
                
                # Show table schema for reference
                # schema = uploader.get_table_schema(database, table)
                # if schema:
                #     st.write("**Current table columns:**")
                #     col_names = [col['name'] for col in schema]
                #     st.write(", ".join(col_names))
                
                if st.button("Insert Rows", type="primary"):
                    with st.spinner("Inserting rows..."):
                        result = uploader.insert_rows(database, table, df)
                    
                    if result.get('success'):
                        st.success(f"✅ Successfully inserted {len(df)} rows into '{table}'!")
                        # st.info(f"View updated table at: {datasette_url}/{database}/{table}")
                        updated_df = uploader.get_table_rows(database, table)
                        if not updated_df.empty:
                            st.write("**Updated Table:**")
                            st.dataframe(updated_df)
                    else:
                        st.error(f"❌ Failed to insert rows: {result.get('error', result.get('response', 'Unknown error'))}")
    
    elif operation == "Drop Table":
        st.subheader("🗑️ Drop Table")
        st.warning("⚠️ This operation will permanently delete the table and all its data!")
        
        databases = uploader.get_databases()
        if not databases:
            st.error("Could not fetch databases. Please check your Datasette URL and connection.")
            return
        
        database = st.selectbox("Select Database", databases)
        tables = uploader.get_tables(database) if database else []
        
        if tables:
            table = st.selectbox("Select Table to Drop", tables)
            
            confirm = st.checkbox("I understand this will permanently delete the table and all its data")
            
            if confirm and st.button("Drop Table", type="primary"):
                with st.spinner("Dropping table..."):
                    result = uploader.drop_table(database, table)
                
                if result.get('success'):
                    st.success(f"✅ Table '{table}' dropped successfully!")
                else:
                    st.error(f"❌ Failed to drop table: {result.get('error', result.get('response', 'Unknown error'))}")
        else:
            st.warning("No tables found in the selected database.")

    elif operation == "Update Rows":
        st.subheader("✏️ Update Rows in Table")

        databases = uploader.get_databases()
        if not databases:
            st.error("Could not fetch databases.")
            return
        
        database = st.selectbox("Select Database", databases)
        tables = uploader.get_tables(database) if database else []

        if tables:
            table = st.selectbox("Select Table", tables)
            schema = uploader.get_table_schema(database, table)
            
            if schema:
                schema_df = pd.DataFrame(schema)
                st.write("**Table Schema:**")
                st.dataframe(schema_df)

                col_names = schema_df['name'].tolist() if 'name' in schema_df else schema_df.columns.tolist()

                uploaded_file = st.file_uploader(
                    "Upload CSV/Excel with updated rows (must include primary key columns)",
                    type=['csv', 'xlsx', 'xls']
                )

                pk_cols = st.multiselect("Select Primary Key Columns", col_names)

                if uploaded_file and pk_cols:
                    df = load_file(uploaded_file)
                    if df is not None:
                        st.write("Preview of updates:")
                        st.dataframe(df.head())

                        if st.button("Update Rows", type="primary"):
                            with st.spinner("Updating rows..."):
                                all_success = True
                                errors = []
                                
                                # Loop over each record and update individually
                                for _, row in df.iterrows():
                                    pk_values = [str(row[pk]) for pk in pk_cols]  # ensure strings
                                    updates = row.drop(labels=pk_cols).to_dict() # rest of the row
                                    
                                    result = uploader.update_rows(database, table, pk_values, updates)
                                    if not result.get("success"):
                                        all_success = False
                                        errors.append(result)

                                if all_success:
                                    st.success("✅ All rows updated successfully!")
                                    # Show updated table
                                    updated_df = uploader.get_table_rows(database, table)
                                    if not updated_df.empty:
                                        st.write("**Updated Table:**")
                                        st.dataframe(updated_df)
                                    else:
                                        st.info("No rows found in table or unable to fetch data.")
                                else:
                                    st.error(f"❌ Some updates failed: {errors}")


    
    elif operation == "Delete Rows":
        st.subheader("🗑️ Delete Rows from Table")

        databases = uploader.get_databases()
        if not databases:
            st.error("Could not fetch databases.")
            st.stop()
        
        database = st.selectbox("Select Database", databases)
        tables = uploader.get_tables(database) if database else []

        if tables:
            table = st.selectbox("Select Table", tables)
            schema = uploader.get_table_schema(database, table)

            if schema:
                schema_df = pd.DataFrame(schema)
                st.write("**Table Schema:**")
                st.dataframe(schema_df)

                # Extract column names
                col_names = schema_df['name'].tolist() if 'name' in schema_df else schema_df.columns.tolist()

                # Pick PK columns (order matters!)
                pk_cols = st.multiselect("Select Primary Key Columns", col_names)

                if pk_cols:
                    st.write("Enter values for the primary key(s) of the row you want to delete:")

                    # Input boxes for each PK column
                    pk_values = []
                    for col in pk_cols:
                        val = st.text_input(f"Value for {col}")
                        pk_values.append(val)

                    if all(pk_values):  # ensure all fields filled
                        if st.button("Delete Row", type="primary"):
                            with st.spinner("Deleting row..."):
                                result = uploader.delete_rows(
                                    database, 
                                    table, 
                                    pk_values  # pass values in correct order
                                )
                            if result.get("ok"):
                                st.success("✅ Row deleted successfully!")

                                # Show updated table
                                updated_df = uploader.get_table_rows(database, table)
                                if isinstance(updated_df, pd.DataFrame):
                                    st.write("**Updated Table:**")
                                    st.dataframe(updated_df)
                                else:
                                    st.warning("Could not fetch updated table.")
                            else:
                                st.error(f"❌ Failed: {result.get('error')}")




    else:
        st.info(f"The '{operation}' feature is coming soon! This prototype focuses on the core create and insert operations.")

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <small>Datasette Data Uploader • Built with Streamlit</small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()