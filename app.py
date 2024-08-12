import streamlit as st
import hashlib
from utils import create_connection, create_tables

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize the database
conn = create_connection("data/database.db")
create_tables(conn)

def register():
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
            return
        
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_pw))
            conn.commit()
            st.success("Registration successful! Please log in.")
        except sqlite3.IntegrityError:
            st.error("Username or email already exists.")

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
        user = cursor.fetchone()
        
        if user:
            st.session_state['user_id'] = user[0]
            st.session_state['username'] = user[1]
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid username or password.")

def logout():
    st.session_state.pop('user_id', None)
    st.session_state.pop('username', None)
    st.success("Logged out successfully.")

def create_project():
    st.title("Create a Project")
    title = st.text_input("Project Title")
    description = st.text_area("Project Description")
    goal = st.number_input("Funding Goal", min_value=0.0)
    
    if st.button("Create Project"):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (title, description, goal, creator_id) VALUES (?, ?, ?, ?)", 
                       (title, description, goal, st.session_state['user_id']))
        conn.commit()
        st.success("Project created successfully!")

def list_projects():
    st.title("Explore Projects")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    
    for project in projects:
        st.subheader(project[1])
        st.write(project[2])
        st.write(f"Goal: ${project[3]:,.2f}")
        st.write(f"Funds Raised: ${project[4]:,.2f}")
        
        if st.session_state.get('user_id') != project[5]:
            amount = st.number_input(f"Fund {project[1]}", min_value=0.0, key=project[0])
            if st.button(f"Fund Project {project[0]}", key=f"fund_{project[0]}"):
                cursor.execute("UPDATE projects SET funds_raised = funds_raised + ? WHERE id = ?", (amount, project[0]))
                cursor.execute("INSERT INTO transactions (project_id, user_id, amount) VALUES (?, ?, ?)", 
                               (project[0], st.session_state['user_id'], amount))
                conn.commit()
                st.success(f"Funded {project[1]} with ${amount:,.2f}")

def view_my_projects():
    st.title("My Projects")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE creator_id=?", (st.session_state['user_id'],))
    projects = cursor.fetchall()
    
    for project in projects:
        st.subheader(project[1])
        st.write(project[2])
        st.write(f"Goal: ${project[3]:,.
