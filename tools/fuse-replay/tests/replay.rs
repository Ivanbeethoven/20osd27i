#![cfg(target_os = "linux")]
use fuse_replay::{
    replay::{self, Config},
    safe, trace,
};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{
    fs,
    path::{Path, PathBuf},
    process::Command,
    sync::atomic::{AtomicU64, Ordering},
};
static NEXT: AtomicU64 = AtomicU64::new(0);
struct Scratch(PathBuf);
impl Scratch {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "fuse-replay-test-{}-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
    fn root(&self) -> PathBuf {
        let p = self.0.join("root");
        safe::init(&p).unwrap();
        p
    }
    fn trace(&self, rows: &[Value]) -> PathBuf {
        let path = self.0.join(format!(
            "trace-{}.jsonl",
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        let mut text="{\"format\":\"mounted-fs-replay\",\"version\":1,\"payload_provenance\":\"synthetic\"}\n".to_owned();
        for row in rows {
            text.push_str(&row.to_string());
            text.push('\n');
        }
        fs::write(&path, text).unwrap();
        path
    }
    fn output(&self) -> PathBuf {
        self.0.join(format!(
            "result-{}.json",
            NEXT.fetch_add(1, Ordering::Relaxed)
        ))
    }
}
impl Drop for Scratch {
    fn drop(&mut self) {
        assert!(self
            .0
            .file_name()
            .unwrap()
            .to_str()
            .unwrap()
            .starts_with("fuse-replay-test-"));
        let _ = fs::remove_dir_all(&self.0);
    }
}
fn config(workers: usize) -> Config {
    Config {
        workers,
        pace: false,
        timing: true,
        timeout_seconds: 10,
        iterations: 1,
    }
}
fn run(trace: &Path, root: &Path, out: &Path, workers: usize) -> replay::Summary {
    replay::run(
        trace::load(trace, 1024 * 1024).unwrap(),
        root,
        out,
        config(workers),
    )
    .unwrap()
}
fn row(op: &str) -> Value {
    json!({"phase":0,"stream":0,"op":op,"path":"file"})
}

#[test]
fn rejects_path_escape_and_unknown_fields() {
    let scratch = Scratch::new();
    for path in [
        "../x",
        "/tmp/x",
        "a/../x",
        "a//x",
        "./x",
        "a\\x",
        ".fuse-replay-root",
        "a/.fuse-replay-root",
    ] {
        let p = scratch.trace(&[json!({"phase":0,"stream":0,"op":"stat","path":path})]);
        assert!(trace::load(&p, 4096).is_err(), "accepted {path}");
    }
    let p = scratch
        .trace(&[json!({"phase":0,"stream":0,"op":"stat","path":"x","silently_ignored":true})]);
    assert!(trace::load(&p, 4096).is_err());
    let p = scratch.trace(&[json!({"phase":0,"stream":0,"op":"mmap","path":"x"})]);
    assert!(trace::load(&p, 4096).is_err());
}

#[test]
fn validates_handles_phase_and_timestamps() {
    let s = Scratch::new();
    let variants = vec![
        vec![json!({"phase":0,"stream":0,"op":"close","fd":1})],
        vec![
            json!({"phase":1,"stream":0,"op":"stat","path":"a"}),
            json!({"phase":0,"stream":0,"op":"stat","path":"b"}),
        ],
        vec![
            json!({"phase":0,"stream":0,"at_ns":10,"op":"stat","path":"a"}),
            json!({"phase":0,"stream":0,"at_ns":9,"op":"stat","path":"b"}),
        ],
        vec![json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"a","access":"read"})],
        vec![
            json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"a","access":"read"}),
            json!({"phase":0,"stream":0,"op":"close","fd":1,"expected_errno":5}),
        ],
    ];
    for rows in variants {
        assert!(trace::load(&s.trace(&rows), 4096).is_err());
    }
}

