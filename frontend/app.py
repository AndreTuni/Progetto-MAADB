import streamlit as st
import requests
import json
import pandas as pd


# --- CONFIGURATION ---
# CORRECTED: FastAPI is running on port 80 as per your entrypoint.sh
FASTAPI_BASE_URL = "http://localhost:80"

st.set_page_config(page_title="Progetto MAADB", layout="wide")
st.title("📊 Progetto MAADB Dashboard")

# --- Sidebar for navigation ---
st.sidebar.title("Navigation")
action = st.sidebar.selectbox(
    "Select an action",
    [
        "Home",
        "MongoDB Actions",
        "Neo4j Actions",
        "PostgreSQL Actions",
        "Find Posts by Email",
        "Find Forums by Email",
        "Find 2nd Degree Commenters on Liked Posts by Email",
        "Find Common Interests by Organisation"
    ],
    index=0  # Default to Home
)


# --- Helper function for API requests ---
def make_api_request(endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
    """Helper function to make API requests and handle common errors."""
    url = f"{FASTAPI_BASE_URL}{endpoint}"  # Construct full URL here
    try:
        st.info(f"⏳ Querying API: {method} {url}")
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)
        # Add other methods (PUT, DELETE) if needed
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()

    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP Error: {e.response.status_code}"
        try:
            error_detail = e.response.json().get("detail", e.response.text)
            st.error(f"{error_message} - {error_detail}")
        except json.JSONDecodeError:
            st.error(f"{error_message} - {e.response.text}")
    except requests.exceptions.ConnectionError:
        st.error(
            f"🔌 Connection Error: Could not connect to the FastAPI backend at {FASTAPI_BASE_URL}. Is it running and accessible on port 80?")
    except json.JSONDecodeError:
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

# --- MongoDB Actions ---
elif action == "MongoDB Actions":
    st.header("MongoDB Actions")
    if st.button("Check MongoDB Connection"):
        result = make_api_request("/mongo/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")

    if st.button("Get First 5 Objects from MongoDB"):
        results = make_api_request("/mongo/first5")
        if results:
            if not results:  # Check if the results dict itself is empty
                st.info("The response from the server was empty or no collections found.")
            else:
                for collection, data in results.items():
                    st.subheader(f"Collection: {collection}")
                    if data:
                        # Convert ObjectId if present, though your endpoint already does
                        for item in data:
                            if '_id' in item and isinstance(item['_id'], dict) and '$oid' in item['_id']:
                                item['_id'] = item['_id']['$oid']
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write(f"No data found or returned for {collection}")


# --- Neo4j Actions ---
elif action == "Neo4j Actions":
    st.header("Neo4j Actions")
    if st.button("Check Neo4j Connection"):
        result = make_api_request("/neo4j/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")

    if st.button("Get First 5 Relationships by Type"):
        results = make_api_request("/neo4j/first5")
        if results:
            if not results:  # Check if the results dict itself is empty
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

# --- PostgreSQL Actions ---
elif action == "PostgreSQL Actions":
    st.header("PostgreSQL Actions")
    if st.button("Check PostgreSQL Connection"):
        result = make_api_request("/postgres/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")

    if st.button("Get First 5 Records from PostgreSQL"):
        results = make_api_request("/postgres/first5")
        if results:
            if not results:  # Check if the results dict itself is empty
                st.info("The response from the server was empty or no tables found.")
            else:
                for table, data in results.items():
                    st.subheader(f"Table: {table}")
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write(f"No data found or returned for {table}")


