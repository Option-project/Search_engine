import streamlit as st
from API.model_integration_streamlit import generate_answer, create_vector_store
import sentence_transformers
print(sentence_transformers.__version__)

# Streamlit app configuration
st.set_page_config(page_title="Search Engine", page_icon="🔍")

# Title of the Streamlit app
st.title("🔍 Search Engine")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Query", "Create Vector Store"])

# Query Page
if page == "Query":
    st.header("💬 Ask a Question")
    question = st.text_input("Enter your question:")

    if st.button("Get Answer"):
        if question.strip():
            with st.spinner("Generating answer..."):
                try:
                    answer, references = generate_answer(question)
                    st.success(f"**Answer:** {answer}")
                    
                    if references:
                        st.info("**References:**")
                        for ref in references:
                            st.write(f"- {ref}")
                    else:
                        st.info("No references found.")
                except RuntimeError as e:
                    st.error(f"🚨 Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question.")

# Create Vector Store Page
elif page == "Create Vector Store":
    st.header("🗂️ Create Vector Store")

    if st.button("Create Vector Store"):
        with st.spinner("Processing documents and creating vector store..."):
            try:
                create_vector_store()
                st.success("✅ Vector store created successfully.")
            except ValueError as e:
                st.error(f"🚨 Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