#[test]
fn concurrent_streams_are_isolated_and_phases_order_visibility() {
    let s = Scratch::new();
    let root = s.root();
    let mut rows = Vec::new();
    for stream in 0..16u8 {
        rows.extend([json!({"phase":0,"stream":stream,"op":"open","fd":7,"path":format!("f{stream}"),"access":"read_write","create":true,"exclusive":true}),json!({"phase":0,"stream":stream,"op":"pwrite","fd":7,"offset":0,"len":8192,"fill":stream}),json!({"phase":0,"stream":stream,"op":"close","fd":7})]);
    }
    for stream in 0..16u8 {
        let other = (stream + 1) % 16;
        let digest = format!("{:x}", Sha256::digest(vec![other; 8192]));
        rows.extend([json!({"phase":1,"stream":stream,"op":"open","fd":7,"path":format!("f{other}"),"access":"read"}),json!({"phase":1,"stream":stream,"op":"pread","fd":7,"offset":0,"len":8192,"expected_sha256":digest}),json!({"phase":1,"stream":stream,"op":"close","fd":7})]);
    }
    let summary = run(&s.trace(&rows), &root, &s.output(), 4);
    assert!(summary.valid);
    assert_eq!(summary.totals.attempted, 96);
    assert_eq!(summary.totals.actual_write_bytes, 16 * 8192);
    assert_eq!(summary.totals.actual_read_bytes, 16 * 8192);
    assert_eq!(summary.cleanup_close_syscalls, 0);
    for stream in 0..16u8 {
        assert_eq!(
            fs::read(root.join(format!("f{stream}"))).unwrap(),
            vec![stream; 8192]
        );
    }
}

#[test]
fn short_read_requires_explicit_expected_length() {
    let s = Scratch::new();
    let root = s.root();
    fs::write(root.join("file"), b"abc").unwrap();
    let mut rows = vec![
        json!({"phase":0,"stream":0,"op":"open","path":"file","fd":1,"access":"read"}),
        json!({"phase":0,"stream":0,"op":"pread","fd":1,"offset":0,"len":8}),
        json!({"phase":0,"stream":0,"op":"close","fd":1}),
    ];
    let result = run(&s.trace(&rows), &root, &s.output(), 1);
    assert!(!result.valid);
    assert_eq!(result.totals.actual_read_bytes, 3);
    assert_eq!(result.totals.requested_read_bytes, 8);
    assert_eq!(result.totals.short_reads, 1);
    rows[1]["expected_bytes"] = json!(3);
    rows[1]["expected_sha256"] = json!(format!("{:x}", Sha256::digest(b"abc")));
    assert!(run(&s.trace(&rows), &root, &s.output(), 1).valid);
    rows[1]["expected_sha256"] = json!("00".repeat(32));
    assert!(!run(&s.trace(&rows), &root, &s.output(), 1).valid);
}

#[test]
fn expected_errors_remain_distinct_from_successes() {
    let s = Scratch::new();
    let root = s.root();
    fs::write(root.join("file"), b"a").unwrap();
    let rows = vec![
        json!({"phase":0,"stream":0,"op":"open","path":"file","fd":1,"access":"read"}),
        json!({"phase":0,"stream":0,"op":"pwrite","fd":1,"offset":0,"len":1,"fill":7,"expected_errno":9}),
        json!({"phase":0,"stream":0,"op":"close","fd":1}),
        json!({"phase":0,"stream":0,"op":"stat","path":"missing","expected_errno":2}),
    ];
    let result = run(&s.trace(&rows), &root, &s.output(), 1);
    assert!(result.valid);
    assert_eq!(result.totals.successful, 2);
    assert_eq!(result.totals.expected_errors, 2);
    assert_eq!(result.totals.io_errors, 2);
    assert_eq!(result.totals.actual_write_bytes, 0);
    assert_eq!(result.totals.requested_write_bytes, 1);
}

