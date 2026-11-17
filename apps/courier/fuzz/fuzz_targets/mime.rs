// SPDX-FileCopyrightText: Courier contributors
// SPDX-License-Identifier: MIT OR Apache-2.0
//! A message (and whether it is Digitally signed or Encrypted), an mbox file, a `mailto:` link and
//! encoded words, from any bytes: by the reader on its own types, and as the mailbox's messages.
#![no_main]

libfuzzer_sys::fuzz_target!(|data: &[u8]| {
    let _ = courier_mime::parse(data);
    let _ = courier_mime::parse_fetched(data);
    let _ = courier_mime::protection(data);
    let _ = courier_mime::mbox_messages(data).count();
    let _ = courier_mime_model::parse_fetched(data);
    let _ = courier_mime_model::parse_mbox(data);
    let text = String::from_utf8_lossy(data);
    let _ = courier_mime::parse_mailto(&text);
    let _ = courier_mime::decode_words(&text);
});
