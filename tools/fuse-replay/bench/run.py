#!/usr/bin/env python3
"""Deterministic warm-local-filesystem replay overhead measurements, not FUSE results."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import time


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def command_text(argv):
    result = subprocess.run(argv, text=True, capture_output=True, check=False)
    return {"argv": argv, "returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def generate_trace(path, workload, operations, streams):
    """Total timed stat/pread requests are fixed; read adds exactly 2*streams FD ops."""
    with path.open("x", encoding="utf-8") as output:
        def emit(value):
            output.write(json.dumps(value, separators=(",", ":")) + "\n")
        emit({"format": "mounted-fs-replay", "version": 1, "payload_provenance": "synthetic", "description": f"{workload}; {operations} fixed requests, {streams} independent streams, warm local fixture"})
        if workload == "pread4k-hot":
            for stream in range(streams):
                emit({"phase": 0, "stream": stream, "op": "open", "fd": 1, "path": f"data-{stream:02d}.bin", "access": "read"})
        for index in range(operations):
            stream = index % streams
            row = {"phase": 0, "stream": stream}
            if workload == "stat-heavy":
                row.update(op="stat", path=f"data-{stream:02d}.bin")
            else:
                row.update(op="pread", fd=1, offset=0, len=4096, expected_bytes=4096)
            emit(row)
        if workload == "pread4k-hot":
            for stream in range(streams):
                emit({"phase": 0, "stream": stream, "op": "close", "fd": 1})


def run_measured(argv, stdout_path, stderr_path):
    # wait4 gives this child alone, not the cumulative high-water mark of past children.
    begin = time.monotonic()
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        proc = subprocess.Popen(argv, stdout=stdout, stderr=stderr)
        _, status, usage = os.wait4(proc.pid, 0)
        proc.returncode = os.waitstatus_to_exitcode(status)
    return {"returncode": proc.returncode, "process_seconds": time.monotonic() - begin,
            "process_user_seconds": usage.ru_utime, "process_system_seconds": usage.ru_stime,
            "process_max_rss_kib": usage.ru_maxrss, "voluntary_context_switches": usage.ru_nvcsw,
            "involuntary_context_switches": usage.ru_nivcsw}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new directory on desired local filesystem; never overwritten/deleted")
    parser.add_argument("--operations", type=int, default=1_048_576)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=8, help="complete read-only trace passes per measured process")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()
    if args.operations < 16 or args.operations % 16 or args.repeats < 3 or not 1 <= args.iterations <= 10000:
        parser.error("operations must be a positive multiple of 16 and repeats >=3")
    binary = args.binary.resolve(strict=True)
    output = args.output.absolute()
    output.mkdir(exist_ok=False)
    root = output / "measured-root"
    subprocess.run([str(binary), "init", "--root", str(root)], check=True)
    fixture = {}
    for stream in range(16):
        content = hashlib.shake_256(f"fuse-replay-benchmark-v1|20261023|{stream}".encode()).digest(4096)
        path = root / f"data-{stream:02d}.bin"
        with path.open("xb") as target:
            target.write(content)
        fixture[path.name] = {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
    write_json(output / "fixture.json", fixture)
    traces = {}
    for workload in ("stat-heavy", "pread4k-hot"):
        trace = output / f"{workload}.jsonl"
        generate_trace(trace, workload, args.operations, 16)
        traces[workload] = trace
    environment = {
        "scope": "warm local filesystem replay-engine overhead; NOT FUSE/BrewFS performance",
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(), "cpu_count": os.cpu_count(),
        "cpuinfo": Path("/proc/cpuinfo").read_text().split("\n\n")[0],
        "meminfo": Path("/proc/meminfo").read_text(),
        "filesystem": command_text(["findmnt", "-T", str(root), "-o", "TARGET,SOURCE,FSTYPE,OPTIONS", "--json"]),
        "rustc": command_text(["rustc", "--version", "--verbose"]),
        "binary": str(binary), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "traces": {name: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size} for name, path in traces.items()},
        "operations_per_trace": args.operations, "streams": 16, "workers": [1, 4, 16], "timing": ["off", "op"], "repeats": args.repeats,
        "complete_trace_iterations_per_run": args.iterations,
        "cache": "fixtures written before run; no cache eviction; preflight scans metadata; repeated same files",
        "oracle": "fixed initial file hashes recorded; pread return-length checked, per-read content hashing disabled equally",
        "timing_boundaries": "parse and tree checks precede execution; process user/system/RSS include parse and setup",
    }
    write_json(output / "environment.json", environment)
    if args.generate_only:
        print(output)
        return
    cells = [(workload, workers, timing, repeat) for repeat in range(args.repeats)
             for workload in traces for workers in (1, 4, 16) for timing in ("off", "op")]
    random.Random(20261023).shuffle(cells)
    rows = []
    for index, (workload, workers, timing, repeat) in enumerate(cells):
        cell = f"{index:02d}-{workload}-w{workers}-{timing}-r{repeat}"
        result_path = output / f"{cell}.result.json"
        argv = [str(binary), "run", "--trace", str(traces[workload]), "--root", str(root),
                "--output", str(result_path), "--workers", str(workers), "--timing", timing,
                "--pace", "asap", "--timeout-seconds", "120", "--iterations", str(args.iterations)]
        usage = run_measured(argv, output / f"{cell}.stdout.txt", output / f"{cell}.stderr.txt")
        result = json.loads(result_path.read_text()) if result_path.exists() and result_path.stat().st_size else None
        row = {"order": index, "workload": workload, "workers": workers, "timing": timing, "repeat": repeat, **usage,
               "valid": bool(result and result.get("valid")), "result": result_path.name}
        if result and result.get("totals"):
            for key in ("parse_seconds", "initial_tree_scan_seconds", "preparation_seconds", "execution_seconds", "logical_operations_per_second", "correct_operations_per_second"):
                row[key] = result[key]
            row.update(result["totals"])
        rows.append(row)
        print(f"{index + 1}/{len(cells)} {cell}: valid={row['valid']} execution={row.get('execution_seconds')}", flush=True)
    write_json(output / "runs.json", rows)
    columns = sorted(set().union(*(row.keys() for row in rows)))
    with (output / "runs.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    groups = []
    for workload in traces:
        for workers in (1, 4, 16):
            for timing in ("off", "op"):
                selected = [row for row in rows if (row["workload"], row["workers"], row["timing"]) == (workload, workers, timing)]
                valid = [row for row in selected if row["valid"] and row["returncode"] == 0]
                summary = {"workload": workload, "workers": workers, "timing": timing, "attempted_runs": len(selected), "valid_runs": len(valid)}
                if valid:
                    for key in ("execution_seconds", "parse_seconds", "preparation_seconds", "logical_operations_per_second", "process_max_rss_kib"):
                        values = [row[key] for row in valid]
                        summary[key] = {"min": min(values), "median": statistics.median(values), "max": max(values)}
                groups.append(summary)
    write_json(output / "summary.json", groups)
    if any(not row["valid"] or row["returncode"] for row in rows):
        raise SystemExit("at least one benchmark failed; all rows retained")


if __name__ == "__main__":
    main()
