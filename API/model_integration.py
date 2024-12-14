from llm.utils import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain

def generate_answer(question):
    # Path to the PDF file
    pdf_docs = ['../data/CoursOptimisation.pdf']

    # Extract text from the PDF
    raw_text = get_pdf_text(pdf_docs)

    # Split the text into chunks
    text_chunks = get_text_chunks(raw_text)

    # Create the vector store
    vector_store = get_vector_store(text_chunks)

    # Create the conversation chain
    conversation = get_conversation_chain(vector_store)

    # Get the answer from the conversation chain
    simulated_answer = conversation.run(question)
    return simulated_answer