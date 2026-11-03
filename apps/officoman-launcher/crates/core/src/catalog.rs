//! The Craft App Suite: the seventeen apps the launcher knows about.
//!
//! The list is data so a later version can fetch it from an API; [`SUITE`] is the built-in copy.
//!
//! Text here is English, the source the UI translates from: each `tagline` has a catalog row
//! keyed by the app id (`tr_ctx(app.id, app.tagline)` in `ui-egui`).

/// Who makes an app. Official apps live under [`GITHUB_OWNER`]; a community app is maintained
/// outside Officoman and is labelled as such wherever it is shown.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AppKind {
    Official,
    Community,
}

/// One app in the suite.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct CraftApp {
    /// Machine name: repo, binary, package and asset stem (`photocraft`).
    pub id: &'static str,
    /// Display name (`PhotoCraft`).
    pub name: &'static str,
    /// What it's for, in a few words (English; the UI translates it by app id).
    pub tagline: &'static str,
    /// Brand colour (sRGB), for surfaces: her3f.github.io/officoman's `--app`.
    pub color: [u8; 3],
    /// The brand colour for text on a light background (the site's light `--app-ink`).
    pub ink_light: [u8; 3],
    /// The brand colour for text on a dark background (the site's dark `--app-ink`).
    pub ink_dark: [u8; 3],
    /// GitHub `owner/repo`.
    pub repo: &'static str,
    /// Older names its release assets may carry (PdfCraft shipped as PrintCraft until 0.2.1).
    pub former_ids: &'static [&'static str],
    /// Older display names its installers registered (PdfCraft's MSI said PrintCraft until 0.2.1).
    pub former_names: &'static [&'static str],
    pub kind: AppKind,
    /// Who publishes it, as the card's byline shows it (`Officoman`, `Tangency Labs`).
    pub publisher: &'static str,
    /// The publisher its Windows installer names, when it isn't Officoman's (`Officoman`).
    pub msi_publisher: Option<&'static str>,
    /// The bundle id when it isn't `io.github.her3f.<id>` (a community app brings its own).
    pub bundle: Option<&'static str>,
    /// Older bundle ids its Flatpak shipped under (SolidCraft was `io.github.her3f.solidcraft`).
    pub former_bundles: &'static [&'static str],
    /// Its website, when it isn't a page on her3f.github.io/officoman (a community app has its own).
    pub site: Option<&'static str>,
    /// The Apple Developer team whose Developer ID signature its macOS build must carry. `None`
    /// while those builds carry no signature the launcher can check: it then opens a copy that's
    /// there and links to the releases, but installs nothing.
    pub mac_team: Option<&'static str>,
}

impl CraftApp {
    /// `io.github.her3f.<id>`: macOS bundle id, Flatpak id and Linux desktop-file id.
    pub fn bundle_id(&self) -> String {
        self.bundle.map_or_else(|| format!("io.github.her3f.{}", self.id), str::to_string)
    }

    pub fn releases_url(&self) -> String {
        format!("https://github.com/{}/releases", self.repo)
    }

    pub fn repo_url(&self) -> String {
        format!("https://github.com/{}", self.repo)
    }

    /// The app's website: its page on her3f.github.io/officoman, or a community app's own site.
    pub fn website(&self) -> String {
        self.site.map_or_else(|| format!("https://her3f.github.io/officoman/apps/{}", self.id), str::to_string)
    }

    /// Whether the launcher installs this app from a `kind` package.
    pub fn installs(&self, kind: crate::PackageKind) -> bool {
        kind != crate::PackageKind::Dmg || self.mac_team.is_some()
    }

    /// Bundle ids this app may be installed under, current first.
    pub fn bundle_ids(&self) -> impl Iterator<Item = String> + '_ {
        std::iter::once(self.bundle_id()).chain(self.former_bundles.iter().map(|b| b.to_string()))
    }

    /// Asset stems this app's releases may use, current first.
    pub fn stems(&self) -> impl Iterator<Item = &'static str> + '_ {
        std::iter::once(self.id).chain(self.former_ids.iter().copied())
    }

    /// Display names this app's installers may have registered, current first.
    pub fn names(&self) -> impl Iterator<Item = &'static str> + '_ {
        std::iter::once(self.name).chain(self.former_names.iter().copied())
    }

    pub fn by_id(id: &str) -> Option<&'static CraftApp> {
        SUITE.iter().find(|a| a.id == id)
    }
}

