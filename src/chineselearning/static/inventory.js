// Transport and selection state are testable without the page DOM.
export function createInventoryController({onChange, fetcher = globalThis.fetch}) {
    const state = {hsk_scheme: "newest", hsk_level: "", page: 1, page_size: 20,
        sort: "simplified", order: "asc", loading: false, error: null, data: null};
    let sequence = 0;
    let controller;
    const notify = () => onChange({...state});

    async function load() {
        controller?.abort();
        controller = new AbortController();
        const current = ++sequence;
        state.loading = true;
        state.error = null;
        state.data = null;
        notify();
        const params = new URLSearchParams();
        for (const key of ["hsk_scheme", "hsk_level", "page", "page_size", "sort", "order"]) {
            if (state[key] !== "") params.set(key, state[key]);
        }
        try {
            const response = await fetcher(`/api/characters?${params}`, {signal: controller.signal});
            if (!response.ok) throw new Error(`Inventory request failed (HTTP ${response.status}).`);
            const data = await response.json();
            if (current !== sequence) return;
            state.data = data;
        } catch (error) {
            if (current !== sequence) return;
            state.error = error.message || "Unable to load the inventory.";
        } finally {
            if (current === sequence) {
                state.loading = false;
                notify();
            }
        }
    }

    return {
        load,
        filter(level) { state.hsk_level = level; state.page = 1; return load(); },
        resize(size) { state.page_size = Number(size); state.page = 1; return load(); },
        sort(field) {
            state.order = state.sort === field && state.order === "asc" ? "desc" : "asc";
            state.sort = field;
            state.page = 1;
            return load();
        },
        navigate(delta) {
            if (state.loading || !state.data) return;
            const page = state.page + delta;
            if (page < 1 || page > state.data.total_pages) return;
            state.page = page;
            return load();
        },
    };
}

function mountInventory() {
    const byId = (id) => document.getElementById(id);
    const body = byId("characters");
    const sortButtons = [...document.querySelectorAll("[data-sort]")];
    const statusLabels = {not_encountered: "Not yet encountered", learning: "Learning", known: "Known"};

    function cell(value, className = "") {
        const td = document.createElement("td");
        const missing = value == null || value === "";
        if (!missing && className === "status") {
            const span = document.createElement("span");
            span.className = "status";
            span.textContent = value;
            td.append(span);
        } else {
            td.textContent = missing ? "Not provided" : value;
            td.className = missing ? "missing" : className;
        }
        if (className.includes("hanzi") && value) td.lang = "zh";
        return td;
    }

    function render(state) {
        byId("inventory").setAttribute("aria-busy", String(state.loading));
        byId("message").className = state.error ? "error" : "";
        byId("message").textContent = state.loading ? "Loading characters…" : state.error
            ? `${state.error} Check the server, then retry.` : state.data?.total === 0
            ? "No characters match this first-appearance band." : state.data?.items.length === 0
            ? "No characters on this page." : "Characters loaded.";
        byId("retry").hidden = !state.error;
        for (const button of sortButtons) {
            const active = button.dataset.sort === state.sort;
            button.closest("th").setAttribute("aria-sort", active
                ? state.order === "asc" ? "ascending" : "descending" : "none");
            button.querySelector("[data-direction]").textContent = active
                ? state.order === "asc" ? "↑" : "↓" : "↕";
        }
        const rows = (state.data?.items || []).map((item) => {
            const tr = document.createElement("tr");
            tr.append(cell(item.simplified, "hanzi simplified"), cell(item.traditional, "hanzi"),
                cell(item.english_gloss), cell(item.hsk_level_label),
                cell(statusLabels[item.recognition_status] ?? item.recognition_status, "status"),
                cell(statusLabels[item.production_status] ?? item.production_status, "status"),
                cell(item.usage_note));
            return tr;
        });
        body.replaceChildren(...rows);
        const data = state.data;
        const start = data?.items.length ? (data.page - 1) * data.page_size + 1 : 0;
        const end = data?.items.length ? start + data.items.length - 1 : 0;
        byId("counts").textContent = state.loading ? "Waiting for results" : !data
            ? "Results unavailable" : data.total === 0 ? "0 characters · 0 pages"
            : `${start}–${end} of ${data.total} characters · Page ${data.page} of ${data.total_pages}`;
        byId("previous").disabled = state.loading || !data || data.page <= 1;
        byId("next").disabled = state.loading || !data || data.page >= data.total_pages;
    }

    const inventory = createInventoryController({onChange: render});
    byId("band").addEventListener("change", (event) => inventory.filter(event.target.value));
    byId("page-size").addEventListener("change", (event) => inventory.resize(event.target.value));
    byId("previous").addEventListener("click", () => inventory.navigate(-1));
    byId("next").addEventListener("click", () => inventory.navigate(1));
    byId("retry").addEventListener("click", () => inventory.load());
    for (const button of sortButtons) {
        button.addEventListener("click", () => inventory.sort(button.dataset.sort));
    }
    inventory.load();
}

if (typeof document !== "undefined") mountInventory();
