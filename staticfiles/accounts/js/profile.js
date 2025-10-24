// static/accounts/js/profile.js

// ========== 1. Handle Availability Check ==========
document.addEventListener("DOMContentLoaded", () => {
    const handleField = document.querySelector("#id_handle");
    const feedback = document.createElement("small");
    if (handleField) {
      handleField.parentElement.appendChild(feedback);
  
      handleField.addEventListener("input", async () => {
        const val = handleField.value.trim();
        if (!val) return (feedback.textContent = "");
        try {
          const res = await fetch(`/profile/ajax/validate-handle/?handle=${encodeURIComponent(val)}`);
          const data = await res.json();
          if (data.available) {
            feedback.textContent = "✅ Handle available";
            feedback.style.color = "green";
          } else {
            feedback.textContent = "❌ Handle already taken";
            feedback.style.color = "red";
          }
        } catch (e) {
          console.error(e);
        }
      });
    }
  
    // ========== 2. Inline Phone Update ==========
    const phoneInput = document.querySelector("#id_phone_inline");
    if (phoneInput) {
      phoneInput.addEventListener("change", async () => {
        const val = phoneInput.value.trim();
        if (!val) return;
        const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
        try {
          const res = await fetch("/profile/ajax/update-phone/", {
            method: "POST",
            headers: {
              "X-CSRFToken": csrf,
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({ phone: val }),
          });
          const data = await res.json();
          alert(data.success ? "Phone updated ✅" : "Invalid phone ❌");
        } catch (e) {
          console.error(e);
        }
      });
    }
  
    // ========== 3. Avatar Upload ==========
    const avatarForm = document.querySelector("#avatarForm");
    if (avatarForm) {
      avatarForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(avatarForm);
        const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
        try {
          const res = await fetch(avatarForm.action, {
            method: "POST",
            headers: { "X-CSRFToken": csrf },
            body: formData,
          });
          const data = await res.json();
          if (data.success) {
            alert("Avatar updated!");
            location.reload();
          } else {
            alert("Failed to upload avatar.");
          }
        } catch (err) {
          console.error(err);
        }
      });
    }
  });
  