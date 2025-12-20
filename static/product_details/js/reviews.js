document.addEventListener("DOMContentLoaded", () => {
  const openBtn = document.getElementById("addReviewBtn");
  const modal = document.getElementById("reviewModal");
  const closeBtn = document.getElementById("closeModalBtn");

  if (openBtn && modal && closeBtn) {
    openBtn.addEventListener("click", () => {
      modal.classList.remove("hidden");
    });

    closeBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
    });

    window.addEventListener("click", (e) => {
      if (e.target === modal) modal.classList.add("hidden");
    });
  } else {
    console.warn("⚠️ Modal elements not found in DOM");
  }
});

