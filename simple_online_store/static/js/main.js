// Small progressive enhancements for the Aurora Store UI

document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss flash messages after a delay
  const FLASH_LIFETIME = 4500;
  const flashContainer = document.getElementById("flash-messages");
  if (flashContainer) {
    const flashes = flashContainer.querySelectorAll(".flash-message");
    flashes.forEach((flash) => {
      const closeBtn = flash.querySelector("[data-dismiss-flash]");
      const remove = () => {
        flash.style.transition = "opacity 180ms ease-out, transform 180ms ease-out";
        flash.style.opacity = "0";
        flash.style.transform = "translateY(-4px)";
        setTimeout(() => flash.remove(), 200);
      };

      if (closeBtn) {
        closeBtn.addEventListener("click", remove);
      }

      setTimeout(remove, FLASH_LIFETIME);
    });
  }
});