# --- Find Posts by Email Action ---
elif action == "Find Posts by Email":
    st.header("Find Posts by User Email")
    email_input = st.text_input("Enter the email address of the user:", placeholder="e.g., Tissa47@gmx.com")

    if st.button("Search Posts 🚀"):
        if email_input:
            # The endpoint path in FastAPI is /by-email/{user_email}
            # The FASTAPI_BASE_URL (http://localhost:80) is prepended by make_api_request
            api_endpoint = f"/by-email/{email_input}"

            posts = make_api_request(api_endpoint)

            if posts is not None:  # Check if request was successful (posts can be an empty list)
                if posts:  # If posts list is not empty
                    st.success(f"✅ Found {len(posts)} post(s) for '{email_input}':")
                    display_posts = []
                    for post in posts:
                        display_posts.append({
                            "Post ID": post.get("id"),
                            "Content": post.get("content", "N/A"),
                            "Creation Date": post.get("creationDate"),
                            "Language": post.get("language", "N/A"),  # Assuming this is a string like "pl;en"
                            "Length": post.get("length", "N/A")
                        })
                    df = pd.DataFrame(display_posts)
                    st.dataframe(df, use_container_width=True)

                    if st.checkbox("Show raw JSON for the first post (if any)", key="show_raw_json_posts"):
                        if posts:
                            st.json(posts[0])
                        else:
                            st.info("No posts to show in JSON format.")
                else:  # posts is an empty list
                    st.warning(
                        f"🤷 No posts found for user with email '{email_input}'. They might exist but have not posted "
                        f"anything."
                    )
            # Error handling (including 404 for "Person not found") is done within make_api_request.
        else:
            st.warning("Doh! Please enter an email address to search.")


# --- Find Forums by Email Action ---
elif action == "Find Forums by Email":
    st.header("Find Forums by User Email (Neo4j)")
    input = st.text_input("Enter the email address of the user:", placeholder="e.g., Tissa47@gmx.com")

    if st.button("Search Forums 🔍"):
        if input:
            endpoint = f"/forumsEmail/{input}"
            print("Send request for" +input)
            forums = make_api_request(endpoint)

            if forums is not None:
                if forums:
                    st.success(f"✅ Found {len(forums)} forum(s) linked to '{input}':")
                    df = pd.DataFrame(forums)
                    st.dataframe(df, use_container_width=True)

                    if st.checkbox("Show raw JSON", key="show_raw_forums_json"):
                        st.json(forums)
                else:
                    st.warning(f"No forums found for user '{input}'.")
        else:
            st.warning("Please enter a valid email address.")

# --- Find 2nd Degree Connections Who Commented on Liked Posts ---
elif action == "Find 2nd Degree Commenters on Liked Posts by Email":
    st.header("Find 2nd Degree Commenters on Liked Posts by Email")
    input = st.text_input("Enter the email address of the user:", placeholder="e.g., Tissa47@gmx.com")

    if st.button("Search Connections 🔍"):
        if input:
            endpoint = f"/second_degree_commenters_on_liked_posts/{input}"
            results = make_api_request(endpoint)

            if results is not None:
                if results:
                    st.success(f"✅ Found {len(results)} comment(s) from 2nd degree connections related to liked posts:")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    if st.checkbox("Show raw JSON", key="show_raw_2nd_degree_json"):
                        st.json(results)
                else:
                    st.warning(f"No matching results found for user '{input}'.")
        else:
            st.warning("Please enter a valid email address.")


# --- Find Common Interests among Active Users ---
elif action == "Find Common Interests by Organisation":
    st.header("Common Interests among Active Users ")
    input = st.text_input("Enter the name of the organisation:", placeholder="e.g., UniTO")

    if st.button("Search Connections 🔍"):
        if input:
            endpoint = f"/common_interests_among_active_people/{input}"
            results = make_api_request(endpoint)

            if results is not None:
                if results:
                    st.success(f"✅ Found {len(results)} the top 10 most used tags by people who work or study in the same organsation:")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)

                    if st.checkbox("Show raw JSON", key="show_raw_2nd_degree_json"):
                        st.json(results)
                else:
                    st.warning(f"No matching results found for user '{input}'.")
        else:
            st.warning("Please enter a valid email address.")

