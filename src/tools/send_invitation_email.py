#!/usr/bin/env python3
"""
Tool: Send Invitation Email
Description: Send meeting invitation emails to attendees
Parameters:
- booking_id: ID of the booked meeting
- organizer_email: Email of the meeting organizer
- custom_message: Optional custom message to include in the email
Returns: Email sending confirmation
"""

import json
import os
from typing import Optional
from datetime import datetime

class EmailTool:
    def __init__(self):
        self.bookings_file = os.path.join(os.path.dirname(__file__), "bookings.json")
        self.sent_emails_file = os.path.join(os.path.dirname(__file__), "sent_emails.json")
        self._load_data()

    def _load_data(self):
        """Load bookings and sent emails data"""
        try:
            with open(self.bookings_file, 'r', encoding='utf-8') as f:
                self.bookings = json.load(f)
        except FileNotFoundError:
            self.bookings = []

        try:
            with open(self.sent_emails_file, 'r', encoding='utf-8') as f:
                self.sent_emails = json.load(f)
        except FileNotFoundError:
            self.sent_emails = []

    def _save_sent_emails(self):
        """Save sent emails log"""
        with open(self.sent_emails_file, 'w', encoding='utf-8') as f:
            json.dump(self.sent_emails, f, indent=2, ensure_ascii=False)

    def send_invitation_email(self, booking_id: str, organizer_email: str, custom_message: Optional[str] = None) -> str:
        """
        Send meeting invitation emails
        Args:
            booking_id: ID of the meeting booking
            organizer_email: Email of the organizer
            custom_message: Optional custom message
        Returns:
            Email sending confirmation
        """
        self._load_data()
        
        # Find booking
        booking = None
        for b in self.bookings:
            if b['id'] == booking_id:
                booking = b
                break

        if not booking:
            return f"Booking with ID '{booking_id}' not found."

        if booking['status'] != 'booked':
            return f"Cannot send invitation for booking '{booking_id}' with status '{booking['status']}'."

        # Prepare email content
        subject = f"Meeting Invitation: {booking['title']}"

        body = f"""Dear Team,

You are invited to the following meeting:

📅 Meeting Details:
   Title: {booking['title']}
   Date: {booking['date']}
   Time: {booking['time']}
   Duration: {booking['duration']} hour(s)
   Attendees: {', '.join(booking['attendees'])}

"""

        if custom_message:
            body += f"\n{custom_message}\n"

        body += f"""
Please confirm your attendance.

Best regards,
Meeting Organizer
{organizer_email}

---
This is an automated message from the Meeting Scheduling System.
Booking ID: {booking_id}
"""

        # Simulate sending emails (in real implementation, use SMTP)
        sent_to = []
        for email in booking['attendee_emails']:
            # Simulate email sending
            email_record = {
                "booking_id": booking_id,
                "to": email,
                "subject": subject,
                "body": body,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            self.sent_emails.append(email_record)
            sent_to.append(email)

        self._save_sent_emails()

        # Update booking status
        booking['status'] = 'invited'
        with open(self.bookings_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookings, f, indent=2, ensure_ascii=False)

        return f"""✅ Meeting invitations sent successfully!

📧 Email Details:
   Subject: {subject}
   Sent to: {', '.join(sent_to)}
   Total recipients: {len(sent_to)}

📅 Meeting: {booking['title']} ({booking['date']} at {booking['time']})
   Booking ID: {booking_id}

Note: In a real implementation, this would use SMTP to send actual emails.
For this demo, emails are logged to sent_emails.json."""

# Global instance for tool execution
email_tool = EmailTool()

def execute(booking_id: str, organizer_email: str, custom_message: Optional[str] = None) -> str:
    """Execute the send_invitation_email tool"""
    return email_tool.send_invitation_email(booking_id, organizer_email, custom_message)