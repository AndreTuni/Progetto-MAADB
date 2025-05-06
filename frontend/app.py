import streamlit as st
import requests
import json

BASE_URL = "http://localhost:80"

st.title("Progetto MAADB")

st.sidebar()
action = st.sidebar.selectbox([
    "MongoDB",
    "Neo4j",
    "PostgreSQL",
    "Cross-database lookup"
])

if action == "MongoDB":
    if st.button("Check MongoDB Connection"):
        try:
            response = requests.get(f"{BASE_URL}/mongo/health")
            if response.status_code == 200:
                result = response.json()  # Parse the JSON response
                st.success(result["status"])
                st.write(f"Server Info: {result['server_info']}")
            else:
                error_data = response.json()  # Parse JSON for error details
                st.error(f"Error: {response.status_code} - {error_data['detail']}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Failed to connect to FastAPI: {e}")
        except json.JSONDecodeError:
            st.error(f"Error: Invalid JSON response from server")  # Handle non-json
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    if st.button("Get First 5 Objects from MongoDB"):
        try:
            response = requests.get(f"{BASE_URL}/mongo/first5")
            if response.status_code == 200:
                results = response.json()  # Parse the JSON response
                for collection, data in results.items():
                    st.subheader(f"Collection: {collection}")
                    if data:
                        st.json(data)  # Display the data as JSON
                    else:
                        st.write(f"No data found in {collection}")
            else:
                error_data = response.json()
                st.error(f"Error: {response.status_code} - {error_data['detail']}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Failed to connect to FastAPI: {e}")
        except json.JSONDecodeError:
            st.error(f"Error: Invalid JSON response from server")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

elif action == "Neo4j":
    name = st.text_input("Enter name (e.g., Alice):")
    if st.button("Get Neo4j friends"):
        response = requests.get(f"{BASE_URL}/neo4j/friends/{name}")
        st.json(response.json())

elif action == "PostgreSQL":
    if st.button("Check PostgreSQL Connection"):
        try:
            response = requests.get(f"{BASE_URL}/postgres/health")
            if response.status_code == 200:
                result = response.json()  # Parse the JSON response
                st.success(result["status"])
                st.write(f"Server Info: {result['server_info']}")
            else:
                error_data = response.json()  # Parse JSON for error details
                st.error(f"Error: {response.status_code} - {error_data['detail']}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Failed to connect to FastAPI: {e}")
        except json.JSONDecodeError:
            st.error(f"Error: Invalid JSON response from server")  # Handle non-json
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    if st.button("Get First 5 Records from PostgreSQL"):
        try:
            response = requests.get(f"{BASE_URL}/postgres/first5")
            if response.status_code == 200:
                results = response.json()  # Parse the JSON response
                for table, data in results.items():
                    st.subheader(f"Table: {table}")
                    if data:
                        st.json(data)  # Display the data as JSON
                    else:
                        st.write(f"No data found in {table}")
            else:
                error_data = response.json()
                st.error(f"Error: {response.status_code} - {error_data['detail']}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Failed to connect to FastAPI: {e}")
        except json.JSONDecodeError:
            st.error(f"Error: Invalid JSON response from server")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")