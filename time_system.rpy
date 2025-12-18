default phone_time_minutes = 8 * 60

init python:
    def format_phone_time():
        total_minutes = int(store.phone_time_minutes)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def advance_phone_time(minutes):
        store.phone_time_minutes += minutes
