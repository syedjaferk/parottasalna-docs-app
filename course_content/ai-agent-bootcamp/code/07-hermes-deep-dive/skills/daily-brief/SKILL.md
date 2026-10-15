---
name: daily-brief
description: Make a short morning brief with the weather for a city and the top 5 Hacker News stories.
version: 1.0.0
metadata:
  hermes:
    tags: [daily, news, weather]
    category: personal
---

# Daily Brief

## When to Use
Use this when the user asks for a "daily brief", "morning brief" or "morning update",
or when a scheduled task asks for one. If the user names a city, use it. Otherwise use Chennai.

## Procedure
1. **Weather.** Fetch the current weather from Open-Meteo (free, no key). For Chennai use:
   `https://api.open-meteo.com/v1/forecast?latitude=13.08&longitude=80.27&current_weather=true`
   Read `current_weather.temperature` (degrees Celsius) and `current_weather.windspeed` (km/h).
   For another city, find its latitude and longitude first.
2. **News.** Fetch the ids of the top stories from
   `https://hacker-news.firebaseio.com/v0/topstories.json`, then fetch the first 5 items from
   `https://hacker-news.firebaseio.com/v0/item/<id>.json` and read each `title`.
3. **Write the brief** in exactly this format, and nothing else:

   ```
   Good morning! ☀️
   Weather in <city>: <temperature> °C, wind <windspeed> km/h
   Top stories:
   1. <title>
   2. <title>
   3. <title>
   4. <title>
   5. <title>
   ```

## Pitfalls
- Never invent numbers or titles. If a request fails, write "(could not fetch)" in that place.
- Keep it short. No extra commentary.

## Verification
The brief has one weather line and exactly five numbered stories.
