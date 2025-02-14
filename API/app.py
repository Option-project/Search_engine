import streamlit as st
import requests

# FastAPI server URL
FASTAPI_URL = "http://127.0.0.1:8000"

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stTextInput input {
        font-size: 16px;
        padding: 10px;
    }
    .stHeader {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
    }
    .stSidebar {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .stSuccess {
        color: #4CAF50;
        font-weight: bold;
    }
    .stError {
        color: #FF0000;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit App Title
st.title("📊 RAG System Monitoring & QA")

# Sidebar for monitoring controls
st.sidebar.markdown("## 🛠️ Monitoring Controls")

# Start Monitoring Button
if st.sidebar.button("▶️ Start Monitoring"):
    with st.spinner("Starting monitoring..."):
        response = requests.post(f"{FASTAPI_URL}/start_monitoring")
        if response.status_code == 200:
            st.sidebar.success("✅ Monitoring started successfully!")
        else:
            st.sidebar.error("❌ Failed to start monitoring.")

# Stop Monitoring Button
if st.sidebar.button("⏹️ Stop Monitoring"):
    with st.spinner("Stopping monitoring..."):
        response = requests.post(f"{FASTAPI_URL}/stop_monitoring")
        if response.status_code == 200:
            st.sidebar.success("✅ Monitoring stopped successfully!")
        else:
            st.sidebar.error("❌ Failed to stop monitoring.")

# Main Section for Question Answering
st.markdown("## ❓ Ask a Question")

# Text input for the question
question_text = st.text_input("Enter your question here:", placeholder="Type your question...")

# Button to submit the question
if st.button("🚀 Ask"):
    if question_text:
        with st.spinner("🔍 Searching for an answer..."):
            response = requests.post(f"{FASTAPI_URL}/ask", json={"text": question_text})
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                st.markdown(f"### 📝 Answer:")
                st.success(f"**{answer}**")
            else:
                st.error("❌ Failed to get an answer.")
    else:
        st.warning("⚠️ Please enter a question.")

# Status Section
st.markdown("## 📊 System Status")

# Button to check the status
if st.button("🔄 Refresh Status"):
    with st.spinner("Fetching system status..."):
        response = requests.get(f"{FASTAPI_URL}/status")
        if response.status_code == 200:
            status = response.json()
            st.markdown("### 🖥️ Current Status:")
            st.json(status)
        else:
            st.error("❌ Failed to retrieve system status.")

# Additional Info Section
with st.expander("ℹ️ About This App"):
    st.markdown(
        """
        This app interacts with a **RAG (Retrieval-Augmented Generation)** system powered by FastAPI. 
        You can:
        - **Start/Stop Monitoring**: Monitor Google Drive for changes.
        - **Ask Questions**: Get answers from the RAG system.
        - **Check Status**: View the current status of the system.
        
        Built with ❤️ using Streamlit and FastAPI.
        """
    )

