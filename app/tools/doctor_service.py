"""Doctor service for searching and checking availability."""

from typing import List, Dict, Any, Optional
import asyncio
import httpx
from app.config.api_config import get_api_config
from app.utils.logger import get_logger

logger = get_logger()


class DoctorInfo:
    """Doctor information model."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.user_id = data.get("userId")
        self.specialty_primary = data.get("specialtyPrimary")
        self.specialties_secondary = data.get("specialtiesSecondary", [])
        self.years_experience = data.get("yearsOfExperience")
        self.bio = data.get("bio", "")
        self.consultation_fee = data.get("consultationFee")
        self.consultation_duration = data.get("consultationDuration")
        self.languages = data.get("languagesSpoken", [])
        self.rating = float(data.get("averageRating", 0))
        self.total_consultations = data.get("totalConsultations", 0)
        
        # User details
        user_data = data.get("user", {})
        self.first_name = user_data.get("firstName", "")
        self.last_name = user_data.get("lastName", "")
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        self.gender = user_data.get("gender")
        
        # Profile details - handle null profile
        profile_data = user_data.get("profile") or {}
        self.city = profile_data.get("city", "") if profile_data else ""
        self.state = profile_data.get("state", "") if profile_data else ""
        self.location = f"{self.city}, {self.state}" if self.city and self.state else self.city or self.state or "Location not specified"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.full_name,
            "specialty_primary": self.specialty_primary,
            "specialties_secondary": self.specialties_secondary,
            "years_experience": self.years_experience,
            "bio": self.bio[:200] + "..." if len(self.bio) > 200 else self.bio,
            "consultation_fee": self.consultation_fee,
            "consultation_duration": self.consultation_duration,
            "languages": self.languages,
            "rating": self.rating,
            "total_consultations": self.total_consultations,
            "location": self.location,
            "city": self.city,
            "state": self.state
        }


async def _retry_request(func, *args, max_retries: int = 3, **kwargs) -> Any:
    """Retry a request with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    api_config = get_api_config()
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = api_config.retry_delay_base * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Request failed after {max_retries} attempts: {e}")
    
    raise last_exception


async def search_doctors(
    specialties: Optional[List[str]] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    language: Optional[str] = None,
    min_rating: Optional[float] = None,
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    """Search for doctors based on filters.
    
    Args:
        specialties: List of required specialties
        city: City filter
        state: State filter
        language: Language filter
        min_rating: Minimum rating filter
        page: Page number
        limit: Results per page
        
    Returns:
        Dict with:
        - doctors: List of DoctorInfo objects
        - total: Total count
        - page: Current page
        - limit: Page size
        
    Raises:
        Exception if API call fails after retries
    """
    logger.info(f"Searching doctors: specialties={specialties}, city={city}, state={state}, language={language}")
    
    api_config = get_api_config()
    
    # Build query params - for now, call without filters
    params = {}
    
    # Uncomment below when filters are needed
    # params = {
    #     "page": page,
    #     "limit": limit
    # }
    # 
    # if specialties:
    #     params["specialties"] = ",".join(specialties)
    # if city:
    #     params["city"] = city
    # if state:
    #     params["state"] = state
    # if language:
    #     params["language"] = language
    # if min_rating:
    #     params["minRating"] = min_rating
    
    async def make_request():
        async with api_config.get_client() as client:
            response = await client.get("/api/search/doctors", params=params)
            logger.info(f"Doctor search response status: {response.status_code}")
            logger.info(f"Doctor search response body: {response.text}")
            response.raise_for_status()
            return response.json()
    
    try:
        data = await _retry_request(make_request, max_retries=api_config.max_retries)
        
        # Handle None or empty response
        if data is None:
            logger.warning("Doctor search returned None response")
            return {"doctors": [], "total": 0, "page": page, "limit": limit}
        
        if not data.get("success"):
            logger.error(f"Doctor search failed: {data}")
            return {"doctors": [], "total": 0, "page": page, "limit": limit}
        
        result = data.get("result", {})
        if result is None:
            logger.warning("Doctor search result is None")
            return {"doctors": [], "total": 0, "page": page, "limit": limit}
            
        items = result.get("items", [])
        
        doctors = [DoctorInfo(item) for item in items]
        
        logger.info(f"Found {len(doctors)} doctors (total: {result.get('total', 0)})")
        
        return {
            "doctors": doctors,
            "total": result.get("total", 0),
            "page": result.get("page", page),
            "limit": result.get("limit", limit)
        }
        
    except Exception as e:
        logger.error(f"Error searching doctors: {e}")
        # Return empty result instead of raising exception
        return {"doctors": [], "total": 0, "page": page, "limit": limit}


async def get_doctor_availability(doctor_id: str, date: str) -> List[str]:
    """Get available time slots for a doctor.
    
    Args:
        doctor_id: Doctor ID
        date: Date in YYYY-MM-DD format (optional, will use current date if not provided)
        
    Returns:
        List of formatted time slots (e.g., ["9:00 AM - 9:30 AM", "10:00 AM - 10:30 AM"])
        
    Raises:
        Exception if API call fails after retries
    """
    from datetime import datetime
    
    logger.info(f"Getting availability for doctor {doctor_id} on {date}")
    
    api_config = get_api_config()
    
    # Build params with date if provided
    params = {}
    if date:
        params["date"] = date
    
    async def make_request():
        async with api_config.get_client() as client:
            # Updated endpoint with optional date param
            response = await client.get(
                f"/api/availability/doctor/{doctor_id}",
                params=params
            )
            logger.info(f"Availability response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
    
    try:
        data = await _retry_request(make_request, max_retries=api_config.max_retries)
        
        # Handle None response
        if data is None:
            logger.warning("Availability check returned None response")
            return []
        
        # The API response structure is {'count': 11, 'slots': [...]}
        # No 'success' or 'result' wrapper
        slots_data = data.get("slots", [])
        
        if not slots_data:
            logger.warning("No slots found in response")
            return []
        
        logger.info(f"Retrieved {len(slots_data)} total slots from API")
        
        # Format slots: convert ISO timestamps to readable format
        formatted_slots = []
        for slot in slots_data:
            if slot.get("status") == "AVAILABLE":
                start_time = slot.get("slotStartTime")
                end_time = slot.get("slotEndTime")
                
                if start_time and end_time:
                    # Parse ISO timestamp and format as readable time
                    try:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        
                        # Format as "9:00 AM - 9:30 AM"
                        formatted_slot = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
                        formatted_slots.append(formatted_slot)
                    except Exception as e:
                        logger.warning(f"Error parsing slot time: {e}")
                        continue
        
        logger.info(f"Found {len(formatted_slots)} available slots")
        
        return formatted_slots
        
    except Exception as e:
        logger.error(f"Error getting doctor availability: {e}")
        return []
