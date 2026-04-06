#!/usr/bin/env python3
"""
Tool: Book Meeting
Description: Book a meeting at a specific time slot for specified people
Parameters:
- person_names: Comma-separated list of attendees
- date: Meeting date (YYYY-MM-DD)
- time: Meeting time (HH:MM format)
- title: Meeting title
- duration: Meeting duration in hours (e.g. 1 or 1.5). Default 1.
Returns: Booking confirmation or error message
"""

import json
import os
from typing import List, Optional
from datetime import datetime, timedelta

class BookingTool:
    def __init__(self):
        self.schedule_file = os.path.join(os.path.dirname(__file__), "schedule.json")
        self.bookings_file = os.path.join(os.path.dirname(__file__), "bookings.json")
        self._load_data()

    def _load_data(self):
        """Load schedule and bookings data"""
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                self.schedule_data = json.load(f)
        except FileNotFoundError:
            self.schedule_data = []

        try:
            with open(self.bookings_file, 'r', encoding='utf-8') as f:
                self.bookings = json.load(f)
        except FileNotFoundError:
            self.bookings = []

    def _save_bookings(self):
        """Save bookings to file"""
        with open(self.bookings_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookings, f, indent=2, ensure_ascii=False)

    def book_meeting(self, person_names: str, date: str, time: str, title: str, duration: float = 1.0) -> str:
        """
        Book a meeting for specified people at given time
        Args:
            person_names: Comma-separated attendee names
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            title: Meeting title
            duration: Duration in hours (if > 12, assumed to be minutes and converted to hours)
        Returns:
            Booking confirmation or error
        """
        self._load_data()
        
        # Auto-correct duration if LLM passed minutes (e.g. 60)
        if duration > 12:
            duration = duration / 60.0
        
        # Parse attendees
        attendees = [name.strip() for name in person_names.split(',')]

        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return f"Invalid date format: {date}. Use YYYY-MM-DD format."

        # Validate time format
        try:
            datetime.strptime(time, '%H:%M')
        except ValueError:
            return f"Invalid time format: {time}. Use HH:MM format."

        # Find attendees in schedule
        attendee_objects = []
        not_found = []

        for name in attendees:
            person = None
            for p in self.schedule_data:
                if p['name'].lower() == name.lower():
                    person = p
                    break
            if person:
                attendee_objects.append(person)
            else:
                not_found.append(name)

        if not_found:
            return f"Attendees not found: {', '.join(not_found)}"

        # Check availability for all attendees
        unavailable = []
        for person in attendee_objects:
            if date not in person['schedule']:
                unavailable.append(f"{person['name']} (no schedule for {date})")
                continue

            if time not in person['schedule'][date]:
                unavailable.append(f"{person['name']} (invalid time slot)")
                continue

            if person['schedule'][date][time] != "free":
                unavailable.append(f"{person['name']} (busy at {time})")

        if unavailable:
            return f"Cannot book meeting. Unavailable attendees: {', '.join(unavailable)}"

        # Create booking
        booking_id = f"meeting_{len(self.bookings) + 1}"
        booking = {
            "id": booking_id,
            "title": title,
            "date": date,
            "time": time,
            "duration": duration,
            "attendees": [p['name'] for p in attendee_objects],
            "attendee_emails": [p['email'] for p in attendee_objects],
            "status": "booked",
            "created_at": datetime.now().isoformat()
        }

        # Add to bookings
        self.bookings.append(booking)
        self._save_bookings()

        # Update schedules (mark as busy)
        for person in attendee_objects:
            person['schedule'][date][time] = "busy"

        # Save updated schedules
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)

        return f"""✅ Meeting booked successfully!

📅 Meeting Details:
   Title: {title}
   Date: {date}
   Time: {time}
   Duration: {duration} hour(s)
   Attendees: {', '.join([p['name'] for p in attendee_objects])}
   Booking ID: {booking_id}"""

# Global instance for tool execution
booking_tool = BookingTool()

def execute(person_names: str, date: str, time: str, title: str, duration: float = 1.0) -> str:
    """Execute the book_meeting tool"""
    return booking_tool.book_meeting(person_names, date, time, title, duration)