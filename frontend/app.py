import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.title("FastAPI + Streamlit Demo")

st.sidebar.header("Available Actions")
action = st.sidebar.selectbox("Choose an action", [
    "Initialize MongoDB",
    "Initialize Neo4j",
    "Initialize PostgreSQL",
    "Find person in MongoDB",
    "Find friends in Neo4j",
    "Find user in PostgreSQL",
    "Cross-database lookup"
])


if action == "Initialize MongoDB":
    if st.button("Insert test person into MongoDB"):
        response = requests.post(f"{BASE_URL}/mongo/init")
        st.write(response.json())

elif action == "Initialize Neo4j":
    if st.button("Insert test graph into Neo4j"):
        response = requests.post(f"{BASE_URL}/neo4j/init")
        st.write(response.json())

elif action == "Find person in MongoDB":
    name = st.text_input("Enter name (e.g., Alice):")
    if st.button("Search MongoDB"):
        response = requests.get(f"{BASE_URL}/mongo/person/{name}")
        st.json(response.json())

elif action == "Find friends in Neo4j":
    name = st.text_input("Enter name (e.g., Alice):")
    if st.button("Get Neo4j friends"):
        response = requests.get(f"{BASE_URL}/neo4j/friends/{name}")
        st.json(response.json())

elif action == "Cross-database lookup":
    name = st.text_input("Enter name (e.g., Alice):")
    if st.button("Get data from MongoDB & Neo4j"):
        response = requests.get(f"{BASE_URL}/cross/{name}")
        st.json(response.json())

elif action == "Initialize PostgreSQL":
    if st.button("Create table and insert test user"):
        response = requests.post(f"{BASE_URL}/postgres/init")
        st.write(response.json())

elif action == "Find user in PostgreSQL":
    name = st.text_input("Enter name (e.g., Alice):", key="pg_name")
    if st.button("Search PostgreSQL"):
        response = requests.get(f"{BASE_URL}/postgres/user/{name}")
        st.json(response.json())

