import os
import re
import pandas as pd
import spacy
import pytesseract
from pdf2image import convert_from_path
from spacy.matcher import Matcher

# Configure Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"E:\boo academic\intern\Tesseract-OCR\tesseract.exe"

# Load SpaCy language model
nlp = spacy.load("en_core_web_sm")

def extract_text_with_ocr(pdf_path):
    """Extract text from an image-based PDF using OCR."""
    text = ""
    try:
        pages = convert_from_path(pdf_path, dpi=500)
        for page in pages:
            page_text = pytesseract.image_to_string(page)
            text += page_text
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  
        text = re.sub(r'\s+', ' ', text).strip()  
    except Exception as e:
        print(f"Error: {e}")
    return text

def preprocess_text(text):
    """Preprocess OCR text to remove irrelevant content."""
    text = re.sub(r'CONTACT|ADDRESS|St\.|Anywhere', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def validate_name(name):
    """Validate extracted names to filter out noise."""
    # Ensure the name consists of exactly two words
    if len(name.split()) == 2:
        # Check if both words start with uppercase
        if all(word[0].isupper() for word in name.split()):
            return True
    return False

def extract_name_with_rules(text):
    """Extract name from text using SpaCy's Matcher with validation."""
    text = preprocess_text(text)  # Preprocess text
    doc = nlp(text)
    matcher = Matcher(nlp.vocab)
    # Define a pattern for proper nouns (e.g., first and last name)
    pattern = [{"POS": "PROPN"}, {"POS": "PROPN"}]
    matcher.add("FULL_NAME", [pattern])
    
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        extracted_name = span.text.strip()
        if validate_name(extracted_name):
            return extracted_name  # Return the first valid name
    return "Not Found"


def extract_phone_numbers(text):
    """Extract phone numbers from text."""
    phone_pattern = r'(\+?[0-9]{1,3}[-.\s]?)?(\(?[0-9]{1,4}\)?[-.\s]?)?(\(?[0-9]{2,3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{3,})'
    matches = re.findall(phone_pattern, text)
    formatted_phones = {phone[0] + phone[1] + phone[2] for phone in matches}
    return list(formatted_phones)

def extract_emails(text):
    """Extract emails from text."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = re.findall(email_pattern, text)
    unique_emails = {email.strip() for email in matches}
    return list(unique_emails)

def process_resumes(folder_path):
    """Process resumes in a folder and extract details."""
    data = []
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith('.pdf') and os.path.isfile(file_path):
                print(f"Processing file: {file_name}")
                text = extract_text_with_ocr(file_path)
                name = extract_name_with_rules(text)
                emails = extract_emails(text)
                phones = extract_phone_numbers(text)
                data.append({
                    'File Name': file_name, 
                    'Name': name, 
                    'Emails': "; ".join(emails), 
                    'Phone Numbers': "; ".join(phones)
                })
    return data

def save_to_csv(data, output_csv):
    """Save extracted data to a CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_csv, index=False)
        print(f"Data saved to {output_csv}")
    else:
        print("No data to save.")

# Folder containing resumes
folder_path = r"E:\boo academic\intern\ResumeParser\rough"
# Output CSV file path
output_csv = "output.csv"

resume_data = process_resumes(folder_path)

if resume_data:
    for entry in resume_data:
        print(f"File Name: {entry['File Name']}, Name: {entry['Name']}, Emails: {entry['Emails']}, Phone Numbers: {entry['Phone Numbers']}")

save_to_csv(resume_data, output_csv)


