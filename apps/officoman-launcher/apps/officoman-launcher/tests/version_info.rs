//! Reading a program's version from its VERSIONINFO, as the launcher does for a portable app it
//! has just unpacked: here, from the launcher's own exe, which `build.rs` gives a VERSIONINFO.

#![cfg(windows)]

use std::path::Path;

use officoman_launcher_core::version;
use officoman_launcher_native::detect::windows::executable_version;

#[test]
fn the_launchers_own_product_version_is_read_from_its_exe() {
    let exe = Path::new(env!("CARGO_BIN_EXE_officoman-launcher"));
    assert_eq!(executable_version(exe), version::parse(env!("CARGO_PKG_VERSION")));
}
