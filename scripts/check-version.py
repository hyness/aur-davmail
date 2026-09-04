#!/usr/bin/env python3
"""Check SourceForge for a newer davmail release than what's pinned in PKGBUILD.

Prints GitHub Actions output variables: needs_update, new_version, new_rev, new_md5.
"""
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = "https://sourceforge.net/projects/davmail/rss?path=/"
# Matches e.g. /davmail/6.8.1/davmail-6.8.1-4210.zip (the exact source PKGBUILD uses)
FILE_RE = re.compile(r"^/davmail/(?P<ver>[\d.]+)/davmail-(?P=ver)-(?P<rev>\d+)\.zip$")
NS = {"media": "http://video.search.yahoo.com/mrss/"}


def current_version():
    with open("PKGBUILD") as f:
        text = f.read()
    pkgver = re.search(r'^pkgver=(\S+)$', text, re.M).group(1)
    rev = re.search(r'^_rev=(\S+)$', text, re.M).group(1)
    return pkgver, rev


def latest_release():
    with urllib.request.urlopen(RSS_URL) as resp:
        root = ET.fromstring(resp.read())
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        m = FILE_RE.match(title)
        if not m:
            continue
        media = item.find("media:content", NS)
        md5 = media.find("media:hash", NS).text if media is not None else None
        return m.group("ver"), m.group("rev"), md5
    return None


def main():
    cur_ver, cur_rev = current_version()
    latest = latest_release()
    if latest is None:
        print("Could not find a matching release in the SourceForge feed", file=sys.stderr)
        sys.exit(1)
    new_ver, new_rev, new_md5 = latest

    needs_update = (new_ver, new_rev) != (cur_ver, cur_rev)

    gh_out = os.environ.get("GITHUB_OUTPUT")
    lines = [
        f"needs_update={'true' if needs_update else 'false'}",
        f"current_version={cur_ver}-{cur_rev}",
        f"new_version={new_ver}",
        f"new_rev={new_rev}",
        f"new_md5={new_md5 or ''}",
    ]
    print("\n".join(lines))
    if gh_out:
        with open(gh_out, "a") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
