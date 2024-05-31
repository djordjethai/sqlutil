import streamlit as st
from myfunc.prompts import PromptDatabase
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
                    st.info(db.update_record(table_name, updated_values, (f'{id_column} = %s', [user_id])))
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
            condition = (f"{id_column} = %s", [existing_details[id_column]])
            
            if st.button(f'Delete {name_column} Record'):
                with PromptDatabase() as db:
                    st.info(db.delete_record(table=table_name, condition=condition))
        else:
            st.error(f"Please select a {name_column} to delete.")


# Mapping table specifics for reuse
table_mappings = {
    "Users": {
        "table_name": "Users",
        "id_column": "UserID",
        "name_column": "Username",
        "additional_fields": None
    },
    "Variables": {
        "table_name": "PromptVariables",
        "id_column": "VariableID",
        "name_column": "VariableName",
        "additional_fields": None
    },
    "Python files": {
        "table_name": "PythonFiles",
        "id_column": "FileID",
        "name_column": "Filename",
        "additional_fields": {"FilePath": "File Path"}
    },
    "Prompts": {
        "table_name": "PromptStrings",
        "id_column": "PromptID",
        "name_column": "PromptName",
        "additional_fields": {"PromptString": "Prompt string", "Comment": "Comment"}
    }
}
table_configurations = {
    "Users": {
        "form_id": "add_user_form",
        "header": "Add a New User",
        "table_name": "Users",
        "input_fields": {"Username": "Username"}
    },
    "Variables": {
        "form_id": "add_variable_form",
        "header": "Add a New Variable",
        "table_name": "PromptVariables",
        "input_fields": {"VariableName": "Variable"}
    },
    "Python files": {
        "form_id": "add_python_form",
        "header": "Add a New Python file name",
        "table_name": "PythonFiles",
        "input_fields": {"Filename": "File name", "FilePath": "Repo"}
    },
    "Prompts": {
        "form_id": "add_prompts_form",
        "header": "Add a New Prompt String",
        "table_name": "PromptStrings",
        "input_fields": {"PromptName": "Prompt name", "PromptString": "Prompt String", "Comment": "Comment"}
    }
}

