import streamlit as st
import requests
import json  # Not strictly used for display here, but good to have if needed for raw JSON later
import pandas as pd
import datetime  # For year input default
import altair as alt

# --- CONFIGURATION ---
# Ensure this matches the port your FastAPI app is running on.
FASTAPI_BASE_URL = "http://localhost:8000"  # Or your actual FastAPI URL

st.set_page_config(page_title="Progetto MAADB", layout="wide")
st.title("📊 Progetto MAADB Dashboard")


# --- Sidebar for navigation ---
action = None
st.sidebar.title("Navigation")
main_menu = st.sidebar.radio(
    "Choose a section",
    ["🏠 Home", "🔗 Check Connections", "⚙️ Parametric Queries", "📈 Analytical Queries"]
)


# Default content
if main_menu == "🏠 Home":
    st.markdown("## 👋 Welcome to the MAADB Project Dashboard")
    st.markdown("""
    <div style='font-size: 18px; line-height: 1.6'>
        This interactive dashboard allows you to explore and analyze the <strong>MAADB</strong> project's data using powerful database queries.
        <br><br>
        Use the menu on the left to navigate through the various features. Each section offers tools and insights powered by:
        <ul>
            <li><strong>📦 MongoDB</strong> — for document-based data like posts, users, and forums</li>
            <li><strong>🔗 Neo4j</strong> — for relationship-based data such as social connections</li>
            <li><strong>🧮 PostgreSQL</strong> — for static data such as organisations or places</li>
        </ul>
        <br>
        💡 <em>Select one of the modules in the sidebar to get started!</em>
    </div>
    """, unsafe_allow_html=True)

    st.info("Tip: You can switch between sections at any time using the sidebar.")


# Section 1: Connection health
elif main_menu == "🔗 Check Connections":
    action = st.sidebar.selectbox("🔍 Select Connection", [
        "-- Select an option --", # Default option
        "MongoDB Connection",
        "Neo4J Connection",
        "PostgreSQL Connection"
    ])
    st.subheader(f"🔗 Action: {action}")


# Section 2: Parametric Queries
elif main_menu == "⚙️ Parametric Queries":
    action = st.sidebar.selectbox("🧪 Select Query", [
        "-- Select an option --", # Default option
        "Post of a Person",
        "Forum of a Person",
        "Friends who Comment",
        "Colleagues in same Forum",
        "Active second-degree Connections",
    ])
    st.subheader(f"⚙️ Action: {action}")


# Section 3: Analytical Queries
elif main_menu == "📈 Analytical Queries":
    action = st.sidebar.selectbox("📊 Select Query", [
        "-- Select an option --", # Default option
        "Cities with active People",
        "Favorite Tags for Birthplace",
        "Common Interests",
        "Forums with interest in TagClass"
    ])
    st.subheader(f"📈 Action: {action}")


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
if action == "-- Select an option --":
    st.markdown("Please select an option from the sidebar!") 


# --- MongoDB Actions ---
if action == "MongoDB Connection":
    st.markdown("ℹ️ This action allows you to check the connection status with the MongoDB database")
    if st.button("Check MongoDB Connection"):
        result = make_api_request("/mongo/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")


# --- Neo4j Actions ---
elif action == "Neo4J Connection":
    st.markdown("ℹ️ This action allows you to check the connection status with the Neo4J database") 
    if st.button("Check Neo4j Connection"):
        result = make_api_request("/neo4j/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")


# --- PostgreSQL Actions ---
elif action == "PostgreSQL Connection":
    st.markdown("ℹ️ This action allows you to check the connection status with the PostgreSQL database") 
    if st.button("Check PostgreSQL Connection"):
        result = make_api_request("/postgres/health")
        if result:
            st.success(result.get("status", "Status not found"))
            st.write(f"Server Info: {result.get('server_info', 'Server info not available')}")


# --- 1. Find Posts by Email Action ---
elif action == "Post of a Person":
    st.markdown("ℹ️ This query allows you to view posts created by a person") 
    email_input = st.text_input("Enter the email address of the user:", placeholder="e.g., Tissa47@gmx.com")

    if st.button("Search Posts 🚀"):
        if email_input:
            # The endpoint path in FastAPI is /by-email/{user_email}
            # The FASTAPI_BASE_URL (http://localhost:8000) is prepended by make_api_request
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
                else:  # posts is an empty list
                    st.warning(
                        f"🤷 No posts found for user with email '{email_input}'. They might exist but have not posted "
                        f"anything."
                    )
            # Error handling (including 404 for "Person not found") is done within make_api_request.
        else:
            st.warning("Doh! Please enter an email address to search.")


