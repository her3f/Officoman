// SPDX-FileCopyrightText: Courier contributors
// SPDX-License-Identifier: MIT OR Apache-2.0
use super::*;

fn c(name: &str, deps: &[(&str, DepKind, bool)]) -> Crate {
    Crate { name: name.into(), deps: deps.iter().map(|(n, k, w)| Dep { name: (*n).into(), kind: *k, workspace: *w }).collect() }
}
use DepKind::*;

#[test]
fn clean_downward_graph_passes() {
    let g = [
        c("courier-time", &[("kurbo", Normal, false)]),
        c("courier-model", &[("courier-time", Normal, true)]),
        c("courier-engine", &[("courier-model", Normal, true), ("courier-testkit", Dev, true)]),
        c("courier-ui-egui", &[("courier-engine", Normal, true), ("egui", Normal, false)]),
        c("courier-cli", &[("courier-ui-egui", Normal, true)]),
    ];
    assert!(check(&g).is_empty(), "{:?}", check(&g));
}

#[test]
fn upward_dependency_flagged() {
    let v = check(&[c("courier-model", &[("courier-engine", Normal, true)])]);
    assert!(matches!(v[..], [Violation::Upward { from: 1, to: 4, .. }]));
}

#[test]
fn sideways_dependency_flagged() {
    let v = check(&[c("courier-mime", &[("courier-ical", Normal, true)])]);
    assert!(matches!(v[..], [Violation::Upward { from: 2, to: 2, .. }]));
}

#[test]
fn l0_foundation_chain_allowed_one_way() {
    assert!(check(&[c("courier-model", &[("courier-time", Normal, true)])]).is_empty());
    let v = check(&[c("courier-time", &[("courier-model", Normal, true)])]);
    assert!(matches!(v[..], [Violation::Upward { from: 0, to: 1, .. }]));
}

#[test]
fn self_dev_dependency_ignored() {
    assert!(check(&[c("courier-model", &[("courier-model", Dev, true)])]).is_empty());
}

#[test]
fn upward_dev_dependency_flagged() {
    let v = check(&[c("courier-time", &[("courier-model", Dev, true)])]);
    assert!(matches!(v[..], [Violation::Upward { kind: Dev, .. }]));
}

#[test]
fn ui_crates_below_l6_flagged() {
    for dep in ["egui", "eframe", "winit", "egui_kittest", "rfd", "bevy_ecs", "bevy"] {
        let v = check(&[c("courier-engine", &[(dep, Normal, false)])]);
        assert!(matches!(v[..], [Violation::UiBelowL6 { layer: 4, .. }]), "{dep}");
    }
    assert!(check(&[c("courier-engine", &[("egui_extras_not", Normal, false)])]).is_empty());
    assert!(!check(&[c("courier-mcp", &[("winit", Normal, false)])]).is_empty());
}

#[test]
fn unregistered_crate_is_error() {
    let v = check(&[c("courier-mystery", &[])]);
    assert!(matches!(&v[..], [Violation::Unregistered { krate }] if krate == "courier-mystery"));
    assert!(v[0].to_string().contains("register"));
}

#[test]
fn testkit_only_as_dev_dependency() {
    let v = check(&[c("courier-proto", &[("courier-testkit", Normal, true)])]);
    assert!(matches!(v[..], [Violation::TestkitAsNormalDep { .. }]));
    assert!(check(&[c("courier-proto", &[("courier-testkit", Dev, true)])]).is_empty());
    // testkit itself may use anything up to L5 but not L6 crates.
    assert!(check(&[c("courier-testkit", &[("courier-engine", Normal, true)])]).is_empty());
    assert!(!check(&[c("courier-testkit", &[("courier-ui-egui", Normal, true)])]).is_empty());
}

#[test]
fn apps_and_xtask_exempt() {
    for app in ["courier", "courier-cli", "courier-web", "xtask"] {
        assert!(check(&[c(app, &[("egui", Normal, false), ("courier-ui-egui", Normal, true)])]).is_empty());
    }
}

#[test]
fn dispatch2_is_for_the_apps_alone() {
    assert!(check(&[c("courier", &[("dispatch2", Normal, false)])]).is_empty());
    for krate in ["courier-ui-egui", "courier-engine", "courier-time"] {
        let v = check(&[c(krate, &[("dispatch2", Normal, false)])]);
        assert!(matches!(&v[..], [Violation::AppOnly { dep, .. }] if dep == "dispatch2"), "{krate}: {v:?}");
    }
}

