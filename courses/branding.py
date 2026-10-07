"""Parottasalna brand details, shared by the portal templates, SEO tags and the Sphinx docs."""
import json

NAME = "Parottasalna"
PRODUCT = "Parottasalna Course Notes"
# Kept under ~60 characters so search results show it in full.
SEO_TITLE = "Parottasalna — Backend, System Design, AWS, Cloud, AI & DSA"
TAGLINE = "Backend Engineering, System Design, AWS, Cloud, AI & DSA explained simply."
DESCRIPTION = (
    "Learn software engineering through practical, easy-to-understand tutorials, "
    "live sessions, and real-world examples."
)
# ~155 characters: what search engines and link previews show.
META_DESCRIPTION = (
    "Parottasalna course notes: Backend Engineering, System Design, AWS, Cloud, AI & DSA "
    "explained simply through practical tutorials and live sessions."
)
KEYWORDS = [
    "Parottasalna", "Syed Jafer K", "Backend Engineering", "System Design", "AWS", "Cloud",
    "AI Engineering", "LLM", "RAG", "AI Agents", "Docker", "Kubernetes", "DevOps", "DSA",
    "Software Engineering tutorials", "course notes",
]

TOPICS = [
    ("Backend Engineering & System Design",
     "Design and build scalable, reliable backend systems."),
    ("AWS & Cloud",
     "Core cloud services and how to use them in real projects."),
    ("AI Engineering",
     "LLMs, RAG, AI agents, tool calling and practical AI systems."),
    ("Docker & Kubernetes",
     "Containers, orchestration, networking, deployment and DevOps."),
    ("Live Sessions & Tech Shorts",
     "Focused sessions, practical demonstrations and quick learning."),
]

AUTHOR = "Syed Jafer K"
AUTHOR_BIO = (
    "I create practical content to help developers understand technology, build real-world "
    "projects, and grow their software engineering skills."
)
CADENCE = "New videos every day."

WEBSITE = "https://parottasalna.com/"
YOUTUBE = "https://www.youtube.com/@parottasalnatech"
YOUTUBE_SUBSCRIBE = YOUTUBE + "?sub_confirmation=1"
INSTAGRAM = "https://www.instagram.com/parottasalna.official/"
GITHUB = "https://github.com/syedjaferk/"
LINKEDIN = "https://www.linkedin.com/in/syedjaferk"

THEME_COLOR = "#2563eb"

# Inline SVG paths (24x24, fill=currentColor) so no icon font or third-party script is needed.
ICONS = {
    "website": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-2.9a15.7 15.7 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8zM12 4a13.9 13.9 0 0 1 1.9 4h-3.8A13.9 13.9 0 0 1 12 4zM4.3 14a8.2 8.2 0 0 1 0-4h3.3a16.5 16.5 0 0 0 0 4zm.8 2h2.9a15.7 15.7 0 0 0 1.4 3.6A8 8 0 0 1 5.1 16zM8 8H5.1a8 8 0 0 1 4.3-3.6A15.7 15.7 0 0 0 8 8zm4 12a13.9 13.9 0 0 1-1.9-4h3.8A13.9 13.9 0 0 1 12 20zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.3 5.6a15.7 15.7 0 0 0 1.4-3.6h2.9a8 8 0 0 1-4.3 3.6zm1.8-5.6a16.5 16.5 0 0 0 0-4h3.3a8.2 8.2 0 0 1 0 4z",
    "youtube": "M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31.4 31.4 0 0 0 0 12a31.4 31.4 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31.4 31.4 0 0 0 24 12a31.4 31.4 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6z",
    "instagram": "M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2-.1-1.3-.1-1.6-.1-4.8s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4 1.2-.1 1.6-.1 4.8-.1zM12 0C8.7 0 8.3 0 7.1.1 5.8.1 4.9.3 4.1.6c-.8.3-1.5.7-2.1 1.4C1.3 2.6.9 3.3.6 4.1.3 4.9.1 5.8.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.1 1.3.3 2.2.6 2.9.3.8.7 1.5 1.4 2.1.6.7 1.3 1.1 2.1 1.4.8.3 1.6.5 2.9.6 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c1.3-.1 2.2-.3 2.9-.6.8-.3 1.5-.7 2.1-1.4.7-.6 1.1-1.3 1.4-2.1.3-.8.5-1.6.6-2.9.1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.1-1.3-.3-2.2-.6-2.9-.3-.8-.7-1.5-1.4-2.1C21.4 1.3 20.7.9 19.9.6 19.1.3 18.2.1 16.9.1 15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9z",
    "github": "M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2.2c-3.3.7-4-1.4-4-1.4-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 0-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2 0-.3-.5-1.5.2-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.7 18.3 5 18.3 5c.7 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .3z",
    "linkedin": "M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.3V9h3.4v1.6c.5-.9 1.6-1.8 3.4-1.8 3.6 0 4.3 2.4 4.3 5.5zM5.3 7.4a2.1 2.1 0 1 1 0-4.1 2.1 2.1 0 0 1 0 4.1zM7.1 20.5H3.6V9h3.5zM22.2 0H1.8C.8 0 0 .8 0 1.7v20.6c0 .9.8 1.7 1.8 1.7h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0z",
}

SOCIAL_LINKS = [
    {"key": "youtube", "name": "YouTube", "handle": "@parottasalnatech", "url": YOUTUBE},
    {"key": "instagram", "name": "Instagram", "handle": "@parottasalna.official", "url": INSTAGRAM},
    {"key": "github", "name": "GitHub", "handle": "syedjaferk", "url": GITHUB},
    {"key": "linkedin", "name": "LinkedIn", "handle": "syedjaferk", "url": LINKEDIN},
    {"key": "website", "name": "Website", "handle": "parottasalna.com", "url": WEBSITE},
]
for _link in SOCIAL_LINKS:
    _link["icon"] = ICONS[_link["key"]]

SAME_AS = [YOUTUBE, INSTAGRAM, GITHUB, LINKEDIN]


def json_ld(site_url: str, logo_url: str = "") -> str:
    """schema.org Organization + Person + WebSite graph, safe to drop inside <script>."""
    org = {
        "@type": "EducationalOrganization",
        "@id": WEBSITE + "#organization",
        "name": NAME,
        "url": WEBSITE,
        "description": f"{TAGLINE} {DESCRIPTION}",
        "sameAs": SAME_AS,
        "founder": {"@id": WEBSITE + "#founder"},
        "knowsAbout": [topic for topic, _ in TOPICS],
    }
    person = {
        "@type": "Person",
        "@id": WEBSITE + "#founder",
        "name": AUTHOR,
        "description": AUTHOR_BIO,
        "url": WEBSITE,
        "sameAs": [GITHUB, LINKEDIN, YOUTUBE, INSTAGRAM],
        "worksFor": {"@id": WEBSITE + "#organization"},
    }
    if logo_url:
        org["logo"] = logo_url
        person["image"] = logo_url
    graph = [org, person]
    if site_url:
        graph.append({
            "@type": "WebSite",
            "name": PRODUCT,
            "url": site_url,
            "description": META_DESCRIPTION,
            "publisher": {"@id": WEBSITE + "#organization"},
            "inLanguage": "en",
        })
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    # Never let content close the <script> element early.
    return data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
