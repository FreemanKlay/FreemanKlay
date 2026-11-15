"""Reads your recent GitHub activity and writes a small JSON file used to draw the banner pulses
and the languages card.

Privacy: the output never contains repository names. Private repositories are skipped unless
INCLUDE_PRIVATE=true, and even then only a language and a count leave this script.

Environment:
  PROFILE_TOKEN    token (read:user is enough for public data; add repo for private)
  PROFILE_USER     your login
  INCLUDE_PRIVATE  "true" to count private repositories (default "false")
  DAYS             window for pulses, default 90
"""
import datetime as dt
import json
import os
import sys
import urllib.request

API = "https://api.github.com/graphql"

Q_COMMITS = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        repository { isPrivate primaryLanguage { name } }
        contributions(first: 100) { nodes { occurredAt commitCount } }
      }
    }
  }
}"""

Q_REPOS = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 40, after: $after, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        isPrivate
        languages(first: 15, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
        stargazers(first: 30, orderBy: {field: STARRED_AT, direction: DESC}) { edges { starredAt } }
        forks(first: 30, orderBy: {field: CREATED_AT, direction: DESC}) { nodes { createdAt } }
        issues(first: 30, orderBy: {field: CREATED_AT, direction: DESC}) { nodes { createdAt author { login } } }
        pullRequests(first: 30, orderBy: {field: CREATED_AT, direction: DESC}) { nodes { createdAt author { login } } }
      }
    }
  }
}"""


def parse_commits(resp, include_private):
    merged = {}
    repos = resp["data"]["user"]["contributionsCollection"]["commitContributionsByRepository"]
    for r in repos:
        repo = r["repository"]
        if repo.get("isPrivate") and not include_private:
            continue
        lang = (repo.get("primaryLanguage") or {}).get("name") or "Other"
        for n in r["contributions"]["nodes"]:
            key = (n["occurredAt"][:10], lang)
            merged[key] = merged.get(key, 0) + int(n["commitCount"])
    return [{"date": d, "language": l, "commits": c}
            for (d, l), c in sorted(merged.items(), reverse=True)]


def parse_repos(resp, login, since, include_private):
    """Returns (language bytes {name: bytes}, events by others [{date, kind}], pageInfo)."""
    block = resp["data"]["user"]["repositories"]
    langs, events = {}, []
    for repo in block["nodes"]:
        if repo.get("isPrivate") and not include_private:
            continue
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + int(e["size"])
        for e in repo["stargazers"]["edges"]:
            if e["starredAt"][:10] >= since:
                events.append({"date": e["starredAt"][:10], "kind": "star"})
        for n in repo["forks"]["nodes"]:
            if n["createdAt"][:10] >= since:
                events.append({"date": n["createdAt"][:10], "kind": "fork"})
        for kind, key in (("issue", "issues"), ("pr", "pullRequests")):
            for n in repo[key]["nodes"]:
                author = (n.get("author") or {}).get("login")
                if author and author.lower() != login.lower() and n["createdAt"][:10] >= since:
                    events.append({"date": n["createdAt"][:10], "kind": kind})
    return langs, events, block["pageInfo"]


def call(token, query, variables):
    req = urllib.request.Request(
        API, data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": "bearer " + token, "User-Agent": "profile-pulse",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if body.get("errors"):
        raise RuntimeError("GitHub API error: " + json.dumps(body["errors"])[:500])
    return body


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "activity.json"
    token = os.environ.get("PROFILE_TOKEN")
    login = os.environ.get("PROFILE_USER")
    if not token or not login:
        sys.exit("PROFILE_TOKEN and PROFILE_USER are required")
    private = os.environ.get("INCLUDE_PRIVATE", "false").lower() == "true"
    days = int(os.environ.get("DAYS", "90"))
    now = dt.datetime.now(dt.timezone.utc)
    since = (now - dt.timedelta(days=days)).strftime("%Y-%m-%d")

    commits = parse_commits(call(token, Q_COMMITS, {
        "login": login, "from": since + "T00:00:00Z", "to": now.strftime("%Y-%m-%dT%H:%M:%SZ")}), private)

    lang_bytes, events, after = {}, [], None
    for _ in range(5):  # up to 200 repositories
        langs, ev, page = parse_repos(call(token, Q_REPOS, {"login": login, "after": after}),
                                      login, since, private)
        for k, v in langs.items():
            lang_bytes[k] = lang_bytes.get(k, 0) + v
        events += ev
        if not page["hasNextPage"]:
            break
        after = page["endCursor"]

    data = {
        "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": days,
        "include_private": private,
        "pulses": commits,
        "others": sorted(events, key=lambda e: e["date"], reverse=True),
        "languages": [{"name": k, "bytes": v} for k, v in sorted(lang_bytes.items(), key=lambda kv: -kv[1])],
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(f"{len(commits)} commit-days, {len(events)} events by others, {len(lang_bytes)} languages")


if __name__ == "__main__":
    main()
