use crate::{
    safe::{self, Root},
    trace::{Op, Record, Trace, OP_NAMES},
    Result,
};
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::{
    io::Write,
    os::fd::{AsRawFd, IntoRawFd, RawFd},
    path::Path,
    sync::{Barrier, OnceLock},
    thread,
    time::{Duration, Instant},
};

#[derive(Clone, Copy)]
pub struct Config {
    pub workers: usize,
    pub pace: bool,
    pub timing: bool,
    pub timeout_seconds: u64,
    pub iterations: usize,
}
#[derive(Debug, Default, Clone, Serialize)]
pub struct Counts {
    pub attempted: u64,
    pub successful: u64,
    pub expected_errors: u64,
    pub mismatches: u64,
    pub io_errors: u64,
    pub short_reads: u64,
    pub short_writes: u64,
    pub requested_read_bytes: u64,
    pub requested_write_bytes: u64,
    pub actual_read_bytes: u64,
    pub actual_write_bytes: u64,
    pub entries_read: u64,
    pub submission_lateness_ns: u64,
    pub max_submission_lateness_ns: u64,
    pub operation_syscalls: u64,
    pub safety_open_syscalls: u64,
    pub safety_close_syscalls: u64,
    pub operation_time_ns: Option<u64>,
    pub max_operation_time_ns: Option<u64>,
}
impl Counts {
    fn merge(&mut self, rhs: &Self) {
        self.attempted += rhs.attempted;
        self.successful += rhs.successful;
        self.expected_errors += rhs.expected_errors;
        self.mismatches += rhs.mismatches;
        self.io_errors += rhs.io_errors;
        self.short_reads += rhs.short_reads;
        self.short_writes += rhs.short_writes;
        self.requested_read_bytes += rhs.requested_read_bytes;
        self.requested_write_bytes += rhs.requested_write_bytes;
        self.actual_read_bytes += rhs.actual_read_bytes;
        self.actual_write_bytes += rhs.actual_write_bytes;
        self.entries_read += rhs.entries_read;
        self.submission_lateness_ns += rhs.submission_lateness_ns;
        self.max_submission_lateness_ns = self
            .max_submission_lateness_ns
            .max(rhs.max_submission_lateness_ns);
        self.operation_syscalls += rhs.operation_syscalls;
        self.safety_open_syscalls += rhs.safety_open_syscalls;
        self.safety_close_syscalls += rhs.safety_close_syscalls;
        if let Some(n) = rhs.operation_time_ns {
            self.operation_time_ns = Some(self.operation_time_ns.unwrap_or(0) + n);
        }
        if let Some(n) = rhs.max_operation_time_ns {
            self.max_operation_time_ns = Some(self.max_operation_time_ns.unwrap_or(0).max(n));
        }
    }
}
#[derive(Debug, Serialize)]
pub struct Failure {
    pub line: u64,
    pub stream: u32,
    pub operation: &'static str,
    pub expected_errno: i32,
    pub actual_errno: i32,
    pub returned_bytes: Option<u64>,
    pub reason: &'static str,
}
#[derive(Debug, Serialize)]
pub struct KindSummary {
    pub operation: &'static str,
    #[serde(flatten)]
    pub counts: Counts,
}
#[derive(Debug, Serialize)]
pub struct Summary {
    pub format: &'static str,
    pub version: u32,
    pub iterations: usize,
    pub operations_per_iteration: usize,
    pub valid: bool,
    pub scope: &'static str,
    pub trace_sha256: String,
    pub trace_bytes: u64,
    pub payload_provenance: String,
    pub declared_initial_tree_sha256: Option<String>,
    pub initial_tree_hash_verified: bool,
    pub root: String,
    pub workers: usize,
    pub streams: usize,
    pub phases: usize,
    pub pace: &'static str,
    pub timing: &'static str,
    pub timeout_seconds: u64,
    pub parse_seconds: f64,
    pub initial_tree_scan_seconds: f64,
    pub preparation_seconds: f64,
    pub execution_seconds: f64,
    pub logical_operations_per_second: f64,
    pub correct_operations_per_second: f64,
    pub totals: Counts,
    pub operations: Vec<KindSummary>,
    pub failures: Vec<Failure>,
    pub omitted_failures: u64,
    pub cleanup_close_syscalls: u64,
}

