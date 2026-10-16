# messages.py - sample customer messages, each with the label WE think is right.
# (In real life you collect these from real chats. 12 are enough to learn from.)
SAMPLES = [
    ("My payment failed twice and I still got charged!", "billing"),
    ("Please send me the invoice for last month.", "billing"),
    ("I want a refund for my order.", "billing"),
    ("The app crashes every time I open the camera.", "technical"),
    ("I get an error when I try to upload a photo.", "technical"),
    ("The website is very slow and keeps freezing.", "technical"),
    ("I forgot my password and cannot log in.", "account"),
    ("How do I change the email address on my account?", "account"),
    ("Please delete my account and my data.", "account"),
    ("What are your opening hours?", "other"),
    ("Do you ship to Sri Lanka?", "other"),
    ("Thanks, you were really helpful!", "other"),
]
CATEGORIES = ["billing", "technical", "account", "other"]
