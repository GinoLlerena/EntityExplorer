from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import spacy

nlp_en = spacy.load("en_core_web_lg")
app = FastAPI()

# Define custom job titles and attendee types
job_title_keywords = ["Manager", "Director", "Engineer", "Specialist", "Representative"]
attendee_type_keywords = ["Crew", "Exhibitor", "Speaker", "Guest", "VIP"]

# Example function to dynamically classify data
def classify_badge_data(extracted_data):
    # Join the data into a single string for NLP processing
    text = " ".join(extracted_data)
    
    # Process the text using spaCy
    doc = nlp_en(text)
    
    # Initialize an object to hold classified data
    classified_data = {
        "firstName": "",
        "lastName": "",
        "companyName": "",
        "jobTitle": "",
        "attendeeType": ""
    }
    
    # Process named entities detected by spaCy
    person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    organization_entities = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    
    # Assign the first two PERSON entities as first name and last name (if available)
    if len(person_entities) > 0:
        classified_data["firstName"] = person_entities[0]
    if len(person_entities) > 1:
        classified_data["lastName"] = person_entities[1]

    # Assign the first ORG entity as the company name
    if organization_entities:
        classified_data["companyName"] = organization_entities[0]
    
    # Iterate over tokens to detect job titles and attendee types
    for token in doc:
        if any(keyword.lower() in token.text.lower() for keyword in job_title_keywords):
            classified_data["jobTitle"] = token.text
        if any(keyword.lower() in token.text.lower() for keyword in attendee_type_keywords):
            classified_data["attendeeType"] = token.text

    # Check for last name if not filled (fallback based on pattern in data)
    if classified_data["firstName"] and not classified_data["lastName"]:
        possible_last_names = [word for word in extracted_data if word not in classified_data.values()]
        if possible_last_names:
            classified_data["lastName"] = possible_last_names[0]

    return classified_data


class Data(BaseModel):
    text: List[str]


@app.post("/text/")
def extract_entities(data: Data, lang: str):
    """ doc_en = classify_badge_data(data.text)
    return { "data": doc_en } """
    text = ",".join(data.text)
    doc_en  = nlp_en(text)
     
    ents = []
    for ent in doc_en.ents:
        ents.append({"text": ent.text, "label_": ent.label_})
    return {"message": data.text, "lang": lang, "ents": ents}