struct WorkerResult {
    counts: Vec<Counts>,
    failures: Vec<Failure>,
    seconds: f64,
    cleanup: u64,
}
#[derive(Default)]
struct Outcome {
    errno: i32,
    bytes: Option<usize>,
    entries: u64,
    operation_syscalls: u64,
    safety_open: u64,
    safety_close: u64,
}
fn errno() -> i32 {
    std::io::Error::last_os_error()
        .raw_os_error()
        .unwrap_or(libc::EIO)
}
fn result(code: i64, out: &mut Outcome) {
    if code < 0 {
        out.errno = errno();
    }
}

fn execute(
    root: RawFd,
    record: &Record,
    fds: &mut [i32],
    buffer: &mut [u8],
    dir_buffer: &mut [u8],
    payloads: &[std::sync::Arc<[u8]>],
) -> Outcome {
    let mut out = Outcome::default();
    macro_rules! call {
        ($expr:expr) => {{
            out.operation_syscalls += 1;
            let code = unsafe { $expr };
            result(code as i64, &mut out);
            code
        }};
    }
    macro_rules! parent {
        ($path:expr) => {{
            out.safety_open += 1;
            match safe::parent(root, $path) {
                Ok(fd) => {
                    out.safety_close += 1;
                    fd
                }
                Err(e) => {
                    out.errno = e.raw_os_error().unwrap_or(libc::EIO);
                    return out;
                }
            }
        }};
    }
    match &record.op {
        Op::Open {
            slot,
            path,
            flags,
            mode,
        } => {
            out.operation_syscalls += 1;
            match safe::open_beneath(root, &path.full, *flags, *mode) {
                Ok(fd) => {
                    // A prior unexpected open success must not leak its descriptor.
                    if fds[*slot] >= 0 {
                        out.operation_syscalls += 1;
                        unsafe {
                            libc::close(fds[*slot]);
                        }
                    }
                    fds[*slot] = fd.into_raw_fd();
                }
                Err(e) => out.errno = e.raw_os_error().unwrap_or(libc::EIO),
            }
        }
        Op::Close { slot } => {
            let fd = std::mem::replace(&mut fds[*slot], -1);
            call!(libc::close(fd));
        }
        Op::Pread {
            slot, offset, len, ..
        } => {
            let n = call!(libc::pread(
                fds[*slot],
                buffer.as_mut_ptr().cast(),
                *len,
                *offset
            ));
            if n >= 0 {
                out.bytes = Some(n as usize);
            }
        }
        Op::Pwrite {
            slot,
            offset,
            len,
            payload,
            ..
        } => {
            let n = call!(libc::pwrite(
                fds[*slot],
                payloads[*payload].as_ptr().cast(),
                *len,
                *offset
            ));
            if n >= 0 {
                out.bytes = Some(n as usize);
            }
        }
        Op::Stat { path, follow } => {
            let mut stat = std::mem::MaybeUninit::<libc::stat>::uninit();
            if *follow {
                out.safety_open += 1;
                match safe::open_beneath(root, &path.full, libc::O_PATH | libc::O_CLOEXEC, 0) {
                    Ok(fd) => {
                        out.safety_close += 1;
                        call!(libc::fstat(fd.as_raw_fd(), stat.as_mut_ptr()));
                    }
                    Err(e) => out.errno = e.raw_os_error().unwrap_or(libc::EIO),
                }
            } else {
                let p = parent!(path);
                call!(libc::fstatat(
                    p.as_raw_fd(),
                    path.name.as_ptr(),
                    stat.as_mut_ptr(),
                    libc::AT_SYMLINK_NOFOLLOW
                ));
            }
        }
        Op::Fstat { slot } => {
            let mut stat = std::mem::MaybeUninit::<libc::stat>::uninit();
            call!(libc::fstat(fds[*slot], stat.as_mut_ptr()));
        }
        Op::Readdir { path, .. } => {
            out.operation_syscalls += 1;
            let dir = match safe::open_beneath(
                root,
                &path.full,
                libc::O_RDONLY | libc::O_DIRECTORY | libc::O_CLOEXEC,
                0,
            ) {
                Ok(dir) => dir,
                Err(e) => {
                    out.errno = e.raw_os_error().unwrap_or(libc::EIO);
                    return out;
                }
            };
            loop {
                let n = call!(libc::syscall(
                    libc::SYS_getdents64,
                    dir.as_raw_fd(),
                    dir_buffer.as_mut_ptr(),
                    dir_buffer.len()
                ));
                if n <= 0 {
                    break;
                }
                let mut cursor = 0;
                while cursor < n as usize {
                    // linux_dirent64 has a 19-byte fixed prefix; records are kernel supplied.
                    if cursor + 19 > n as usize {
                        out.errno = libc::EIO;
                        break;
                    }
                    let reclen =
                        u16::from_ne_bytes([dir_buffer[cursor + 16], dir_buffer[cursor + 17]])
                            as usize;
                    if reclen < 20 || cursor + reclen > n as usize {
                        out.errno = libc::EIO;
                        break;
                    }
                    let name = &dir_buffer[cursor + 19..cursor + reclen];
                    let end = name.iter().position(|b| *b == 0).unwrap_or(name.len());
                    if &name[..end] != b"."
                        && &name[..end] != b".."
                        && &name[..end] != safe::MARKER.as_bytes()
                    {
                        out.entries += 1;
                    }
                    cursor += reclen;
                }
                if out.errno != 0 {
                    break;
                }
            }
            let raw = dir.into_raw_fd();
            out.operation_syscalls += 1;
            let closed = unsafe { libc::close(raw) };
            if closed < 0 && out.errno == 0 {
                out.errno = errno();
            }
        }
        Op::Mkdir { path, mode } => {
            let p = parent!(path);
            call!(libc::mkdirat(p.as_raw_fd(), path.name.as_ptr(), *mode));
        }
        Op::Rename { from, to } => {
            let a = parent!(from);
            let b = parent!(to);
            call!(libc::renameat(
                a.as_raw_fd(),
                from.name.as_ptr(),
                b.as_raw_fd(),
                to.name.as_ptr()
            ));
        }
        Op::Unlink { path, directory } => {
            let p = parent!(path);
            call!(libc::unlinkat(
                p.as_raw_fd(),
                path.name.as_ptr(),
                if *directory { libc::AT_REMOVEDIR } else { 0 }
            ));
        }
        Op::Fsync { slot, data_only } => {
            if *data_only {
                call!(libc::fdatasync(fds[*slot]));
            } else {
                call!(libc::fsync(fds[*slot]));
            }
        }
        Op::Truncate { slot, len } => {
            call!(libc::ftruncate(fds[*slot], *len));
        }
    }
    out
}