#[test]
fn symlink_escape_is_rejected_without_modifying_target() {
    let s = Scratch::new();
    let root = s.root();
    let outside = s.0.join("outside");
    fs::write(&outside, b"safe").unwrap();
    std::os::unix::fs::symlink(&outside, root.join("link")).unwrap();
    let rows = vec![
        json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"link","access":"write","truncate":true,"expected_errno":40}),
    ];
    assert!(run(&s.trace(&rows), &root, &s.output(), 1).valid);
    assert_eq!(fs::read(outside).unwrap(), b"safe");
}

#[test]
fn hardlink_and_special_files_are_rejected_before_execution() {
    let s = Scratch::new();
    let root = s.root();
    let outside = s.0.join("outside");
    fs::write(&outside, b"safe").unwrap();
    fs::hard_link(&outside, root.join("file")).unwrap();
    let trace = trace::load(&s.trace(&[row("stat")]), 4096).unwrap();
    assert!(replay::run(trace, &root, &s.output(), config(1))
        .unwrap_err()
        .contains("hardlinked"));
    assert_eq!(fs::read(outside).unwrap(), b"safe");
}

#[test]
fn refuses_output_overwrite_and_output_inside_root() {
    let s = Scratch::new();
    let root = s.root();
    let rows = [json!({"phase":0,"stream":0,"op":"mkdir","path":"never-created"})];
    let trace = s.trace(&rows);
    let existing = s.output();
    fs::write(&existing, b"keep").unwrap();
    assert!(replay::run(
        trace::load(&trace, 4096).unwrap(),
        &root,
        &existing,
        config(1)
    )
    .is_err());
    assert_eq!(fs::read(existing).unwrap(), b"keep");
    assert!(!root.join("never-created").exists());
    assert!(replay::run(
        trace::load(&trace, 4096).unwrap(),
        &root,
        &root.join("output.json"),
        config(1)
    )
    .is_err());
    assert!(!root.join("never-created").exists());
}

#[test]
fn namespace_sync_truncate_and_exact_payload() {
    let s = Scratch::new();
    let root = s.root();
    let rows = vec![
        json!({"phase":0,"stream":0,"op":"mkdir","path":"d"}),
        json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"d/a","access":"read_write","create":true}),
        json!({"phase":0,"stream":0,"op":"pwrite","fd":1,"offset":0,"len":4,"data_hex":"01020304"}),
        json!({"phase":0,"stream":0,"op":"truncate","fd":1,"len":2}),
        json!({"phase":0,"stream":0,"op":"fstat","fd":1}),
        json!({"phase":0,"stream":0,"op":"fsync","fd":1}),
        json!({"phase":0,"stream":0,"op":"fdatasync","fd":1}),
        json!({"phase":0,"stream":0,"op":"close","fd":1}),
        json!({"phase":0,"stream":0,"op":"rename","from":"d/a","to":"d/b"}),
        json!({"phase":0,"stream":0,"op":"lstat","path":"d/b"}),
        json!({"phase":0,"stream":0,"op":"readdir","path":"d","expected_entries":1}),
        json!({"phase":0,"stream":0,"op":"unlink","path":"d/b"}),
        json!({"phase":0,"stream":0,"op":"rmdir","path":"d"}),
    ];
    let result = run(&s.trace(&rows), &root, &s.output(), 1);
    assert!(result.valid);
    assert_eq!(result.totals.attempted, 13);
    assert_eq!(result.totals.actual_write_bytes, 4);
    assert!(!root.join("d").exists());
}

#[test]
fn fingerprint_changes_when_content_changes_and_is_enforced() {
    let s = Scratch::new();
    let root = s.root();
    fs::write(root.join("file"), b"abc").unwrap();
    let opened = safe::Root::open(&root).unwrap();
    let hash = opened.check_initial_tree(true).unwrap().unwrap();
    let path = s.trace(&[row("stat")]);
    let text = fs::read_to_string(&path).unwrap();
    let mut lines = text.lines();
    let mut head: Value = serde_json::from_str(lines.next().unwrap()).unwrap();
    head["initial_tree_sha256"] = json!(hash);
    fs::write(
        &path,
        format!("{}\n{}\n", head, lines.collect::<Vec<_>>().join("\n")),
    )
    .unwrap();
    assert!(run(&path, &root, &s.output(), 1).initial_tree_hash_verified);
    fs::write(root.join("file"), b"def").unwrap();
    assert!(replay::run(
        trace::load(&path, 4096).unwrap(),
        &root,
        &s.output(),
        config(1)
    )
    .unwrap_err()
    .contains("fingerprint mismatch"));
}