const fn app(
    id: &'static str,
    name: &'static str,
    tagline: &'static str,
    [color, ink_light, ink_dark]: [[u8; 3]; 3],
    repo: &'static str,
) -> CraftApp {
    CraftApp {
        id,
        name,
        tagline,
        color,
        ink_light,
        ink_dark,
        repo,
        former_ids: &[],
        former_names: &[],
        kind: AppKind::Official,
        publisher: "Officoman",
        msi_publisher: Some("Officoman"),
        bundle: None,
        former_bundles: &[],
        site: None,
        // These builds are not code-signed, so macOS installs are not offered.
        mac_team: None,
    }
}

/// The Craft App Suite, in display order matching her3f.github.io/officoman, then the community apps:
pub const SUITE: [CraftApp; 4] = [
    app(
        "nib",
        "Nib",
        "Documents",
        [[0x33, 0x43, 0x9b], [0x24, 0x2f, 0x70], [0x6b, 0x7d, 0xd6]],
        "her3f/officoman",
    ),
    app(
        "tally",
        "Tally",
        "Spreadsheets",
        [[0x1f, 0x7a, 0x6b], [0x15, 0x57, 0x4c], [0x4f, 0xc2, 0xae]],
        "her3f/officoman",
    ),
    app(
        "podium",
        "Podium",
        "Presentations",
        [[0xb4, 0x50, 0x2e], [0x8a, 0x3a, 0x1f], [0xe8, 0x8a, 0x63]],
        "her3f/officoman",
    ),
    app(
        "sheaf",
        "Sheaf",
        "PDF",
        [[0x6b, 0x4e, 0x9e], [0x4d, 0x37, 0x76], [0xa5, 0x8a, 0xd6]],
        "her3f/officoman",
    ),
];

/// The Apple Developer team that signs every official Craft App and Officoman Launcher (Learning
/// Machines LLC): the macOS side of the Windows publisher check.
pub const OFFICOMAN_TEAM_ID: &str = "DJ6XS33FX8";

/// Officoman's website.
pub const WEBSITE_URL: &str = "https://her3f.github.io/officoman";
/// The GitHub account every official Craft App's repository lives under. The release feed can
/// only move an app within it; a community app installs from its own repo, pinned in [`SUITE`].
pub const GITHUB_OWNER: &str = "her3f";
/// Officoman on GitHub: every Craft App's source.
pub const GITHUB_URL: &str = "https://github.com/her3f/officoman";
/// Officoman's social accounts: (service, URL). Shown as small icons, less prominent than Discord.
pub const SOCIAL: [(&str, &str); 0] = [];

/// The Officoman community on Discord.
pub const DISCORD_URL: &str = "https://github.com/her3f/officoman/discussions";
/// Deep link into the Discord application for the Officoman server invite.
pub const DISCORD_APP_URL: &str = "discord://-/invite/officoman";

/// Officoman Launcher itself, described like a Craft App so it can update itself with the same
/// machinery (asset names `officoman-launcher-<ver>-…`, bundle id `io.github.her3f.officoman-launcher`,
/// `Officoman Launcher.app`). Not part of [`SUITE`].
pub const LAUNCHER: CraftApp = app(
    "officoman-launcher",
    "Officoman Launcher",
    "Installs and updates the Craft App Suite",
    [[0x0b, 0x0b, 0x0c], [0x0b, 0x0b, 0x0c], [0xf2, 0xf1, 0xee]],
    "her3f/officoman",
);

/// The launcher's own repo, checked so it can say when a newer launcher is out.
pub const LAUNCHER_REPO: &str = "her3f/officoman";
/// The launcher's own asset stem.
pub const LAUNCHER_ID: &str = "officoman-launcher";

