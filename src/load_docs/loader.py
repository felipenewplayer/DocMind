from langchain_community.document_loaders  import (
   PyPDFLoader,
   TextLoader,
   UnstructuredExcelLoader
) 

LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt":TextLoader,
    ".xlsx": UnstructuredExcelLoader
}