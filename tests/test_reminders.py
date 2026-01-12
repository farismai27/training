"""
Test script for the reminder tools integrated into demo.py.
Demonstrates the three-tool workflow: get_current_datetime → add_duration → set_reminder
"""

import json
from datetime import datetime, timedelta

# Simulated reminder tools (copied from demo.py for standalone testing)
reminders = []

def get_current_datetime():
    """Get current date and time in ISO 8601 format."""
    now = datetime.now()
    return {
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": "local"
    }

def add_duration_to_datetime(base_datetime, days=0, hours=0, minutes=0):
    """Add days/hours/minutes to a datetime and return result."""
    try:
        base_dt = datetime.fromisoformat(base_datetime)
        result_dt = base_dt + timedelta(days=days, hours=hours, minutes=minutes)
        return {
            "input": base_datetime,
            "result": result_dt.isoformat(),
            "duration_added": f"{days} days, {hours} hours, {minutes} minutes"
        }
    except Exception as e:
        return {"error": f"Date calculation failed: {str(e)}"}

def set_reminder(reminder_datetime, message, reminder_id=None):
    """Set a reminder for a specific datetime."""
    import uuid
    try:
        reminder_dt = datetime.fromisoformat(reminder_datetime)
        if reminder_id is None:
            reminder_id = str(uuid.uuid4())[:8]
        
        reminder = {
            "id": reminder_id,
            "datetime": reminder_datetime,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        reminders.append(reminder)
        
        return {
            "success": True,
            "reminder_id": reminder_id,
            "reminder_datetime": reminder_datetime,
            "message": message,
            "confirmation": f"Reminder set for {reminder_datetime}. You will be reminded: {message}"
        }
    except Exception as e:
        return {"error": f"Failed to set reminder: {str(e)}"}

if __name__ == "__main__":
    print("=" * 70)
    print("REMINDER TOOL WORKFLOW TEST")
    print("=" * 70)
    
    # Step 1: Get current datetime
    print("\nStep 1: GET CURRENT DATETIME")
    print("-" * 70)
    now_result = get_current_datetime()
    print(json.dumps(now_result, indent=2))
    current_dt = now_result["datetime"]
    
    # Step 2: Add duration (e.g., 7 days from now)
    print("\nStep 2: ADD DURATION (7 days from now)")
    print("-" * 70)
    future_result = add_duration_to_datetime(current_dt, days=7)
    print(json.dumps(future_result, indent=2))
    future_dt = future_result["result"]
    
    # Step 3: Set reminder
    print("\nStep 3: SET REMINDER")
    print("-" * 70)
    reminder_result = set_reminder(future_dt, "Doctor's appointment")
    print(json.dumps(reminder_result, indent=2))
    
    # Show all stored reminders
    print("\nAll Stored Reminders:")
    print("-" * 70)
    print(json.dumps(reminders, indent=2))
    
    print("\n✓ Reminder workflow test complete!")
