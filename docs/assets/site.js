"use strict";

const header = document.querySelector("header.site");
const menu = document.querySelector(".menu-toggle");
if (header && menu) {
  header.classList.add("js-menu");
  menu.hidden = false;
  const closeMenu = () => {
    header.classList.remove("menu-open");
    menu.setAttribute("aria-expanded", "false");
  };
  menu.addEventListener("click", () => {
    const expanded = menu.getAttribute("aria-expanded") !== "true";
    menu.setAttribute("aria-expanded", String(expanded));
    header.classList.toggle("menu-open", expanded);
  });
  header.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.getAttribute("aria-expanded") === "true") {
      closeMenu();
      menu.focus();
    }
  });
  header.querySelectorAll("nav a").forEach((link) => link.addEventListener("click", closeMenu));
}

const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
function selectTab(tab) {
  tabs.forEach((item) => {
    const selected = item === tab;
    item.setAttribute("aria-selected", String(selected));
    item.tabIndex = selected ? 0 : -1;
    document.getElementById(item.getAttribute("aria-controls")).hidden = !selected;
  });
}
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectTab(tab));
  tab.addEventListener("keydown", (event) => {
    let next;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = tabs.length - 1;
    if (next !== undefined) {
      event.preventDefault();
      selectTab(tabs[next]);
      tabs[next].focus();
    }
  });
});

const filters = document.querySelector(".platform-filter");
if (filters) {
  filters.hidden = false;
  const names = { all: "All platforms", windows: "Windows x64", macos: "macOS · Apple silicon + Intel", linux: "Linux x86_64" };
  filters.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      const platform = button.dataset.os;
      filters.querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      document.querySelectorAll("[data-platform]").forEach((cell) => {
        cell.hidden = platform !== "all" && cell.dataset.platform !== platform;
      });
      document.querySelector(".downloads").classList.toggle("filtered", platform !== "all");
      document.getElementById("download-status").textContent = `Showing downloads for ${names[platform]}`;
    });
  });
}
