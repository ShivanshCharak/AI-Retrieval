from langchain_community.document_loaders import PyPDFLoader 

def document_loader(path: str):
    loader = PyPDFLoader(path)
    loaded_doc = loader.load()
    return loaded_doc