# --- 2. Find Forums by Email Action ---
elif action == "Forum of a Person":
    st.markdown("ℹ️ This query allows you to find all forums a person belongs to") 
    input = st.text_input("Enter the email address of the user:", placeholder="e.g., Tissa47@gmx.com")

    if st.button("Search Forums 🔍"):
        if input:
            endpoint = f"/forumsEmail/{input}"
            forums = make_api_request(endpoint)

            if forums is not None:
                if forums:
                    st.success(f"✅ Found {len(forums)} forum(s) linked to '{input}':")
                    df = pd.DataFrame(forums)
                    st.dataframe(df, use_container_width=True)
                    st.write(" ")
                    if not df.empty:
                        chart = alt.Chart(df).mark_bar().encode(
                            x=alt.X("forum_id:N", title="Forum ID"),
                            y=alt.Y("member_count:Q", title="Member Count"),
                            tooltip=["forum_id", "member_count", "title"]
                        ).properties(
                            title="📊 Member Count per Forum",
                            width=600,
                            height=400
                        )
                        st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning(f"No forums found for user '{input}'.")
        else:
            st.warning("Please enter a valid email address.")


# --- 3. Find Persons who Know and Commented Action ---
elif action == "Friends who Comment":
    st.markdown("ℹ️ This query allows you to find all the people who know a person and have commented on his posts, with forum details ")
    target_email = st.text_input("Enter the email address of the user:", placeholder="e.g., Jeorge74@gmail.com")

    if st.button("Search Persons 🚀"):
        if target_email:
            # The FASTAPI_BASE_URL (http://localhost:8000) is prepended by make_api_request
            api_endpoint = f"/find-person/by-email/{target_email}"

            results = make_api_request(api_endpoint)

            if results is not None:  # Check if request was successful (persons can be an empty list)
                if results:  # If persons list is not empty
                    # Get the name of target user from first result
                    target_name = f"{results[0]['target_person']['firstName']} {results[0]['target_person']['lastName']}"
                    st.success(f"✅ Found {len(results)} persons who know {target_name} ({target_email}) and have commented on his posts!")
                    
                    for idx, item in enumerate(results):
                        knowing_person = item.get("knowing_person", {})
                        full_name = knowing_person.get("firstName", "N/A") + " " + knowing_person.get("lastName", "N/A")
                        st.subheader(f"👤 {full_name}")

                        # Comments with posts
                        st.markdown("**🗨️ Comments & Related Posts:**")
                        comment_data = []
                        for comment in item.get("comments", []):
                            post = comment.get("post", {})
                            comment_data.append({
                                "Comment ID": comment.get("id"),
                                "Content": comment.get("content", "N/A"),
                                "Post ID": post.get("id", "N/A"),
                                "Post Content": post.get("content", "N/A"),
                                "Forum ID": post.get("forum_id", "N/A"),
                                "Post Creation": post.get("creationDate", "N/A")
                            })
                        st.dataframe(pd.DataFrame(comment_data), use_container_width=True)

                        # Forums
                        forums = item.get("forums", [])
                        if forums:
                            st.markdown(f"**📚 Forums of {target_name}'s Posts:**")
                            forum_data = [{
                                "Forum ID": forum.get("id"),
                                "Title": forum.get("title", "N/A"),
                                "Creation Date": forum.get("creationDate", "N/A")
                            } for forum in forums]
                            st.dataframe(pd.DataFrame(forum_data), use_container_width=True)
                else:  # Persons is an empty list
                    st.warning(
                        f"🤷 No persons found that knows user with email '{target_email}' and has commented on his posts. "
                    )
        # Error handling (including 404 for "Person not found") is done within make_api_request.
        else:
            st.warning("Doh! Please enter an email address to search.")


