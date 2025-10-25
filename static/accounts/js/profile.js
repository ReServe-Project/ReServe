// static/accounts/js/profile.js
(function () {
  // ---- helpers ----
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
  }
  const csrftoken = getCookie('csrftoken');

  // ---- modal open/close (matches template/CSS) ----
  const openBtn   = document.querySelector("[data-open='edit']");
  const modal     = document.getElementById("edit-modal");
  const closeBtn  = document.getElementById("close-edit");
  const cancelBtn = document.getElementById("cancel-edit");

  function open()  { modal?.classList.add("show"); }
  function close() { modal?.classList.remove("show"); }

  openBtn?.addEventListener("click", open);
  closeBtn?.addEventListener("click", close);
  cancelBtn?.addEventListener("click", close);
  modal?.addEventListener("click", (e) => { if (e.target === modal) close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });

  // ---- AJAX: profile form (display_name, height_cm, weight_kg) ----
  const form = document.getElementById("editForm");
  const toast = document.getElementById("toast");
  const errors = document.getElementById("edit-errors");

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 1600);
  }

  function setLiveError(msg) {
    if (errors) errors.textContent = msg || "";
  }

  function setFieldInvalid(id, bad) {
    const el = document.getElementById(id);
    if (el) el.setAttribute("aria-invalid", bad ? "true" : "false");
  }

  function updateMetric(field, value, unit) {
    const box = document.querySelector(`.metrics .value[data-field="${field}"]`);
    if (!box) return;
    if (value === null || value === undefined || value === "") {
      box.textContent = "—";
    } else {
      box.textContent = value;
      if (unit) {
        const span = document.createElement("span");
        span.className = "unit";
        span.textContent = ` ${unit}`;
        box.appendChild(span);
      }
    }
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      setLiveError("");
      setFieldInvalid("id_display_name", false);
      setFieldInvalid("id_height_cm", false);
      setFieldInvalid("id_weight_kg", false);

      const submit = form.querySelector('button[type="submit"]');
      const original = submit?.textContent;
      if (submit) { submit.disabled = true; submit.textContent = "Saving..."; }

      try {
        const fd = new FormData(form);
        const resp = await fetch(form.action, {
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
          body: fd
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) {
          const errs = data.errors || {};
          if (errs.display_name) setFieldInvalid("id_display_name", true);
          if (errs.height_cm)    setFieldInvalid("id_height_cm", true);
          if (errs.weight_kg)    setFieldInvalid("id_weight_kg", true);
          const first = Object.values(errs)[0]?.[0]?.message || "Could not save. Check your input.";
          throw new Error(first);
        }

        const u = data.updated || {};
        const nameEl = document.querySelector(".display-name");
        if (nameEl && u.display_name) nameEl.textContent = u.display_name;

        updateMetric("height", u.height_cm, "cm");
        updateMetric("weight", u.weight_kg, "kg");

        close();
        showToast("Profile updated");
      } catch (err) {
        console.error(err);
        setLiveError(String(err.message || err));
      } finally {
        if (submit) { submit.disabled = false; submit.textContent = original; }
      }
    });
  }

  // ---- AJAX: avatar upload (instant preview, then upload) ----
  const avatarFile = document.getElementById("avatar-file");
  const avatarImg  = document.getElementById("avatar-img");

  async function uploadAvatar(file) {
    const fd = new FormData();
    fd.append("avatar", file);
    try {
      const r = await fetch("/profile/avatar/", {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken, "X-Requested-With": "XMLHttpRequest" },
        body: fd
      });
      const d = await r.json();
      if (!r.ok || !d.success) throw new Error("Upload failed");
      if (avatarImg && d.avatar_url) avatarImg.src = d.avatar_url;
      showToast("Avatar updated");
    } catch (e) {
      console.error(e);
      alert("Avatar upload failed. Try a smaller JPG/PNG/WebP (max 2 MB).");
    }
  }

  avatarFile?.addEventListener("change", () => {
    const f = avatarFile.files?.[0];
    if (!f) return;
    if (avatarImg) avatarImg.src = URL.createObjectURL(f); // instant preview
    uploadAvatar(f);
  });
})();
