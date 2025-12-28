"""Booking service for creating appointments."""

from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from app.config.api_config import get_api_config
from app.utils.logger import get_logger

logger = get_logger()


async def create_appointment(
    doctor_id: str,
    patient_id: str,
    date: str,
    time_slot: str,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Create an appointment booking.
    
    Args:
        doctor_id: Doctor's ID
        patient_id: Patient's user ID
        date: Appointment date (YYYY-MM-DD)
        time_slot: Time slot (e.g., "2:00 PM")
        symptoms: Patient symptoms summary
        notes: Additional notes
        
    Returns:
        Dict with:
        - success: bool
        - appointment_id: str
        - status: str
        - details: Dict with booking details
        
    Raises:
        Exception if API call fails after retries
    """
    logger.info(f"Creating appointment: doctor={doctor_id}, patient={patient_id}, date={date}, slot={time_slot}")
    
    api_config = get_api_config()
    
    # Build request payload
    payload = {
        "doctorId": doctor_id,
        "patientId": patient_id,
        "date": date,
        "timeSlot": time_slot,
    }
    
    if symptoms:
        payload["symptoms"] = symptoms
    if notes:
        payload["notes"] = notes
    
    # Retry logic with exponential backoff
    last_exception = None
    for attempt in range(api_config.max_retries):
        try:
            async with api_config.get_client() as client:
                response = await client.post("/api/consultation/book", json=payload)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success"):
                    logger.error(f"Booking failed: {data}")
                    return {
                        "success": False,
                        "error": data.get("message", "Booking failed"),
                        "appointment_id": None
                    }
                
                result = data.get("result", {})
                appointment_id = result.get("appointmentId") or result.get("id")
                
                logger.info(f"Appointment created successfully: {appointment_id}")
                
                return {
                    "success": True,
                    "appointment_id": appointment_id,
                    "status": result.get("status", "confirmed"),
                    "details": result
                }
                
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            last_exception = e
            if attempt < api_config.max_retries - 1:
                import asyncio
                delay = api_config.retry_delay_base * (2 ** attempt)
                logger.warning(f"Booking failed (attempt {attempt + 1}/{api_config.max_retries}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Booking failed after {api_config.max_retries} attempts: {e}")
    
    # All retries failed
    raise Exception(f"Failed to create appointment after {api_config.max_retries} attempts: {str(last_exception)}")


async def cancel_appointment(appointment_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """Cancel an appointment.
    
    Args:
        appointment_id: Appointment ID to cancel
        reason: Cancellation reason
        
    Returns:
        Dict with success status
        
    Raises:
        Exception if API call fails
    """
    logger.info(f"Cancelling appointment: {appointment_id}")
    
    api_config = get_api_config()
    
    payload = {"appointmentId": appointment_id}
    if reason:
        payload["reason"] = reason
    
    try:
        async with api_config.get_client() as client:
            response = await client.post("/api/consultation/cancel", json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Appointment cancelled: {data}")
            
            return {
                "success": data.get("success", False),
                "message": data.get("message", "Cancelled successfully")
            }
            
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        raise Exception(f"Failed to cancel appointment: {str(e)}")
