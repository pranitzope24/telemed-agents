"""Prompts for doctor matching graph - Simplified."""


SPECIALTY_MAPPING_PROMPT = """You are a medical specialty advisor. Based on the patient's symptoms, suggest appropriate Ayurvedic specialties.

Patient Symptoms:
{symptoms_summary}

Additional Context:
{additional_context}

Available Ayurvedic Specialties:
- Panchakarma (detoxification, chronic diseases)
- Rasayana (rejuvenation, immunity, anti-aging)
- General Ayurveda (common ailments, preventive care)
- Ayurvedic Dermatology (skin conditions, hair problems)
- Ayurvedic Gastroenterology (digestive issues, gut health)
- Ayurvedic Gynecology (women's health, reproductive issues)
- Kayachikitsa (internal medicine, fever, infections)

Guidelines:
- Suggest 1-2 most relevant specialties
- Provide brief reasoning
- Be confident but not overly technical

Respond with ONLY a JSON object:
{{
  "specialties": ["specialty1", "specialty2"],
  "explanation": "brief explanation for patient"
}}

Example:
{{
  "specialties": ["Kayachikitsa", "General Ayurveda"],
  "explanation": "Your fever and body ache suggest an acute infection that can be treated with Ayurvedic internal medicine."
}}
"""


DOCTOR_PRESENTATION_PROMPT = """Provide a brief overview about the available doctors based on the list provided.

Doctors List:
{doctors_json}

Instructions:
- Give a 3-4 line overview only
- Mention how many doctors were found and their general specialties
- Mention the location/city
- End with: "You can view the complete list of doctors and book an appointment using the button below."
- Keep it brief and conversational
- Do NOT list individual doctor details

Example Output:
Great! I found 3 highly-rated Ayurvedic specialists in Delhi who can help with your condition. They specialize in Panchakarma and Kayachikitsa with ratings above 4.5 stars. You can view the complete list of doctors and book an appointment using the button below.
"""




