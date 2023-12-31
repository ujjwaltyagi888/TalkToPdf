import streamlit as st
import pickle
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback

# st.title("talk to pdf")
# st.write('Hello guys')

def main():
    st.header("Talk to pdf")

    load_dotenv()

    pdf= st.file_uploader("Upload your pdf",type='pdf')
    # pdf= st.file_uploader("Upload your pdf",type='text')

    if pdf is not None:
        pdf_reader =PdfReader(pdf)
        

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # st.write(text)

        text_splitter  = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap= 200,
            length_function= len
            )
        chunks= text_splitter.split_text(text=text)

    
        store_name = pdf.name[:-4]
        st.write(f'{store_name}')


        if os.path.exists (f"{store_name}.pkl"):
            with open(f"{store_name}.pkl","rb") as f:
                VectorStore =pickle.load(f)
            # st.write("Embeddings Loaded from the disk")
        else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks,embedding=embeddings)
            with open(f"{store_name}.pkl","wb") as f:
                pickle.dump(VectorStore,f)

        query = st.text_input("Ask something")

        if query:
            docs= VectorStore.similarity_search(query=query,k=3)

            llm= OpenAI()
            chain = load_qa_chain(llm=llm,chain_type="stuff")
            with get_openai_callback() as cb: 
                response = chain.run(input_documents=docs, question=query)
                print(cb)
            st.write(response)

if __name__=='__main__':
    main()