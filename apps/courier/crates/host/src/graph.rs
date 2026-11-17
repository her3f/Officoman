// SPDX-FileCopyrightText: Courier contributors
// SPDX-License-Identifier: MIT OR Apache-2.0
//! The Microsoft Graph run for one account: what the host is asked ([`GraphRequest`]) and what it
//! brings back ([`GraphResult`]), both plain data that build for the browser, and the run itself
//! (`graph`, native only: it needs sockets): send the Outbox, tell the server what changed in the
//! calendar, read the mail (folders, delta, pages) as the request says, bring the calendar, the
//! contacts, the categories, the working hours and the Favorites down. What to ask for and when is
//! the engine's and the front end's; nothing of a message, an event or a contact is logged.

#[cfg(not(target_arch = "wasm32"))]
mod run;
/// The seams the flow tests run the whole way through with a renewal of their own (a test's
/// build only: `test-support`).
#[cfg(all(not(target_arch = "wasm32"), any(test, feature = "test-support")))]
pub use run::{Renew, RenewSend, graph_in, graph_in_with, graph_sending_with, graph_with};
#[cfg(not(target_arch = "wasm32"))]
pub use run::{graph, local_zone, open_by_address};

use courier_model::Id;

/// What the host is asked to do with Microsoft Graph for one account (the front end's `Services::graph`).
pub struct GraphRequest {
    pub account: courier_model::Account,
    /// The account's sign-in settings, with the application id filled in.
    pub oauth: courier_model::OAuth,
    /// The account's refresh token, to get a Graph token with when `access` is empty.
    pub refresh: String,
    /// A Graph access token from earlier in this session that is still good; else empty.
    pub access: String,
    /// Mail waiting in the Outbox, to send through Graph.
    pub outbox: Vec<courier_model::Message>,
    /// Also bring the calendar and the contacts down.
    pub directory: bool,
    /// A stretch of the calendar to bring down when `directory` isn't asked for (Unix seconds,
    /// from and up to): the days on screen, for a refresh that costs one question.
    pub calendar: Option<(i64, i64)>,
    /// What was made, changed or deleted in the calendar here, for the server to be told before
    /// the calendar is brought down.
    pub changes: Option<courier_model::remote::EventsUpload>,
    /// The calendars of the account to bring down, each with the series the mailbox expects in
    /// the stretch (the account's main calendar is the one with no name; it comes anyway).
    pub asks: Vec<courier_model::remote::CalendarAsk>,
    /// Also bring the working hours the mailbox has set: an extra that takes a permission of its
    /// own, without which the answer says [`GraphResult::extras_missing`].
    pub settings: bool,
    /// Also read the Favorites as Outlook has them ([`GraphResult::favorites`]).
    pub favorites: bool,
    /// A token that is obtained for this job is asked for with the permissions that reading the
    /// Favorites takes ([`GraphResult::favorites_covered`] says whether it has them). Without
    /// it, a token is asked for as it always was.
    pub favorites_scopes: bool,
    /// For an account kept in step through Microsoft Graph (R3): the folder changes to make and
    /// the folders to list ([`GraphResult::mail`]). A token obtained for this job is asked for
    /// with `Mail.ReadWrite`.
    pub mail: Option<courier_model::sync::GraphMailRequest>,
    /// Where the pieces of that mail run go as they come (R3.2): the folders, then a page at a
    /// time, each taken in by the window as it arrives. `None`: the run comes back whole in
    /// [`GraphResult::mail`].
    pub mail_pieces: Option<std::sync::mpsc::SyncSender<courier_model::sync::GraphMailResult>>,
    /// Set when the owner stops the run (Cancel): it stops after the page in hand.
    pub cancel: std::sync::Arc<std::sync::atomic::AtomicBool>,
}

/// What a [`GraphRequest`] came to. Never an error as a whole: mail goes on either way.
#[derive(Default)]
pub struct GraphResult {
    pub account: courier_model::Id,
    /// A Graph token that was obtained for this (kept for the session; its refresh token is the
    /// account's newest).
    pub tokens: Option<courier_model::sync::Tokens>,
    /// The owner hasn't allowed this program to use Graph: "Connect calendar and contacts" asks.
    pub consent_needed: bool,
    /// A shared mailbox's run had mail to send, and the owner hasn't allowed sending from shared
    /// mailboxes yet (`Mail.Send.Shared`, #70): none of it was sent (it waits); the window asks.
    pub send_consent_needed: bool,
    /// The account has calendars opened by address (#70) and the owner hasn't allowed reading
    /// other people's calendars yet (`Calendars.ReadWrite.Shared`): they weren't read; the
    /// window asks.
    pub shared_calendars_consent_needed: bool,
    /// The Graph token that was handed in is no longer taken.
    pub token_refused: bool,
    /// The sign-in itself was refused when a token was asked for (it has run out, or was taken
    /// back): the owner has to sign in again.
    pub sign_in_refused: bool,
    /// Outbox messages that were sent (Microsoft files the Sent Items copy itself).
    pub sent: Vec<Id>,
    /// Outbox messages that must not be sent another way in this run: whether they went is not
    /// known, or the server said to try later.
    pub held: Vec<Id>,
    /// Those of `held` whose answer was lost after they were handed over (a timeout, a broken
    /// connection, an answer that doesn't say): they may have gone, and are held for the owner
    /// (AU3-26). The rest of `held` didn't go, and goes with the next run.
    pub unsure: Vec<Id>,
    pub events: Option<courier_model::remote::EventsDownload>,
    pub contacts: Option<courier_model::remote::ContactsDownload>,
    /// What the server said to the calendar changes it was told ([`GraphRequest::changes`]).
    pub uploaded: Option<courier_model::remote::EventsUploaded>,
    pub errors: Vec<String>,
    /// The same stretch of the account's other calendars.
    pub more_events: Vec<courier_model::remote::EventsDownload>,
    /// The account's calendars and the groups they are listed in, when they were asked for.
    pub calendars: Option<courier_model::remote::CalendarsDownload>,
    /// The mailbox's own categories with their colours, when they could be read.
    pub categories: Option<courier_model::remote::CategoriesDownload>,
    /// The sign-in covers everything but an optional extra (reading the mailbox's category
    /// list): all else works, and "Connect calendar and contacts" would add it.
    pub extras_missing: bool,
    /// The working hours the mailbox has set, when they were asked for and could be read.
    pub mailbox_hours: Option<courier_engine::cmd::calendar_settings::MailboxHours>,
    /// The Favorites as Outlook has them, when they were asked for: the list, or how the read
    /// went instead (the mailbox has none, the sign-in doesn't cover it, it failed).
    pub favorites: Option<courier_model::remote::FavoritesDownload>,
    /// Why reading the Favorites failed, in a few plain words for the folder pane; no name
    /// and no id in it.
    pub favorites_error: String,
    /// When a token was obtained for this job: whether it is good for reading the Favorites
    /// (it was asked for with that, and the sign-in covers it).
    pub favorites_covered: Option<bool>,
    /// What the folders came to, when [`GraphRequest::mail`] asked.
    pub mail: Option<courier_model::sync::GraphMailResult>,
}
