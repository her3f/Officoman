// SPDX-FileCopyrightText: Courier contributors
// SPDX-License-Identifier: MIT OR Apache-2.0
//! Hostile DAV XML is bounded and never panics.
#![no_main]
libfuzzer_sys::fuzz_target!(|data: &[u8]| {
    if let Ok(root) = courier_dav::xml::parse(data) {
        let _ = courier_dav::xml::properties(&root).count();
    }
});
