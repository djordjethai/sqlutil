import streamlit as st
from promptdb import PromptDatabase
import pandas as pd

st.set_page_config(layout="wide")
# UI Components
st.title("Prompt Database Manager")
st.caption("Choose DB operation")
st.caption("ver 20.03.24")

operation = st.radio("Choose operation", ["Create New Record", "Select and Update Record", "Select and Delete Record", "Search Prompt Records"], horizontal=True)

def handle_table_update(table_name, id_column, name_column, additional_fields=None):
    with col1:
        with PromptDatabase() as db:
            prompt_names = db.get_records_from_column(table_name, name_column)
            print(f"Prompt names fetched: {prompt_names}")  # Debug print

            selected_name = st.selectbox(f"Select {name_column} to Update", [''] + prompt_names)
            existing_details = db.get_record_by_name(table=table_name, name_column=name_column, value=selected_name) if selected_name else None

        if existing_details:
            st.subheader(f"Edit {name_column}")
            user_id = existing_details[id_column]
            updated_values = {name_column: st.text_area(f"{name_column}", value=existing_details[name_column])}
            
            # Handle additional fields if any
            for field_name, field_label in additional_fields.items() if additional_fields else []:
                updated_values[field_name] = st.text_area(field_label, value=existing_details[field_name])

            if st.button(f'Update {name_column} Record'):
                with PromptDatabase() as db:
                    st.info(db.update_record(table_name, updated_values, (f'{id_column} = ?', [user_id])))
            else:
                st.error(f"Please select a {name_column} to update its details.")

    with col2:
        show_all_table_data(table_name)

def handle_record_deletion(table_name, id_column, name_column):
    with col1:
        with PromptDatabase() as db:
            item_names = db.get_records_from_column(table_name, name_column)
            selected_item_name = st.selectbox(f"Select {name_column} to Delete", [''] + item_names)
            existing_details = db.get_record_by_name(table=table_name, name_column=name_column, value=selected_item_name) if selected_item_name else None

        if existing_details:
            st.subheader(f"Delete {name_column}")
            condition = (f"{id_column} = ?", [existing_details[id_column]])
            
            if st.button(f'Delete {name_column} Record'):
                with PromptDatabase() as db:
                    st.info(db.delete_record(table=table_name, condition=condition))
        else:
            st.error(f"Please select a {name_column} to delete.")

# Mapping table specifics for reuse
table_mappings = {
    "Prompts": {
        "table_name": "PromptStrings",
        "id_column": "PromptID",
        "name_column": "PromptName",
        "additional_fields": {"PromptString": "Prompt string", "Comment": "Comment"}
    }
}
table_configurations = {
    "Prompts": {
        "form_id": "add_prompts_form",
        "header": "Add a New Prompt String",
        "table_name": "PromptStrings",
        "input_fields": {"PromptName": "Prompt name", "PromptString": "Prompt String", "Comment": "Comment"}
    }
}

deletion_configurations = {
    "Prompts": {
        "table_name": "PromptStrings",
        "id_column": "PromptID",
        "name_column": "PromptName"
    }
}

def add_new_record(form_id, header, table_name, input_fields):
    with col1:
        with st.form(form_id, clear_on_submit=True):
            st.subheader(header)
            form_data = {}
            first_field_name = next(iter(input_fields)) 
            for field_name, field_label in input_fields.items():
                form_data[field_name] = st.text_input(field_label, "")
            submit = st.form_submit_button("Add")

            if submit and form_data[first_field_name]:
                with PromptDatabase() as db:
                    if db.add_record(table_name, **form_data):
                        st.success(f"{input_fields[next(iter(input_fields))]} added successfully!")
                    else:
                        st.error("This record already exists and cannot be duplicated.")

def show_all_table_data2(table_name):
    with PromptDatabase() as db: 
        records, columns = db.get_all_records_from_table(table_name) 
    df = pd.DataFrame(records, columns=columns)
    st.caption("To see entire text: Double Click on actual text, or move slider, or enlarge the table view")
    st.dataframe(df, use_container_width=True, hide_index=True)                

import pandas as pd

def show_all_table_data(table_name):
    with PromptDatabase() as db:
        records, columns = db.get_all_records_from_table(table_name)
    
    # Convert records to tuples explicitly to avoid any hidden issues
    records = [tuple(record) for record in records]
    
    # Ensure each record is a tuple and has the correct length
    if records and all(len(record) == len(columns) for record in records):
        try:
            df = pd.DataFrame(records, columns=columns)
            st.caption("To see entire text: Double Click on actual text, or move slider, or enlarge the table view")
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Failed to create DataFrame: {e}")
            print(f"Failed to create DataFrame: {e}")
    else:
        st.error("Mismatch between record data and column definitions. Please check the database schema and data consistency.")

        
if operation == "Create New Record":
    st.subheader("Create a New Prompt Record")
    
    tabela_za_unos = "Prompts"
    col1, col2 = st.columns(2)
    
    if tabela_za_unos in table_configurations:
        config = table_configurations[tabela_za_unos]
        add_new_record(**config)

        with col2:
            show_all_table_data(config["table_name"])
           

elif operation == "Select and Update Record":
    st.subheader("Edit Record")
    tabela_za_unos = "Prompts"
    col1, col2 = st.columns(2)
   
    if tabela_za_unos in table_mappings:
        handle_table_update(**table_mappings[tabela_za_unos])

elif operation == "Select and Delete Record":
    st.subheader("Delete Record")
    tabela_za_unos = "Prompts"
    col1, col2 = st.columns(2)
   
    if tabela_za_unos in deletion_configurations:
        config = deletion_configurations[tabela_za_unos]
        handle_record_deletion(**config)

        with col2:
            show_all_table_data(config["table_name"])

elif operation == "Search Prompt Records":
    st.subheader("Display Prompt Records Filtered by Search String")
    
    with st.form("search_prompts"):
        search_string = st.text_input("Enter a search string to filter prompts (empty for all):")
        submit_search = st.form_submit_button("Submit")
        
        if submit_search:
            st.caption("To see entire text: Double Click on actual text, or move slider, or enlarge the table view")
            with PromptDatabase() as db:
                records = db.search_for_string_in_prompt_text(search_string)
            
            if records:
                df = pd.DataFrame(records, columns=['PromptName', 'PromptString'])
                st.dataframe(df, use_container_width=True, hide_index=True, column_config={
                "PromptName": st.column_config.Column("Naziv Prompta", width="small"),
                "PromptString": st.column_config.Column("Tekst Prompta", width="large")
            },)
            else:
                st.write("No records found.")
