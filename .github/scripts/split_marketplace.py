#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def shard_for(name: str, shard_count: int) -> int:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % shard_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create one deterministic shard of a Claude plugin marketplace."
    )
    parser.add_argument(
        "--file",
        default=".claude-plugin/marketplace.json",
        help="Marketplace JSON to rewrite in place.",
    )
    parser.add_argument("--shard", type=int, required=True, help="1-based shard number.")
    parser.add_argument("--shards", type=int, default=3, help="Total number of shards.")
    parser.add_argument(
        "--max-plugins",
        type=int,
        default=1900,
        help="Fail if any generated shard would exceed this many plugins.",
    )
    args = parser.parse_args()

    if args.shards < 2:
        raise SystemExit("--shards must be at least 2")
    if not 1 <= args.shard <= args.shards:
        raise SystemExit("--shard must be between 1 and --shards")

    path = Path(args.file)
    data = json.loads(path.read_text(encoding="utf-8"))

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise SystemExit("marketplace.json does not contain a plugins array")

    names = []
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict) or not isinstance(plugin.get("name"), str):
            raise SystemExit(f"plugin at index {index} has no string name")
        names.append(plugin["name"])

    if len(names) != len(set(names)):
        raise SystemExit("duplicate plugin names found in upstream marketplace")

    buckets = [[] for _ in range(args.shards)]
    for plugin in plugins:
        buckets[shard_for(plugin["name"], args.shards)].append(plugin)

    distribution = [len(bucket) for bucket in buckets]
    if any(count > args.max_plugins for count in distribution):
        raise SystemExit(
            f"shard size limit exceeded: {distribution}; "
            f"max allowed per shard is {args.max_plugins}"
        )

    original_name = data.get("name")
    if not isinstance(original_name, str) or not original_name:
        original_name = "claude-plugins-community"

    data["name"] = f"{original_name}-split-{args.shard}"

    description = data.get("description")
    suffix = (
        f" Split shard {args.shard}/{args.shards}; generated automatically "
        "from anthropics/claude-plugins-community."
    )
    if isinstance(description, str):
        data["description"] = description.rstrip() + suffix
    else:
        data["description"] = suffix.strip()

    data["plugins"] = buckets[args.shard - 1]

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Total plugins: {len(plugins)}")
    print(f"Shard distribution: {distribution}")
    print(
        f"Wrote shard {args.shard}/{args.shards}: "
        f"{len(data['plugins'])} plugins -> {path}"
    )


if __name__ == "__main__":
    main()
