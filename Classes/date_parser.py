from datetime import datetime, timedelta
import re

weekdays = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6,
    }

def get_weekday_date(weekday_name, nextFlag):
    weekday_name = weekday_name.lower()
    if weekday_name not in weekdays:
        return None  # Return None for invalid weekday names

    today = datetime.now()
    target_weekday = weekdays[weekday_name]
    current_weekday = today.weekday()
    
    # Calculate days until the specified weekday
    days_until_next_weekday = (target_weekday - current_weekday + 7) % 7
    if(nextFlag == True):
        days_until_next_weekday +=7
    if days_until_next_weekday == 0:
        days_until_next_weekday = 7  # Ensure it's the "next" weekday, not today
    
    return today + timedelta(days=days_until_next_weekday)

def parse_date(input_text):
    reference_date = datetime.now()

    try:
        # Handle specific phrases
        if "tomorrow" in input_text:
            return reference_date + timedelta(days=1)
        elif "next week" in input_text:
            return reference_date + timedelta(weeks=1)
        elif "in " in input_text and " days" in input_text:
            days = int(re.search(r'in (\d+) days', input_text).group(1))
            return reference_date + timedelta(days=days)
        
        # Handle 'next' weekdays
        match = re.match(r'next (\w+)', input_text.lower())
        if match:
            weekday_name = match.group(1)
            return get_weekday_date(weekday_name, True)
        # Handle weekdays without 'next'
        for weekday in weekdays:
            if weekday in input_text.lower():
                return get_weekday_date(weekday, False)

        # Handle specific date format 
        return datetime.strptime(input_text, '%d-%m-%Y')
    except (ValueError, AttributeError):
        return None  # Return None for invalid input


