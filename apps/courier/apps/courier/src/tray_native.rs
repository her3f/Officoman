// SPDX-FileCopyrightText: Courier contributors
// SPDX-License-Identifier: MIT OR Apache-2.0
//! Windows notification area and macOS menu bar, created and owned on the GUI thread.

use std::sync::Arc;

#[cfg(target_os = "windows")]
use tray_icon::menu::MenuEvent;
use tray_icon::menu::{Menu, MenuItem, PredefinedMenuItem};
use tray_icon::{MouseButton, MouseButtonState, TrayIcon, TrayIconBuilder, TrayIconEvent};

#[cfg(target_os = "windows")]
use super::{QUIT, SYNC};
use super::{SHOW, Signals};
use courier_ui_egui::i18n::{self, Lang};

pub struct Backend {
    icon: Option<TrayIcon>,
    show: MenuItem,
    sync: MenuItem,
    quit: MenuItem,
    lang: Lang,
}

impl Backend {
    pub fn start(signals: Arc<Signals>) -> Self {
        let (show, sync, quit) = courier_ui_egui::menubar::tray_text();
        let show = MenuItem::with_id("courier.tray.show", show, true, None);
        let sync = MenuItem::with_id("courier.tray.sync", sync, true, None);
        let quit = MenuItem::with_id("courier.tray.quit", quit, true, None);
        let build = || -> Result<TrayIcon, Box<dyn std::error::Error>> {
            let image = crate::app_icon().ok_or("Courier icon couldn't be read")?;
            let image = tray_icon::Icon::from_rgba(image.rgba, image.width, image.height)?;
            let menu = Menu::new();
            menu.append_items(&[&show, &sync, &PredefinedMenuItem::separator(), &quit])?;
            Ok(TrayIconBuilder::new()
                .with_icon(image)
                .with_tooltip("Courier")
                .with_menu(Box::new(menu))
                .with_menu_on_left_click(cfg!(target_os = "macos"))
                .build()?)
        };
        let icon = match build() {
            Ok(icon) => Some(icon),
            Err(e) => {
                log::warn!("system tray unavailable; closing will exit Courier: {e}");
                None
            }
        };
        signals.online(icon.is_some());
        // muda has one global menu handler. The macOS app menu dispatches our ids too.
        #[cfg(target_os = "windows")]
        {
            let signals = signals.clone();
            MenuEvent::set_event_handler(Some(move |event: MenuEvent| {
                if let Some(action) = menu_action(event.id.as_ref()) {
                    signals.send(action);
                }
            }));
        }
        let clicks = signals;
        TrayIconEvent::set_event_handler(Some(move |event| {
            if matches!(event, TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. }) {
                clicks.send(SHOW);
            }
        }));
        Self { icon, show, sync, quit, lang: i18n::current() }
    }

    pub fn poll(&mut self) {
        let lang = i18n::current();
        if self.lang != lang {
            self.lang = lang;
            let (show, sync, quit) = courier_ui_egui::menubar::tray_text();
            self.show.set_text(show);
            self.sync.set_text(sync);
            self.quit.set_text(quit);
        }
    }
    pub fn ready(&self) -> bool {
        self.icon.is_some()
    }
}

#[cfg(target_os = "windows")]
fn menu_action(id: &str) -> Option<u8> {
    match id {
        "courier.tray.show" => Some(SHOW),
        "courier.tray.quit" => Some(QUIT),
        "courier.tray.sync" => Some(SYNC),
        _ => None,
    }
}
