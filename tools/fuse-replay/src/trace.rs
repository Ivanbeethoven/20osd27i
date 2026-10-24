use crate::Result;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, HashMap},
    ffi::CString,
    fs::File,
    io::{BufRead, BufReader},
    path::Path,
    sync::Arc,
    time::Instant,
};

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Header {
    pub format: String,
    pub version: u32,
    pub payload_provenance: String,
    #[serde(default)]
    pub description: Option<String>,
    #[serde(default)]
    pub initial_tree_sha256: Option<String>,
}

#[derive(Debug, Deserialize, Clone, Copy)]
#[serde(rename_all = "snake_case")]
pub enum Access {
    Read,
    Write,
    ReadWrite,
}

#[derive(Debug, Deserialize)]
struct RawRecord {
    phase: u32,
    stream: u32,
    #[serde(default)]
    at_ns: Option<u64>,
    #[serde(default)]
    expected_errno: i32,
    #[serde(flatten)]
    op: RawOp,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum RawOp {
    Open {
        fd: u32,
        path: String,
        access: Access,
        #[serde(default)]
        create: bool,
        #[serde(default)]
        exclusive: bool,
        #[serde(default)]
        truncate: bool,
        #[serde(default = "file_mode")]
        mode: u32,
    },
    Close {
        fd: u32,
    },
    Pread {
        fd: u32,
        offset: u64,
        len: usize,
        #[serde(default)]
        expected_bytes: Option<usize>,
        #[serde(default)]
        expected_sha256: Option<String>,
    },
    Pwrite {
        fd: u32,
        offset: u64,
        len: usize,
        #[serde(default)]
        fill: Option<u8>,
        #[serde(default)]
        data_hex: Option<String>,
        #[serde(default)]
        expected_bytes: Option<usize>,
    },
    Stat {
        path: String,
    },
    Lstat {
        path: String,
    },
    Fstat {
        fd: u32,
    },
    Readdir {
        path: String,
        #[serde(default)]
        expected_entries: Option<u64>,
    },
    Mkdir {
        path: String,
        #[serde(default = "directory_mode")]
        mode: u32,
    },
    Rename {
        from: String,
        to: String,
    },
    Unlink {
        path: String,
    },
    Rmdir {
        path: String,
    },
    Fsync {
        fd: u32,
    },
    Fdatasync {
        fd: u32,
    },
    Truncate {
        fd: u32,
        len: u64,
    },
}
fn file_mode() -> u32 {
    0o644
}
fn directory_mode() -> u32 {
    0o755
}

#[derive(Debug, Clone)]
pub struct SafePath {
    pub full: CString,
    pub parent: CString,
    pub name: CString,
}
impl SafePath {
    pub fn new(path: &str, allow_root: bool) -> Result<Self> {
        if path == "." && allow_root {
            return Ok(Self {
                full: CString::new(".").unwrap(),
                parent: CString::new(".").unwrap(),
                name: CString::new(".").unwrap(),
            });
        }
        if path.is_empty()
            || path.len() > 4095
            || path.starts_with('/')
            || path.contains('\\')
            || path.contains('\0')
            || path.split('/').any(|p| {
                p.is_empty() || p == "." || p == ".." || p.len() > 255 || p == ".fuse-replay-root"
            })
        {
            return Err(format!("unsafe or reserved relative path: {path:?}"));
        }
        let (parent, name) = path.rsplit_once('/').unwrap_or((".", path));
        Ok(Self {
            full: CString::new(path).unwrap(),
            parent: CString::new(parent).unwrap(),
            name: CString::new(name).unwrap(),
        })
    }
}

#[derive(Debug)]
pub enum Op {
    Open {
        slot: usize,
        path: SafePath,
        flags: i32,
        mode: u32,
    },
    Close {
        slot: usize,
    },
    Pread {
        slot: usize,
        offset: i64,
        len: usize,
        expected_bytes: Option<usize>,
        expected_sha256: Option<[u8; 32]>,
    },
    Pwrite {
        slot: usize,
        offset: i64,
        len: usize,
        payload: usize,
        expected_bytes: Option<usize>,
    },
    Stat {
        path: SafePath,
        follow: bool,
    },
    Fstat {
        slot: usize,
    },
    Readdir {
        path: SafePath,
        expected_entries: Option<u64>,
    },
    Mkdir {
        path: SafePath,
        mode: u32,
    },
    Rename {
        from: SafePath,
        to: SafePath,
    },
    Unlink {
        path: SafePath,
        directory: bool,
    },
    Fsync {
        slot: usize,
        data_only: bool,
    },
    Truncate {
        slot: usize,
        len: i64,
    },
}
pub const OP_NAMES: [&str; 15] = [
    "open",
    "close",
    "pread",
    "pwrite",
    "stat",
    "lstat",
    "fstat",
    "readdir",
    "mkdir",
    "rename",
    "unlink",
    "rmdir",
    "fsync",
    "fdatasync",
    "truncate",
];
impl Op {
    pub fn kind(&self) -> usize {
        match self {
            Self::Open { .. } => 0,
            Self::Close { .. } => 1,
            Self::Pread { .. } => 2,
            Self::Pwrite { .. } => 3,
            Self::Stat { follow: true, .. } => 4,
            Self::Stat { follow: false, .. } => 5,
            Self::Fstat { .. } => 6,
            Self::Readdir { .. } => 7,
            Self::Mkdir { .. } => 8,
            Self::Rename { .. } => 9,
            Self::Unlink {
                directory: false, ..
            } => 10,
            Self::Unlink {
                directory: true, ..
            } => 11,
            Self::Fsync {
                data_only: false, ..
            } => 12,
            Self::Fsync {
                data_only: true, ..
            } => 13,
            Self::Truncate { .. } => 14,
        }
    }
}

#[derive(Debug)]
pub struct Record {
    pub line: u64,
    pub phase: usize,
    pub stream: usize,
    pub at_ns: u64,
    pub expected_errno: i32,
    pub op: Op,
}
pub struct Trace {
    pub header: Header,
    pub records: Vec<Record>,
    pub payloads: Vec<Arc<[u8]>>,
    pub stream_ids: Vec<u32>,
    pub handle_slots: Vec<usize>,
    pub phase_ids: Vec<u32>,
    pub max_read: usize,
    pub input_sha256: String,
    pub parse_seconds: f64,
    pub trace_bytes: u64,
}
#[derive(Default)]
struct StreamParse {
    slots: HashMap<u32, (usize, bool)>,
    at_ns: u64,
}

pub fn decode_hex(text: &str) -> Result<Vec<u8>> {
    if !text.len().is_multiple_of(2) {
        return Err("hex must contain an even number of characters".into());
    }
    text.as_bytes()
        .as_chunks::<2>()
        .0
        .iter()
        .map(|pair| {
            let a = (pair[0] as char).to_digit(16).ok_or("invalid hex")?;
            let b = (pair[1] as char).to_digit(16).ok_or("invalid hex")?;
            Ok(((a << 4) | b) as u8)
        })
        .collect()
}

pub fn load(path: &Path, max_io: usize) -> Result<Trace> {
    if max_io == 0 || max_io > 64 * 1024 * 1024 {
        return Err("max-io must be 1..67108864".into());
    }
    let begin = Instant::now();
    let file = File::open(path).map_err(|e| format!("trace open: {e}"))?;
    let trace_bytes = file.metadata().map_err(|e| e.to_string())?.len();
    let mut reader = BufReader::with_capacity(1024 * 1024, file);
    let mut line = String::new();
    let mut hasher = Sha256::new();
    if reader.read_line(&mut line).map_err(|e| e.to_string())? == 0 {
        return Err("empty trace".into());
    }
    hasher.update(line.as_bytes());
    let header: Header = serde_json::from_str(&line).map_err(|e| format!("line 1: {e}"))?;
    if header.format != "mounted-fs-replay"
        || header.version != 1
        || !["synthetic", "captured", "mixed"].contains(&header.payload_provenance.as_str())
    {
        return Err("unsupported format/version/payload_provenance".into());
    }
    if let Some(hash) = &header.initial_tree_sha256 {
        if decode_hex(hash)?.len() != 32 || hash != &hash.to_ascii_lowercase() {
            return Err("initial_tree_sha256 must be 64 lowercase hexadecimal digits".into());
        }
    }
    let mut records = Vec::new();
    let mut streams: BTreeMap<u32, StreamParse> = BTreeMap::new();
    let mut phase_ids = Vec::new();
    let mut max_read = 0;
    let mut payloads: Vec<Arc<[u8]>> = Vec::new();
    let mut fills: HashMap<u8, (usize, usize)> = HashMap::new();
    let mut line_number = 1u64;
    loop {
        line.clear();
        if reader.read_line(&mut line).map_err(|e| e.to_string())? == 0 {
            break;
        }
        hasher.update(line.as_bytes());
        line_number += 1;
        if line.len() > max_io * 2 + 16384 {
            return Err(format!("line {line_number}: record too large"));
        }
        let raw: RawRecord =
            serde_json::from_str(&line).map_err(|e| format!("line {line_number}: {e}"))?;
        if raw.expected_errno < 0 || raw.expected_errno > 4095 {
            return Err(format!(
                "line {line_number}: expected_errno outside 0..4095"
            ));
        }
        if let Some(&previous) = phase_ids.last() {
            if raw.phase < previous {
                return Err(format!("line {line_number}: phases must be nondecreasing"));
            }
        }
        if phase_ids.last().copied() != Some(raw.phase) {
            phase_ids.push(raw.phase);
        }
        if phase_ids.len() > 65536 {
            return Err("too many phases".into());
        }
        if streams.len() >= 4096 && !streams.contains_key(&raw.stream) {
            return Err("at most 4096 streams".into());
        }
        let state = streams.entry(raw.stream).or_default();
        let at_ns = raw.at_ns.unwrap_or(state.at_ns);
        if at_ns > 86_400_000_000_000 {
            return Err(format!(
                "line {line_number}: at_ns exceeds 24-hour format limit"
            ));
        }
        if at_ns < state.at_ns {
            return Err(format!("line {line_number}: at_ns decreased within stream"));
        }
        state.at_ns = at_ns;
        let required_slot = |fd: u32, state: &StreamParse| -> Result<usize> {
            state
                .slots
                .get(&fd)
                .filter(|(_, open)| *open)
                .map(|(slot, _)| *slot)
                .ok_or_else(|| format!("line {line_number}: fd {fd} is not logically open"))
        };
        let offset_len = |offset: u64, len: usize| -> Result<i64> {
            if len == 0
                || len > max_io
                || offset > i64::MAX as u64
                || offset
                    .checked_add(len as u64)
                    .is_none_or(|end| end > i64::MAX as u64)
            {
                return Err(format!(
                    "line {line_number}: invalid offset/len or max-io exceeded"
                ));
            }
            Ok(offset as i64)
        };
        let check_expected = |bytes: Option<usize>, len: usize| -> Result<Option<usize>> {
            if bytes.is_some_and(|n| n > len) || (raw.expected_errno != 0 && bytes.is_some()) {
                return Err(format!("line {line_number}: incompatible expected_bytes"));
            }
            Ok(bytes.or_else(|| (raw.expected_errno == 0).then_some(len)))
        };
        let op = match raw.op {
            RawOp::Open {
                fd,
                path,
                access,
                create,
                exclusive,
                truncate,
                mode,
            } => {
                if mode > 0o777
                    || exclusive && !create
                    || truncate && matches!(access, Access::Read)
                {
                    return Err(format!("line {line_number}: invalid open flags/mode"));
                }
                let next = state.slots.len();
                let entry = state.slots.entry(fd).or_insert((next, false));
                if entry.1 {
                    return Err(format!("line {line_number}: fd {fd} opened twice"));
                }
                entry.1 = raw.expected_errno == 0;
                let flags = match access {
                    Access::Read => libc::O_RDONLY,
                    Access::Write => libc::O_WRONLY,
                    Access::ReadWrite => libc::O_RDWR,
                } | if create { libc::O_CREAT } else { 0 }
                    | if exclusive { libc::O_EXCL } else { 0 }
                    | if truncate { libc::O_TRUNC } else { 0 }
                    | libc::O_CLOEXEC;
                Op::Open {
                    slot: entry.0,
                    path: SafePath::new(&path, false)?,
                    flags,
                    mode: if create { mode } else { 0 },
                }
            }
            RawOp::Close { fd } => {
                if raw.expected_errno != 0 {
                    return Err(
                        "error-close lifecycle is unsupported; close must expect success".into(),
                    );
                }
                let slot = required_slot(fd, state)?;
                state.slots.get_mut(&fd).unwrap().1 = false;
                Op::Close { slot }
            }
            RawOp::Pread {
                fd,
                offset,
                len,
                expected_bytes,
                expected_sha256,
            } => {
                let expected_sha256 = expected_sha256
                    .map(|hex| {
                        let bytes = decode_hex(&hex)?;
                        <[u8; 32]>::try_from(bytes)
                            .map_err(|_| "expected_sha256 must be 32 bytes".to_string())
                    })
                    .transpose()?;
                if raw.expected_errno != 0 && expected_sha256.is_some() {
                    return Err("read hash cannot accompany expected error".into());
                }
                max_read = max_read.max(len);
                Op::Pread {
                    slot: required_slot(fd, state)?,
                    offset: offset_len(offset, len)?,
                    len,
                    expected_bytes: check_expected(expected_bytes, len)?,
                    expected_sha256,
                }
            }
            RawOp::Pwrite {
                fd,
                offset,
                len,
                fill,
                data_hex,
                expected_bytes,
            } => {
                offset_len(offset, len)?;
                let payload = match (fill, data_hex) {
                    (Some(byte), None) => {
                        if header.payload_provenance == "captured" {
                            return Err(
                                "captured traces must store exact data_hex, not synthetic fill"
                                    .into(),
                            );
                        }
                        if let Some((index, size)) = fills.get_mut(&byte) {
                            *size = (*size).max(len);
                            *index
                        } else {
                            let index = payloads.len();
                            payloads.push(Arc::from([]));
                            fills.insert(byte, (index, len));
                            index
                        }
                    }
                    (None, Some(hex)) => {
                        let bytes = decode_hex(&hex)?;
                        if bytes.len() != len {
                            return Err(format!(
                                "line {line_number}: data_hex length differs from len"
                            ));
                        }
                        let index = payloads.len();
                        payloads.push(Arc::from(bytes));
                        index
                    }
                    _ => {
                        return Err(format!(
                            "line {line_number}: specify exactly one of fill or data_hex"
                        ))
                    }
                };
                Op::Pwrite {
                    slot: required_slot(fd, state)?,
                    offset: offset as i64,
                    len,
                    payload,
                    expected_bytes: check_expected(expected_bytes, len)?,
                }
            }
            RawOp::Stat { path } => Op::Stat {
                path: SafePath::new(&path, true)?,
                follow: true,
            },
            RawOp::Lstat { path } => Op::Stat {
                path: SafePath::new(&path, true)?,
                follow: false,
            },
            RawOp::Fstat { fd } => Op::Fstat {
                slot: required_slot(fd, state)?,
            },
            RawOp::Readdir {
                path,
                expected_entries,
            } => Op::Readdir {
                path: SafePath::new(&path, true)?,
                expected_entries,
            },
            RawOp::Mkdir { path, mode } => {
                if mode > 0o777 {
                    return Err("invalid mkdir mode".into());
                }
                Op::Mkdir {
                    path: SafePath::new(&path, false)?,
                    mode,
                }
            }
            RawOp::Rename { from, to } => Op::Rename {
                from: SafePath::new(&from, false)?,
                to: SafePath::new(&to, false)?,
            },
            RawOp::Unlink { path } => Op::Unlink {
                path: SafePath::new(&path, false)?,
                directory: false,
            },
            RawOp::Rmdir { path } => Op::Unlink {
                path: SafePath::new(&path, false)?,
                directory: true,
            },
            RawOp::Fsync { fd } => Op::Fsync {
                slot: required_slot(fd, state)?,
                data_only: false,
            },
            RawOp::Fdatasync { fd } => Op::Fsync {
                slot: required_slot(fd, state)?,
                data_only: true,
            },
            RawOp::Truncate { fd, len } => {
                if len > i64::MAX as u64 {
                    return Err("truncate length too large".into());
                }
                Op::Truncate {
                    slot: required_slot(fd, state)?,
                    len: len as i64,
                }
            }
        };
        records.push(Record {
            line: line_number,
            phase: phase_ids.len() - 1,
            stream: raw.stream as usize,
            at_ns,
            expected_errno: raw.expected_errno,
            op,
        });
    }
    if records.is_empty() {
        return Err("trace has no operations".into());
    }
    for (id, state) in &streams {
        if state.slots.values().any(|(_, open)| *open) {
            return Err(format!(
                "stream {id}: all successful opens require explicit close"
            ));
        }
    }
    for (byte, (index, len)) in fills {
        payloads[index] = Arc::from(vec![byte; len]);
    }
    let stream_ids: Vec<u32> = streams.keys().copied().collect();
    let handle_slots = streams.values().map(|state| state.slots.len()).collect();
    for record in &mut records {
        record.stream = stream_ids.binary_search(&(record.stream as u32)).unwrap();
    }
    Ok(Trace {
        header,
        records,
        payloads,
        stream_ids,
        handle_slots,
        phase_ids,
        max_read,
        input_sha256: format!("{:x}", hasher.finalize()),
        parse_seconds: begin.elapsed().as_secs_f64(),
        trace_bytes,
    })
}
