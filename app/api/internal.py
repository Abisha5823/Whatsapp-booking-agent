from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.booking_manager import get_booking, get_bookings_by_customer, update_booking_status
from app.models.booking import Booking
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/bookings/{booking_id}")
async def get_booking_details(booking_id: str):
    """Get booking by ID"""
    booking = await get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.get("/bookings")
async def list_bookings(
    whatsapp_number: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """List bookings for a customer"""
    if not whatsapp_number:
        return {"message": "Please provide whatsapp_number parameter"}
    
    bookings = await get_bookings_by_customer(whatsapp_number, limit)
    return {"bookings": bookings, "count": len(bookings)}

@router.put("/bookings/{booking_id}/status")
async def update_status(booking_id: str, status: str):
    """Update booking status"""
    valid_statuses = ["pending", "confirmed", "cancelled", "completed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    success = await update_booking_status(booking_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": f"Booking {booking_id} status updated to {status}"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "booking-api"}