# --- 4. Find Colleagues in same Forum ---
elif action == "Colleagues in same Forum":
    st.markdown("""
                ℹ️ This query allows you to find Finds groups of people (2 or more) who work at the same company (having started in or before the target year) 
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
                            else:
                                st.write("No members listed for this group (though the group itself was identified).")
                else:  # API returned an empty list
                    st.info(
                        f"No groups found matching the criteria for target year {target_year_input} (limit: {limit_input}).")
            # Error messages from make_api_request (like connection errors or 500s) are handled by the helper.
        else:
            st.warning("Please enter a target year.")


# --- 5. Find 2nd Degree Connections Who Commented on Liked Posts ---
elif action == "Active second-degree Connections":
    st.markdown("ℹ️ This query allows you to find second degree connection of a person who have commented posts that the person likes")
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


# --- 6. Find Cities of active people ---
elif action == "Cities with active People":
    st.markdown("ℹ️ This query allows you to find all the cities from which a minimium number of active people come (ie who have created or commented at least 5/post comments) ")
    min_active_input = st.number_input("Minimum number of active users (who posted or commented at least 5 times):", min_value=1,value=10,step=1)
    if st.button("Search Cities 🏙️"):
        if min_active_input: 
            # The FASTAPI_BASE_URL (http://localhost:8000) is prepended by make_api_request
            api_endpoint = f"/find-cities/by-activeuser?min_active_people={min_active_input}"

            cities = make_api_request(api_endpoint)

            if cities is not None:  # Check if request was successful (cities can be an empty list)
                if cities:  # If posts list is not empty
                    st.success(f"✅ Found {len(cities)} city/cities with at least {min_active_input} active users:")
                    display_cities = []
                    for city in cities:
                        display_cities.append({
                            "City ID": city.get("cityId"),
                            "City Name": city.get("cityName", "N/A"),
                            "Active Users": city.get("activeUserCount")
                        })

                    df = pd.DataFrame(display_cities)
                    st.dataframe(df, use_container_width=True)
                else:  # posts is an empty list
                    st.warning(
                        f"🤷 No cities found with at least {min_active_input} active users."
                    )
            # Error handling (including 404 for "Person not found") is done within make_api_request.
        else:
            st.warning("Doh! Please enter a minimium active number of users to search.")


# --- 7. Favorite Tags for Birthplace ---
elif action == "Favorite Tags for Birthplace":
    st.markdown("""
    ℹ️ This query allows you to find the city of a given a user's email. Then, it identifies the tags
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
        else:
            st.warning("Please enter a user email address.")


# --- 8. Find Common Interests among Active Users ---
elif action == "Common Interests":
    st.markdown("ℹ️ This query allows you to find the most common interests among people who have posted at least 10 posts and work in the same place or study at the same university ")
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
                    st.write(" ")
                    # Pie chart if data is present
                    if "usage_count" in df.columns and not df.empty:
                        df["usage_count"] = pd.to_numeric(df["usage_count"], errors="coerce").fillna(0)
                        df["percent"] = df["usage_count"] / df["usage_count"].sum()

                        pie_chart = alt.Chart(df).mark_arc().encode(
                            theta=alt.Theta(field="usage_count", type="quantitative"),
                            color=alt.Color(field="tag_name", type="nominal"),
                            tooltip=[
                                alt.Tooltip("tag_name:N", title="Tag"),
                                alt.Tooltip("usage_count:Q", title="Usage Count"),
                                alt.Tooltip("percent:Q", format=".1%", title="Percentage")
                            ]
                        ).properties(
                            title="📊 Tag Usage Distribution (Pie Chart)",
                            width=400,
                            height=400
                        )

                        st.altair_chart(pie_chart, use_container_width=True)
                else:
                    st.warning(f"No matching results found for user '{input}'.")
        else:
            st.warning("Please enter a valid email address.")


# --- 9. Find Forum of Members interested in same tagClass by tag class name ---
elif action == "Forums with interest in TagClass":
    st.markdown("ℹ️ This query allows you to view all forums with more than a certain number of members interested in tags of the same tag class  ")
    tagclass_input = st.text_input("Enter the name of the tagClass:", placeholder="e.g., University")
    min_members_input = st.number_input("Minimum number of interested members:", min_value=1, value=5, step=1)
    
    if st.button("Search Forums 🔍"):
        if tagclass_input:
            # Construct query parameters
            api_endpoint = f"/find-forum/by-tagclass/{tagclass_input}?min_members={min_members_input}"

            forums = make_api_request(api_endpoint)

            if forums is not None:  # Check if request was successful (forums can be an empty list)
                if forums:  # If posts list is not empty
                    st.success(f"✅ Found {len(forums)} forum(s) with at least {min_members_input} interested members in tagClass '{tagclass_input}':")
                    display_forums = []
                    for forum in forums:
                        display_forums.append({
                            "Forum ID": forum.get("id"),
                            "Title": forum.get("title", "N/A"),
                            "Creation Date": forum.get("creationDate", "N/A"),
                            "Moderator Person ID": forum.get("ModeratorPersonId", "N/A"),
                            "Interested Members": forum.get("interested_members", "N/A")
                        })

                    df = pd.DataFrame(display_forums)
                    st.dataframe(df, use_container_width=True)
                else:  # posts is an empty list
                    st.warning(
                        f"🤷  No forums found with at least {min_members_input} interested members in tagClass '{tagclass_input}'."
                    )
            # Error handling (including 404 for "Person not found") is done within make_api_request.
        else:
            st.warning("Doh! Please enter a tag class to search.")