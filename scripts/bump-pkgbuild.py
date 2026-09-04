#!/usr/bin/env python3
"""Bump PKGBUILD's pkgver/_rev/md5sums[0] to the given values and reset pkgrel."""
import re
import sys


def main():
    new_ver, new_rev, new_md5 = sys.argv[1], sys.argv[2], sys.argv[3]

    with open("PKGBUILD") as f:
        text = f.read()

    text = re.sub(r'^pkgver=\S+$', f'pkgver={new_ver}', text, count=1, flags=re.M)
    text = re.sub(r'^pkgrel=\S+$', 'pkgrel=1', text, count=1, flags=re.M)
    text = re.sub(r'^_rev=\S+$', f'_rev={new_rev}', text, count=1, flags=re.M)

    md5sums = re.search(r"^md5sums=\(([\s\S]*?)\)$", text, re.M)
    entries = [e.strip() for e in md5sums.group(1).strip().splitlines()]
    entries[0] = re.sub(r"'[a-f0-9]+'", f"'{new_md5}'", entries[0])
    new_block = "md5sums=(" + "\n         ".join(entries) + ")"
    text = text[:md5sums.start()] + new_block + text[md5sums.end():]

    with open("PKGBUILD", "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
