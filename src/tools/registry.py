from typing import Callable, Dict, Any, List

import src.tools.check_schedule as check_schedule
import src.tools.find_common_free_slots as find_common_free_slots
import src.tools.book_meeting as book_meeting
import src.tools.send_invitation_email as send_invitation_email

def get_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "check_schedule",
            "description": "Check the schedule of a specific person for a given date or week. Provide person_name and optional date (YYYY-MM-DD).",
            "function": check_schedule.execute
        },
        {
            "name": "find_common_free_slots",
            "description": "Find time slots where all specified people are free. Provide person_names (comma-separated).",
            "function": find_common_free_slots.execute
        },
        {
            "name": "book_meeting",
            "description": "Book a meeting at a specific time slot for specified people. Provide person_names, date (YYYY-MM-DD), time (HH:MM), title, and duration (IN HOURS, e.g. 1 or 1.5).",
            "function": book_meeting.execute
        },
        {
            "name": "send_invitation_email",
            "description": "Send meeting invitation emails. Provide booking_id, organizer_email, custom_message (optional).",
            "function": send_invitation_email.execute
        }
    ]
