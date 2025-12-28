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


DOCTOR_PRESENTATION_PROMPT = """Format the available doctors in a clear, conversational way.

Doctors List:
{doctors_json}

Instructions:
- Present top 3 doctors
- Include: name, specialty, rating, experience, location, consultation fee
- Use emojis for visual appeal (⭐ 📍 💰 🗣️)
- End with: "Click 'Book Appointment' button to schedule with your preferred doctor."
- Be warm and helpful

Format each doctor like this:
**Dr. [Name]** - [Specialty]
⭐ [Rating] | [Years] years experience
📍 [Location]
💰 ₹[Fee] for [Duration] mins
🗣️ Speaks: [Languages]

Example Output:
Here are the best Ayurvedic doctors in your area:

**1. Dr. Rajesh Sharma** - Panchakarma Specialist
⭐ 4.8 | 15 years experience
📍 South Delhi
💰 ₹600 for 30 mins
🗣️ Speaks: Hindi, English

**2. Dr. Priya Verma** - Rasayana Expert
⭐ 4.6 | 10 years experience
📍 North Delhi
💰 ₹500 for 30 mins
🗣️ Speaks: Hindi, English

✨ Click 'Book Appointment' button below to schedule with your preferred doctor.
"""




