#!/usr/bin/env python3
"""
kb_pipeline.py - build a source-grounded, verified interview KB efficiently.

Commands
  triage   --kb synthetic_kb --out topics.csv [--core 100]   (offline, instant)
  resolve  --topics topics.csv                                (finds Wikipedia source per core topic, no LLM)
  build    --topics topics.csv --out kb_v2 [--limit N] [--domain D] [--workers 2]
  validate --dir kb_v2                                        (offline checks, non-zero exit on failure)

Env: GROQ_API_KEY (or LLM_API_KEY), optional LLM_API_BASE, GEN_MODEL, CRITIC_MODEL.
Build is resumable: re-run the same command; finished topics are skipped (progress.json).
"""
import argparse, csv, datetime, glob, json, os, re, sys, time
import concurrent.futures as cf
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

TODAY = datetime.date.today().isoformat()
UA = {"User-Agent": "SmartInterviewKB/1.0 (student project; contact: team)"}

# ---------- triage config ----------
DOMAIN_W = {"dsa": 10, "dbms": 9, "os": 9, "cn": 8, "oop": 8, "system-design": 8,
            "design-patterns": 7, "programming-languages": 6, "software-engineering": 6,
            "security": 6, "cloud-devops": 5, "ml-ai": 5, "coa": 5, "theory-cs": 4,
            "data-engineering": 4, "nlp": 3, "emerging-tech": 2}
HOT = ["sql", "index", "acid", "normalization", "transaction", "deadlock", "scheduling", "paging",
       "virtual memory", "tcp", "http", "dns", "osi", "solid", "singleton", "factory", "observer",
       "rest", "cap ", "caching", "load balanc", "sharding", "replication", "hash", "tree", "graph",
       "dynamic programming", "sort", "binary search", "linked list", "stack", "queue", "big o",
       "thread", "process", "mutex", "semaphore", "jwt", "oauth", "sql injection", "xss", "docker",
       "kubernetes", "microservices", "python", "java", "garbage", "transformer", "overfitting"]
MERGE_GROUPS = {  # keep highest-priority file, merge the rest into it
    "replication": r"replication", "sharding": r"shard", "cap": r"\bcap theorem",
    "tls": r"tls|ssl", "kafka": r"kafka", "cicd": r"ci_?/?cd|ci cd",
    "window": r"window functions", "cache-evict": r"cache (eviction|replacement)",
    "sla": r"sli|slo|sla",
}
REQUIRED = ["Definition", "How It Works", "Key Properties", "Comparison",
            "Interview Q&A", "Common Misconceptions", "Tradeoffs"]
BANNED = ["Note: This output", "as an ai", "i hope this", "let me know", "Reactor-Augmented"]


