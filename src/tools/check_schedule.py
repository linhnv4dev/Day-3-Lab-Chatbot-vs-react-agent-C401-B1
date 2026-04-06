#!/usr/bin/env python3
"""
Tool: Check Schedule
Description: Check the schedule of a specific person for a given date or week
Parameters:
- person_name: Name of the person to check
- date: Optional specific date (YYYY-MM-DD), if not provided, returns entire week
Returns: Schedule information for the person
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class ScheduleTool:
    def __init__(self):
        self.schedule_file = os.path.join(os.path.dirname(__file__), "schedule.json")
        self._load_schedule()

    def _load_schedule(self):
        """Load schedule data from JSON file"""
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                self.schedule_data = json.load(f)
        except FileNotFoundError:
            self.schedule_data = []

    def check_schedule(self, person_name: str, date: Optional[str] = None) -> str:
        """
        Check schedule for a person
        Args:
            person_name: Name of the person
            date: Optional date in YYYY-MM-DD format
        Returns:
            Schedule information as formatted string
        """
        self._load_schedule()
        
        # Find person in schedule data
        person = None
        for p in self.schedule_data:
            if p['name'].lower() == person_name.lower():
                person = p
                break

        if not person:
            return f"Person '{person_name}' not found in schedule database."

        if date:
            # Check specific date
            if date in person['schedule']:
                schedule = person['schedule'][date]
                free_slots = [time for time, status in schedule.items() if status == "free"]
                busy_slots = [time for time, status in schedule.items() if status == "busy"]

                result = f"Schedule for {person['name']} on {date}:\n"
                result += f"Free slots: {', '.join(free_slots) if free_slots else 'None'}\n"
                result += f"Busy slots: {', '.join(busy_slots) if busy_slots else 'None'}"
                return result
            else:
                return f"No schedule data available for {person['name']} on {date}."
        else:
            # Return entire week schedule
            result = f"Weekly schedule for {person['name']} ({person['email']}):\n\n"
            for date_key, daily_schedule in person['schedule'].items():
                free_slots = [time for time, status in daily_schedule.items() if status == "free"]
                result += f"{date_key}: Free at {', '.join(free_slots)}\n"
            return result

# Global instance for tool execution
schedule_tool = ScheduleTool()

def execute(person_name: str, date: Optional[str] = None) -> str:
    """Execute the check_schedule tool"""
    return schedule_tool.check_schedule(person_name, date)