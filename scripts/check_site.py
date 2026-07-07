#!/usr/bin/env python3
"""
Static-site sanity checks for the Steve Ostermiller Advisory site.

Runs in CI (and locally) with nothing but the Python standard library, so it
never depends on external network calls or third-party actions. It guards the
kinds of breakage that actually happen when hand-editing a static page:

  1. Malformed HTML   — unclosed or stray tags.
  2. Broken assets    — a local href/src (css, js, image, favicon) that points
                        at a file that isn't in the repo.
  3. Broken anchors   — an in-page href="#id" with no matching element id.

External URLs (https://, mailto:, the not-yet-live custom domain, the Formspree
endpoint) are intentionally NOT fetched — that would make CI flaky and is out of
scope for a build-time check.

Exit code 0 = all good; 1 = problems found (fails the CI job).
"""

import html.parser
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILES = ["index.html", "privacy.html"]

VOID = {"meta", "link", "img", "br", "hr", "input", "area", "base",
        "col", "embed", "source", "track", "wbr"}


class SiteParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []            # open (non-void) tags
        self.tag_errors = []       # malformed-tag messages
        self.ids = set()           # every id="" on the page
        self.local_refs = []       # (attr_value, kind) for href/src to check
        self.anchor_refs = []      # in-page #fragment links

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        # Collect linkable references
        for attr in ("href", "src"):
            if attr in a and a[attr] is not None:
                self._classify(a[attr])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # e.g. <img ... /> — treat as void, still collect attrs
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for attr in ("href", "src"):
            if attr in a and a[attr] is not None:
                self._classify(a[attr])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.tag_errors.append(
                    f"<{self.stack[-1]}> is not closed before </{tag}>")
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.tag_errors.append(f"stray </{tag}> with no matching open tag")

    def _classify(self, value):
        v = value.strip()
        if not v:
            return
        if v.startswith("#"):
            self.anchor_refs.append(v)
        elif re.match(r"^(https?:|mailto:|tel:|data:|//)", v):
            return  # external / non-file — out of scope
        else:
            self.local_refs.append(v)


def check_file(path):
    problems = []
    abspath = os.path.join(ROOT, path)
    with open(abspath, encoding="utf-8") as fh:
        source = fh.read()

    p = SiteParser()
    p.feed(source)

    # 1. Malformed HTML
    for err in p.tag_errors:
        problems.append(f"[html] {err}")
    for leftover in p.stack:
        problems.append(f"[html] <{leftover}> is never closed")

    # 2. Local assets exist
    base = os.path.dirname(abspath)
    for ref in p.local_refs:
        clean = ref.split("?", 1)[0].split("#", 1)[0]  # drop ?v=/query + fragment
        target = os.path.normpath(os.path.join(base, clean))
        if not os.path.isfile(target):
            problems.append(f"[asset] '{ref}' -> missing file {os.path.relpath(target, ROOT)}")

    # 3. In-page anchors resolve to an id
    for frag in p.anchor_refs:
        anchor = frag[1:]
        if anchor and anchor not in p.ids:
            problems.append(f"[anchor] '{frag}' has no matching id on the page")

    return problems, p


def main():
    total = 0
    for rel in HTML_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print(f"::error::{rel} not found")
            total += 1
            continue
        problems, p = check_file(rel)
        print(f"\n{rel}: {len(p.local_refs)} local asset(s), "
              f"{len(p.anchor_refs)} in-page anchor(s), {len(p.ids)} id(s)")
        if problems:
            for msg in problems:
                print(f"::error file={rel}::{msg}")
            total += len(problems)
        else:
            print(f"  OK — no issues")

    print("\n" + ("-" * 48))
    if total:
        print(f"FAILED: {total} problem(s) found")
        sys.exit(1)
    print("PASSED: all checks green")


if __name__ == "__main__":
    main()