def split_depth0(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([": depth += 1
        if ch in ")]": depth -= 1
        if ch in ",;" and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip(): out.append(cur.strip())
    return [x for x in out if x]


def parse_h1(title):
    i, j = title.find("("), title.rfind(")")
    if i == -1 or j < i: return title.strip(), []
    return title[:i].strip(), split_depth0(title[i + 1:j].replace(" — ", ", "))


def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]


# ---------- triage ----------
def triage(kb, out, core_n):
    rows = []
    for f in sorted(glob.glob(os.path.join(kb, "*", "*.md"))):
        t = open(f, encoding="utf-8", errors="replace").read().replace("\r", "")
        h1 = re.match(r"#\s+(.*)", t).group(1)
        topic, subs = parse_h1(h1)
        model = (re.search(r"\*\*Model:\*\*\s*(\S+)", t) or [0, "?"])[1]
        dom = Path(f).parent.name
        end = t.rstrip()
        trunc = (not end.endswith((".", "?", ")", "`", "!", "*", "|"))) or t.count("```") % 2 == 1
        leak = "Note: This output" in t
        gptoss = "gpt-oss" in model
        action = "REWRITE" if not gptoss else ("COMPLETE" if trunc else "PATCH_VERIFY")
        score = DOMAIN_W.get(dom, 3) + 3 * sum(k in topic.lower() + " " for k in HOT)
        algo = dom == "dsa" or bool(re.search(r"algorithm|sort|search|heap|tree|graph|knapsack|subsequence|complexity", topic, re.I))
        rows.append(dict(file=f, domain=dom, topic=topic, subtopics=" | ".join(subs), model=model,
                         action=action, leak=int(leak), truncated=int(trunc), priority=score,
                         algorithmic=int(algo), tier="later", wiki_title="", extra_urls="",
                         draft_path=f if action != "REWRITE" else ""))
    rows.sort(key=lambda r: (-r["priority"], r["topic"]))
    seen = {}
    for r in rows:  # merge duplicates into highest-priority sibling
        for g, pat in MERGE_GROUPS.items():
            if re.search(pat, r["topic"], re.I):
                if g in seen: r["tier"] = "merge:" + seen[g]
                else: seen[g] = slug(r["topic"])
                break
    n = 0
    for r in rows:
        if r["tier"] == "later" and n < core_n: r["tier"] = "core"; n += 1
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(f"{len(rows)} topics -> {out}")
    print("actions:", dict(Counter(r["action"] for r in rows)))
    print("core:", n, "| merged-away:", sum(r["tier"].startswith("merge") for r in rows),
          "| leaked prompt text:", sum(r["leak"] for r in rows), "| truncated:", sum(r["truncated"] for r in rows))


# ---------- sources ----------
def wiki_search(q):
    for attempt in range(3):
        r = requests.get("https://en.wikipedia.org/w/api.php", headers=UA, timeout=30, params=dict(
            action="query", list="search", srsearch=q, srlimit=1, format="json"))
        if r.status_code == 200:
            try:
                hits = r.json().get("query", {}).get("search", [])
                return hits[0]["title"] if hits else None
            except Exception:
                pass
        time.sleep(2)
    return None


def wiki_text(title, limit=14000):
    r = requests.get("https://en.wikipedia.org/w/api.php", headers=UA, timeout=30, params=dict(
        action="query", prop="extracts", explaintext=1, exsectionformat="plain", redirects=1,
        titles=title, format="json"))
    page = next(iter(r.json()["query"]["pages"].values()))
    txt = page.get("extract", "")
    return page.get("title", title), txt[:limit]


def html_text(url, limit=14000):
    h = requests.get(url, headers=UA, timeout=30).text
    try:
        from bs4 import BeautifulSoup
        s = BeautifulSoup(h, "html.parser")
        for x in s(["script", "style", "nav", "footer", "header"]): x.decompose()
        t = s.get_text(" ")
    except ImportError:
        t = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", h); t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)[:limit]


def get_sources(row):
    srcs = []
    title = row["wiki_title"] or wiki_search(row["topic"])
    if title:
        t, txt = wiki_text(title)
        if txt:
            srcs.append(dict(title="Wikipedia: " + t, url="https://en.wikipedia.org/wiki/" + t.replace(" ", "_"),
                             license="CC BY-SA 4.0", text=txt))
    for u in filter(None, (row["extra_urls"] or "").split("|")):
        try: srcs.append(dict(title=u, url=u, license="see site", text=html_text(u.strip())))
        except Exception as e: print("  extra url failed", u, e)
    return srcs


def resolve(topics):
    rows = list(csv.DictReader(open(topics, encoding="utf-8")))
    for r in rows:
        if r["tier"] == "core":
            print(f"{r['topic'][:55]:55} -> {r['wiki_title'] or wiki_search(r['topic'])}")
    print("\nFix wrong matches by filling wiki_title / extra_urls (use | between URLs) in topics.csv.")


# ---------- LLM ----------
def call_llm(model, messages, max_tokens=7000, temperature=0.2, effort=None):
    key = os.environ.get("GROQ_API_KEY") or os.environ.get("LLM_API_KEY")
    base = os.environ.get("LLM_API_BASE", "https://api.groq.com/openai/v1")
    payload = dict(model=model, messages=messages, temperature=temperature, max_completion_tokens=max_tokens)
    if effort and "gpt-oss" in model: payload["reasoning_effort"] = effort
    for a in range(7):
        r = requests.post(base + "/chat/completions", headers={"Authorization": f"Bearer {key}"},
                          json=payload, timeout=240)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(90, 3 * 2 ** a)); continue
        r.raise_for_status()
        ch = r.json()["choices"][0]
        return ch["message"].get("content") or "", ch.get("finish_reason")
    raise RuntimeError("LLM retries exhausted")


GEN_RULES = """You write ONE interview-prep reference article from the SOURCES below.
Rules:
1. Use ONLY facts supported by the SOURCES or textbook-standard facts you are certain of. Never invent names, expansions, numbers or versions. If unsure, write [VERIFY] next to the claim.
2. Every subtopic listed must get its own subsection with a mechanism and a concrete worked example (numbers, trace, or code).
3. Include a 'Complexity' section ONLY if the topic is an algorithm/data structure.
4. Output exactly these H2 sections in order: Definition; How It Works; Complexity (only if applicable); Key Properties; Real-World Use; Comparison; Tradeoffs / When NOT to Use; Interview Q&A (5 questions, each with a model answer and one follow-up); Common Misconceptions (real mistakes candidates make).
5. 700-1100 words. No disclaimers, no meta commentary. Do not output front matter.
6. Finish with the exact final line: <!-- END -->"""


def gen_prompt(row, srcs, feedback="", draft=""):
    s = "\n\n".join(f"### SOURCE {i+1}: {x['title']} ({x['url']})\n{x['text']}" for i, x in enumerate(srcs))
    u = f"TOPIC: {row['topic']}\nSUBTOPICS (each needs its own subsection): {row['subtopics']}\nALGORITHMIC: {'yes' if row['algorithmic']=='1' else 'no'}\n\nSOURCES:\n{s}"
    if draft: u += f"\n\nEXISTING DRAFT (may contain errors; keep only what the sources support and complete missing parts):\n{draft[:9000]}"
    if feedback: u += f"\n\nFIX THESE PROBLEMS FROM THE LAST ATTEMPT:\n{feedback}"
    return [{"role": "system", "content": GEN_RULES}, {"role": "user", "content": u}]


def critic(article, srcs, model):
    s = "\n\n".join(f"SOURCE {i+1}: {x['text'][:9000]}" for i, x in enumerate(srcs))
    msg = [{"role": "system", "content": "You are a strict technical fact-checker. Return ONLY JSON: "
            '{"issues":[{"claim":"","problem":"","severity":"high|medium|low","fix":""}]}. '
            "List claims that are wrong, contradicted by the sources, or unsupported AND not standard textbook fact. "
            "Check formulas, complexities, definitions, versions, and 'X is used in Y' claims. Empty list if none."},
           {"role": "user", "content": f"{s}\n\nARTICLE:\n{article}"}]
    out, _ = call_llm(model, msg, max_tokens=3000, temperature=0.0, effort="low")
    try:
        return json.loads(out[out.index("{"): out.rindex("}") + 1]).get("issues", [])
    except Exception:
        return [{"claim": "critic output unparsable", "problem": "needs human", "severity": "high", "fix": ""}]


# ---------- validation ----------
def validate_text(text, subtopics, algorithmic=False):
    errs = []
    if not text.rstrip().endswith("<!-- END -->"): errs.append("missing END sentinel (truncated?)")
    if text.count("```") % 2: errs.append("unbalanced code fence")
    heads = " ".join(re.findall(r"^#{2,3}\s+(.*)", text, re.M)).lower()
    for h in REQUIRED:
        if h.lower().split()[0] not in heads: errs.append("missing section: " + h)
    if algorithmic and "complexity" not in heads: errs.append("missing Complexity")
    low = text.lower()
    for b in BANNED:
        if b.lower() in low: errs.append("banned text: " + b)
    for s in subtopics:
        words = [w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3]
        if words and sum(w in low for w in words) < max(1, len(words) // 2): errs.append("subtopic not covered: " + s)
    return errs


def front_matter(row, srcs, status, issues, gm, cm):
    y = ["---", f"topic: {row['topic']}", f"domain: {row['domain']}",
         "subtopics: [" + ", ".join(json.dumps(x) for x in row["subtopics"].split(" | ") if x) + "]", "sources:"]
    for s in srcs: y += [f"  - title: {json.dumps(s['title'])}", f"    url: {s['url']}", f"    license: {s['license']}"]
    y += [f"status: {status}", f"open_issues: {len(issues)}", f"generator: {gm}", f"critic: {cm}",
          f"last_verified: {TODAY}", "human_reviewed: false", "---", ""]
    return "\n".join(y)


def process(row, out, gm, cm):
    srcs = get_sources(row)
    if not srcs: return "NO_SOURCE", None
    draft = open(row["draft_path"], encoding="utf-8", errors="replace").read() if row["draft_path"] else ""
    feedback, art, issues, errs = "", "", [], []
    for attempt in range(3):
        art, fin = call_llm(gm, gen_prompt(row, srcs, feedback, draft), effort="low")
        if fin == "length":
            art, fin = call_llm(gm, gen_prompt(row, srcs, feedback, draft), max_tokens=14000, effort="low")
        art = art.strip()
        if "<!-- END -->" in art: art = art[:art.rindex("<!-- END -->")].rstrip() + "\n\n<!-- END -->"
        errs = validate_text(art, row["subtopics"].split(" | "), row["algorithmic"] == "1")
        issues = [i for i in critic(art, srcs, cm) if i.get("severity") in ("high", "medium")] if not errs else []
        high = [i for i in issues if i.get("severity") == "high"]
        if not errs and not high: break
        feedback = "\n".join(errs + [f"- {i['claim']}: {i['problem']} -> {i['fix']}" for i in issues])
    status = "AUTO_VERIFIED" if not errs and not issues and "[VERIFY]" not in art else "NEEDS_HUMAN"
    d = Path(out) / row["domain"]; d.mkdir(parents=True, exist_ok=True)
    (d / (slug(row["topic"]) + ".md")).write_text(front_matter(row, srcs, status, issues + [{}] * len(errs), gm, cm) + art + "\n", encoding="utf-8")
    if issues or errs:
        (d / (slug(row["topic"]) + ".issues.json")).write_text(json.dumps(dict(errors=errs, issues=issues), indent=1), encoding="utf-8")
    return status, None


def build(topics, out, limit, domain, workers):
    gm = os.environ.get("GEN_MODEL", "openai/gpt-oss-120b")
    cm = os.environ.get("CRITIC_MODEL", "openai/gpt-oss-20b")  # fallback to available model
    rows = [r for r in csv.DictReader(open(topics, encoding="utf-8")) if r["tier"] == "core" and (not domain or r["domain"] == domain)]
    Path(out).mkdir(exist_ok=True); pf = Path(out) / "progress.json"
    prog = json.loads(pf.read_text()) if pf.exists() else {}
    todo = [r for r in rows if prog.get(r["topic"]) in (None, "ERROR")][: limit or None]
    print(f"{len(todo)} topics to build ({len(rows)-len(todo)} already done)")

    def job(r):
        try: return r["topic"], process(r, out, gm, cm)[0]
        except Exception as e:
            print(f"Error on {r['topic']}: {e}")
            return r["topic"], "ERROR"
    with cf.ThreadPoolExecutor(workers) as ex:
        for k, (topic, st) in enumerate(ex.map(job, todo), 1):
            prog[topic] = st; pf.write_text(json.dumps(prog, indent=1))  # checkpoint after every topic
            print(f"[{k}/{len(todo)}] {st:14} {topic}")
    from collections import Counter
    print("summary:", dict(Counter(prog.values())))


def validate_dir(d):
    bad = 0; n = 0
    for f in glob.glob(os.path.join(d, "*", "*.md")):
        t = open(f, encoding="utf-8").read(); n += 1
        subs = re.findall(r'"([^"]+)"', (re.search(r"subtopics: \[(.*)\]", t) or [0, ""])[1])
        e = validate_text(t.split("---", 2)[-1], subs, "complexity" in t.lower())
        if e: bad += 1; print(f, "->", "; ".join(e))
    print(f"{n} files, {bad} failing"); sys.exit(1 if bad else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("triage"); a.add_argument("--kb", required=True); a.add_argument("--out", default="topics.csv"); a.add_argument("--core", type=int, default=100)
    b = sp.add_parser("resolve"); b.add_argument("--topics", default="topics.csv")
    c = sp.add_parser("build"); c.add_argument("--topics", default="topics.csv"); c.add_argument("--out", default="kb_v2")
    c.add_argument("--limit", type=int, default=0); c.add_argument("--domain", default=""); c.add_argument("--workers", type=int, default=2)
    d = sp.add_parser("validate"); d.add_argument("--dir", default="kb_v2")
    x = ap.parse_args()
    if x.cmd == "triage": triage(x.kb, x.out, x.core)
    elif x.cmd == "resolve": resolve(x.topics)
    elif x.cmd == "build": build(x.topics, x.out, x.limit, x.domain, x.workers)
    else: validate_dir(x.dir)
