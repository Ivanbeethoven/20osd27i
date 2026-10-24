use crate::{trace::SafePath, Result};
use std::{
    env,
    ffi::{CStr, CString},
    fs::{self, File, OpenOptions},
    io::Write,
    os::{
        fd::{AsRawFd, FromRawFd, OwnedFd, RawFd},
        unix::{ffi::OsStrExt, fs::OpenOptionsExt},
    },
    path::{Component, Path, PathBuf},
};

pub const MARKER: &str = ".fuse-replay-root";
const MARKER_BYTES: &[u8] = b"mounted-fs-replay dedicated root v1\n";
#[repr(C)]
struct OpenHow {
    flags: u64,
    mode: u64,
    resolve: u64,
}

pub fn open_beneath(root: RawFd, path: &CStr, flags: i32, mode: u32) -> std::io::Result<OwnedFd> {
    // Linux openat2: BENEATH | NO_SYMLINKS | NO_MAGICLINKS. No insecure fallback.
    let how = OpenHow {
        flags: flags as u64,
        mode: mode as u64,
        resolve: 0x08 | 0x04 | 0x02,
    };
    let fd = unsafe {
        libc::syscall(
            libc::SYS_openat2,
            root,
            path.as_ptr(),
            &how,
            std::mem::size_of::<OpenHow>(),
        )
    } as i32;
    if fd < 0 {
        Err(std::io::Error::last_os_error())
    } else {
        Ok(unsafe { OwnedFd::from_raw_fd(fd) })
    }
}
pub fn parent(root: RawFd, path: &SafePath) -> std::io::Result<OwnedFd> {
    open_beneath(
        root,
        &path.parent,
        libc::O_PATH | libc::O_DIRECTORY | libc::O_CLOEXEC,
        0,
    )
}

fn check_root_name(root: &Path) -> Result<()> {
    if !root.is_absolute()
        || root
            .components()
            .any(|c| matches!(c, Component::ParentDir | Component::CurDir))
    {
        return Err("root must be an absolute path without . or ..".into());
    }
    if root.components().count() < 3
        || [
            "/", "/home", "/mnt", "/tmp", "/var", "/var/tmp", "/usr", "/opt", "/root", "/dev",
            "/proc", "/sys", "/run", "/media",
        ]
        .iter()
        .any(|p| root == Path::new(p))
        || env::var_os("HOME").is_some_and(|home| root == Path::new(&home))
    {
        return Err("refusing broad root; select a dedicated experiment subdirectory".into());
    }
    Ok(())
}

fn checked_canonical(root: &Path) -> Result<PathBuf> {
    check_root_name(root)?;
    let canonical = root.canonicalize().map_err(|e| format!("root: {e}"))?;
    if canonical != root {
        return Err("root and its ancestors must not contain symlinks".into());
    }
    Ok(canonical)
}

pub fn init(root: &Path) -> Result<()> {
    check_root_name(root)?;
    if !root.exists() {
        let parent = root.parent().ok_or("root needs a parent")?;
        let canonical = parent
            .canonicalize()
            .map_err(|e| format!("root parent must already exist: {e}"))?;
        if canonical != parent {
            return Err("root parent must not contain symlinks".into());
        }
        fs::create_dir(root).map_err(|e| e.to_string())?;
    }
    checked_canonical(root)?;
    if fs::read_dir(root)
        .map_err(|e| e.to_string())?
        .next()
        .is_some()
    {
        return Err(
            "init requires an empty dedicated directory; populate fixture after init".into(),
        );
    }
    let mut marker = OpenOptions::new()
        .write(true)
        .create_new(true)
        .mode(0o644)
        .custom_flags(libc::O_NOFOLLOW)
        .open(root.join(MARKER))
        .map_err(|e| e.to_string())?;
    marker.write_all(MARKER_BYTES).map_err(|e| e.to_string())?;
    marker.sync_all().map_err(|e| e.to_string())?;
    Ok(())
}