struct Coordination<'a> {
    ready: &'a Barrier,
    go: &'a Barrier,
    phases: &'a Barrier,
    start: &'a OnceLock<Instant>,
}

fn run_worker(
    worker: usize,
    root: RawFd,
    program: &[Vec<&Record>],
    trace: &Trace,
    config: Config,
    coordination: &Coordination<'_>,
) -> WorkerResult {
    let mut handles: Vec<Vec<i32>> = trace
        .handle_slots
        .iter()
        .enumerate()
        .map(|(id, &n)| {
            if id % config.workers == worker {
                vec![-1; n]
            } else {
                Vec::new()
            }
        })
        .collect();
    let mut buffer = vec![0u8; trace.max_read.max(1)];
    let mut dir_buffer = vec![0u8; 65536];
    let mut counts = vec![Counts::default(); OP_NAMES.len()];
    if config.timing {
        for c in &mut counts {
            c.operation_time_ns = Some(0);
            c.max_operation_time_ns = Some(0);
        }
    }
    let mut failures = Vec::with_capacity(64);
    coordination.ready.wait();
    coordination.go.wait();
    let start = *coordination.start.get().unwrap();
    for _iteration in 0..config.iterations {
        for phase in program {
            for record in phase {
                if config.pace {
                    let due = Duration::from_nanos(record.at_ns);
                    let elapsed = start.elapsed();
                    if due > elapsed {
                        thread::sleep(due - elapsed);
                    }
                }
                let kind = record.op.kind();
                let count = &mut counts[kind];
                if config.pace {
                    let late = start
                        .elapsed()
                        .as_nanos()
                        .saturating_sub(record.at_ns as u128)
                        .min(u64::MAX as u128) as u64;
                    count.submission_lateness_ns =
                        count.submission_lateness_ns.saturating_add(late);
                    count.max_submission_lateness_ns = count.max_submission_lateness_ns.max(late);
                }
                let timer = config.timing.then(Instant::now);
                let out = execute(
                    root,
                    record,
                    &mut handles[record.stream],
                    &mut buffer,
                    &mut dir_buffer,
                    &trace.payloads,
                );
                if let Some(timer) = timer {
                    let ns = timer.elapsed().as_nanos().min(u64::MAX as u128) as u64;
                    *count.operation_time_ns.as_mut().unwrap() += ns;
                    let max = count.max_operation_time_ns.as_mut().unwrap();
                    *max = (*max).max(ns);
                }
                count.attempted += 1;
                count.operation_syscalls += out.operation_syscalls;
                count.safety_open_syscalls += out.safety_open;
                count.safety_close_syscalls += out.safety_close;
                count.entries_read += out.entries;
                if out.errno != 0 {
                    count.io_errors += 1;
                }
                let mut reason = if out.errno != record.expected_errno {
                    Some("errno_mismatch")
                } else {
                    None
                };
                match &record.op {
                    Op::Pread {
                        len,
                        expected_bytes,
                        expected_sha256,
                        ..
                    } => {
                        count.requested_read_bytes += *len as u64;
                        count.actual_read_bytes += out.bytes.unwrap_or(0) as u64;
                        if let Some(n) = out.bytes {
                            if n < *len {
                                count.short_reads += 1;
                            }
                            if expected_bytes.is_some_and(|expected| expected != n) {
                                reason = Some("returned_bytes_mismatch");
                            }
                            if expected_sha256.is_some_and(|expected| {
                                <[u8; 32]>::from(Sha256::digest(&buffer[..n])) != expected
                            }) {
                                reason = Some("content_sha256_mismatch");
                            }
                        }
                    }
                    Op::Pwrite {
                        len,
                        expected_bytes,
                        ..
                    } => {
                        count.requested_write_bytes += *len as u64;
                        count.actual_write_bytes += out.bytes.unwrap_or(0) as u64;
                        if let Some(n) = out.bytes {
                            if n < *len {
                                count.short_writes += 1;
                            }
                            if expected_bytes.is_some_and(|expected| expected != n) {
                                reason = Some("returned_bytes_mismatch");
                            }
                        }
                    }
                    Op::Readdir {
                        expected_entries, ..
                    } if out.errno == 0 && expected_entries.is_some_and(|n| n != out.entries) => {
                        reason = Some("directory_entry_count_mismatch");
                    }
                    _ => {}
                }
                if let Some(reason) = reason {
                    count.mismatches += 1;
                    if failures.len() < 64 {
                        failures.push(Failure {
                            line: record.line,
                            stream: trace.stream_ids[record.stream],
                            operation: OP_NAMES[kind],
                            expected_errno: record.expected_errno,
                            actual_errno: out.errno,
                            returned_bytes: out.bytes.map(|n| n as u64),
                            reason,
                        });
                    }
                } else if out.errno == 0 {
                    count.successful += 1;
                } else {
                    count.expected_errors += 1;
                }
            }
            coordination.phases.wait();
        }
    }
    let seconds = start.elapsed().as_secs_f64();
    let mut cleanup = 0;
    for stream in handles {
        for fd in stream {
            if fd >= 0 {
                unsafe {
                    libc::close(fd);
                }
                cleanup += 1;
            }
        }
    }
    WorkerResult {
        counts,
        failures,
        seconds,
        cleanup,
    }
}

