import streamlit as st
import pandas as pd
import requests
import base64
import io
from PIL import Image


# ==========================================
# 🚀 Configuration
# ==========================================
BACKEND_URL = "http://127.0.0.1:8000"

# ==========================================
# 🧠 Streamlit Page Setup
# ==========================================
st.set_page_config(page_title="AI CSV Analyst", layout="wide")



def get_chat_history(user_id):
    """Fetch or create a new chat session from backend."""
    try:
        # If user_id is None, create a new session by calling with 'new' or empty
        session_id = user_id if user_id else "new"
        response = requests.get(f"{BACKEND_URL}/chat/history/{session_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("user_id")  # Returns the user_id (new or existing)
        else:
            st.warning("⚠️ Unable to fetch chat history.")
            return None
    except requests.exceptions.RequestException as e:
        st.warning("⚠️ Backend not reachable.")
        return None





# ==========================================
# 📤 File Upload Function
# ==========================================
def file_upload_interface():
    """Returns file_id if a file is uploaded and selected, None otherwise"""
    
    # Initialize session state for storing multiple files
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}
    if "selected_file_id" not in st.session_state:
        st.session_state.selected_file_id = None

    # File uploader
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], accept_multiple_files=False)

    # If a file is uploaded by the user
    if uploaded_file:
        df_preview = pd.read_csv(uploaded_file)
        
        # Check if this file is already uploaded (by name)
        file_already_exists = any(
            file_data["name"] == uploaded_file.name 
            for file_data in st.session_state.uploaded_files.values()
        )
        
        if not file_already_exists:
            with st.spinner(f"Uploading {uploaded_file.name} to backend..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                try:
                    response = requests.post(f"{BACKEND_URL}/upload/", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        file_id = data["file_id"]
                        
                        st.session_state.uploaded_files[file_id] = {
                            "name": uploaded_file.name,
                            "df": df_preview
                        }
                        
                        st.session_state.selected_file_id = file_id
                        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Error uploading file: {e}")
        else:
            st.info(f" {uploaded_file.name} is already uploaded.")

    # Display file selector if files are uploaded
    if st.session_state.uploaded_files:
        st.subheader("📂 Uploaded Files")
        
        file_options = {
            file_id: file_data["name"] 
            for file_id, file_data in st.session_state.uploaded_files.items()
        }
        
        selected_file_name = st.selectbox(
            "Select a file to work with:",
            options=list(file_options.keys()),
            format_func=lambda x: file_options[x],
            index=list(file_options.keys()).index(st.session_state.selected_file_id) 
                if st.session_state.selected_file_id in file_options else 0
        )
        
        st.session_state.selected_file_id = selected_file_name
        
        # Display preview
        st.subheader(f"Preview: {file_options[selected_file_name]}")
        st.dataframe(st.session_state.uploaded_files[selected_file_name]["df"].head())
        
        # Remove file button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Remove Selected File"):
                del st.session_state.uploaded_files[st.session_state.selected_file_id]
                st.session_state.selected_file_id = (
                    list(st.session_state.uploaded_files.keys())[0] 
                    if st.session_state.uploaded_files else None
                )
                st.rerun()
        
        return st.session_state.selected_file_id
    
    return None

# ==========================================
#  Chat Interface
# ==========================================
def run_chat_interface(file_id, chat_name):
    """Display the chat interface for asking questions"""
    
    st.title("📊 AI-Powered CSV Data Analyst")
    st.caption(f"💬 **{chat_name}** | File ID: `{file_id}`")
    
    # Get file info
    if file_id in st.session_state.uploaded_files:
        file_name = st.session_state.uploaded_files[file_id]["name"]
        st.info(f"📄 Working with: **{file_name}**")
    
    st.markdown("---")
    
    # Query input
    st.subheader("💬 Ask a question about your data:")
    query = st.text_area("Type your question here...", placeholder="e.g., What is the average revenue by region?")

    if st.button("Run Query", type="primary"):
        if not query.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Analyzing data..."):
                try:
                    payload = {
                        "query": query, 
                        "file_id": file_id, 
                        "user_id": st.session_state.user_id
                    }
                    response = requests.post(f"{BACKEND_URL}/chat/", json=payload)

                    if response.status_code == 200:
                        data = response.json()
                        
                        # Store result in session state so it persists
                        st.session_state.last_result = data
                    else:
                        st.error(f"Backend error: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Something went wrong: {e}")
    
    # Display results if they exist in session state
    if "last_result" in st.session_state:
        data = st.session_state.last_result
        
        st.write("### 🧩 Generated Code:")
        st.code(data.get("generated_code", "No code generated"), language="python")

        st.write("### 📊 Result:")

        result = data.get("result")
        image = data.get("image")
        error = data.get("error")
        
        if result is not None:
            st.write(result)
        if image is not None:
            try:
                img_data = base64.b64decode(image)
                image = Image.open(io.BytesIO(img_data))
                st.image(image, caption="Generated plot")
            except Exception:
                st.error("Could not decode backend image")
        if error is not None:
            st.error(error)
        
        # =====================================================
        # 👍 Feedback Section (OUTSIDE spinner, PERSISTS)
        # =====================================================
        st.markdown("---")
        st.write("### 👍 Was this helpful?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Thumbs Up"):
                try:
                    feedback_payload = {
                        "query": query,
                        "code": data.get("generated_code", ""),
                        "feedback": "thumbs_up"
                    }
                    feedback_response = requests.post(
                        f"{BACKEND_URL}/chat/feedback", 
                        json=feedback_payload
                    )
                    if feedback_response.status_code == 200:
                        st.success("✅ Thanks for your feedback!")
                    else:
                        st.error("Failed to submit feedback")
                except Exception as e:
                    st.error(f"Error submitting feedback: {e}")
        
        with col2:
            if st.button("👎 Thumbs Down"):
                try:
                    feedback_payload = {
                        "query": query,
                        "code": data.get("generated_code", ""),
                        "feedback": "thumbs_down"
                    }
                    feedback_response = requests.post(
                        f"{BACKEND_URL}/chat/feedback", 
                        json=feedback_payload
                    )
                    if feedback_response.status_code == 200:
                        st.success("✅ Thanks for your feedback!")
                    else:
                        st.error("Failed to submit feedback")
                except Exception as e:
                    st.error(f"Error submitting feedback: {e}")

# ==========================================
#  Main Application Logic
# ==========================================

# Initialize session state
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}  # {user_id: [chat_name, file_id]}
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "creating_new_chat" not in st.session_state:
    st.session_state.creating_new_chat = False

# ==========================================
# 📱 Sidebar
# ==========================================
st.sidebar.title("💬 Chat Sessions")

# New Chat Button
if st.sidebar.button("➕ New Chat"):
    st.session_state.creating_new_chat = True
    st.session_state.user_id = None  # Deselect current chat
    st.rerun()

# Show Existing Chats
if st.session_state.chat_sessions:
    st.sidebar.subheader("🗂 Your Chats")
    
    for uid, data in st.session_state.chat_sessions.items():
        chat_name, file_id = data
        # Highlight the active chat
        button_type = "primary" if uid == st.session_state.user_id else "secondary"
        
        if st.sidebar.button(f"{'🟢 ' if uid == st.session_state.user_id else ''}{chat_name}", key=uid, type=button_type):
            st.session_state.user_id = uid
            st.session_state.creating_new_chat = False
            st.rerun()

# ==========================================
# 🖥️ Main Content Area
# ==========================================

# Case 1: Creating a new chat
if st.session_state.creating_new_chat:
    st.title("📁 Create New Chat")
    st.caption("Upload a CSV file to start analyzing")
    st.markdown("---")
    
    file_id = file_upload_interface()
    
    if file_id is not None:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Start Chat with This File", type="primary", use_container_width=True):
                
                chat_name = f"Chat {len(st.session_state.chat_sessions) + 1}"
                new_id = get_chat_history(user_id=None)
                st.session_state.chat_sessions[new_id] = [chat_name, file_id]
                st.session_state.user_id = new_id
                st.session_state.creating_new_chat = False
                st.success(f"✅ Started {chat_name}!")
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.creating_new_chat = False
                st.rerun()
    else:
        st.info("Please upload a CSV file to continue")
        
        if st.button("❌ Cancel"):
            st.session_state.creating_new_chat = False
            st.rerun()

# Case 2: Active chat session
elif st.session_state.user_id and st.session_state.user_id in st.session_state.chat_sessions:
    chat_name, file_id = st.session_state.chat_sessions[st.session_state.user_id]
    run_chat_interface(file_id, chat_name)

# Case 3: No chat selected
else:
    st.title("📊 AI-Powered CSV Data Analyst")
    st.caption("Ask questions about your data in plain English — powered by OpenAI & FastAPI backend")
    st.markdown("---")
    
    st.info("Click **'➕ New Chat'** in the sidebar to get started!")
    
    # Show a welcome message or instructions
    st.markdown("""
    ###  Welcome to AI CSV Analyst!
    
    **How to use:**
    1. Click "➕ New Chat" in the sidebar
    2. Upload your CSV file
    3. Ask questions in plain English
    4. Get instant insights and visualizations
    
    **Example questions:**
    - "What is the total revenue by region?"
    - "Show me a bar chart of sales by category"
    - "What are the top 5 customers by purchase amount?"
    """)

# ==========================================
# Footer
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit + FastAPI + OpenAI")