#![cfg(target_os = "linux")]
pub mod replay;
pub mod safe;
pub mod trace;
pub type Result<T> = std::result::Result<T, String>;