pub fn run(trace: Trace, root_path: &Path, output: &Path, config: Config) -> Result<Summary> {
    if config.iterations == 0 || config.iterations > 10000 {
        return Err("iterations must be 1..10000".into());
    }
    if config.iterations > 1 {
        if config.pace {
            return Err("iterations >1 requires asap pacing".into());
        }
        for record in &trace.records {
            let readonly = match &record.op {
                Op::Open { flags, .. } => {
                    flags & (libc::O_ACCMODE | libc::O_CREAT | libc::O_TRUNC | libc::O_EXCL) == 0
                }
                Op::Close { .. }
                | Op::Pread { .. }
                | Op::Stat { .. }
                | Op::Fstat { .. }
                | Op::Readdir { .. } => true,
                _ => false,
            };
            if !readonly {
                return Err("iterations >1 only supports read-only traces; fixture is not reset between iterations".into());
            }
        }
    }
    if config.workers == 0 || config.workers > 256 {
        return Err("workers must be 1..256".into());
    }
    if config.pace && config.workers < trace.stream_ids.len() {
        return Err(
            "paced replay requires at least one worker per stream to prevent head-of-line delays"
                .into(),
        );
    }
    if config.timeout_seconds == 0 || config.timeout_seconds > 86400 {
        return Err("timeout-seconds must be 1..86400".into());
    }
    let prep = Instant::now();
    let root = Root::open(root_path)?;
    let mut output = root.reserve_output(output)?;
    let mut deadline_output = output.try_clone().map_err(|e| e.to_string())?;
    let tree = Instant::now();
    let actual_tree_hash = root.check_initial_tree(trace.header.initial_tree_sha256.is_some())?;
    let tree_seconds = tree.elapsed().as_secs_f64();
    if trace.header.initial_tree_sha256.is_some()
        && actual_tree_hash != trace.header.initial_tree_sha256
    {
        return Err("initial tree fingerprint mismatch".into());
    }
    let mut programs: Vec<Vec<Vec<&Record>>> = (0..config.workers)
        .map(|_| (0..trace.phase_ids.len()).map(|_| Vec::new()).collect())
        .collect();
    for record in &trace.records {
        programs[record.stream % config.workers][record.phase].push(record);
    }
    let ready = Barrier::new(config.workers + 1);
    let go = Barrier::new(config.workers + 1);
    let phases = Barrier::new(config.workers);
    let start = OnceLock::new();
    let fd = root.fd.as_raw_fd();
    let coordination = Coordination {
        ready: &ready,
        go: &go,
        phases: &phases,
        start: &start,
    };
    let (results, preparation_seconds) = thread::scope(|scope| {
        let mut handles = Vec::new();
        for (worker, program) in programs.iter().enumerate() {
            let trace = &trace;
            let coordination = &coordination;
            handles.push(
                scope.spawn(move || run_worker(worker, fd, program, trace, config, coordination)),
            );
        }
        ready.wait();
        let preparation_seconds = prep.elapsed().as_secs_f64();
        let (cancel_send, cancel_recv) = std::sync::mpsc::channel();
        let watchdog=scope.spawn(move||{
            if cancel_recv.recv_timeout(Duration::from_secs(config.timeout_seconds)).is_err(){
                let _=serde_json::to_writer_pretty(&mut deadline_output,&serde_json::json!({"format":"mounted-fs-replay-result","version":1,"valid":false,"termination":"execution_deadline_exceeded","timeout_seconds":config.timeout_seconds,"totals":null,"note":"Workers may be blocked; partial counts are unavailable and must not be treated as zero."}));
                let _=deadline_output.flush();
                std::process::exit(124);
            }
        });
        start.set(Instant::now()).unwrap();
        go.wait();
        let results = handles
            .into_iter()
            .map(|handle| handle.join().expect("worker panicked"))
            .collect::<Vec<_>>();
        let _ = cancel_send.send(());
        watchdog.join().unwrap();
        (results, preparation_seconds)
    });
    let mut combined = vec![Counts::default(); OP_NAMES.len()];
    let mut totals = Counts::default();
    let mut failures = Vec::new();
    let mut seconds: f64 = 0.0;
    let mut cleanup = 0;
    for result in results {
        for (i, c) in result.counts.iter().enumerate() {
            combined[i].merge(c);
        }
        seconds = seconds.max(result.seconds);
        cleanup += result.cleanup;
        failures.extend(result.failures);
    }
    for c in &combined {
        totals.merge(c);
    }
    failures.sort_unstable_by_key(|f| f.line);
    let omitted = totals.mismatches.saturating_sub(failures.len() as u64);
    let initial_tree_hash_verified = trace.header.initial_tree_sha256.is_some();
    let summary = Summary {
        format: "mounted-fs-replay-result",
        version: 1,
        iterations: config.iterations,
        operations_per_iteration: trace.records.len(),
        valid: totals.mismatches == 0,
        scope: "mounted filesystem POSIX workload; logical operations are not FUSE wire operations",
        trace_sha256: trace.input_sha256,
        trace_bytes: trace.trace_bytes,
        payload_provenance: trace.header.payload_provenance,
        declared_initial_tree_sha256: trace.header.initial_tree_sha256,
        initial_tree_hash_verified,
        root: root.path.display().to_string(),
        workers: config.workers,
        streams: trace.stream_ids.len(),
        phases: trace.phase_ids.len(),
        pace: if config.pace { "trace" } else { "asap" },
        timing: if config.timing { "op" } else { "off" },
        timeout_seconds: config.timeout_seconds,
        parse_seconds: trace.parse_seconds,
        initial_tree_scan_seconds: tree_seconds,
        preparation_seconds,
        execution_seconds: seconds,
        logical_operations_per_second: totals.attempted as f64 / seconds,
        correct_operations_per_second: (totals.successful + totals.expected_errors) as f64
            / seconds,
        totals,
        operations: combined
            .into_iter()
            .enumerate()
            .filter(|(_, c)| c.attempted > 0)
            .map(|(i, counts)| KindSummary {
                operation: OP_NAMES[i],
                counts,
            })
            .collect(),
        failures,
        omitted_failures: omitted,
        cleanup_close_syscalls: cleanup,
    };
    serde_json::to_writer_pretty(&mut output, &summary).map_err(|e| e.to_string())?;
    output.write_all(b"\n").map_err(|e| e.to_string())?;
    output.sync_all().map_err(|e| e.to_string())?;
    Ok(summary)
}