deletion_configurations = {
    "Users": {
        "table_name": "Users",
        "id_column": "UserID",
        "name_column": "Username"
    },
    "Variables": {
        "table_name": "PromptVariables",
        "id_column": "VariableID",
        "name_column": "VariableName"
    },
    "Python files": {
        "table_name": "PythonFiles",
        "id_column": "FileID",
        "name_column": "Filename"
    },
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


def show_all_table_data(table_name):
     with PromptDatabase() as db: 
        records, columns = db.get_all_records_from_table(table_name) 
     df = pd.DataFrame(records, columns=columns)
     st.caption("To see entire text: Double Click on actual text, or move slider, or enlarge the table view")
     st.dataframe(df, use_container_width=True, hide_index=True)                

if operation == "Create New Record":
    st.subheader("Create a New Prompt Record")
    
    # prvo cemo da odaberemo bazu. ako su pomocne idemo sa add_record, a ako je glavna onda sa add_new_record
    # pa polako
    tabela_za_unos = st.selectbox("Choose table",[''] + ["Users", "Variables", "Python files", "Prompts", "Relations"])
    col1, col2 = st.columns(2)
   
    
    if tabela_za_unos in table_configurations:
        config = table_configurations[tabela_za_unos]
        add_new_record(**config)

        with col2:
            show_all_table_data(config["table_name"])

           
    elif tabela_za_unos == "Relations":
        with col1:
            st.subheader('Add a New Relationship Record')
            # Fetch options for each selectbox
            with PromptDatabase() as db:
                # Fetch names for the selectboxes
                prompt_options = db.get_records_from_column('PromptStrings', 'PromptName')
                user_options = db.get_records_from_column('Users', 'Username')
                variable_options = db.get_records_from_column('PromptVariables', 'VariableName')
                file_options = db.get_records_from_column('PythonFiles', 'Filename')

            # Create selectboxes for each ID needed in the relationship record
            selected_prompt_name = st.selectbox('Select Prompt', [''] + prompt_options)
            selected_user_name = st.selectbox('Select User', [''] + user_options)
            selected_variable_name = st.selectbox('Select Variable', [''] + variable_options)
            selected_file_name = st.selectbox('Select File', [''] + file_options)

            # Fetch IDs for the selected names
            if st.button('Add Relationship'):
                with PromptDatabase() as db:
                    if all([selected_prompt_name, selected_user_name, selected_variable_name, selected_file_name]):
                        prompt_id = db.get_record_by_name('PromptStrings', 'PromptName', selected_prompt_name).get('PromptID') if selected_prompt_name else None
                        user_id = db.get_record_by_name('Users', 'Username', selected_user_name).get('UserID') if selected_user_name else None
                        variable_id = db.get_record_by_name('PromptVariables', 'VariableName', selected_variable_name).get('VariableID') if selected_variable_name else None
                        file_id = db.get_record_by_name('PythonFiles', 'Filename', selected_file_name).get('FileID') if selected_file_name else None
                
                        # Assuming add_relationship_record method exists and accepts IDs
                        result = db.add_relationship_record(prompt_id, user_id, variable_id, file_id)
                        if result:
                            st.success('Relationship added successfully!')
                        else:
                            st.error('Failed to add the relationship.')
                    else:
                        st.error('Please make sure all fields are selected.')
        with col2:
            show_all_table_data("CentralRelationshipTable")     

elif operation == "Select and Update Record":
    st.subheader("Edit Record")
    tabela_za_unos = st.selectbox("Choose table",[''] + ["Users", "Variables", "Python files", "Prompts", "Relations"])
    col1, col2 = st.columns(2)
   
    if tabela_za_unos in table_mappings:
        handle_table_update(**table_mappings[tabela_za_unos])
             
    elif tabela_za_unos == "Relations" :
        with col1:    
            with PromptDatabase() as db:
               user_names = db.get_records_from_column('Users', 'Username')
            selected_user_name = st.selectbox("Select User Name to Edit Relationship", [''] + user_names, key="edit_rel")
            if selected_user_name:
                with PromptDatabase() as db:
                    # Fetch the existing details for the selected username
                    user_details = db.get_record_by_name('Users', 'Username', selected_user_name)
                if user_details:
                    # Use the custom function to fetch relationship details
                    with PromptDatabase() as db:
                        relationships = db.get_relationships_by_user_id(user_details['UserID'])
                    if relationships:
                        # Assuming the relationships variable is a list of dictionaries with each relationship's details
                        for relationship in relationships:
                            # Directly use the values from the relationship dictionary
                            current_prompt_name = relationship['PromptName']
                            current_variable_name = relationship['VariableName']
                            current_file_name = relationship['Filename']
                            # Display current selections
                            with PromptDatabase() as db:
                                prompt_names = db.get_records_from_column('PromptStrings', 'PromptName')
                                variable_names = db.get_records_from_column('PromptVariables', 'VariableName')
                                file_names = db.get_records_from_column('PythonFiles', 'Filename')

                            new_selected_prompt_name = col1.selectbox("Select New Prompt", prompt_names, index=prompt_names.index(current_prompt_name))
                            new_selected_variable_name = col1.selectbox("Select New Variable", variable_names, index=variable_names.index(current_variable_name))
                            new_selected_file_name = col1.selectbox("Select New File", file_names, index=file_names.index(current_file_name))

                            if col1.button(f'Update Relationship for {selected_user_name}'):
                                # Convert selected names back to IDs
                                with PromptDatabase() as db:
                                    new_prompt_id = db.get_record_by_name('PromptStrings', 'PromptName', new_selected_prompt_name)['PromptID']
                                    new_variable_id = db.get_record_by_name('PromptVariables', 'VariableName', new_selected_variable_name)['VariableID']
                                    new_file_id = db.get_record_by_name('PythonFiles', 'Filename', new_selected_file_name)['FileID']

                                    # Update the relationship record
                                    success = db.update_relationship_record(relationship['ID'], new_prompt_id, user_details['UserID'], new_variable_id, new_file_id)
                                if success:
                                    col1.success("Relationship updated successfully!")
                                else:
                                    col1.error("Failed to update the relationship.")
                    else:
                        col1.error("Failed to update the relationship.")                
                else:
                    col1.error("No relationships found for the selected user.")

        with col2:
         # Assuming show_all_table_data is a function defined elsewhere to display data from a table
            with PromptDatabase() as db:
                df = db.fetch_relationship_data()
            st.dataframe(df)
        
        
        
                    
elif operation == "Select and Delete Record":
    st.subheader("Delete Record")
    tabela_za_unos = st.selectbox("Choose table",[''] + ["Users", "Variables", "Python files", "Prompts", "Relations"])
    col1, col2 = st.columns(2)
   
    if tabela_za_unos in deletion_configurations:
        config = deletion_configurations[tabela_za_unos]
        handle_record_deletion(**config)

        with col2:
            show_all_table_data(config["table_name"])


    elif tabela_za_unos == "Relations":
        with col1:
            with PromptDatabase() as db:
                prompt_names = db.get_records_from_column('PromptStrings', 'PromptName')
                selected_prompt_id = st.selectbox("Select Prompts to Delete", [''] + prompt_names)
                existing_details = db.get_record_by_name(table="PromptStrings", name_column="PromptName", value=selected_prompt_id) if selected_prompt_id else None
          
            if existing_details:
                prompt_id = existing_details['PromptID']
                with PromptDatabase() as db:
                    records = db.fetch_relationship_data(prompt_id)
                df = pd.DataFrame(records, columns=['RelationshipID', 'PromptName', 'Username', 'VariableName', 'Filename'])
                with col2: 
                    st.dataframe(df)
                    
                # Let user select a RelationshipID to operate on
                relationship_ids = df['RelationshipID'].tolist()
                selected_relationship_id = st.selectbox("Select a Relationship to Edit or Delete", relationship_ids)

                # Now you can use selected_relationship_id for further operations like editing or deletion
                if st.button('Delete Relationship'):
                    with PromptDatabase() as db:
                        # Assuming delete_record function accepts a table name and condition
                        success = db.delete_record('CentralRelationshipTable', ('ID = %s', [selected_relationship_id]))
                        if success:
                            st.success("Relationship deleted successfully.")
                            with PromptDatabase() as db:
                                records = db.fetch_relationship_data(prompt_id)
                            df = pd.DataFrame(records, columns=['RelationshipID', 'PromptName', 'Username', 'VariableName', 'Filename'])
                            with col2: 
                                st.dataframe(df)
                            
                        else:
                            st.error("Failed to delete the relationship.")
                else:
                    st.error("Choose an existing record")                
            else:
                st.error("Choose Prompt")
                

elif operation == "Search Prompt Records":
    st.subheader("Display Prompt Records Filtered by Search String")
    
    # Creating a form for user input
    with st.form("search_prompts"):
        # Input for entering the search string
        search_string = st.text_input("Enter a search string to filter prompts (empty for all):")
        submit_search = st.form_submit_button("Submit")
        
        if submit_search:
            st.caption("To see entire text: Double Click on actual text, or move slider, or enlarge the table view")
            # Fetching records based on the search string
            with PromptDatabase() as db:
                # Assuming the method for searching prompts by text is named 'search_for_string_in_prompt_text'
                records = db.search_for_string_in_prompt_text(search_string)
            
            # Displaying the records in a DataFrame
            if records:
                
                df = pd.DataFrame(records, columns=['PromptName', 'PromptString'])
                st.dataframe(df, use_container_width=True, hide_index=True, column_config={
                "PromptName": st.column_config.Column("Naziv Prompta", width="small"),
                "PromptString": st.column_config.Column("Tekst Prompta", width="large")

            },)
            else:
                st.write("No records found.")
