import streamlit as st
import requests
import json  # Not strictly used for display here, but good to have if needed for raw JSON later
import pandas as pd
import datetime  # For year input default

# --- CONFIGURATION ---
# Ensure this matches the port your FastAPI app is running on.
FASTAPI_BASE_URL = "http://localhost:8000"  # Or your actual FastAPI URL

st.set_page_config(page_title="Progetto MAADB", layout="wide")
st.title("📊 Progetto MAADB Dashboard")

# --- Sidebar for navigation ---
st.sidebar.title("Navigation")
action_options = [
    "Home",
    "MongoDB Actions",
    "Neo4j Actions",
    "PostgreSQL Actions",
    "Find Posts by Email",
    "Find Groups by Work & Forum",
    "Find Most Used Tags by City Interest"  # New Action
]
# Update default_index if you want this new one to be default for testing
try:
    # default_index = action_options.index("Find Groups by Work & Forum")
    default_index = action_options.index("Find Most Used Tags by City Interest") # Default to new query
except ValueError:
    default_index = 0

action = st.sidebar.selectbox(
    "Select an action",
    action_options,
    index=default_index
)


# --- Helper function for API requests ---
def make_api_request(endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
    """Helper function to make API requests and handle common errors."""
    url = f"{FASTAPI_BASE_URL}{endpoint}"
    try:
        # For GET requests with params, requests library handles URL encoding
        log_params = params if params else "{}"
        st.info(f"⏳ Querying API: {method} {url} with params: {log_params}")
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)  # For POST, data is usually in json body
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()

    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP Error: {e.response.status_code}"
        try:
            error_detail = e.response.json().get("detail", e.response.text)
            st.error(f"{error_message} - Detail: {error_detail}")
        except json.JSONDecodeError:  # If error response is not JSON
            st.error(f"{error_message} - Server Response: {e.response.text}")
    except requests.exceptions.ConnectionError:
        st.error(
            f"🔌 Connection Error: Could not connect to the FastAPI backend at {FASTAPI_BASE_URL}. "
            f"Is it running and accessible?")
    except json.JSONDecodeError:  # If successful response is not valid JSON
        st.error("Error: Invalid JSON response from the server.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return None


# --- Page Content based on Action ---

if action == "Home":
    st.header("Welcome to the MAADB Project Dashboard!")
    st.markdown(f"""
        Use the sidebar to navigate through different database actions and queries.
        Ensure your FastAPI backend is running and accessible.
        Streamlit is attempting to connect to FastAPI at: `{FASTAPI_BASE_URL}`.
    """)

elif action == "MongoDB Actions":
    st.header("MongoDB Actions")
    if st.button("Check MongoDB Connection", key="mongo_health_btn"):
        result = make_api_request("/mongo/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")

    if st.button("Get First 5 Objects from MongoDB", key="mongo_first5_btn"):
        results = make_api_request("/mongo/first5")
        if results:
            if not results:
                st.info("The response from the server was empty or no collections found.")
            else:
                for collection, data_list in results.items():
                    st.subheader(f"Collection: {collection}")
                    if data_list:
                        # ObjectId conversion if necessary (though your backend might handle it)
                        for item in data_list:
                            if '_id' in item and isinstance(item['_id'], dict) and '$oid' in item['_id']:
                                item['_id'] = item['_id']['$oid']
                        df = pd.DataFrame(data_list)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write(f"No data found or returned for {collection}")


elif action == "Neo4j Actions":
    st.header("Neo4j Actions")
    if st.button("Check Neo4j Connection", key="neo4j_health_btn"):
        result = make_api_request("/neo4j/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")

    if st.button("Get First 5 Relationships by Type", key="neo4j_first5_btn"):
        results = make_api_request("/neo4j/first5")
        if results:
            if not results:
                st.info("No relationship types found or the response was empty.")
            else:
                st.subheader("First 5 Relationships by Type:")
                for rel_type, relationships in results.items():
                    st.write(f"**Relationship Type: `{rel_type}`**")
                    if relationships:
                        df = pd.DataFrame(relationships)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info(f"No relationships found for type `{rel_type}`.")

elif action == "PostgreSQL Actions":
    st.header("PostgreSQL Actions")
    if st.button("Check PostgreSQL Connection", key="pg_health_btn"):
        result = make_api_request("/postgres/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")

    if st.button("Get First 5 Records from PostgreSQL", key="pg_first5_btn"):
        results = make_api_request("/postgres/first5")
        if results:
            if not results:
                st.info("The response from the server was empty or no tables found.")
            else:
                for table, data_list in results.items():
                    st.subheader(f"Table: {table}")
                    if data_list:
                        df = pd.DataFrame(data_list)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write(f"No data found or returned for {table}")


elif action == "Find Posts by Email":
    st.header("Find Posts by User Email")
    email_input = st.text_input("Enter the email address of the user:", placeholder="e.g., Tissa47@gmx.com",
                                key="email_input_posts")

    if st.button("Search Posts 🚀", key="search_posts_email_btn"):
        if email_input:
            api_endpoint = f"/by-email/{email_input}"
            posts_data = make_api_request(api_endpoint)

            if posts_data is not None:
                if posts_data:
                    st.success(f"✅ Found {len(posts_data)} post(s) for '{email_input}':")
                    display_data_for_df = []
                    for post_item in posts_data:
                        display_data_for_df.append({
                            "Post ID": post_item.get("id"),
                            "Content": post_item.get("content", "N/A"),
                            "Media": post_item.get("imageFile", "N/A"),
                            "Creation Date": post_item.get("creationDate")
                        })
                    column_order = ["Post ID", "Content", "Media", "Creation Date"]
                    df = pd.DataFrame(display_data_for_df, columns=column_order)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(
                        f"🤷 No posts found for user with email '{email_input}'. They might exist but have not posted anything."
                    )
        else:
            st.warning("Doh! Please enter an email address to search.")

elif action == "Find Groups by Work & Forum":
    st.header("👥 Find Groups by Shared Work & Forum")
    st.markdown("""
    Finds groups of people (2 or more) who work at the same company (having started in or before the target year) 
    and are members of the same forum.
    """)

    current_year = datetime.datetime.now().year
    target_year_input = st.number_input(
        "Enter Target Year (worked since this year or earlier):",
        min_value=1900,
        max_value=current_year + 5,  # Allow a bit into the future if needed
        value=2009,  # Default to a year we know has data from tests
        step=1,
        format="%d",
        key="group_target_year"
    )

    limit_input = st.number_input(
        "Maximum number of groups to return:",
        min_value=1,
        max_value=100000,  # A reasonable upper bound for UI display
        value=2000,  # Default limit for display
        step=5,
        format="%d",
        key="group_limit"
    )

    if st.button("Find Groups 🔎", key="find_groups_btn"):
        if target_year_input:
            api_endpoint = f"/groups/by-work-and-forum/{target_year_input}"
            # Pass the limit as a query parameter
            api_params = {"limit": limit_input}

            groups_result = make_api_request(api_endpoint, params=api_params)

            if groups_result is not None:  # Check if API call itself was successful (returned data or empty list)
                if groups_result:  # If the list of groups is not empty
                    st.success(
                        f"Found {len(groups_result)} group(s) for target year {target_year_input} (limit: {limit_input}):")

                    for i, group in enumerate(groups_result):
                        company_name = group.get("companyName", "N/A")
                        company_id = group.get("companyId", "N/A")
                        forum_title = group.get("forumTitle", "N/A")
                        forum_id = group.get("forumId", "N/A")
                        members = group.get("members", [])

                        expander_title = (
                            f"Group {i + 1}: Company '{company_name}' (ID: {company_id}) & "
                            f"Forum '{forum_title}' (ID: {forum_id}) - {len(members)} member(s)"
                        )
                        with st.expander(expander_title):
                            if members:
                                member_data_for_df = []
                                for member in members:
                                    member_data_for_df.append({
                                        "Person ID": member.get("id"),
                                        "First Name": member.get("firstName"),
                                        "Last Name": member.get("lastName"),
                                        "Email(s)": ", ".join(member.get("email", []))  # Join list of emails
                                    })

                                member_df_columns = ["Person ID", "First Name", "Last Name", "Email(s)"]
                                member_df = pd.DataFrame(member_data_for_df, columns=member_df_columns)
                                st.dataframe(member_df, use_container_width=True)

                                if st.checkbox(f"Show raw JSON for Group {i + 1}", key=f"show_raw_json_group_{i}"):
                                    st.json(group)
                            else:
                                # This case should ideally not happen if backend logic ensures groups have >1 member
                                st.write("No members listed for this group (though the group itself was identified).")
                else:  # API returned an empty list
                    st.info(
                        f"No groups found matching the criteria for target year {target_year_input} (limit: {limit_input}).")
            # Error messages from make_api_request (like connection errors or 500s) are handled by the helper.
        else:
            st.warning("Please enter a target year.")

elif action == "Find Most Used Tags by City Interest":
    st.header("🏷️ Find Most Used Tags by City (User Interest)")
    st.markdown("""
    Given a user's email, this query finds their city. Then, it identifies the tags
    (along with their URL and class) that people in that same city have most
    frequently marked as a direct interest (`HAS_INTEREST`).
    """)

    user_email_input = st.text_input(
        "Enter User Email:",
        placeholder="e.g., Jan16@hotmail.com",
        key="q7_user_email"
    )
    top_n_input = st.number_input(
        "Number of top tags to display:",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        key="q7_top_n"
    )

    if st.button("Find Tags 🔎", key="q7_find_tags_btn"):
        if user_email_input:
            api_endpoint = f"/tags/most-used-by-city-interest/{user_email_input}"
            api_params = {"top_n": top_n_input}

            response_data = make_api_request(api_endpoint, params=api_params)

            if response_data:
                message = response_data.get("message")
                tags_list = response_data.get("tags", [])
                city_name_from_response = response_data.get('city_name')
                city_info_display = f"(City: {city_name_from_response})" if city_name_from_response else "(City information not available)"

                if message:
                    if not tags_list and (
                            "not found" in message.lower() or "no other persons" in message.lower() or "no tags found" in message.lower()):
                        st.warning(f"{message} {city_info_display}")
                    elif not tags_list and "error occurred" in message.lower():
                        st.error(f"{message} {city_info_display}")
                    else:
                        st.info(f"{message} {city_info_display}")

                if tags_list:
                    st.success(f"Found {len(tags_list)} tag(s) for user '{user_email_input}' in {city_info_display}:")

                    # Prepare data for DataFrame
                    df_data = []
                    for tag_item in tags_list:
                        df_data.append({
                            "Name": tag_item.get("tag_name"),
                            "Count": tag_item.get("count"),
                            "URL": tag_item.get("tag_url"),
                            "Class": tag_item.get("tag_class_name")
                        })
                    df = pd.DataFrame(df_data)

                    # Display DataFrame with column configuration for URL
                    st.dataframe(
                        df,
                        column_config={
                            "Name": "Tag Name",
                            "Count": st.column_config.NumberColumn("Interest Count", format="%d"),
                            "URL": st.column_config.LinkColumn("Tag URL", display_text="🔗 Link"),
                            "Class": "Tag Class"
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                elif not message:
                    st.info(f"No tags found {city_info_display} and no specific message from API.")

                if st.checkbox("Show raw API response JSON", key="q7_show_raw_json"):
                    st.json(response_data)
        else:
            st.warning("Please enter a user email address.")
