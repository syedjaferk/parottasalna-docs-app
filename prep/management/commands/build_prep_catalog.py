"""Builds prep/data/*.json (problem catalog + study materials) from the InterviewPreparations folder.

    python manage.py build_prep_catalog [--src ../InterviewPreparations]
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

# Raw pattern tags in the source data -> the 22 canonical patterns (the sections of the "20 Essential DSA Patterns" sheet).
ALIASES = {
    "dynammic-programming": "Dynamic Programming", "dynamic-programming": "Dynamic Programming",
    "dynammic-programming-kadanes-algorithm": "Dynamic Programming",
    "trees": "Trees", "binary-tree": "Trees", "binary-trees": "Trees", "bst": "Trees", "tree-traversal-bst": "Trees",
    "sliding-window": "Sliding Window", "sliding-window-hashmap": "Sliding Window",
    "graphs": "Graphs", "graphs-topological-sort": "Graphs", "bfs-dfs-graph-traversals": "Graphs",
    "two-pointers": "Two Pointers", "arrays-and-slicing": "Two Pointers",
    "modified-binary-search": "Modified Binary Search", "binary-search": "Modified Binary Search", "binary": "Modified Binary Search",
    "backtracking": "Backtracking", "greedy": "Greedy",
    "monotonic-stack": "Monotonic Stack", "stack": "Monotonic Stack", "stacks-queues": "Monotonic Stack",
    "design-data-structure": "Design Data Structure", "trie": "Design Data Structure",
    "depth-first-search-dfs": "Depth First Search (DFS)", "bfs-dfs-recursion-matrix-grid": "Depth First Search (DFS)",
    "breadth-first-search-bfs": "Breadth First Search (BFS)", "bfs": "Breadth First Search (BFS)", "matrix-bfs": "Breadth First Search (BFS)",
    "prefix-sum": "Prefix Sum", "bitwise-xor": "Bitwise XOR", "overlapping-intervals": "Overlapping Intervals",
    "cyclic-sort-index-based": "Cyclic Sort", "k-way-merge": "K-way Merge", "heap-merge-sort": "K-way Merge",
    "fast-and-slow-pointer": "Fast and Slow Pointer", "matrix-manipulation": "Matrix Manipulation",
    "top-k-elements": "Top K Elements", "heap-priorityq": "Top K Elements",
    "reversal-of-linked-list-in-place": "Reversal of Linked List", "linked-list": "Reversal of Linked List",
    "linked-list-bfs-dfs-recursion": "Reversal of Linked List", "two-heaps": "Two Heaps",
    "hash-map": "Hash Map", "hashmap-strings": "Hash Map", "map": "Hash Map", "map-counter": "Hash Map",
}
# Keyword -> canonical pattern, used to fill in patterns from topic tags and sheet section names when a
# problem has no explicit pattern tag. First match wins per keyword; a problem can match several.
KEYWORDS = [
    ("sliding window", "Sliding Window"), ("two pointer", "Two Pointers"), ("2 pointer", "Two Pointers"),
    ("binary search", "Modified Binary Search"), ("backtrack", "Backtracking"), ("greedy", "Greedy"),
    ("dynamic programming", "Dynamic Programming"), ("memoization", "Dynamic Programming"), ("dp", "Dynamic Programming"),
    ("monotonic", "Monotonic Stack"), ("prefix sum", "Prefix Sum"), ("bit manipulation", "Bitwise XOR"), ("xor", "Bitwise XOR"),
    ("depth-first", "Depth First Search (DFS)"), ("dfs", "Depth First Search (DFS)"),
    ("breadth-first", "Breadth First Search (BFS)"), ("bfs", "Breadth First Search (BFS)"),
    ("binary tree", "Trees"), ("binary search tree", "Trees"), ("tree", "Trees"), ("bst", "Trees"),
    ("graph", "Graphs"), ("topological", "Graphs"), ("union find", "Graphs"), ("shortest path", "Graphs"),
    ("heap", "Top K Elements"), ("priority queue", "Top K Elements"), ("k-way", "K-way Merge"),
    ("two heaps", "Two Heaps"), ("interval", "Overlapping Intervals"), ("merge intervals", "Overlapping Intervals"),
    ("hash", "Hash Map"), ("linked list", "Reversal of Linked List"), ("matrix", "Matrix Manipulation"),
    ("cyclic sort", "Cyclic Sort"), ("fast and slow", "Fast and Slow Pointer"), ("cycle", "Fast and Slow Pointer"),
    ("trie", "Design Data Structure"), ("design", "Design Data Structure"), ("lru", "Design Data Structure"),
]


def keyword_patterns(text):
    text = f" {text.lower()} "
    return {pat for kw, pat in KEYWORDS if (f" {kw} " in text or (len(kw) > 3 and kw in text))}


FREQ = {"Cold": 1, "Warm": 2, "Hot": 3, "Very Hot": 4}
DIFF = {"Basic": 0, "Easy": 1, "Medium": 2, "Hard": 3}


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")


class Command(BaseCommand):
    help = "Build the interview-prep catalog JSON files from the InterviewPreparations folder."

    def add_arguments(self, parser):
        parser.add_argument("--src", default=str(Path(settings.BASE_DIR).parent / "InterviewPreparations"))

    def handle(self, *args, src, **opts):
        src = Path(src)
        db, scrape = src / "dsa-interview-db" / "data", src / "hynts_scrape" / "json"
        out = Path(__file__).resolve().parents[2] / "data"

        problems = {r["problem_id"]: r for r in rows(db / "problems.csv")}
        topics = {r["topic_id"]: r["name"] for r in rows(db / "topics.csv")}
        companies = {r["company_id"]: r["name"] for r in rows(db / "companies.csv")}
        sheets = rows(db / "sheets.csv")

        p_topics, p_patterns, p_companies = defaultdict(set), defaultdict(set), defaultdict(dict)
        for r in rows(db / "problem_topics.csv"):
            p_topics[r["problem_id"]].add(r["topic_id"])
        for r in rows(db / "problem_patterns.csv"):
            if r["pattern_id"] in ALIASES:
                p_patterns[r["problem_id"]].add(ALIASES[r["pattern_id"]])
        for r in rows(db / "problem_companies.csv"):
            cur = p_companies[r["problem_id"]].get(r["company_id"], 0)
            p_companies[r["problem_id"]][r["company_id"]] = max(cur, FREQ.get(r["frequency"], 1))

        # Normalise topic tags: merge "Array"/"Arrays", "Graph"/"Graphs", ... (prefer the singular spelling).
        groups = defaultdict(list)
        for tid, name in topics.items():
            groups[name.lower().rstrip("s") if name.lower() not in ("dbms", "sql", "oop", "binary", "loops") else name.lower()].append(name)
        canon_topic = {}
        for tid, name in topics.items():
            key = name.lower().rstrip("s") if name.lower() not in ("dbms", "sql", "oop", "binary", "loops") else name.lower()
            canon_topic[tid] = min(groups[key], key=len)

        # Problems used by at least one sheet or company list, in a stable order.
        used = {r["problem_id"] for r in rows(db / "sheet_problems.csv")} | set(p_companies)
        pids = sorted(used & set(problems))
        index = {pid: i for i, pid in enumerate(pids)}
        pattern_list = sorted({v for s in p_patterns.values() for v in s})
        company_list = sorted(companies, key=lambda c: companies[c])
        topic_list = sorted(set(canon_topic.values()))
        t_idx, pa_idx, c_idx = ({n: i for i, n in enumerate(l)} for l in (topic_list, pattern_list, company_list))

        sections = defaultdict(set)
        for r in rows(db / "sheet_problems.csv"):
            sections[r["problem_id"]] |= {r["section"], r["subsection"]}
        for pid in pids:
            if not p_patterns[pid]:
                text = " ; ".join([topics[t] for t in p_topics[pid] if t in topics] + sorted(sections[pid]))
                p_patterns[pid] |= keyword_patterns(text)
        pattern_list = sorted({v for pid in pids for v in p_patterns[pid]})
        pa_idx = {n: i for i, n in enumerate(pattern_list)}

        plist = []
        for pid in pids:
            p = problems[pid]
            plist.append({
                "id": pid, "t": p["title"], "pl": p["platform"], "u": p["url"], "d": DIFF.get(p["difficulty"], 1),
                "tg": sorted({t_idx[canon_topic[t]] for t in p_topics[pid] if t in canon_topic}),
                "pa": sorted(pa_idx[x] for x in p_patterns[pid]),
                "co": sorted([c_idx[c], f] for c, f in p_companies[pid].items()),
            })

        sheet_items = defaultdict(list)
        for r in sorted(rows(db / "sheet_problems.csv"), key=lambda r: (r["sheet_id"], int(r["position"]))):
            if r["problem_id"] in index:
                sheet_items[r["sheet_id"]].append([index[r["problem_id"]], r["section"], r["subsection"]])
        slist = [{"id": s["sheet_id"], "name": s["name"], "by": s["creator"], "kind": s["kind"], "items": sheet_items[s["sheet_id"]]}
                 for s in sheets if sheet_items[s["sheet_id"]]]

        catalog = {"problems": plist, "sheets": slist, "topics": topic_list, "patterns": pattern_list,
                   "companies": [companies[c] for c in company_list], "difficulties": ["Basic", "Easy", "Medium", "Hard"]}
        (out / "catalog.json").write_text(json.dumps(catalog, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

        # ---- study materials -------------------------------------------------------------------
        def load(name):
            return json.load(open(scrape / f"{name}.json", encoding="utf-8"))

        def qa(name, keep_source=False):
            return [{"q": r.get("title") or r.get("question", ""), "a": r.get("answer", ""), "d": r.get("difficulty", ""), "c": r.get("category", ""),
                     **({"s": r["source"].split("/")[-1]} if keep_source and r.get("source") else {})} for r in load(name)]

        materials = {
            "hr": qa("hr"), "sql": qa("sql"), "cs": qa("interview_questions", True),
            "roles": qa("role_wise", True),
            "system_design": [{"t": r["title"], "type": r["type"], "article": r["articleLink"], "video": r["ytLink"],
                               "companies": [c.strip() for c in r["companies"].split(";") if c.strip()]} for r in load("system_design")],
            "notes": [{"t": r["title"], "cat": r["category"], "url": r["file_url"]} for r in load("notes")],
            "playlists": [{"pl": r["playlist"], "by": r["creator"], "sec": r["section"], "t": r["title"], "u": r["link"]} for r in load("playlists")],
            "cold_emails": [{k: r.get(k, "") for k in ("id", "category", "role", "title", "purpose", "subject", "body", "tips", "bestTimeToSend", "expectedResponseRate")} for r in load("cold_emails")],
            "resumes": [{"t": r["name"], "u": r["link"]} for r in load("resumes")],
        }
        for key, value in materials.items():
            (out / f"mat_{key}.json").write_text(json.dumps(value, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        self.stdout.write(f"{len(plist)} problems, {len(slist)} sheets, {len(company_list)} companies, {len(pattern_list)} patterns, {len(topic_list)} topics")
        for key, value in materials.items():
            self.stdout.write(f"  mat_{key}: {len(value)}")
