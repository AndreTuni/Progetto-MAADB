import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date

# Set page configuration
st.set_page_config(
    page_title="LDBC SNB Query Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and introduction
st.title("LDBC SNB Database Query Dashboard")
st.markdown("""
This dashboard interacts with a NoSQL dataset (LDBC SNB) spread across MongoDB, Neo4j, and PostgreSQL.
Select a query type from the sidebar and provide the required parameters to execute queries.
""")

# Assume these are imported from backend modules
def query_person_posts(person_id):
    """Placeholder for backend function to get posts by person ID"""
    # This would be implemented in the backend
    # For demonstration, return mock data
    mock_data = {
        'PostID': [f"post_{i}" for i in range(1, 6)],
        'Content': [f"Content of post {i}" for i in range(1, 6)],
        'CreationDate': pd.date_range(start='2023-01-01', periods=5),
        'Likes': np.random.randint(0, 100, size=5)
    }
    return pd.DataFrame(mock_data)

def query_comments_by_tag(tag_name):
    """Placeholder for backend function to get comments by tag"""
    mock_data = {
        'CommentID': [f"comment_{i}" for i in range(1, 8)],
        'Content': [f"Comment about {tag_name} #{i}" for i in range(1, 8)],
        'CreationDate': pd.date_range(start='2023-01-01', periods=7),
        'Author': [f"Person_{i}" for i in range(10, 17)]
    }
    return pd.DataFrame(mock_data)

def query_person_forums(person_id):
    """Placeholder for backend function to get forums by person ID"""
    mock_data = {
        'ForumID': [f"forum_{i}" for i in range(1, 5)],
        'Title': [f"Forum about topic {i}" for i in range(1, 5)],
        'CreationDate': pd.date_range(start='2022-01-01', periods=4),
        'MemberCount': np.random.randint(10, 500, size=4)
    }
    return pd.DataFrame(mock_data)

def query_same_company_same_forum():
    """Placeholder for backend function to find people working in same company and same forum"""
    mock_data = {
        'Person1': [f"Person_{i}" for i in range(1, 6)],
        'Person2': [f"Person_{i+10}" for i in range(1, 6)],
        'Company': ['Tech Inc.', 'DataCorp', 'Tech Inc.', 'InfoSys', 'DataCorp'],
        'Forum': ['Programming', 'Data Science', 'AI Discussion', 'Web Dev', 'ML Research']
    }
    return pd.DataFrame(mock_data)

def query_second_degree_comments(person_id):
    """Placeholder for backend function to find second-degree connections with comments"""
    mock_data = {
        'Friend_of_Friend': [f"Person_{i}" for i in range(20, 25)],
        'PostID': [f"post_{i}" for i in range(1, 6)],
        'CommentContent': [f"This is an interesting comment on post {i}" for i in range(1, 6)],
        'CommentDate': pd.date_range(start='2023-01-01', periods=5)
    }
    return pd.DataFrame(mock_data)

def query_forums_by_tagclass_members(min_members):
    """Placeholder for backend function to find forums with X members interested in same tagclass"""
    mock_data = {
        'ForumID': [f"forum_{i}" for i in range(1, 5)],
        'Title': [f"Forum about topic {i}" for i in range(1, 5)],
        'MemberCount': [min_members + i*5 for i in range(1, 5)],
        'TagClass': ['Technology', 'Science', 'Art', 'Sports']
    }
    return pd.DataFrame(mock_data)

def query_active_cities():
    """Placeholder for backend function to find cities with 10+ active people"""
    mock_data = {
        'City': ['New York', 'London', 'Berlin', 'Tokyo', 'Paris'],
        'ActivePersons': [25, 18, 12, 15, 11],
        'TotalPosts': [145, 98, 67, 103, 78],
        'TotalComments': [234, 187, 121, 198, 145]
    }
    return pd.DataFrame(mock_data)

def query_tags_by_city(person_id):
    """Placeholder for backend function to find tags used by people from same city"""
    mock_data = {
        'Tag': ['Programming', 'Data', 'Python', 'AI', 'Web', 'Database', 'Cloud'],
        'UsageCount': [45, 38, 32, 28, 25, 22, 18]
    }
    return pd.DataFrame(mock_data)

def query_common_tags_workplace_university():
    """Placeholder for backend function to find common interests among people with 10+ posts"""
    mock_data = {
        'Tag': ['AI', 'MachineLearning', 'BigData', 'Python', 'Cloud'],
        'Count': [67, 54, 42, 38, 31],
        'Workplace/University': ['Google', 'Stanford', 'Microsoft', 'MIT', 'Amazon']
    }
    return pd.DataFrame(mock_data)

# Sidebar for navigation
st.sidebar.title("Navigation")
query_type = st.sidebar.radio(
    "Select Query Type:",
    ["Parametric Lookup Queries", "Analytical Queries"]
)

if query_type == "Parametric Lookup Queries":
    # Create tabs for each parametric query
    tab1, tab2, tab3 = st.tabs(["Posts by Person", "Comments by Tag", "Forums by Person"])
    
    with tab1:
        st.header("1. Mostra i post creati da una persona")
        
        person_id = st.text_input("PersonID", value="person_1", key="person_posts_id")
        
        if st.button("Run Query", key="run_person_posts"):
            with st.spinner("Querying database..."):
                result_df = query_person_posts(person_id)
                
            st.success(f"Found {len(result_df)} posts created by Person {person_id}")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                st.subheader("Posts Popularity")
                fig = px.bar(result_df, x='PostID', y='Likes', title='Number of Likes per Post')
                st.plotly_chart(fig)
    
    with tab2:
        st.header("2. Mostra tutti i commenti con un certo tag")
        
        tag_name = st.text_input("Tag Name", value="Python", key="comments_tag")
        
        if st.button("Run Query", key="run_comments_tag"):
            with st.spinner("Querying database..."):
                result_df = query_comments_by_tag(tag_name)
                
            st.success(f"Found {len(result_df)} comments with tag '{tag_name}'")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                st.subheader("Comments Timeline")
                fig = px.line(result_df, x='CreationDate', y=result_df.index, title=f'Comments with tag "{tag_name}" over time')
                st.plotly_chart(fig)
    
    with tab3:
        st.header("3. Mostra i forum a cui partecipa una persona")
        
        person_id = st.text_input("PersonID", value="person_2", key="person_forums_id")
        
        if st.button("Run Query", key="run_person_forums"):
            with st.spinner("Querying database..."):
                result_df = query_person_forums(person_id)
                
            st.success(f"Found {len(result_df)} forums for Person {person_id}")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                st.subheader("Forum Membership")
                fig = px.bar(result_df, x='Title', y='MemberCount', title='Member Count by Forum')
                st.plotly_chart(fig)

else:  # Analytical Queries
    # Create tabs for each analytical query
    analytical_query = st.sidebar.selectbox(
        "Select Analytical Query:",
        [
            "1. Same Company & Forum",
            "2. Second-Degree Connections with Comments",
            "3. Forums by TagClass Members",
            "4. Active Cities",
            "5. Tags by City",
            "6. Common Interests by Workplace/University"
        ]
    )
    
    if analytical_query == "1. Same Company & Forum":
        st.header("1. Trova tutte le persone che lavorano nella stessa azienda dal 2020 e sono membri dello stesso forum")
        
        min_year = st.slider("Minimum Employment Year", min_value=2015, max_value=2023, value=2020)
        
        if st.button("Run Query", key="run_company_forum"):
            with st.spinner("Querying database..."):
                result_df = query_same_company_same_forum()
                
            st.success(f"Found {len(result_df)} pairs of people in the same company since {min_year} and same forum")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                company_counts = result_df['Company'].value_counts().reset_index()
                company_counts.columns = ['Company', 'Count']
                
                fig = px.pie(company_counts, values='Count', names='Company', 
                            title='Distribution by Company')
                st.plotly_chart(fig)
    
    elif analytical_query == "2. Second-Degree Connections with Comments":
        st.header("2. Trova le connessioni di secondo grado di una persona che hanno scritto commenti su post che piacciono alla persona stessa")
        
        person_id = st.text_input("PersonID", value="person_5", key="second_degree_id")
        
        if st.button("Run Query", key="run_second_degree"):
            with st.spinner("Querying database..."):
                result_df = query_second_degree_comments(person_id)
                
            st.success(f"Found {len(result_df)} second-degree connections with comments on posts liked by Person {person_id}")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                st.subheader("Comments Timeline")
                fig = px.scatter(result_df, x='CommentDate', y='Friend_of_Friend', 
                                title=f'Comments by Second-Degree Connections of Person {person_id}')
                st.plotly_chart(fig)
    
    elif analytical_query == "3. Forums by TagClass Members":
        st.header("3. Tutti i forum con più di X membri interessati a tag della stessa tagclass")
        
        min_members = st.number_input("Minimum Members (X)", min_value=5, max_value=100, value=20)
        
        if st.button("Run Query", key="run_forums_tagclass"):
            with st.spinner("Querying database..."):
                result_df = query_forums_by_tagclass_members(min_members)
                
            st.success(f"Found {len(result_df)} forums with more than {min_members} members interested in tags of the same tagclass")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                fig = px.bar(result_df, x='Title', y='MemberCount', color='TagClass',
                            title=f'Forums with > {min_members} members by TagClass')
                st.plotly_chart(fig)
    
    elif analytical_query == "4. Active Cities":
        st.header("4. Trova le città da cui provengono almeno 10 persone attive (che hanno creato o commentato almeno 5 post/commenti)")
        
        min_people = st.slider("Minimum Active People", min_value=5, max_value=30, value=10)
        min_activity = st.slider("Minimum Posts/Comments per Person", min_value=1, max_value=20, value=5)
        
        if st.button("Run Query", key="run_active_cities"):
            with st.spinner("Querying database..."):
                result_df = query_active_cities()
                
            st.success(f"Found {len(result_df)} cities with at least {min_people} people who created/commented on {min_activity}+ posts")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                fig = px.bar(result_df, x='City', y=['TotalPosts', 'TotalComments'], 
                            title='Activity by City', barmode='group')
                st.plotly_chart(fig)
    
    elif analytical_query == "5. Tags by City":
        st.header("5. Trova i tag più usati da persone nate nella stessa città di un utente dato")
        
        person_id = st.text_input("PersonID", value="person_3", key="tags_city_id")
        
        if st.button("Run Query", key="run_tags_city"):
            with st.spinner("Querying database..."):
                result_df = query_tags_by_city(person_id)
                
            city_name = "Milan"  # This would come from the actual query
            st.success(f"Found {len(result_df)} popular tags used by people from {city_name} (same as Person {person_id})")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                fig = px.bar(result_df, x='Tag', y='UsageCount', 
                            title=f'Most Used Tags by People from {city_name}')
                st.plotly_chart(fig)
    
    elif analytical_query == "6. Common Interests by Workplace/University":
        st.header("6. Trova gli interessi più comuni (Tag) tra le persone che hanno pubblicato almeno 10 post e lavorano nello stesso posto o studiano nella stessa università")
        
        min_posts = st.slider("Minimum Posts per Person", min_value=5, max_value=50, value=10)
        entity_type = st.radio("Entity Type", ["Workplace", "University", "Both"])
        
        if st.button("Run Query", key="run_common_interests"):
            with st.spinner("Querying database..."):
                result_df = query_common_tags_workplace_university()
                
            st.success(f"Found {len(result_df)} common interests among people with {min_posts}+ posts in the same workplace/university")
            st.dataframe(result_df)
            
            # Example visualization
            if not result_df.empty:
                fig = px.bar(result_df, x='Tag', y='Count', color='Workplace/University',
                            title=f'Common Interests Among People with {min_posts}+ Posts')
                st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown("LDBC SNB Query Dashboard | University Project")