#[test]
fn init_refuses_broad_or_nonempty_roots() {
    assert!(safe::init(Path::new("/tmp")).is_err());
    let s = Scratch::new();
    fs::write(s.0.join("valuable"), b"keep").unwrap();
    assert!(safe::init(&s.0).is_err());
    assert_eq!(fs::read(s.0.join("valuable")).unwrap(), b"keep");
}

#[test]
fn paced_requires_a_worker_per_stream() {
    let s = Scratch::new();
    let root = s.root();
    let rows = [
        json!({"phase":0,"stream":0,"op":"stat","path":"x","expected_errno":2}),
        json!({"phase":0,"stream":1,"op":"stat","path":"x","expected_errno":2}),
    ];
    let mut cfg = config(1);
    cfg.pace = true;
    assert!(replay::run(
        trace::load(&s.trace(&rows), 4096).unwrap(),
        &root,
        &s.output(),
        cfg
    )
    .unwrap_err()
    .contains("one worker per stream"));
}

#[test]
fn cli_timeout_is_failure_with_unknown_partial_counts() {
    let s = Scratch::new();
    let root = s.root();
    let trace=s.trace(&[json!({"phase":0,"stream":0,"at_ns":2_000_000_000u64,"op":"stat","path":"x","expected_errno":2})]);
    let output = s.output();
    let result = Command::new(env!("CARGO_BIN_EXE_fuse-replay"))
        .args(["run", "--trace"])
        .arg(trace)
        .args(["--root"])
        .arg(root)
        .args(["--output"])
        .arg(&output)
        .args(["--pace", "trace", "--timeout-seconds", "1"])
        .output()
        .unwrap();
    assert_eq!(result.status.code(), Some(124));
    let result: Value = serde_json::from_slice(&fs::read(output).unwrap()).unwrap();
    assert_eq!(result["termination"], "execution_deadline_exceeded");
    assert!(result["totals"].is_null());
    assert_eq!(result["valid"], false);
}

#[test]
fn cli_mismatch_is_nonzero_and_validate_never_executes() {
    let s = Scratch::new();
    let root = s.root();
    let trace = s.trace(&[row("stat")]);
    let out = Command::new(env!("CARGO_BIN_EXE_fuse-replay"))
        .arg("--trace")
        .arg(&trace)
        .output()
        .unwrap();
    assert!(out.status.success());
    let result = Command::new(env!("CARGO_BIN_EXE_fuse-replay"))
        .args(["run", "--trace"])
        .arg(trace)
        .arg("--root")
        .arg(root)
        .arg("--output")
        .arg(s.output())
        .output()
        .unwrap();
    assert_eq!(result.status.code(), Some(1));
}

#[test]
fn captured_trace_cannot_claim_synthetic_fill_is_original() {
    let s = Scratch::new();
    let p = s.trace(&[
        json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"a","access":"write","create":true}),
        json!({"phase":0,"stream":0,"op":"pwrite","fd":1,"offset":0,"len":4,"fill":0}),
        json!({"phase":0,"stream":0,"op":"close","fd":1}),
    ]);
    let text = fs::read_to_string(&p)
        .unwrap()
        .replace("synthetic", "captured");
    fs::write(&p, text).unwrap();
    assert!(trace::load(&p, 4096).is_err());
}

