from embedding.embedding_generator import dataPreprocessing
import os
def generate_answer(question):
    # Path to the PDF file
    folder_path = '../data'
    pdf_docs = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.endswith('.pdf')
    ]

    # Extract text from the PDF
    raw_text = dataPreprocessing.load_file(pdf_docs)

    # Split the text into chunks
    text_chunks = dataPreprocessing.split_documents(raw_text)

    # Create the vector store
    normalized_embeddings = dataPreprocessing.generate_embeddings(text_chunks)

    # Create the conversation chain
    conversation = get_conversation_chain(vector_store)

    # Get the answer from the conversation chain
    simulated_answer = conversation.run(question)
    return simulated_answer