// static/accounts/js/profile.js
(function () {
  const openBtn  = document.getElementById('editProfileBtn');
  const modal    = document.getElementById('editProfileModal');
  const closeBtn = document.getElementById('modalCloseBtn');
  const cancel2  = document.getElementById('modalCloseBtn2');
  const form     = document.getElementById('profileEditForm');
  const avatarInput = document.getElementById('id_avatar');
  const avatarImg   = document.getElementById('profileAvatarImg');

  // --- CSRF helper ---
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
  }
  const csrftoken = getCookie('csrftoken');

  // --- Modal open/close ---
  function open() { modal?.classList.add('is-open'); }
  function close() { modal?.classList.remove('is-open'); }
  if (openBtn) openBtn.addEventListener('click', e => { e.preventDefault(); open(); });
  if (closeBtn) closeBtn.addEventListener('click', close);
  if (cancel2)  cancel2.addEventListener('click', close);
  modal?.addEventListener('click', e => { if (e.target === modal) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  // --- Update UI text helper ---
  const setText = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };

  // --- AJAX save profile ---
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submit = form.querySelector('button[type="submit"]');
      const orig = submit?.textContent;
      if (submit) { submit.disabled = true; submit.textContent = 'Saving...'; }
      try {
        const fd = new FormData(form);
        const resp = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrftoken },
          body: fd
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) throw data.errors || 'Save failed';

        const u = data.updated || {};
        setText('displayName', u.display_name ?? '');
        setText('heightValue', u.height_cm ? `${u.height_cm} cm` : '—');
        setText('weightValue', (u.weight_kg || u.weight_kg === 0) ? `${u.weight_kg} kg` : '—');

        close();
      } catch (err) {
        console.error('Save failed', err);
        alert('Could not save. Please check your input.');
      } finally {
        if (submit) { submit.disabled = false; submit.textContent = orig; }
      }
    });
  }

  // --- Avatar preview + upload ---
  async function uploadAvatar(file) {
    const fd = new FormData();
    fd.append('avatar', file);
    try {
      const r = await fetch('/profile/avatar/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        body: fd
      });
      const d = await r.json();
      if (!r.ok || !d.success) throw new Error('Upload failed');
      if (avatarImg && d.avatar_url) avatarImg.src = d.avatar_url;
    } catch (e) {
      console.error(e);
      alert('Avatar upload failed');
    }
  }
  if (avatarInput) {
    avatarInput.addEventListener('change', () => {
      const f = avatarInput.files?.[0];
      if (!f) return;
      if (avatarImg) avatarImg.src = URL.createObjectURL(f); // instant preview
      uploadAvatar(f); // then upload
    });
  }
})();