#[test]
fn file_descriptor_survives_rename_and_unlink() {
    let s = Scratch::new();
    let root = s.root();
    let rows = [
        json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"a","access":"read_write","create":true}),
        json!({"phase":0,"stream":0,"op":"pwrite","fd":1,"offset":0,"len":3,"data_hex":"616263"}),
        json!({"phase":0,"stream":0,"op":"rename","from":"a","to":"b"}),
        json!({"phase":0,"stream":0,"op":"unlink","path":"b"}),
        json!({"phase":0,"stream":0,"op":"pwrite","fd":1,"offset":3,"len":3,"data_hex":"646566"}),
        json!({"phase":0,"stream":0,"op":"pread","fd":1,"offset":0,"len":6,"expected_sha256":format!("{:x}",Sha256::digest(b"abcdef"))}),
        json!({"phase":0,"stream":0,"op":"close","fd":1}),
    ];
    let result = run(&s.trace(&rows), &root, &s.output(), 1);
    assert!(result.valid);
    assert_eq!(result.totals.actual_read_bytes, 6);
    assert_eq!(result.totals.actual_write_bytes, 6);
    assert_eq!(result.cleanup_close_syscalls, 0);
    assert!(!root.join("a").exists());
    assert!(!root.join("b").exists());
}

#[test]
fn readonly_iterations_count_every_request_and_byte() {
    let s = Scratch::new();
    let root = s.root();
    fs::write(root.join("file"), b"abcd").unwrap();
    let rows = [
        json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"file","access":"read"}),
        json!({"phase":1,"stream":0,"op":"pread","fd":1,"offset":0,"len":4}),
        json!({"phase":2,"stream":0,"op":"close","fd":1}),
    ];
    let mut cfg = config(4);
    cfg.iterations = 8;
    let result = replay::run(
        trace::load(&s.trace(&rows), 4096).unwrap(),
        &root,
        &s.output(),
        cfg,
    )
    .unwrap();
    assert!(result.valid);
    assert_eq!(result.operations_per_iteration, 3);
    assert_eq!(result.iterations, 8);
    assert_eq!(result.totals.attempted, 24);
    assert_eq!(result.totals.actual_read_bytes, 32);
    assert_eq!(result.totals.requested_read_bytes, 32);
    assert_eq!(result.cleanup_close_syscalls, 0);
}

#[test]
fn iterations_reject_mutation_sync_and_pacing() {
    let s = Scratch::new();
    let root = s.root();
    let mut cfg = config(1);
    cfg.iterations = 2;
    for (access, create, truncate) in [
        ("write", false, false),
        ("read", true, false),
        ("read_write", false, true),
    ] {
        let rows = [
            json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"file","access":access,"create":create,"truncate":truncate}),
            json!({"phase":0,"stream":0,"op":"close","fd":1}),
        ];
        assert!(replay::run(
            trace::load(&s.trace(&rows), 4096).unwrap(),
            &root,
            &s.output(),
            cfg
        )
        .unwrap_err()
        .contains("read-only"));
    }
    let rows = [
        json!({"phase":0,"stream":0,"op":"open","fd":1,"path":"file","access":"read"}),
        json!({"phase":0,"stream":0,"op":"fsync","fd":1}),
        json!({"phase":0,"stream":0,"op":"close","fd":1}),
    ];
    assert!(replay::run(
        trace::load(&s.trace(&rows), 4096).unwrap(),
        &root,
        &s.output(),
        cfg
    )
    .unwrap_err()
    .contains("read-only"));
    cfg.pace = true;
    assert!(replay::run(
        trace::load(&s.trace(&[row("stat")]), 4096).unwrap(),
        &root,
        &s.output(),
        cfg
    )
    .unwrap_err()
    .contains("asap"));
}

#[test]
fn fixture_fifo_is_rejected_without_blocking() {
    use std::os::unix::ffi::OsStrExt;
    let s = Scratch::new();
    let root = s.root();
    let fifo = std::ffi::CString::new(root.join("pipe").as_os_str().as_bytes()).unwrap();
    assert_eq!(unsafe { libc::mkfifo(fifo.as_ptr(), 0o600) }, 0);
    assert!(safe::Root::open(&root)
        .unwrap()
        .check_initial_tree(false)
        .unwrap_err()
        .contains("special"));
}
