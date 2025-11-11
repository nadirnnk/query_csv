import streamlit as st
import pandas as pd
import requests
import base64
import io
from PIL import Image

# ==========================================
# 🚀 Configuration
# ==========================================
# Backend API base URL — change if running separately or deployed on cloud
BACKEND_URL = "http://127.0.0.1:8000"

# ==========================================
# 🧠 Streamlit Page Setup
# ==========================================
st.set_page_config(page_title="AI CSV Analyst", layout="wide")
st.title("📊 AI-Powered CSV Data Analyst")
st.caption("Ask questions about your data in plain English — powered by OpenAI & FastAPI backend")

# ==========================================
# 📤 File Upload Section
# ==========================================
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# To store the backend's file_id for later chat requests
if "file_id" not in st.session_state:
    st.session_state.file_id = None

# If a file is uploaded by the user
if uploaded_file:
    # Display a small preview of the uploaded file
    st.subheader("Preview of Uploaded File:")
    df_preview = pd.read_csv(uploaded_file)
    st.dataframe(df_preview.head())

    # Upload file to FastAPI backend only once
    if st.session_state.file_id is None:
        with st.spinner("Uploading file to backend..."):
            # Prepare multipart form data
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            try:
                response = requests.post(f"{BACKEND_URL}/upload/", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.file_id = data["file_id"]
                    st.success("✅ File uploaded successfully!")
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except Exception as e:
                st.error(f"⚠️ Error uploading file: {e}")

# ==========================================
# 💬 Chat / Query Section
# ==========================================
if st.session_state.file_id:
    st.subheader("💬 Ask a question about your data:")
    query = st.text_area("Type your question here...", placeholder="e.g., What is the average revenue by region?")

    # When user clicks submit
    if st.button("Run Query", type="primary"):
        if not query.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Analyzing data..."):
                try:
                    # Send query and file_id to backend /chat endpoint
                    payload = {"query": query, "file_id": st.session_state.file_id}
                    response = requests.post(f"{BACKEND_URL}/chat/", json=payload)

                    st.write("### 🔍 Backend Response:", response.json)

                    # Parse the response
                    if response.status_code == 200:
                        data = response.json()

                        st.write("### 🧩 Generated Code:")
                        st.code(data.get("generated_code", "No code generated"), language="python")

                        st.write("### 📊 Result:")

                        # Display result if present
                        result = data.get("result")
                        image = data.get("image")
                        error = data.get("error")
                        if result is not None:
                            st.write(result)
                        if image is not None:
                            img_data = base64.b64decode(data["image"])
                            image = Image.open(io.BytesIO(img_data))
                            st.image(image, caption="Backend-generated plot")
                        if error is not None:
                            st.write(error)
                    else:
                        st.error(f"Backend error: {response.text}")
                except Exception as e:
                    st.error(f"⚠️ Something went wrong: {e}")

# ==========================================
# 🧹 Footer
# ==========================================
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + FastAPI + OpenAI")
