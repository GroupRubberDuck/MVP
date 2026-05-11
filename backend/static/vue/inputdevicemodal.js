import { openBlock as s, createElementBlock as c, withModifiers as v, createElementVNode as o, createTextVNode as f, normalizeClass as L, createCommentVNode as m, toDisplayString as d, ref as p, computed as b } from "vue";
import { _ as T } from "./_plugin-vue_export-helper-CHgC5LLL.js";
const j = {
  __name: "InputDeviceModal",
  emits: ["close", "imported"],
  setup(y, { expose: t, emit: D }) {
    t();
    const e = D, l = p(null), _ = p(!1), n = p(!1), u = p(""), a = p(""), I = ["json", "csv", "xml"], x = b(() => {
      if (!l.value) return "";
      const i = l.value.name.split(".").pop().toLowerCase();
      return i === "json" ? "📄" : i === "xml" ? "📋" : "📊";
    }), C = b(() => {
      if (!l.value) return "";
      const i = l.value.size;
      return i < 1024 ? `${i} B` : i < 1024 * 1024 ? `${(i / 1024).toFixed(1)} KB` : `${(i / (1024 * 1024)).toFixed(2)} MB`;
    });
    function F(i) {
      const r = i.name.split(".").pop().toLowerCase();
      return I.includes(r) ? null : `Formato ".${r}" non supportato. Usa JSON, CSV o XML.`;
    }
    function g(i) {
      a.value = "", u.value = "";
      const r = F(i);
      if (r) {
        a.value = r;
        return;
      }
      l.value = i;
    }
    function w(i) {
      i.target.files[0] && g(i.target.files[0]), i.target.value = "";
    }
    function M(i) {
      _.value = !1, i.dataTransfer.files[0] && g(i.dataTransfer.files[0]);
    }
    function z() {
      l.value = null, a.value = "", u.value = "";
    }
    function E() {
      n.value || e("close");
    }
    async function h() {
      if (!l.value || n.value) return;
      n.value = !0, a.value = "", u.value = "";
      const i = new FormData();
      i.append("file", l.value);
      try {
        const r = await fetch("/api/devices/import", {
          method: "POST",
          body: i
        }), k = await r.json();
        r.ok ? (u.value = k.message || "Dispositivo importato con successo.", l.value = null, setTimeout(() => e("imported"), 1200)) : a.value = k.error || `Errore ${r.status}: importazione fallita.`;
      } catch {
        a.value = "Errore di rete. Verifica la connessione e riprova.";
      } finally {
        n.value = !1;
      }
    }
    const S = { emit: e, importFile: l, isDragging: _, isImporting: n, importSuccess: u, importError: a, ALLOWED_EXT: I, fileIcon: x, fileSizeLabel: C, validateFile: F, setFile: g, onFileSelected: w, onDrop: M, removeFile: z, closeModal: E, submitImport: h, ref: p, computed: b };
    return Object.defineProperty(S, "__isScriptSetup", { enumerable: !1, value: !0 }), S;
  }
}, B = {
  class: "modal",
  role: "dialog",
  "aria-modal": "true",
  "aria-labelledby": "import-modal-title"
}, V = {
  key: 1,
  class: "file-preview"
}, N = { class: "file-preview__icon" }, O = { class: "file-preview__info" }, X = { class: "file-preview__name" }, A = { class: "file-preview__size" }, J = {
  key: 2,
  class: "alert-inline alert-inline--success"
}, P = {
  key: 3,
  class: "alert-inline alert-inline--error"
}, q = { class: "modal__footer" }, K = ["disabled"], R = ["disabled"], U = {
  key: 0,
  class: "spinner"
};
function W(y, t, D, e, l, _) {
  return s(), c("div", {
    class: "modal-overlay",
    onClick: v(e.closeModal, ["self"])
  }, [
    o("div", B, [
      t[4] || (t[4] = o(
        "h2",
        {
          class: "modal__title",
          id: "import-modal-title"
        },
        "Importa Dispositivo",
        -1
        /* CACHED */
      )),
      t[5] || (t[5] = o(
        "p",
        { class: "modal__body" },
        [
          f(" Carica un file di configurazione per aggiungere un dispositivo al sistema."),
          o("br"),
          f(" Formati supportati: "),
          o("strong", null, "JSON, CSV, XML"),
          f(" — max 10 MB. ")
        ],
        -1
        /* CACHED */
      )),
      e.importFile ? m("v-if", !0) : (s(), c(
        "div",
        {
          key: 0,
          class: L(["upload-area", { "upload-area--dragover": e.isDragging }]),
          onDragover: t[0] || (t[0] = v((n) => e.isDragging = !0, ["prevent"])),
          onDragleave: t[1] || (t[1] = v((n) => e.isDragging = !1, ["prevent"])),
          onDrop: v(e.onDrop, ["prevent"]),
          onClick: t[2] || (t[2] = (n) => y.$refs.fileInput.click())
        },
        [...t[3] || (t[3] = [
          o(
            "div",
            { class: "upload-area__icon" },
            "📂",
            -1
            /* CACHED */
          ),
          o(
            "p",
            { class: "upload-area__title" },
            "Trascina qui il file o clicca per selezionarlo",
            -1
            /* CACHED */
          ),
          o(
            "p",
            { class: "upload-area__hint" },
            ".json  ·  .csv  ·  .xml",
            -1
            /* CACHED */
          )
        ])],
        34
        /* CLASS, NEED_HYDRATION */
      )),
      o(
        "input",
        {
          ref: "fileInput",
          type: "file",
          accept: ".json,.csv,.xml",
          style: { display: "none" },
          onChange: e.onFileSelected
        },
        null,
        544
        /* NEED_HYDRATION, NEED_PATCH */
      ),
      e.importFile ? (s(), c("div", V, [
        o(
          "span",
          N,
          d(e.fileIcon),
          1
          /* TEXT */
        ),
        o("div", O, [
          o(
            "p",
            X,
            d(e.importFile.name),
            1
            /* TEXT */
          ),
          o(
            "p",
            A,
            d(e.fileSizeLabel),
            1
            /* TEXT */
          )
        ]),
        o("button", {
          class: "file-preview__remove",
          onClick: e.removeFile,
          title: "Rimuovi"
        }, "✕")
      ])) : m("v-if", !0),
      e.importSuccess ? (s(), c(
        "div",
        J,
        d(e.importSuccess),
        1
        /* TEXT */
      )) : m("v-if", !0),
      e.importError ? (s(), c(
        "div",
        P,
        d(e.importError),
        1
        /* TEXT */
      )) : m("v-if", !0),
      o("div", q, [
        o("button", {
          class: "btn btn--outline",
          onClick: e.closeModal,
          disabled: e.isImporting
        }, " Annulla ", 8, K),
        o("button", {
          class: "btn btn--primary",
          onClick: e.submitImport,
          disabled: !e.importFile || e.isImporting
        }, [
          e.isImporting ? (s(), c("span", U)) : m("v-if", !0),
          f(
            " " + d(e.isImporting ? "Importazione…" : "Importa"),
            1
            /* TEXT */
          )
        ], 8, R)
      ])
    ])
  ]);
}
const Q = /* @__PURE__ */ T(j, [["render", W], ["__file", "/app/frontend/src/components/InputDeviceModal.vue"]]);
export {
  Q as default
};