/// A Craft App's 128 px icon (PNG), as copied from its repo into `assets/app-icons`: the UI
/// draws it, and the Linux install puts it in the desktop menu.
pub fn app_icon_png(id: &str) -> Option<&'static [u8]> {
    Some(match id {
        "nib" => include_bytes!("../../../assets/app-icons/nib.png"),
        "tally" => include_bytes!("../../../assets/app-icons/tally.png"),
        "podium" => include_bytes!("../../../assets/app-icons/podium.png"),
        "sheaf" => include_bytes!("../../../assets/app-icons/sheaf.png"),
        _ => return None,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_app_has_its_icon() {
        for app in &SUITE {
            let png = app_icon_png(app.id).unwrap_or_else(|| panic!("no icon for {}", app.id));
            assert!(png.starts_with(b"\x89PNG\r\n\x1a\n"), "{} icon isn't a PNG", app.id);
        }
        assert!(app_icon_png("notacraft").is_none());
    }

    /// Every catalog entry must have a distinct lookup key.
    #[test]
    fn suite_has_seventeen_apps_with_unique_ids() {
        assert_eq!(SUITE.len(), 17);
        let mut ids: Vec<_> = SUITE.iter().map(|a| a.id).collect();
        ids.sort_unstable();
        ids.dedup();
        assert_eq!(ids.len(), SUITE.len());
        for a in &SUITE {
            // `Craft Anything` is `craft-anything`.
            assert_eq!(a.name.to_lowercase().replace(' ', "-"), a.id);
            match a.kind {
                AppKind::Official => assert_eq!(a.repo, format!("storytold/{}", a.id)),
                AppKind::Community => assert!(!a.repo.starts_with("storytold/"), "{} is community", a.id),
            }
        }
    }

    #[test]
    fn solidcraft_is_a_community_app_with_its_own_bundle_id() {
        let sc = CraftApp::by_id("solidcraft").unwrap();
        assert_eq!(sc.kind, AppKind::Community);
        assert_eq!(sc.repo, "tangency-labs/solidcraft");
        assert_eq!(sc.bundle_id(), "io.tangencylabs.solidcraft");
        assert_eq!(sc.bundle_ids().collect::<Vec<_>>(), ["io.tangencylabs.solidcraft", "io.github.her3f.solidcraft", "io.github.her3f.solvecraft"]);
        assert_eq!(CraftApp::by_id("gridcraft").unwrap().bundle_id(), "io.github.her3f.gridcraft");
        assert_eq!(CraftApp::by_id("gridcraft").unwrap().kind, AppKind::Official);
        assert_eq!(sc.website(), "https://solidcraft.io");
        assert!(sc.installs(crate::PackageKind::Dmg) && sc.installs(crate::PackageKind::Msi) && sc.installs(crate::PackageKind::Flatpak));
        assert_eq!(sc.mac_team, Some("G5QA5U5X2S"));
        assert_eq!(CraftApp::by_id("gridcraft").unwrap().mac_team, Some(OFFICOMAN_TEAM_ID));
    }

    #[test]
    fn texturecraft_is_an_official_app() {
        let app = CraftApp::by_id("texturecraft").unwrap();
        assert_eq!(app.kind, AppKind::Official);
        assert_eq!(app.repo, "storytold/texturecraft");
        assert_eq!(app.bundle_id(), "io.github.her3f.texturecraft");
        assert_eq!(app.website(), "https://her3f.github.io/officoman/apps/texturecraft");
        assert_eq!(app.mac_team, Some(OFFICOMAN_TEAM_ID));
    }

    #[test]
    fn materialcraft_is_an_official_app() {
        let app = CraftApp::by_id("materialcraft").unwrap();
        assert_eq!(app.kind, AppKind::Official);
        assert_eq!(app.repo, "storytold/materialcraft");
        assert_eq!(app.bundle_id(), "io.github.her3f.materialcraft");
        assert_eq!(app.website(), "https://github.com/storytold/materialcraft");
        assert_eq!(app.mac_team, Some(OFFICOMAN_TEAM_ID));
    }

    #[test]
    fn craft_anything_is_an_official_app() {
        let ca = CraftApp::by_id("craft-anything").unwrap();
        assert_eq!(ca.kind, AppKind::Official);
        assert_eq!(ca.repo, "storytold/craft-anything");
        assert_eq!(ca.bundle_id(), "io.github.her3f.craft-anything");
        assert_eq!(ca.website(), "https://her3f.github.io/officoman/apps/craft-anything");
        assert_eq!(ca.mac_team, Some(OFFICOMAN_TEAM_ID));
    }

    #[test]
    fn pdfcraft_also_answers_to_printcraft() {
        let pdf = CraftApp::by_id("pdfcraft").unwrap();
        assert_eq!(pdf.stems().collect::<Vec<_>>(), ["pdfcraft", "printcraft"]);
        assert_eq!(pdf.names().collect::<Vec<_>>(), ["PdfCraft", "PrintCraft"]);
        assert_eq!(pdf.website(), "https://her3f.github.io/officoman/apps/pdfcraft");
        assert_eq!(CraftApp::by_id("wordcraft").unwrap().website(), "https://her3f.github.io/officoman/apps/wordcraft");
    }
}
