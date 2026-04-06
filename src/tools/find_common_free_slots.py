#!/usr/bin/env python3
"""
Tool: Find Common Free Slots
Description: Find time slots where all specified people are free
Parameters:
- person_names: Comma-separated list of person names
- date: Optional specific date (YYYY-MM-DD), if not provided, searches entire week
Returns: Common free time slots for all people
"""

import json
import os
from typing import List, Optional
from datetime import datetime, timedelta

class CommonSlotsTool:
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

    def find_common_free_slots(self, person_names: str, date: Optional[str] = None) -> str:
        """
        Find time slots where all specified people are free
        Args:
            person_names: Comma-separated names (e.g., "Minh Anh, Tuấn Khoa")
            date: Optional specific date
        Returns:
            Common free slots information
        """
        self._load_schedule()
        
        # Parse person names
        names = [name.strip() for name in person_names.split(',')]

        # Find people in schedule data
        people = []
        not_found = []

        for name in names:
            person = None
            for p in self.schedule_data:
                if p['name'].lower() == name.lower():
                    person = p
                    break
            if person:
                people.append(person)
            else:
                not_found.append(name)

        if not_found:
            return f"People not found: {', '.join(not_found)}"

        if not people:
            return "No valid people specified."

        # Get all dates to check
        if date:
            dates_to_check = [date]
        else:
            # Get all dates from the first person's schedule
            dates_to_check = list(people[0]['schedule'].keys())

        result = f"Finding common free slots for: {', '.join([p['name'] for p in people])}\n\n"

        found_slots = False

        for check_date in dates_to_check:
            # Check if all people have schedule for this date
            if not all(check_date in p['schedule'] for p in people):
                continue

            # Get all time slots (assuming same slots for all)
            time_slots = list(people[0]['schedule'][check_date].keys())

            # Find slots where ALL people are free
            common_free_slots = []
            for slot in time_slots:
                if all(p['schedule'][check_date].get(slot) == "free" for p in people):
                    common_free_slots.append(slot)

            if common_free_slots:
                found_slots = True
                result += f"{check_date}: {', '.join(common_free_slots)}\n"

        if not found_slots:
            result += "No common free slots found in the specified period."

        return result

# Global instance for tool execution
common_slots_tool = CommonSlotsTool()

def execute(person_names: str, date: Optional[str] = None) -> str:
    """Execute the find_common_free_slots tool"""
    return common_slots_tool.find_common_free_slots(person_names, date)