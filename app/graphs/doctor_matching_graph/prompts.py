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


DATE_COLLECTION_PROMPT = """Ask the user for their preferred appointment date.

Current date: {current_date}

Ask the user when they would like to schedule their appointment. Guide them to provide a specific date.
Be conversational and helpful.

Examples:
- "When would you like to schedule your appointment? Please provide a date (e.g., tomorrow, 2025-12-30, or next Monday)."
- "What date works best for you? You can say 'tomorrow', 'next week', or give me a specific date like '2025-12-30'."

Respond with ONLY the question text (no labels, no JSON).
"""


BOOKING_CONFIRMATION_PROMPT = """Create a booking confirmation message for the user.

Doctor Details:
{doctor_details}

Appointment Details:
- Date: {date}
- Time: {time_slot}

Patient Symptoms:
{symptoms}

Create a professional confirmation message asking the user to confirm the booking.
Include all relevant details and end with: "Would you like to confirm this booking? (yes/no)"
"""


FINAL_RESPONSE_PROMPT = """Generate a final confirmation message for a successfully booked appointment.

Appointment Details:
{appointment_details}

Create a friendly, professional message that:
1. Confirms the booking
2. Provides appointment ID
3. Summarizes key details (doctor, date, time, location)
4. Gives helpful next steps or reminders

Be warm and reassuring.
"""

