"""Helper for the Git workflow. It never runs git for you and never sets who you are.

Show your plan:    python ../vulnsight-full/tools/git_plan.py --module 1 --member 2
Copy commit 1:     python ../vulnsight-full/tools/git_plan.py --module 1 --member 2 --copy 1

Run it from inside YOUR clone of the repository. --source is the folder of the full project (default: the folder this script is in).
Modules: setup, 1, 2, 3.   Members: 1, 2, 3.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path


def chunks(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def main():
    ap = argparse.ArgumentParser(description="Show or copy your files for one module.")
    ap.add_argument("--module", required=True, choices=["setup", "1", "2", "3"])
    ap.add_argument("--member", required=True, type=int, choices=[1, 2, 3])
    ap.add_argument("--source", default=str(Path(__file__).resolve().parent.parent), help="folder of the full project")
    ap.add_argument("--copy", type=int, metavar="N", help="copy the files of commit number N into the current folder")
    args = ap.parse_args()

    source = Path(args.source)
    manifest = json.loads((source / "ownership.json").read_text(encoding="utf-8"))
    phase = next(p for p in manifest["phases"] if p["id"] == args.module)
    mine = phase["members"][str(args.member)]
    commits = mine["commits"]

    if args.copy is not None:
        if not 1 <= args.copy <= len(commits):
            sys.exit(f"Commit number must be between 1 and {len(commits)}.")
        commit = commits[args.copy - 1]
        for rel in commit["files"]:
            src, dst = source / rel, Path.cwd() / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"copied  {rel}")
        print("\nNow run:")
        for group in chunks(commit["files"], 6):
            print("  git add " + " ".join(group))
        print(f'  git commit -m "{commit["message"]}"')
        return

    print(f'{phase["title"]} ({phase["week"]}), Member {args.member}')
    print(f'Branch: {mine["branch"]}\n')
    print("  git checkout main")
    print("  git pull")
    print(f'  git checkout -b {mine["branch"]}\n')
    for i, commit in enumerate(commits, 1):
        print(f'Commit {i}: {commit["message"]}')
        print(f"  python {source.name}/tools/git_plan.py --module {args.module} --member {args.member} --copy {i}   (copies these files)")
        for rel in commit["files"]:
            print(f"      {rel}")
        for group in chunks(commit["files"], 6):
            print("  git add " + " ".join(group))
        print(f'  git commit -m "{commit["message"]}"\n')
    print(f'  git push -u origin {mine["branch"]}')
    print("\nThen open a Pull Request on GitHub (branch -> main) and tell the member who merges this phase.")


if __name__ == "__main__":
    main()