#[test]
fn the_jmap_client_sits_at_layer_3() {
    assert_eq!(classify("courier-jmap"), Some(Class::Layer(3)));
    // It may use what is below it...
    let below =
        [("courier-time", Normal, true), ("courier-model", Normal, true), ("courier-mime", Normal, true), ("serde_json", Normal, false)];
    assert!(check(&[c("courier-jmap", &below)]).is_empty());
    // ... and nothing at its own layer or above it, in the code or in the tests.
    for (dep, kind, to) in
        [("courier-net", Normal, 3), ("courier-proto", Normal, 3), ("courier-engine", Dev, 4), ("courier-ui-egui", Normal, 6)]
    {
        let v = check(&[c("courier-jmap", &[(dep, kind, true)])]);
        assert!(matches!(v[..], [Violation::Upward { from: 3, to: t, .. }] if t == to), "{dep}: {v:?}");
    }
    // The engine and the front end may use it.
    assert!(check(&[c("courier-engine", &[("courier-jmap", Normal, true)])]).is_empty());
    assert!(check(&[c("courier-ui-egui", &[("courier-jmap", Normal, true)])]).is_empty());
}

#[test]
fn the_ews_client_sits_at_layer_3() {
    assert_eq!(classify("courier-ews"), Some(Class::Layer(3)));
    // It may use what is below it...
    let below = [("courier-model", Normal, true), ("courier-mime", Normal, true), ("quick-xml", Normal, false)];
    assert!(check(&[c("courier-ews", &below)]).is_empty());
    // ... and nothing at its own layer or above it, in the code or in the tests.
    for (dep, kind, to) in
        [("courier-net", Normal, 3), ("courier-jmap", Normal, 3), ("courier-engine", Dev, 4), ("courier-ui-egui", Normal, 6)]
    {
        let v = check(&[c("courier-ews", &[(dep, kind, true)])]);
        assert!(matches!(v[..], [Violation::Upward { from: 3, to: t, .. }] if t == to), "{dep}: {v:?}");
    }
    // The engine may use it.
    assert!(check(&[c("courier-engine", &[("courier-ews", Normal, true)])]).is_empty());
}

#[test]
fn link_uses_names_and_not_the_other_way() {
    assert_eq!(classify("courier-link"), Some(Class::Layer(0)));
    assert!(check(&[c("courier-link", &[("courier-names", Normal, true)])]).is_empty());
    // `names` stays standalone: it may use no workspace crate.
    let v = check(&[c("courier-names", &[("courier-link", Normal, true)])]);
    assert!(matches!(&v[..], [Violation::StandaloneHasWorkspaceDep { dep, .. }] if dep == "courier-link"), "{v:?}");
    // The order is for these two alone: another crate at layer 0 may not use `link`.
    let v = check(&[c("courier-time", &[("courier-link", Normal, true)])]);
    assert!(matches!(v[..], [Violation::Upward { from: 0, to: 0, .. }]), "{v:?}");
}

#[test]
fn metadata_parsing() {
    let meta: Value = serde_json::from_str(
        r#"{"packages":[
            {"name":"courier-model","dependencies":[
                {"name":"courier-time","kind":null,"path":"/x/crates/time"},
                {"name":"serde","kind":null},
                {"name":"proptest","kind":"dev"}]},
            {"name":"courier-time","dependencies":[]}
        ]}"#,
    )
    .unwrap();
    let g = from_metadata(&meta).unwrap();
    assert_eq!(g.len(), 2);
    let doc = g.iter().find(|c| c.name == "courier-model").unwrap();
    assert!(doc.deps[0].workspace && !doc.deps[1].workspace);
    assert_eq!(doc.deps[2].kind, Dev);
    assert!(check(&g).is_empty());
}

#[test]
fn the_mailbox_adapter_uses_the_reader_and_not_the_other_way() {
    assert_eq!(classify("courier-mime-model"), Some(Class::Layer(2)));
    assert!(check(&[c("courier-mime-model", &[("courier-mime", Normal, true), ("courier-model", Normal, true)])]).is_empty());
    let v = check(&[c("courier-mime", &[("courier-mime-model", Normal, true)])]);
    assert!(matches!(v[..], [Violation::Upward { from: 2, to: 2, .. }]), "{v:?}");
    // `ber` stands on its own.
    let v = check(&[c("courier-ber", &[("courier-time", Normal, true)])]);
    assert!(matches!(&v[..], [Violation::StandaloneHasWorkspaceDep { .. }]), "{v:?}");
}
