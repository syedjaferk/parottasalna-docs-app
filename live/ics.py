"""Write iCalendar (.ics) files by hand: the format is small, and this avoids a dependency.

Rules that matter (RFC 5545): lines end with CRLF, long lines are folded at 75 octets, and text values
escape backslash, semicolon, comma and newline.
"""
from datetime import datetime, timezone as dt_timezone

PRODID = "-//Parottasalna//Course Portal//EN"

# India has no daylight saving, so one STANDARD block describes Asia/Kolkata completely.
VTIMEZONE_KOLKATA = [
    "BEGIN:VTIMEZONE", "TZID:Asia/Kolkata",
    "BEGIN:STANDARD", "DTSTART:19700101T000000", "TZOFFSETFROM:+0530", "TZOFFSETTO:+0530", "TZNAME:IST",
    "END:STANDARD", "END:VTIMEZONE",
]


def escape(text):
    return (str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def utc(dt):
    """A timezone-aware datetime as an iCalendar UTC timestamp."""
    return dt.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def fold(line):
    """Split a content line into 75-octet pieces, never inside a UTF-8 character."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, start, limit = [], 0, 75
    while start < len(raw):
        end = min(start + limit, len(raw))
        while end < len(raw) and (raw[end] & 0xC0) == 0x80:     # don't cut a multi-byte character
            end -= 1
        parts.append(raw[start:end].decode("utf-8"))
        start, limit = end, 74                                    # continuation lines start with a space
    return "\r\n ".join(parts)


def calendar(events, name=None, extra=(), refresh_hours=None):
    """events: lists of already-built VEVENT lines. Returns the whole .ics document as a string."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{PRODID}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    if name:
        lines += [f"X-WR-CALNAME:{escape(name)}", "X-WR-TIMEZONE:Asia/Kolkata"]
    if refresh_hours:
        # How often subscribed calendars should check for changes (Apple and Outlook honour these).
        lines += [f"REFRESH-INTERVAL;VALUE=DURATION:PT{refresh_hours}H", f"X-PUBLISHED-TTL:PT{refresh_hours}H"]
    lines += list(extra)
    for event in events:
        lines += event
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(line) for line in lines) + "\r\n"


def event(uid, summary, start, end=None, *, duration=None, description="", url="", location="",
          rrule=None, status=None, tzid=None, alarm_minutes=None, now=None):
    """One VEVENT. start/end are aware datetimes (written in UTC), or naive ones written in tzid."""
    def when(name, dt):
        if tzid:
            return f"{name};TZID={tzid}:{dt.strftime('%Y%m%dT%H%M%S')}"
        return f"{name}:{utc(dt)}"

    lines = ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{utc(now or datetime.now(dt_timezone.utc))}", when("DTSTART", start)]
    if end is not None:
        lines.append(when("DTEND", end))
    elif duration:
        lines.append(f"DURATION:PT{int(duration.total_seconds() // 60)}M")
    if rrule:
        lines.append(f"RRULE:{rrule}")
    lines.append(f"SUMMARY:{escape(summary)}")
    if description:
        lines.append(f"DESCRIPTION:{escape(description)}")
    if location:
        lines.append(f"LOCATION:{escape(location)}")
    if url:
        lines.append(f"URL:{url}")
    if status:
        lines.append(f"STATUS:{status}")
    if alarm_minutes is not None:
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{escape(summary)}",
                  f"TRIGGER:-PT{alarm_minutes}M", "END:VALARM"]
    lines.append("END:VEVENT")
    return lines