pub struct Root {
    pub path: PathBuf,
    pub fd: OwnedFd,
}
impl Root {
    pub fn open(root: &Path) -> Result<Self> {
        let path = checked_canonical(root)?;
        let croot = CString::new(root.as_os_str().as_bytes()).map_err(|e| e.to_string())?;
        let fd = unsafe {
            libc::open(
                croot.as_ptr(),
                libc::O_PATH | libc::O_DIRECTORY | libc::O_CLOEXEC | libc::O_NOFOLLOW,
            )
        };
        if fd < 0 {
            return Err(std::io::Error::last_os_error().to_string());
        }
        let fd = unsafe { OwnedFd::from_raw_fd(fd) };
        let marker = open_beneath(
            fd.as_raw_fd(),
            &CString::new(MARKER).unwrap(),
            libc::O_RDONLY | libc::O_CLOEXEC,
            0,
        )
        .map_err(|e| format!("root marker/openat2 unavailable: {e}"))?;
        let mut file = File::from(marker);
        use std::io::Read;
        let metadata = file.metadata().map_err(|e| e.to_string())?;
        if !metadata.is_file() || metadata.len() != MARKER_BYTES.len() as u64 {
            return Err("invalid root marker".into());
        }
        let mut bytes = Vec::new();
        file.read_to_end(&mut bytes).map_err(|e| e.to_string())?;
        if bytes != MARKER_BYTES {
            return Err("invalid root marker".into());
        }
        Ok(Self { path, fd })
    }
    pub fn reserve_output(&self, output: &Path) -> Result<File> {
        let parent = output
            .parent()
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or(Path::new("."));
        let parent = parent
            .canonicalize()
            .map_err(|e| format!("output parent: {e}"))?;
        let name = output.file_name().ok_or("output needs filename")?;
        let resolved = parent.join(name);
        if resolved.starts_with(&self.path) {
            return Err("output must be outside measured root".into());
        }
        OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .custom_flags(libc::O_NOFOLLOW)
            .open(&resolved)
            .map_err(|e| format!("reserve output (never overwritten): {e}"))
    }
    pub fn check_initial_tree(&self, fingerprint: bool) -> Result<Option<String>> {
        use sha2::{Digest, Sha256};
        use std::io::Read;
        use std::os::unix::fs::{FileTypeExt, MetadataExt};
        let mut stack = vec![self.path.clone()];
        let mut entries = Vec::new();
        while let Some(dir) = stack.pop() {
            for item in fs::read_dir(dir).map_err(|e| e.to_string())? {
                let item = item.map_err(|e| e.to_string())?;
                let meta = fs::symlink_metadata(item.path()).map_err(|e| e.to_string())?;
                let kind = meta.file_type();
                if kind.is_dir() {
                    stack.push(item.path());
                } else if kind.is_symlink() { /* Never followed by replay. lstat/unlink may inspect it. */
                } else if kind.is_file() {
                    if meta.nlink() != 1 {
                        return Err(format!(
                            "hardlinked fixture file refused: {}",
                            item.path().display()
                        ));
                    }
                } else if kind.is_block_device()
                    || kind.is_char_device()
                    || kind.is_fifo()
                    || kind.is_socket()
                {
                    return Err(format!(
                        "special fixture file refused: {}",
                        item.path().display()
                    ));
                }
                if fingerprint && item.path() != self.path.join(MARKER) {
                    entries.push((item.path(), meta));
                }
            }
        }
        if !fingerprint {
            return Ok(None);
        }
        entries.sort_unstable_by(|a, b| a.0.as_os_str().as_bytes().cmp(b.0.as_os_str().as_bytes()));
        let mut tree = Sha256::new();
        tree.update(b"mounted-fs-replay-tree-v1\0");
        let mut buffer = vec![0u8; 65536];
        for (path, meta) in entries {
            let relative = path
                .strip_prefix(&self.path)
                .unwrap()
                .as_os_str()
                .as_bytes();
            let kind = if meta.is_dir() {
                b'd'
            } else if meta.is_file() {
                b'f'
            } else {
                b'l'
            };
            tree.update([kind]);
            tree.update((relative.len() as u64).to_le_bytes());
            tree.update(relative);
            tree.update((meta.mode() & 0o777).to_le_bytes());
            if meta.is_file() {
                tree.update(meta.len().to_le_bytes());
                let fd = open_beneath(
                    self.fd.as_raw_fd(),
                    &CString::new(relative).map_err(|e| e.to_string())?,
                    libc::O_RDONLY | libc::O_CLOEXEC,
                    0,
                )
                .map_err(|e| e.to_string())?;
                let mut file = File::from(fd);
                let mut digest = Sha256::new();
                loop {
                    let n = file.read(&mut buffer).map_err(|e| e.to_string())?;
                    if n == 0 {
                        break;
                    }
                    digest.update(&buffer[..n]);
                }
                tree.update(digest.finalize());
            } else if meta.file_type().is_symlink() {
                let target = fs::read_link(path).map_err(|e| e.to_string())?;
                let bytes = target.as_os_str().as_bytes();
                tree.update((bytes.len() as u64).to_le_bytes());
                tree.update(bytes);
            }
        }
        Ok(Some(format!("{:x}", tree.finalize())))
    }
}
