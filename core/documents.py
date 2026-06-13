import fitz  # pymupdf
import os

def read_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        return f"Could not read PDF: {e}"

def read_text_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"Could not read file: {e}"

def read_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return read_pdf(file_path)
    elif ext in [".txt", ".md", ".py", ".js", ".html", ".css"]:
        return read_text_file(file_path)
    else:
        return f"Unsupported file type: {ext}"

def summarize_document(file_path, question=None):
    content = read_document(file_path)
    if content.startswith("Could not"):
        return content

    # Trim if too long
    if len(content) > 6000:
        content = content[:6000] + "\n\n[Document truncated...]"

    if question:
        prompt = f"""
        Here is the content of a document:
        
        {content}
        
        Answer this question about it:
        {question}
        """
    else:
        prompt = f"""
        Here is the content of a document:
        
        {content}
        
        Please:
        1. Summarize the key points in plain English
        2. List the most important takeaways
        3. Note anything a student should pay attention to
        """
    return prompt