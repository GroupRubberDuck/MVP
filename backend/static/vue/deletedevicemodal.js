import { openBlock as n, createElementBlock as l, withModifiers as C, createElementVNode as o, createTextVNode as s, toDisplayString as d, Fragment as j, renderList as M, normalizeClass as h, createCommentVNode as f, ref as a } from "vue";
import { _ as z } from "./_plugin-vue_export-helper-CHgC5LLL.js";
const L = {
  __name: "DeleteDeviceModal",
  props: {
    deviceId: { type: String, required: !0 },
    deviceName: { type: String, required: !0 }
  },
  emits: ["close", "deleted"],
  setup(E, { expose: e, emit: _ }) {
    e();
    const t = E, c = _, p = a("json"), r = a(!1), m = a(!1), b = a(""), u = a(!1);
    function D() {
      u.value || c("close");
    }
    async function k() {
      r.value = !0, m.value = !1, b.value = "";
      try {
        const i = await fetch(
          `/api/devices/${t.deviceId}/export?extension=${p.value}`
        );
        if (!i.ok) {
          const w = await i.json().catch(() => ({}));
          throw new Error(w.error || `Errore ${i.status}`);
        }
        const x = await i.blob(), v = document.createElement("a");
        v.href = URL.createObjectURL(x), v.download = `device_${t.deviceId}.${p.value}`, v.click(), URL.revokeObjectURL(v.href), m.value = !0;
      } catch (i) {
        b.value = i.message || "Esportazione fallita.";
      } finally {
        r.value = !1;
      }
    }
    async function y() {
      u.value = !0;
      try {
        const i = await fetch(`/devices/${t.deviceId}`, { method: "DELETE" });
        if (!i.ok) {
          const x = await i.json().catch(() => ({}));
          throw new Error(x.error || `Errore ${i.status}`);
        }
        c("deleted");
      } catch (i) {
        alert(`Eliminazione fallita: ${i.message}`), u.value = !1;
      }
    }
    const g = { props: t, emit: c, selectedFormat: p, isExporting: r, exportDone: m, exportError: b, isDeleting: u, closeModal: D, exportDevice: k, confirmDelete: y, ref: a };
    return Object.defineProperty(g, "__isScriptSetup", { enumerable: !1, value: !0 }), g;
  }
}, S = {
  class: "modal",
  role: "dialog",
  "aria-modal": "true"
}, F = { class: "modal__body" }, N = { class: "export-section" }, U = { class: "export-format-group" }, I = ["onClick"], R = { class: "export-actions" }, V = ["disabled"], O = {
  key: 0,
  class: "spinner"
}, q = {
  key: 0,
  class: "alert-inline alert-inline--success"
}, B = {
  key: 1,
  class: "alert-inline alert-inline--error"
}, T = { class: "modal__footer" }, A = ["disabled"], P = ["disabled"], Q = {
  key: 0,
  class: "spinner"
};
function G(E, e, _, t, c, p) {
  return n(), l("div", {
    class: "modal-overlay",
    onClick: C(t.closeModal, ["self"])
  }, [
    o("div", S, [
      e[10] || (e[10] = o(
        "h2",
        { class: "modal__title" },
        "Elimina dispositivo",
        -1
        /* CACHED */
      )),
      o("p", F, [
        e[0] || (e[0] = s(
          " Stai per eliminare il dispositivo ",
          -1
          /* CACHED */
        )),
        o(
          "strong",
          null,
          "« " + d(_.deviceName) + " »",
          1
          /* TEXT */
        ),
        e[1] || (e[1] = s(
          ". ",
          -1
          /* CACHED */
        )),
        e[2] || (e[2] = o(
          "br",
          null,
          null,
          -1
          /* CACHED */
        )),
        e[3] || (e[3] = s(
          "Questa operazione è ",
          -1
          /* CACHED */
        )),
        e[4] || (e[4] = o(
          "strong",
          null,
          "irreversibile",
          -1
          /* CACHED */
        )),
        e[5] || (e[5] = s(
          ".",
          -1
          /* CACHED */
        )),
        e[6] || (e[6] = o(
          "br",
          null,
          null,
          -1
          /* CACHED */
        )),
        e[7] || (e[7] = o(
          "br",
          null,
          null,
          -1
          /* CACHED */
        )),
        e[8] || (e[8] = s(
          " Vuoi esportare una copia prima di eliminarlo? ",
          -1
          /* CACHED */
        ))
      ]),
      o("div", N, [
        e[9] || (e[9] = o(
          "p",
          { class: "export-section__title" },
          "Esporta prima di eliminare",
          -1
          /* CACHED */
        )),
        o("div", U, [
          (n(), l(
            j,
            null,
            M(["json", "csv", "xml"], (r) => o("button", {
              key: r,
              class: h(["export-format-btn", { "export-format-btn--active": t.selectedFormat === r }]),
              onClick: (m) => t.selectedFormat = r
            }, d(r.toUpperCase()), 11, I)),
            64
            /* STABLE_FRAGMENT */
          ))
        ]),
        o("div", R, [
          o("button", {
            class: "btn btn--secondary btn--sm",
            onClick: t.exportDevice,
            disabled: t.isExporting
          }, [
            t.isExporting ? (n(), l("span", O)) : f("v-if", !0),
            s(
              " " + d(t.isExporting ? "Esportazione…" : "Esporta"),
              1
              /* TEXT */
            )
          ], 8, V),
          t.exportDone ? (n(), l("span", q, " File scaricato ")) : f("v-if", !0),
          t.exportError ? (n(), l(
            "span",
            B,
            d(t.exportError),
            1
            /* TEXT */
          )) : f("v-if", !0)
        ])
      ]),
      o("div", T, [
        o("button", {
          class: "btn btn--outline",
          onClick: t.closeModal,
          disabled: t.isDeleting
        }, " Annulla ", 8, A),
        o("button", {
          class: "btn btn--danger",
          onClick: t.confirmDelete,
          disabled: t.isDeleting
        }, [
          t.isDeleting ? (n(), l("span", Q)) : f("v-if", !0),
          s(
            " " + d(t.isDeleting ? "Eliminazione…" : "Elimina definitivamente"),
            1
            /* TEXT */
          )
        ], 8, P)
      ])
    ])
  ]);
}
const K = /* @__PURE__ */ z(L, [["render", G], ["__file", "/app/frontend/src/components/DeleteDeviceModal.vue"]]);
export {
  K as default
};
