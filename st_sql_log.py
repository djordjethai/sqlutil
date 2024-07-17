import streamlit as st
import pandas as pd
import os
import pyodbc

st.set_page_config(layout="wide")

class ConversationDatabaseManager:
    """
    A class to interact with a MSSQL database for storing and retrieving conversation data.
    """
    
    def __init__(self, host=None, user=None, password=None, database=None):
        """
        Initializes the connection details for the database, with the option to use environment variables as defaults.
        """
        self.host = host if host is not None else os.getenv('MSSQL_HOST')
        self.user = user if user is not None else os.getenv('MSSQL_USER')
        self.password = password if password is not None else os.getenv('MSSQL_PASS')
        self.database = database if database is not None else os.getenv('MSSQL_DB')
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Establishes the database connection and returns the instance itself when entering the context.
        """
        self.conn = pyodbc.connect(
            driver='{ODBC Driver 18 for SQL Server}',
            server=self.host,
            database=self.database,
            uid=self.user,
            pwd=self.password,
            TrustServerCertificate='yes'
        )
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection and cursor when exiting the context.
        Handles any exceptions that occurred within the context.
        """
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
        if exc_type or exc_val or exc_tb:
            pass
    
    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()

    def fetch_distinct_column_values(self, column_name):
        """
        Fetches distinct values of a specified column from the conversations table.
        
        Parameters:
        - column_name: The name of the column (e.g., user_name, app_name, thread_id).

        Returns:
        - A list of distinct values for the specified column.
        """
        query = f"SELECT DISTINCT {column_name} FROM conversations"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_records_by_column(self, column_name, column_value):
        """
        Fetches records from the conversations table where the specified column matches the given value.
        
        Parameters:
        - column_name: The name of the column to filter by (e.g., user_name, app_name, thread_id).
        - column_value: The value to match in the specified column.
        
        Returns:
        - A list of tuples containing the matching records, or None if no records are found.
        """
        query = f"SELECT * FROM conversations WHERE {column_name} = ?"
        self.cursor.execute(query, (column_value,))
        rows = self.cursor.fetchall()
        return rows if rows else None

    def fetch_thread_ids(self, filter_column, filter_value):
        """
        Fetches thread IDs based on a filter (either app_name or user_name).

        Parameters:
        - filter_column: Column to filter by ('app_name' or 'user_name').
        - filter_value: Value to filter on in the specified column.

        Returns:
        - A list of thread IDs.
        """
        query = f"SELECT DISTINCT thread_id FROM conversations WHERE {filter_column} = ?"
        self.cursor.execute(query, (filter_value,))
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_distinct_thread_ids(self, column_name, column_value):
        """
        Fetches distinct thread IDs based on the specified column name and value.
    
        Parameters:
        - column_name: The column to filter by ('app_name' or 'user_name').
        - column_value: The value to match in the specified column.
    
        Returns:
        - A list of distinct thread IDs.
        """
        query = f"SELECT DISTINCT thread_id FROM conversations WHERE {column_name} = ?"
        self.cursor.execute(query, (column_value,))
        return [row[0] for row in self.cursor.fetchall()]



# Main app structure
import streamlit as st

def edit_delete_record_ui(filter_type):
    # Step 1: Select either app_name or user_name
    with ConversationDatabaseManager() as db:
        if filter_type == "App Name":
            options = db.fetch_distinct_column_values("app_name")
        else:  # Assuming User Name
            options = db.fetch_distinct_column_values("user_name")
    
    selected_filter_option = st.selectbox(f"Select {filter_type}", ['Select...'] + options, key="first_selection")

    # Step 2: Select thread_id based on the first selection
    if selected_filter_option and selected_filter_option != 'Select...':
        with ConversationDatabaseManager() as db:
            thread_ids = db.fetch_distinct_thread_ids(filter_type.replace(" ", "_").lower(), selected_filter_option)
        
        selected_thread_id = st.selectbox("Select Thread ID", ['Select...'] + thread_ids)
    
        # Proceed to edit/delete once a thread_id is selected
        if selected_thread_id and selected_thread_id != 'Select...':
            with ConversationDatabaseManager() as db:
                record = db.fetch_records_by_column("thread_id", selected_thread_id)
                if record:
                    record = record[0] 
                    conversation = record[4] 
                    new_conversation = st.text_area("Edit Conversation", value=conversation)

                    if st.button("Submit Changes"):
                        with ConversationDatabaseManager() as db:
                            update_query = "UPDATE conversations SET conversation = ? WHERE thread_id = ?"
                            db.cursor.execute(update_query, (new_conversation, selected_thread_id))
                            db.conn.commit()
                            st.success("Conversation updated successfully!")

                    if st.button("Delete Record"):
                        # Delete the record from the database
                        with ConversationDatabaseManager() as db:
                            delete_query = "DELETE FROM conversations WHERE thread_id = ?"
                            db.cursor.execute(delete_query, (selected_thread_id,))
                            db.conn.commit()
                            st.success("Record deleted successfully!")

                else:
                    st.error("No record found for the selected Thread ID.")


def search_and_edit_conversation():
    # Step 1: Input for search string
    search_query = st.text_input("Enter a string to search in conversations:")

    if search_query:
        # Fetch records containing the search string in the conversation column
        with ConversationDatabaseManager() as db:
            query = "SELECT * FROM conversations WHERE conversation LIKE ?"
            db.cursor.execute(query, (f"%{search_query}%",))
            records = db.cursor.fetchall()
        
        ph = st.empty()
        if records:
            # Convert records to DataFrame for better display
            df = pd.DataFrame(records, columns=[desc[0] for desc in db.cursor.description])
            st.dataframe(df, use_container_width=True, hide_index=True)
            with ph.container():
                # Step 2: Select a record to edit
                thread_ids = df['thread_id'].tolist()  # Assuming 'thread_id' is the identifier
                selected_thread_id = st.selectbox("Select Thread ID of the record to edit:", ['Select...'] + thread_ids)
            
                if selected_thread_id and selected_thread_id != 'Select...':
                    selected_record = df[df['thread_id'] == selected_thread_id].iloc[0]
                    conversation_to_edit = selected_record['conversation']
                
                    # Step 3: Edit the selected conversation
                    edited_conversation = st.text_area("Edit Conversation", value=conversation_to_edit)
                
                    if st.button("Submit Changes"):
                        # Update the conversation in the database
                        with ConversationDatabaseManager() as db:
                            update_query = "UPDATE conversations SET conversation = ? WHERE thread_id = ?"
                            db.cursor.execute(update_query, (edited_conversation, selected_thread_id))
                            db.conn.commit()
                            st.success("Conversation updated successfully!")
        else:
            st.error("No records found containing the search string.")

def main():
    st.subheader("Conversation Database Manager")
    st.caption("Choose DB operation")
    st.caption("ver 20.03.24")
    col1, col2 = st.columns(2)

    with col1:
        odabir = st.radio("Choose search criteria :", ["App", "User"], horizontal=True, index=None)
    if odabir == "User":
        st.info("Search and Edit Conversation")
        search_and_edit_conversation()
    elif odabir == "App":
        with col2:
            filter_type = st.radio("Filter By", ["App Name", "User Name"], key="filter_type", horizontal=True)
            st.info("Edit/Delete Conversation Record")
        edit_delete_record_ui(filter_type)

if __name__ == "__main__":
    main()
