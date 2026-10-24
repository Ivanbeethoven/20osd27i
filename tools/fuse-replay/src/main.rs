#[cfg(not(target_os = "linux"))]
fn main() {
    eprintln!("fuse-replay requires Linux with openat2 (kernel >=5.6)");
    std::process::exit(2);
}

#[cfg(target_os = "linux")]
fn main() {
    match cli() {
        Ok(code) => std::process::exit(code),
        Err(error) => {
            eprintln!("error: {error}");
            std::process::exit(2);
        }
    }
}

#[cfg(target_os = "linux")]
fn cli() -> fuse_replay::Result<i32> {
    use fuse_replay::{
        replay::{self, Config},
        safe, trace,
    };
    use std::{collections::BTreeMap, path::Path};
    const HELP:&str="fuse-replay: Linux mounted-filesystem POSIX workload replay\n\n  fuse-replay validate --trace FILE [--max-io BYTES]\n  fuse-replay init --root /absolute/empty/dedicated-directory\n  fuse-replay run --trace FILE --root /absolute/dedicated-directory --output OUTSIDE.json\n      [--workers N] [--pace asap|trace] [--timing off|op] [--max-io BYTES]\n\nNo command means validate. Only explicit run executes trace operations.\ninit refuses nonempty directories. Outputs are never overwritten.\n";
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() || args[0] == "--help" || args[0] == "-h" {
        print!("{HELP}");
        return Ok(0);
    }
    if args[0] == "--version" {
        println!("fuse-replay {}", env!("CARGO_PKG_VERSION"));
        return Ok(0);
    }
    let (command, rest) = if args[0].starts_with("--") {
        ("validate", &args[..])
    } else {
        (args[0].as_str(), &args[1..])
    };
    if !["validate", "init", "fingerprint", "run"].contains(&command) {
        return Err(format!("unknown command {command}\n{HELP}"));
    }
    let mut opts = BTreeMap::new();
    if rest.len() % 2 != 0 {
        return Err("every option requires one value".into());
    }
    let allowed = match command {
        "init" | "fingerprint" => vec!["--root"],
        "validate" => vec!["--trace", "--max-io"],
        _ => vec![
            "--trace",
            "--root",
            "--output",
            "--workers",
            "--pace",
            "--timing",
            "--max-io",
            "--timeout-seconds",
            "--iterations",
        ],
    };
    for pair in rest.as_chunks::<2>().0 {
        if !allowed.contains(&pair[0].as_str())
            || opts.insert(pair[0].as_str(), pair[1].as_str()).is_some()
        {
            return Err(format!("unknown or duplicate option {}", pair[0]));
        }
    }
    let required = |key| {
        opts.get(key)
            .copied()
            .ok_or_else(|| format!("missing {key}"))
    };
    if command == "init" {
        let root = Path::new(required("--root")?);
        safe::init(root)?;
        println!("initialized dedicated root {}", root.display());
        return Ok(0);
    }
    if command == "fingerprint" {
        let root = safe::Root::open(Path::new(required("--root")?))?;
        println!(
            "{}",
            serde_json::json!({"initial_tree_sha256":root.check_initial_tree(true)?})
        );
        return Ok(0);
    }
    let max_io = opts
        .get("--max-io")
        .copied()
        .unwrap_or("1048576")
        .parse::<usize>()
        .map_err(|_| "invalid max-io")?;
    let trace = trace::load(Path::new(required("--trace")?), max_io)?;
    if command == "validate" {
        println!(
            "{}",
            serde_json::json!({"valid":true,"trace_sha256":trace.input_sha256,"trace_bytes":trace.trace_bytes,"operations":trace.records.len(),"streams":trace.stream_ids.len(),"phases":trace.phase_ids.len(),"parse_seconds":trace.parse_seconds,"payload_provenance":trace.header.payload_provenance,"execution_performed":false})
        );
        return Ok(0);
    }
    let workers = opts
        .get("--workers")
        .map(|s| s.parse::<usize>().map_err(|_| "invalid workers"))
        .transpose()?
        .unwrap_or(trace.stream_ids.len());
    let pace = match opts.get("--pace").copied().unwrap_or("asap") {
        "asap" => false,
        "trace" => true,
        _ => return Err("pace must be asap or trace".into()),
    };
    let timing = match opts.get("--timing").copied().unwrap_or("off") {
        "off" => false,
        "op" => true,
        _ => return Err("timing must be off or op".into()),
    };
    let timeout_seconds = opts
        .get("--timeout-seconds")
        .copied()
        .unwrap_or("300")
        .parse::<u64>()
        .map_err(|_| "invalid timeout-seconds")?;
    let iterations = opts
        .get("--iterations")
        .copied()
        .unwrap_or("1")
        .parse::<usize>()
        .map_err(|_| "invalid iterations")?;
    let summary = replay::run(
        trace,
        Path::new(required("--root")?),
        Path::new(required("--output")?),
        Config {
            workers,
            pace,
            timing,
            timeout_seconds,
            iterations,
        },
    )?;
    println!(
        "{}",
        serde_json::json!({"valid":summary.valid,"attempted":summary.totals.attempted,"mismatches":summary.totals.mismatches,"execution_seconds":summary.execution_seconds,"logical_operations_per_second":summary.logical_operations_per_second,"output":required("--output")?})
    );
    Ok(if summary.valid { 0 } else { 1 })
}
