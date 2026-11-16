/* Folio 通讯录 — front-end controller
   Plain ES2020, no build step. All API data is rendered through text-safe
   helpers (esc) or textContent so contact data can never inject markup. */

(() => {
  "use strict";

  /* ------------------------------------------------------------- icons ---- */

  const ICONS = {
    plus: '<path d="M12 5v14M5 12h14"/>',
    users:
      '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    star: '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1L3.2 9.5l6.1-.9Z"/>',
    database:
      '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.3-3.3"/>',
    upload:
      '<path d="M12 16V4m0 0L7 9m5-5 5 5"/><path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>',
    download:
      '<path d="M12 4v12m0 0 5-5m-5 5-5-5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>',
    grid:
      '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    close: '<path d="M18 6 6 18M6 6l12 12"/>',
    edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    trash:
      '<path d="M3 6h18M8 6V4h8v2"/><path d="M19 6l-1 15H6L5 6"/><path d="M10 11v6M14 11v6"/>',
    copy:
      '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
    phone:
      '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2Z"/>',
    mail: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    chat: '<path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.4 8.6 8.6 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 1 1 16.1-3.8Z"/>',
    qq: '<circle cx="12" cy="11" r="6"/><path d="m15.2 14.6 3.3 4.4"/><path d="M9.5 10h.01M14.5 10h.01"/>',
    mapPin:
      '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    link:
      '<path d="M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7-7l-1.2 1.2"/><path d="M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7 7l1.2-1.2"/>',
    check: '<path d="m20 6-11 11-5-5"/>',
    alert: '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
    file:
      '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>',
    arrowLeft: '<path d="M19 12H5m0 0 7 7m-7-7 7-7"/>',
    chevronRight: '<path d="m9 18 6-6-6-6"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    refresh: '<path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 21v-5h5"/>',
  };

  const svgIcon = (name) =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;

  const icon = (name, className = "") => `<span class="icon ${className}">${svgIcon(name)}</span>`;

  const KIND_META = {
    phone: { label: "电话", icon: "phone", placeholder: "手机号或座机，如 138 0013 8000" },
    email: { label: "邮箱", icon: "mail", placeholder: "name@example.com" },
    wechat: { label: "微信", icon: "chat", placeholder: "微信号" },
    qq: { label: "社交", icon: "qq", placeholder: "社交账号" },
    address: { label: "地址", icon: "mapPin", placeholder: "省 / 市 / 区 / 详细地址" },
    other: { label: "其他", icon: "link", placeholder: "账号、主页或其它联系方式" },
  };

  /* ----------------------------------------------------------- helpers ---- */

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const esc = (value) =>
    String(value ?? "").replace(/[&<>"']/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[ch]);

  const PALETTES = [
    ["#0f766e", "#134e4a"],
    ["#a16207", "#713f12"],
    ["#4338ca", "#312e81"],
    ["#be185d", "#831843"],
    ["#0369a1", "#164e63"],
    ["#4d7c0f", "#365314"],
    ["#7c3aed", "#4c1d95"],
    ["#b45309", "#7c2d12"],
  ];

  function palette(name) {
    let hash = 0;
    for (const ch of String(name)) hash = (hash * 31 + ch.codePointAt(0)) >>> 0;
    return PALETTES[hash % PALETTES.length];
  }

  function initials(name) {
    const text = String(name || "?").trim();
    if (!text) return "?";
    if (/^[A-Za-z]/.test(text)) {
      return text
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0].toUpperCase())
        .join("");
    }
    return text.slice(0, 1);
  }

  function avatar(name, extra = "") {
    const [a, b] = palette(name);
    return `<div class="avatar ${extra}" style="--av1:${a};--av2:${b}" aria-hidden="true">${esc(initials(name))}</div>`;
  }

  function formatDate(iso) {
    if (!iso) return "";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return String(iso);
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function contactSubline(contact) {
    return [contact.company, contact.jobTitle].filter(Boolean).join(" · ");
  }

  function kindMeta(kind) {
    return KIND_META[kind] || KIND_META.other;
  }

  function methodPlaceholder(kind) {
    return kindMeta(kind).placeholder;
  }

  function debounce(fn, delay) {
    let timer = null;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }

  /* ------------------------------------------------------------- state ---- */

  const state = {
    view: "all",
    tag: null,
    query: "",
    layout: "list",
    contacts: [],
    meta: { tags: [], stats: { total: 0, bookmarked: 0, methods: 0, tags: 0 } },
    loading: true,
    requestSeq: 0,
    activeId: null,
    importData: null,
  };

  const elements = {
    area: $("#contact-area"),
    pageTitle: $("#page-title"),
    pageSub: $("#page-sub"),
    search: $("#search"),
    scrim: $("#scrim"),
    drawer: $("#drawer"),
    sidebar: $("#sidebar"),
    modalRoot: $("#modal-root"),
    toastRoot: $("#toast-root"),
    filterSlot: $("#filter-slot"),
    resultCount: $("#result-count"),
    tagList: $("#tag-list"),
    navAll: $("#nav-all-count"),
    navStar: $("#nav-star-count"),
    methodCount: $("#method-count"),
    tagTotal: $("#tag-total"),
  };

  class ApiError extends Error {
    constructor(message, fields = {}, status = 400) {
      super(message);
      this.fields = fields;
      this.status = status;
    }
  }

  async function api(path, options = {}) {
    const isForm = options.body instanceof FormData;
    const headers = { ...(isForm ? {} : { "Content-Type": "application/json" }), ...(options.headers || {}) };
    const response = await fetch(path, { ...options, headers });
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : null;
    if (!response.ok) {
      throw new ApiError(
        payload?.error?.message || `请求失败（${response.status}）`,
        payload?.error?.fields || {},
        response.status,
      );
    }
    return payload;
  }

  /* ------------------------------------------------------------ toasts ---- */

  function toast(message, type = "info") {
    const node = document.createElement("div");
    node.className = `toast${type === "error" ? " is-error" : type === "success" ? " is-success" : ""}`;
    const iconName = type === "error" ? "alert" : "check";
    node.innerHTML = `${icon(iconName)}<span>${esc(message)}</span>`;
    elements.toastRoot.appendChild(node);
    setTimeout(() => {
      node.style.opacity = "0";
      node.style.transform = "translateY(6px)";
      node.style.transition = "opacity .2s ease, transform .2s ease";
      setTimeout(() => node.remove(), 220);
    }, 3200);
  }

  /* -------------------------------------------------------------- icons ---- */

  function hydrateIcons(root = document) {
    $$("[data-icon]", root).forEach((node) => {
      if (node.dataset.iconReady) return;
      node.innerHTML = svgIcon(node.dataset.icon);
      node.dataset.iconReady = "1";
    });
  }

  /* ------------------------------------------------------------- fetch ---- */

  async function loadData({ quiet = false } = {}) {
    const seq = ++state.requestSeq;
    if (!quiet) {
      state.loading = true;
      renderContacts();
    }
    const params = new URLSearchParams();
    if (state.query) params.set("q", state.query);
    if (state.tag) params.set("tag", state.tag);
    if (state.view === "bookmarked") params.set("bookmarked", "1");
    params.set("_", String(Date.now()));

    try {
      const [list, meta] = await Promise.all([
        api(`/api/contacts?${params.toString()}`),
        api("/api/meta"),
      ]);
      if (seq !== state.requestSeq) return;
      state.contacts = list.contacts;
      state.meta = meta;
      state.loading = false;
      renderAll();
    } catch (error) {
      if (seq !== state.requestSeq) return;
      state.loading = false;
      renderError(error);
      toast(error.message || "加载失败", "error");
    }
  }

  /* ------------------------------------------------------------ render ---- */

  function renderAll() {
    renderMeta();
    renderHeader();
    renderFilters();
    renderContacts();
    syncDrawer();
  }

  function renderMeta() {
    const stats = state.meta.stats || {};
    elements.navAll.textContent = stats.total ?? 0;
    elements.navStar.textContent = stats.bookmarked ?? 0;
    elements.methodCount.textContent = `${stats.methods ?? 0} 条联系方式`;
    elements.tagTotal.textContent = (state.meta.tags || []).length;
    renderTags();
  }

  function renderTags() {
    const tags = state.meta.tags || [];
    if (!tags.length) {
      elements.tagList.innerHTML = '<div class="tag-empty">还没有标签</div>';
      return;
    }
    elements.tagList.innerHTML = tags
      .map(
        (tag) => `<button type="button" class="tag-pill${state.tag === tag.name ? " is-active" : ""}" data-tag="${esc(tag.name)}" title="筛选标签：${esc(tag.name)}">
          <span>${esc(tag.name)}</span><b>${tag.count}</b>
        </button>`,
      )
      .join("");
  }

  function renderHeader() {
    const stats = state.meta.stats || {};
    let title = "全部联系人";
    if (state.view === "bookmarked") title = "书签";
    else if (state.tag) title = `标签 · ${state.tag}`;
    elements.pageTitle.textContent = title;

    const current = state.contacts.length;
    if (state.query || state.tag || state.view === "bookmarked") {
      elements.pageSub.textContent = `当前筛选 ${current} 位 · 通讯录共 ${stats.total ?? 0} 位`;
    } else {
      elements.pageSub.textContent = `共 ${stats.total ?? 0} 位联系人 · ${stats.bookmarked ?? 0} 位已加书签`;
    }

    $$(".nav-item").forEach((button) => {
      const view = button.dataset.view;
      button.classList.toggle(
        "is-active",
        view === "all" ? state.view === "all" : state.view === "bookmarked",
      );
    });
  }

  function renderFilters() {
    const chips = [];
    if (state.query) {
      chips.push(`<span class="filter-chip">搜索 <strong>${esc(state.query)}</strong>
        <button type="button" data-action="clear-search" aria-label="清除搜索">${icon("close")}</button></span>`);
    }
    if (state.tag) {
      chips.push(`<span class="filter-chip">标签 <strong>${esc(state.tag)}</strong>
        <button type="button" data-action="clear-tag" aria-label="清除标签筛选">${icon("close")}</button></span>`);
    }
    elements.filterSlot.innerHTML = chips.join("");
    elements.resultCount.textContent = `${state.contacts.length} 位联系人`;
  }

  function renderContacts() {
    elements.area.setAttribute("aria-busy", state.loading ? "true" : "false");
    if (state.loading) {
      renderSkeleton();
      return;
    }
    if (!state.contacts.length) {
      renderEmpty();
      return;
    }
    if (state.layout === "grid") {
      elements.area.innerHTML = `<div class="contact-grid">${state.contacts.map(renderCard).join("")}</div>`;
      markActiveRows();
      return;
    }

    const bookmarked = state.contacts.filter((contact) => contact.bookmarked);
    const others = state.contacts.filter((contact) => !contact.bookmarked);
    let html = "";
    if (state.view === "all" && bookmarked.length && others.length) {
      html += groupHead("书签", bookmarked.length);
      html += `<div class="contact-list">${bookmarked.map(renderRow).join("")}</div>`;
      html += groupHead("其他联系人", others.length);
      html += `<div class="contact-list">${others.map(renderRow).join("")}</div>`;
    } else {
      html = `<div class="contact-list">${state.contacts.map(renderRow).join("")}</div>`;
    }
    elements.area.innerHTML = html;
    markActiveRows();
  }

  function groupHead(label, count) {
    return `<div class="group-head">${esc(label)}<span class="count">${count}</span></div>`;
  }

  function methodChips(contact, limit = 3) {
    if (!contact.methods.length) {
      return '<span class="method-chip is-more">暂无联系方式</span>';
    }
    const shown = contact.methods.slice(0, limit);
    const extras = contact.methods.length - shown.length;
    return (
      shown
        .map(
          (method) => `<span class="method-chip" title="${esc(method.value)}">
            ${icon(kindMeta(method.kind).icon)}<span>${esc(method.value)}</span>
          </span>`,
        )
        .join("") + (extras > 0 ? `<span class="method-chip is-more">+${extras}</span>` : "")
    );
  }

  function starButton(contact, extraClass = "") {
    return `<button type="button" class="star-btn ${contact.bookmarked ? "is-on" : ""} ${extraClass}"
      data-star="${contact.id}" aria-pressed="${contact.bookmarked}"
      aria-label="${contact.bookmarked ? "移出书签" : "加入书签"}" title="${contact.bookmarked ? "移出书签" : "加入书签"}">
      ${icon("star")}
    </button>`;
  }

  function tagMarkup(tags) {
    if (!tags.length) return "";
    return `<span class="mini-tags">${tags
      .slice(0, 2)
      .map((tag) => `<span class="mini-tag">${esc(tag)}</span>`)
      .join("")}</span>`;
  }

  function renderRow(contact) {
    const sub = contactSubline(contact);
    return `<article class="contact-row" data-id="${contact.id}" tabindex="0" role="button"
      aria-label="查看 ${esc(contact.name)} 的联系方式">
      ${avatar(contact.name)}
      <div class="contact-identity">
        <div class="contact-name">
          <span class="name-text">${esc(contact.name)}</span>
          ${contact.bookmarked ? `<span class="star-mark">${icon("star")}</span>` : ""}
        </div>
        <div class="contact-sub">${esc(sub || "未填写公司或职位")}${tagMarkup(contact.tags)}</div>
      </div>
      <div class="method-chips">${methodChips(contact)}</div>
      <div class="row-side">${starButton(contact)}</div>
    </article>`;
  }

  function renderCard(contact) {
    const sub = contactSubline(contact);
    return `<article class="contact-card" data-id="${contact.id}" tabindex="0" role="button"
      aria-label="查看 ${esc(contact.name)} 的联系方式">
      <div class="card-top">
        ${avatar(contact.name)}
        <div class="contact-identity">
          <div class="contact-name">
            <span class="name-text">${esc(contact.name)}</span>
            ${contact.bookmarked ? `<span class="star-mark">${icon("star")}</span>` : ""}
          </div>
          <div class="contact-sub">${esc(sub || "未填写公司或职位")}</div>
        </div>
      </div>
      <div class="method-chips">${methodChips(contact, 2)}</div>
      <div class="card-foot">
        <span>${contact.methods.length} 条联系方式</span>
        <span>${contact.tags.length ? contact.tags.map((tag) => `#${esc(tag)}`).join(" ") : "未加标签"}</span>
      </div>
      ${starButton(contact)}
    </article>`;
  }

  function renderSkeleton() {
    elements.area.innerHTML = `<div class="skeleton-list" aria-hidden="true">
      ${Array.from({ length: 6 })
        .map(
          () => `<div class="skeleton-row">
            <div class="sk sk-avatar"></div>
            <div class="sk-lines">
              <div class="sk sk-line w40"></div>
              <div class="sk sk-line w70"></div>
            </div>
          </div>`,
        )
        .join("")}
    </div>`;
  }

  function renderEmpty() {
    const filtered = Boolean(state.query || state.tag || state.view === "bookmarked");
    if (filtered) {
      elements.area.innerHTML = `<div class="empty">
        ${emptyArt()}
        <h3>没有找到匹配的联系人</h3>
        <p>换个关键词试试，或者清除筛选条件查看全部联系人。</p>
        <div class="empty-actions">
          <button class="btn btn-ghost" type="button" data-action="clear-filters">清除筛选</button>
          <button class="btn btn-primary" type="button" data-action="create">新建联系人</button>
        </div>
      </div>`;
      return;
    }
    elements.area.innerHTML = `<div class="empty">
      ${emptyArt()}
      <h3>通讯录还是空的</h3>
      <p>从第一位联系人开始，或者直接导入已有的 Excel 通讯录。支持书签、多电话、多邮箱与自定义联系方式。</p>
      <div class="empty-actions">
        <button class="btn btn-primary" type="button" data-action="create">${icon("plus")}新建联系人</button>
        <button class="btn btn-ghost" type="button" data-action="import">${icon("upload")}导入 Excel</button>
        <a class="btn btn-ghost" href="/api/import/template">${icon("download")}下载模板</a>
      </div>
    </div>`;
  }

  function emptyArt() {
    return `<svg class="empty-art" viewBox="0 0 160 120" fill="none" aria-hidden="true">
      <rect x="22" y="24" width="96" height="70" rx="10" stroke="currentColor" stroke-width="1.6" opacity=".45"/>
      <rect x="34" y="34" width="96" height="70" rx="10" fill="#fffdf9" stroke="currentColor" stroke-width="1.8"/>
      <circle cx="55" cy="55" r="8" stroke="currentColor" stroke-width="1.6"/>
      <path d="M45 54c0 4-4 6-4 6h28s-4-2-4-6" stroke="currentColor" stroke-width="1.4" opacity=".55"/>
      <path d="M70 51h45M70 61h34M70 71h40" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity=".55"/>
      <path d="M70 88h24" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity=".3"/>
      <circle cx="126" cy="93" r="13" fill="#fbf0d7"/>
      <path d="m126 86 2.2 4.6 5 .7-3.6 3.5.8 5-4.4-2.4-4.4 2.4.8-5-3.6-3.5 5-.7Z" fill="#c98a12"/>
    </svg>`;
  }

  function renderError(error) {
    elements.area.innerHTML = `<div class="empty">
      ${emptyArt()}
      <h3>没有加载成功</h3>
      <p>${esc(error.message || "请检查服务是否在运行，然后重试。")}</p>
      <div class="empty-actions">
        <button class="btn btn-primary" type="button" data-action="retry">${icon("refresh")}重新加载</button>
      </div>
    </div>`;
  }

  function markActiveRows() {
    $$("[data-id]", elements.area).forEach((node) => {
      node.classList.toggle("is-active", Number(node.dataset.id) === state.activeId);
    });
  }

  /* ------------------------------------------------------------- drawer ---- */

  function renderDrawer(contact) {
    const sub = contactSubline(contact);
    const methods = contact.methods
      .map(
        (method) => `<div class="method-item">
          <div class="method-icon">${icon(kindMeta(method.kind).icon)}</div>
          <div class="method-body">
            <div class="method-label">${esc(method.label || kindMeta(method.kind).label)}</div>
            <div class="method-value">${esc(method.value)}</div>
          </div>
          <button class="copy-btn" type="button" data-copy="${esc(method.value)}" aria-label="复制${esc(method.label || kindMeta(method.kind).label)}" title="复制">
            ${icon("copy")}
          </button>
        </div>`,
      )
      .join("");

    elements.drawer.innerHTML = `<div class="drawer-head">
      <div class="drawer-topline">
        <span class="drawer-eyebrow">CONTACT</span>
        <button class="icon-btn" type="button" data-drawer-action="close" aria-label="关闭详情">${icon("close")}</button>
      </div>
      <div class="drawer-person">
        ${avatar(contact.name)}
        <div>
          <div class="drawer-name">${esc(contact.name)}</div>
          <div class="drawer-company">${esc(sub || "未填写公司或职位")}</div>
        </div>
      </div>
      <div class="drawer-actions">
        <button class="btn btn-ghost" type="button" data-drawer-action="edit">${icon("edit")}编辑</button>
        ${starButton(contact)}
        <button class="btn btn-ghost" type="button" data-drawer-action="delete">${icon("trash")}删除</button>
      </div>
    </div>
    <div class="drawer-body">
      <section class="drawer-section">
        <div class="section-label">联系方式 <span class="count">${contact.methods.length}</span></div>
        ${methods || '<p class="empty-note">还没有联系方式，点击“编辑”添加电话、邮箱或地址。</p>'}
      </section>
      <section class="drawer-section">
        <div class="section-label">标签</div>
        <div class="tag-row">${contact.tags.length ? contact.tags.map((tag) => `<span class="tag-chip">${esc(tag)}</span>`).join("") : '<span class="empty-note">未添加标签</span>'}</div>
      </section>
      <section class="drawer-section">
        <div class="section-label">备注</div>
        ${contact.notes ? `<div class="notes">${esc(contact.notes)}</div>` : '<p class="empty-note">暂无备注</p>'}
      </section>
      <div class="drawer-meta">
        <span>创建于 ${esc(formatDate(contact.createdAt))}</span>
        <span>最近更新 ${esc(formatDate(contact.updatedAt))}</span>
      </div>
    </div>`;
    hydrateIcons(elements.drawer);
  }

  async function openDrawer(id) {
    let contact = state.contacts.find((item) => item.id === id);
    if (!contact) {
      try {
        contact = (await api(`/api/contacts/${id}`)).contact;
      } catch (error) {
        toast(error.message, "error");
        return;
      }
    }
    state.activeId = id;
    renderDrawer(contact);
    elements.drawer.classList.add("is-open");
    elements.drawer.setAttribute("aria-hidden", "false");
    markActiveRows();
    updateScrim();
  }

  function closeDrawer() {
    state.activeId = null;
    elements.drawer.classList.remove("is-open");
    elements.drawer.setAttribute("aria-hidden", "true");
    markActiveRows();
    updateScrim();
  }

  function syncDrawer() {
    if (!state.activeId) return;
    const contact = state.contacts.find((item) => item.id === state.activeId);
    if (!contact) {
      closeDrawer();
      return;
    }
    if (elements.drawer.classList.contains("is-open")) renderDrawer(contact);
  }

  function updateScrim() {
    const drawerOpen = elements.drawer.classList.contains("is-open");
    const sidebarOpen = elements.sidebar.classList.contains("is-open");
    const show = drawerOpen || sidebarOpen;
    elements.scrim.hidden = false;
    elements.scrim.classList.toggle("is-visible", show);
    updateScrollLock();
  }

  function updateScrollLock() {
    const locked =
      Boolean(elements.modalRoot.children.length) ||
      elements.drawer.classList.contains("is-open") ||
      elements.sidebar.classList.contains("is-open");
    document.body.classList.toggle("is-locked", locked);
  }

  /* -------------------------------------------------------------- modal ---- */

  function openModal(html, { wide = false, compact = false } = {}) {
    closeModal();
    elements.modalRoot.innerHTML = `<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div class="modal-backdrop" data-modal-close></div>
      <div class="modal-panel${wide ? " is-wide" : ""}${compact ? " is-compact" : ""}" tabindex="-1">${html}</div>
    </div>`;
    hydrateIcons(elements.modalRoot);
    updateScrollLock();
    const focusTarget =
      $("[autofocus]", elements.modalRoot) ||
      $(".modal-body input, .modal-body textarea, .modal-body select", elements.modalRoot) ||
      $(".modal-panel", elements.modalRoot);
    if (focusTarget) setTimeout(() => focusTarget.focus(), 30);
  }

  function closeModal() {
    elements.modalRoot.innerHTML = "";
    state.importData = null;
    updateScrollLock();
  }

  function openConfirm({ title, message, confirmText = "确认", danger = false, onConfirm }) {
    openModal(
      `<div class="modal-head">
        <div>
          <h2 class="modal-title" id="modal-title">${esc(title)}</h2>
        </div>
        <button class="icon-btn" type="button" data-modal-close aria-label="关闭">${icon("close")}</button>
      </div>
      <div class="modal-body"><p style="font-size:13.5px;color:var(--ink-soft);line-height:1.7">${message}</p></div>
      <div class="modal-foot">
        <button class="btn btn-ghost" type="button" data-modal-close>取消</button>
        <button class="btn ${danger ? "btn-danger" : "btn-primary"}" type="button" id="confirm-action">${esc(confirmText)}</button>
      </div>`,
      { compact: true },
    );
    $("#confirm-action").addEventListener("click", async (event) => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await onConfirm();
        closeModal();
      } catch (error) {
        toast(error.message, "error");
      } finally {
        button.disabled = false;
      }
    });
  }

  /* ------------------------------------------------------------ contact ---- */

  function methodRowHTML(method = { kind: "phone", label: "", value: "" }) {
    const kind = KIND_META[method.kind] ? method.kind : "phone";
    return `<div class="method-edit-row" data-method-row>
      <select class="method-kind" aria-label="联系方式类型">
        ${Object.entries(KIND_META)
          .map(
            ([value, meta]) =>
              `<option value="${value}"${value === kind ? " selected" : ""}>${meta.label}</option>`,
          )
          .join("")}
      </select>
      <input class="method-label-input" maxlength="40" placeholder="标签（可选）" value="${esc(method.label || "")}" aria-label="联系方式标签">
      <input class="method-value-input" maxlength="200" placeholder="${esc(methodPlaceholder(kind))}" value="${esc(method.value || "")}" aria-label="联系方式内容">
      <button class="method-remove" type="button" aria-label="删除这条联系方式">${icon("trash")}</button>
    </div>`;
  }

  function openContactForm(contact = null) {
    const methods = contact && contact.methods.length ? contact.methods : [{ kind: "phone", label: "", value: "" }];
    const isEdit = Boolean(contact);
    openModal(
      `<div class="modal-head">
        <div>
          <h2 class="modal-title" id="modal-title">${isEdit ? "编辑联系人" : "新建联系人"}</h2>
          <p class="modal-sub">${isEdit ? "修改资料并保存，改动会立即生效。" : "填写基本信息，并为 TA 添加一种或多种联系方式。"}</p>
        </div>
        <button class="icon-btn" type="button" data-modal-close aria-label="关闭">${icon("close")}</button>
      </div>
      <form id="contact-form" novalidate>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field" data-field="name">
              <label for="f-name">姓名<span class="req">*</span></label>
              <input id="f-name" maxlength="80" autocomplete="off" placeholder="例如：林晚晴" value="${esc(contact?.name || "")}" autofocus>
              <div class="field-error" hidden>请填写联系人姓名</div>
            </div>
            <div class="field">
              <label for="f-company">公司 / 组织</label>
              <input id="f-company" maxlength="80" autocomplete="off" placeholder="例如：星野科技" value="${esc(contact?.company || "")}">
            </div>
            <div class="field">
              <label for="f-title">职位</label>
              <input id="f-title" maxlength="80" autocomplete="off" placeholder="例如：产品经理" value="${esc(contact?.jobTitle || "")}">
            </div>
            <div class="field">
              <label for="f-tags">标签</label>
              <input id="f-tags" maxlength="180" autocomplete="off" placeholder="用逗号分隔，如：客户, 重点" value="${esc((contact?.tags || []).join(", "))}">
              <div class="hint">最多 8 个标签</div>
            </div>
            <div class="field is-full">
              <label>联系方式</label>
              <div class="method-editor" id="method-editor">
                ${methods.map((method) => methodRowHTML(method)).join("")}
                <button class="add-method" type="button" id="add-method">${icon("plus")}添加联系方式</button>
              </div>
              <div class="hint">电话、邮箱、微信、社交账号、地址都可以各添加多条，空的联系方式行会被忽略。</div>
            </div>
            <div class="field is-full">
              <label for="f-notes">备注</label>
              <textarea id="f-notes" maxlength="2000" placeholder="补充说明，例如沟通偏好、合作背景…">${esc(contact?.notes || "")}</textarea>
            </div>
            <div class="field is-full">
              <label class="switch">
                <input type="checkbox" id="f-bookmarked"${contact?.bookmarked ? " checked" : ""}>
                <span class="switch-track"></span>
                加入书签，在“书签”中优先显示
              </label>
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-ghost" type="button" data-modal-close>取消</button>
          <button class="btn btn-primary" type="submit" id="save-contact">${isEdit ? "保存修改" : "创建联系人"}</button>
        </div>
      </form>`,
    );

    const form = $("#contact-form");
    const editor = $("#method-editor");
    const nameField = $('[data-field="name"]');

    editor.addEventListener("click", (event) => {
      const remove = event.target.closest(".method-remove");
      if (remove) {
        remove.closest("[data-method-row]").remove();
      }
    });

    editor.addEventListener("change", (event) => {
      if (!event.target.classList.contains("method-kind")) return;
      const row = event.target.closest("[data-method-row]");
      const valueInput = $(".method-value-input", row);
      valueInput.placeholder = methodPlaceholder(event.target.value);
    });

    $("#add-method").addEventListener("click", () => {
      const template = document.createElement("template");
      template.innerHTML = methodRowHTML();
      editor.insertBefore(template.content.firstElementChild, $("#add-method"));
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const name = $("#f-name").value.trim();
      if (!name) {
        nameField.classList.add("is-invalid");
        $(".field-error", nameField).hidden = false;
        $("#f-name").focus();
        return;
      }
      nameField.classList.remove("is-invalid");
      $(".field-error", nameField).hidden = true;

      const methods = $$("[data-method-row]", editor)
        .map((row) => ({
          kind: $(".method-kind", row).value,
          label: $(".method-label-input", row).value.trim(),
          value: $(".method-value-input", row).value.trim(),
        }))
        .filter((method) => method.value);

      const payload = {
        name,
        company: $("#f-company").value.trim(),
        jobTitle: $("#f-title").value.trim(),
        tags: $("#f-tags").value.trim(),
        notes: $("#f-notes").value.trim(),
        bookmarked: $("#f-bookmarked").checked,
        methods,
      };

      const saveButton = $("#save-contact");
      const original = saveButton.innerHTML;
      saveButton.disabled = true;
      saveButton.innerHTML = '<span class="spinner"></span> 保存中…';
      try {
        const response = contact
          ? await api(`/api/contacts/${contact.id}`, { method: "PUT", body: JSON.stringify(payload) })
          : await api("/api/contacts", { method: "POST", body: JSON.stringify(payload) });
        closeModal();
        await loadData({ quiet: true });
        await openDrawer(response.contact.id);
        toast(contact ? "联系人已更新" : "联系人已创建", "success");
      } catch (error) {
        if (error.fields?.name) {
          nameField.classList.add("is-invalid");
          $(".field-error", nameField).textContent = error.fields.name;
          $(".field-error", nameField).hidden = false;
        }
        toast(error.message, "error");
      } finally {
        saveButton.disabled = false;
        saveButton.innerHTML = original;
      }
    });
  }

  async function toggleStar(id) {
    try {
      const result = await api(`/api/contacts/${id}/bookmark`, { method: "PATCH", body: JSON.stringify({}) });
      const contact = state.contacts.find((item) => item.id === id);
      if (contact) contact.bookmarked = result.bookmarked;
      if (typeof state.meta.stats.bookmarked === "number") {
        state.meta.stats.bookmarked += result.bookmarked ? 1 : -1;
        if (state.meta.stats.bookmarked < 0) state.meta.stats.bookmarked = 0;
      }
      toast(result.bookmarked ? "已加入书签" : "已移出书签", "success");
      if (state.view === "bookmarked" && !result.bookmarked) {
        await loadData({ quiet: true });
      } else {
        renderAll();
      }
    } catch (error) {
      toast(error.message, "error");
    }
  }

  function deleteContact(contact) {
    openConfirm({
      title: "删除联系人",
      message: `确定要删除「<strong>${esc(contact.name)}</strong>」吗？该联系人的所有联系方式也会一并删除，此操作无法撤销。`,
      confirmText: "删除",
      danger: true,
      onConfirm: async () => {
        await api(`/api/contacts/${contact.id}`, { method: "DELETE" });
        if (state.activeId === contact.id) closeDrawer();
        await loadData({ quiet: true });
        toast("联系人已删除", "success");
      },
    });
  }

  /* ------------------------------------------------------------- import ---- */

  function importIntroContent() {
    return `<div class="dropzone" id="dropzone" tabindex="0" role="button" aria-label="选择要导入的 Excel 文件">
        <div class="drop-icon">${icon("file")}</div>
        <h3>把 Excel 文件拖到这里</h3>
        <p>或 <span class="browse">点击选择文件</span> · 支持 .xlsx，最大 8 MB</p>
        <input type="file" id="import-file" accept=".xlsx,.xlsm" hidden>
      </div>
      <div class="template-row">
        <span>第一次导入？先用模板整理数据，表头会自动匹配。</span>
        <a href="/api/import/template" download>${icon("download")}下载 Excel 模板</a>
      </div>
      <div class="field-error" id="import-error" hidden></div>`;
  }

  function openImport() {
    openModal(
      `<div class="modal-head">
        <div>
          <h2 class="modal-title" id="modal-title">导入 Excel</h2>
          <p class="modal-sub">一行一位联系人；导入前会先预览，并检查重复项。</p>
        </div>
        <button class="icon-btn" type="button" data-modal-close aria-label="关闭">${icon("close")}</button>
      </div>
      <div class="modal-body">
        <div id="import-upload">${importIntroContent()}</div>
        <div id="import-preview" hidden></div>
      </div>
      <div class="modal-foot">
        <span class="foot-note" id="import-foot-note">尚未选择文件</span>
        <button class="btn btn-ghost" type="button" data-modal-close>取消</button>
        <button class="btn btn-primary" type="button" id="confirm-import" disabled>导入</button>
      </div>`,
      { wide: true },
    );
    wireImport();
  }

  function wireImport() {
    const dropzone = $("#dropzone");
    const fileInput = $("#import-file");

    const chooseFile = () => fileInput.click();
    dropzone.addEventListener("click", chooseFile);
    dropzone.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        chooseFile();
      }
    });
    fileInput.addEventListener("change", () => {
      if (fileInput.files[0]) handleImportFile(fileInput.files[0]);
    });
    ["dragenter", "dragover"].forEach((name) =>
      dropzone.addEventListener(name, (event) => {
        event.preventDefault();
        dropzone.classList.add("is-dragging");
      }),
    );
    ["dragleave", "drop"].forEach((name) =>
      dropzone.addEventListener(name, (event) => {
        event.preventDefault();
        dropzone.classList.remove("is-dragging");
      }),
    );
    dropzone.addEventListener("drop", (event) => {
      const file = event.dataTransfer.files[0];
      if (file) handleImportFile(file);
    });

    $("#confirm-import").addEventListener("click", commitImport);
  }

  async function handleImportFile(file) {
    if (!/\.(xlsx|xlsm)$/i.test(file.name)) {
      showImportError("仅支持 .xlsx 格式的 Excel 文件，请重新选择。");
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      showImportError("文件超过 8 MB，请拆分后再上传。");
      return;
    }
    const upload = $("#import-upload");
    upload.innerHTML = `<div class="import-empty"><span class="spinner" style="display:inline-block;vertical-align:-3px;margin-right:8px"></span>正在解析「${esc(file.name)}」…</div>`;

    const formData = new FormData();
    formData.append("file", file);
    try {
      const data = await api("/api/import/preview", { method: "POST", body: formData });
      state.importData = data;
      renderImportPreview(data);
      $("#import-foot-note").textContent = `${data.filename} · ${data.sheet}`;
    } catch (error) {
      upload.innerHTML = importIntroContent();
      wireImport();
      showImportError(error.message);
    }
  }

  function showImportError(message) {
    const error = $("#import-error");
    if (!error) {
      toast(message, "error");
      return;
    }
    error.hidden = false;
    error.textContent = message;
  }

  function renderImportPreview(data) {
    const rows = data.rows || [];
    const summary = data.summary || {};
    const tableRows = rows
      .map((row, index) => {
        const contact = row.contact || {};
        const methodText = (contact.methods || [])
          .slice(0, 2)
          .map((method) => `${kindMeta(method.kind).label} ${method.value}`)
          .join(" · ");
        const extra = (contact.methods || []).length > 2 ? " …" : "";
        const selectable = row.status === "ok";
        const badge =
          row.status === "ok"
            ? '<span class="status-badge ok">可导入</span>'
            : row.status === "duplicate"
              ? '<span class="status-badge dup">重复</span>'
              : '<span class="status-badge error">错误</span>';
        return `<tr class="${row.status === "error" ? "is-error" : row.status === "duplicate" ? "is-duplicate" : ""}">
          <td class="col-check"><input type="checkbox" data-import-row="${index}" ${selectable ? "checked" : "disabled"} aria-label="选择第 ${row.row} 行"></td>
          <td>${row.row}</td>
          <td>
            <div class="preview-name">${esc(contact.name || "（缺少姓名）")}</div>
            <div class="preview-sub">${esc([contact.company, contact.jobTitle].filter(Boolean).join(" · ") || "—")}</div>
          </td>
          <td>${esc(methodText || "—")}${extra}</td>
          <td>${badge}${(row.messages || []).map((message) => `<div class="preview-message${row.status === "duplicate" ? " is-dup" : ""}">${esc(message)}</div>`).join("")}</td>
        </tr>`;
      })
      .join("");

    $("#import-upload").hidden = true;
    const preview = $("#import-preview");
    preview.hidden = false;
    preview.innerHTML = `<div class="import-summary">
        <div class="summary-card"><b>${summary.total ?? rows.length}</b><span>数据行</span></div>
        <div class="summary-card is-ok"><b>${summary.ready ?? 0}</b><span>可导入</span></div>
        <div class="summary-card is-warn"><b>${summary.duplicates ?? 0}</b><span>重复</span></div>
        <div class="summary-card is-bad"><b>${summary.errors ?? 0}</b><span>错误</span></div>
      </div>
      <div class="import-toolbar">
        <span id="import-selection">已选择 0 条</span>
        <button type="button" class="link-btn" id="select-importable">全选可导入项</button>
      </div>
      <div class="preview-wrap">
        <table class="preview-table">
          <thead><tr><th class="col-check"></th><th>行</th><th>姓名 / 公司</th><th>联系方式</th><th>状态</th></tr></thead>
          <tbody>${tableRows}</tbody>
        </table>
      </div>`;

    preview.addEventListener("change", (event) => {
      if (event.target.matches("[data-import-row]")) updateImportSelection();
    });
    $("#select-importable").addEventListener("click", () => {
      $$("[data-import-row]:not(:disabled)", preview).forEach((box) => (box.checked = true));
      updateImportSelection();
    });
    updateImportSelection();
  }

  function selectedImportRows() {
    if (!state.importData) return [];
    const boxes = $$("[data-import-row]", elements.modalRoot).filter((box) => box.checked && !box.disabled);
    return boxes.map((box) => state.importData.rows[Number(box.dataset.importRow)]);
  }

  function updateImportSelection() {
    const count = selectedImportRows().length;
    const label = $("#import-selection");
    if (label) label.textContent = `已选择 ${count} 条`;
    const button = $("#confirm-import");
    button.disabled = count === 0;
    button.textContent = count ? `导入 ${count} 位联系人` : "导入";
  }

  async function commitImport() {
    const rows = selectedImportRows();
    if (!rows.length) return;
    const button = $("#confirm-import");
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span> 正在导入…';
    try {
      const result = await api("/api/import", {
        method: "POST",
        body: JSON.stringify({ rows: rows.map((row) => ({ contact: row.contact, selected: true })) }),
      });
      closeModal();
      await loadData({ quiet: true });
      const skipped = result.skipped ? `，跳过 ${result.skipped} 条重复` : "";
      const failed = result.failed ? `，${result.failed} 条未通过校验` : "";
      toast(`成功导入 ${result.imported} 位联系人${skipped}${failed}`, result.imported ? "success" : "error");
    } catch (error) {
      toast(error.message, "error");
      button.disabled = false;
      button.textContent = `导入 ${rows.length} 位联系人`;
    }
  }

  /* ------------------------------------------------------------- export ---- */

  function exportContacts() {
    if (!state.contacts.length) {
      toast("当前没有可导出的联系人", "error");
      return;
    }
    const params = new URLSearchParams();
    if (state.query) params.set("q", state.query);
    if (state.tag) params.set("tag", state.tag);
    if (state.view === "bookmarked") params.set("bookmarked", "1");
    const link = document.createElement("a");
    link.href = `/api/export?${params.toString()}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    toast(`正在导出 ${state.contacts.length} 位联系人…`, "success");
  }

  function clearFilters() {
    state.query = "";
    state.tag = null;
    state.view = "all";
    elements.search.value = "";
    loadData();
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    toast("已复制到剪贴板", "success");
  }

  /* ------------------------------------------------------------- events ---- */

  function bindEvents() {
    document.addEventListener("click", async (event) => {
      const star = event.target.closest("[data-star]");
      if (star) {
        event.preventDefault();
        event.stopPropagation();
        await toggleStar(Number(star.dataset.star));
        return;
      }

      const action = event.target.closest("[data-action]")?.dataset.action;
      if (action) {
        if (action === "create") openContactForm();
        else if (action === "import") openImport();
        else if (action === "export") exportContacts();
        else if (action === "retry") loadData();
        else if (action === "clear-filters") clearFilters();
        else if (action === "clear-search") {
          state.query = "";
          elements.search.value = "";
          loadData();
        } else if (action === "clear-tag") {
          state.tag = null;
          loadData();
        }
        return;
      }

      const tagButton = event.target.closest("[data-tag]");
      if (tagButton) {
        const tag = tagButton.dataset.tag;
        state.tag = state.tag === tag ? null : tag;
        state.view = "all";
        closeSidebar();
        loadData();
        return;
      }

      const viewButton = event.target.closest("[data-view]");
      if (viewButton) {
        state.view = viewButton.dataset.view;
        state.tag = null;
        closeSidebar();
        loadData();
        return;
      }

      const layoutButton = event.target.closest("[data-layout]");
      if (layoutButton) {
        state.layout = layoutButton.dataset.layout;
        $$("[data-layout]").forEach((button) => {
          button.classList.toggle("is-active", button.dataset.layout === state.layout);
          button.setAttribute("aria-pressed", String(button.dataset.layout === state.layout));
        });
        renderContacts();
        return;
      }

      const copyButton = event.target.closest("[data-copy]");
      if (copyButton) {
        await copyText(copyButton.dataset.copy);
        return;
      }

      const drawerAction = event.target.closest("[data-drawer-action]")?.dataset.drawerAction;
      if (drawerAction) {
        const contact = state.contacts.find((item) => item.id === state.activeId);
        if (!contact) return;
        if (drawerAction === "close") closeDrawer();
        else if (drawerAction === "edit") openContactForm(contact);
        else if (drawerAction === "delete") deleteContact(contact);
        return;
      }

      if (event.target.closest("[data-modal-close]")) {
        closeModal();
        return;
      }
    });

    elements.area.addEventListener("click", (event) => {
      if (event.target.closest("[data-star]")) return;
      const card = event.target.closest("[data-id]");
      if (card) openDrawer(Number(card.dataset.id));
    });

    elements.area.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const card = event.target.closest("[data-id]");
      if (!card) return;
      if (event.target.closest("[data-star]")) return;
      event.preventDefault();
      openDrawer(Number(card.dataset.id));
    });

    elements.search.addEventListener(
      "input",
      debounce(() => {
        state.query = elements.search.value.trim();
        loadData();
      }, 220),
    );

    $("#menu-btn").addEventListener("click", () => {
      elements.sidebar.classList.toggle("is-open");
      updateScrim();
    });

    elements.scrim.addEventListener("click", () => {
      closeDrawer();
      closeSidebar();
    });

    document.addEventListener("keydown", (event) => {
      const target = event.target;
      const typing = target instanceof HTMLElement && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName);
      if ((event.key === "/" && !typing) || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k")) {
        event.preventDefault();
        elements.search.focus();
        elements.search.select();
        return;
      }
      if (event.key === "Escape") {
        if (elements.modalRoot.children.length) closeModal();
        else if (elements.drawer.classList.contains("is-open")) closeDrawer();
        else if (elements.sidebar.classList.contains("is-open")) closeSidebar();
      }
    });
  }

  function closeSidebar() {
    elements.sidebar.classList.remove("is-open");
    updateScrim();
  }

  /* --------------------------------------------------------------- init ---- */

  function init() {
    hydrateIcons();
    elements.scrim.hidden = false;
    bindEvents();
    updateScrim();
    loadData();
    setInterval(() => {
      if (!state.loading) loadData({ quiet: true });
      // Polling keeps multiple tabs in sync; the app is single-user local.
    }, 60000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();