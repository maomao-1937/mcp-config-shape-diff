from __future__ import annotations
import argparse
import json
import os
import re
import stat
import sys
import math
from pathlib import Path

MAX_INPUT = 256 * 1024
MAX_OUTPUT = 32 * 1024
ERROR = {"error": "E_INPUT"}

class InvalidInput(Exception):
    pass

def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise InvalidInput()
        out[key] = value
    return out

def _constant(_):
    raise InvalidInput()

def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise InvalidInput()
    return number

def read_input(arg: str) -> bytes:
    if arg == "-":
        data = sys.stdin.buffer.read(MAX_INPUT + 1)
    else:
        if not arg or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", arg):
            raise InvalidInput()
        # Reject network/device spellings independent of host OS, while leaving
        # native POSIX absolute paths intact on POSIX systems.
        if arg.startswith(("\\\\", "//", "\\?\\", "\\.\\")):
            raise InvalidInput()
        s = arg.replace("/", "\\") if os.name == "nt" else arg
        if re.match(r"^[A-Za-z]:[^\\]", s):
            raise InvalidInput()  # drive-relative
        # A colon is allowed only as the drive separator; reject ADS and URI-like forms.
        if ":" in s[2:] if len(s) >= 2 and s[1] == ":" else ":" in s:
            raise InvalidInput()
        p = Path(arg)
        try:
            st = os.stat(p, follow_symlinks=True)
        except (OSError, ValueError):
            raise InvalidInput() from None
        if not stat.S_ISREG(st.st_mode):
            raise InvalidInput()
        with open(p, "rb") as f:
            data = f.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise InvalidInput()
    return data

def load_snapshot(data: bytes):
    try:
        text = data.decode("utf-8", errors="strict")
        obj = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_finite_float)
    except (UnicodeError, json.JSONDecodeError, InvalidInput, RecursionError):
        raise InvalidInput() from None
    if type(obj) is not dict or set(obj) != {"before", "after"}:
        raise InvalidInput()
    sides = []
    for side in (obj["before"], obj["after"]):
        if type(side) is not dict or set(side) != {"mcpServers"} or type(side["mcpServers"]) is not dict:
            raise InvalidInput()
        servers = side["mcpServers"]
        if len(servers) > 128:
            raise InvalidInput()
        for name, cfg in servers.items():
            if type(name) is not str or not (1 <= len(name) <= 128) or type(cfg) is not dict or len(cfg) > 64:
                raise InvalidInput()
            if "args" in cfg and type(cfg["args"]) is not list:
                raise InvalidInput()
            if "env" in cfg and type(cfg["env"]) is not dict:
                raise InvalidInput()
            for field in ("command", "url", "cwd"):
                if field in cfg and type(cfg[field]) is not str:
                    raise InvalidInput()
        sides.append(servers)
    return sides

def transport(cfg):
    t = cfg.get("type")
    if type(t) is str:
        if t in ("local", "stdio"):
            return "stdio"
        if t in ("http", "sse"):
            return "remote"
    command = "command" in cfg
    url = "url" in cfg
    if command and not url:
        return "stdio"
    if url and not command:
        return "remote"
    return "unknown"

def facts(cfg):
    env = cfg.get("env")
    keys = set(env) if type(env) is dict else set()
    args = cfg.get("args")
    return {
        "command_present_changed": False,
        "url_present_changed": False,
        "transport_changed": False,
        "cwd_present_changed": False,
        "args_count_before": len(args) if type(args) is list else 0,
        "args_count_after": 0,
        "env_key_count_before": len(keys),
        "env_key_count_after": 0,
        "env_key_set_changed": False,
    }

def compare(before, after):
    rows = []
    different = False
    for name in sorted(before.keys() | after.keys()):
        if name not in before:
            row = {"server": name, "status": "added"}
            different = True
        elif name not in after:
            row = {"server": name, "status": "removed"}
            different = True
        else:
            a, b = before[name], after[name]
            af, bf = facts(a), facts(b)
            af["args_count_after"] = len(b.get("args")) if type(b.get("args")) is list else 0
            af["env_key_count_after"] = len(b.get("env")) if type(b.get("env")) is dict else 0
            af["command_present_changed"] = ("command" in a) != ("command" in b)
            af["url_present_changed"] = ("url" in a) != ("url" in b)
            af["transport_changed"] = transport(a) != transport(b)
            af["cwd_present_changed"] = ("cwd" in a) != ("cwd" in b)
            ka = set(a.get("env", {})) if type(a.get("env")) is dict else set()
            kb = set(b.get("env", {})) if type(b.get("env")) is dict else set()
            af["env_key_set_changed"] = ka != kb
            changed = any(af[k] for k in ("command_present_changed", "url_present_changed", "transport_changed", "cwd_present_changed", "env_key_set_changed")) or af["args_count_before"] != af["args_count_after"] or af["env_key_count_before"] != af["env_key_count_after"]
            row = {"server": name, "status": "changed" if changed else "unchanged", **af}
            different |= changed
        rows.append(row)
    result = json.dumps({"servers": rows}, ensure_ascii=True, separators=(",", ":"))
    # Include the terminating newline in the output budget on all platforms.
    if len((result + os.linesep).encode("utf-8")) > MAX_OUTPUT:
        raise InvalidInput()
    return result, (1 if different else 0)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare structural facts in two MCP JSON snapshots.")
    parser.add_argument("input", help="JSON snapshot file, or - for stdin")
    args = parser.parse_args(argv)
    try:
        before, after = load_snapshot(read_input(args.input))
        output, code = compare(before, after)
        sys.stdout.write(output + "\n")
        return code
    except (InvalidInput, OSError, ValueError):
        sys.stdout.write(json.dumps(ERROR, separators=(",", ":")) + "\n")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
