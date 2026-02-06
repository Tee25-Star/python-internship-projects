(() => {
  const root = document.documentElement;
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  // Theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light" || savedTheme === "dark") {
    root.setAttribute("data-theme", savedTheme);
  } else {
    root.setAttribute("data-theme", "dark");
  }

  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
    });
  }

  // Reveal on scroll
  const revealEls = Array.from(document.querySelectorAll(".reveal"));
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add("on");
          io.unobserve(e.target);
        }
      }
    },
    { threshold: 0.12 }
  );
  revealEls.forEach((el) => io.observe(el));

  // Rotating role text (typing-like swap)
  const roles = (window.__PROFILE__ && window.__PROFILE__.roles) || [
    "Python Developer",
    "Full-Stack Builder",
    "Automation Engineer",
  ];
  const roleText = document.getElementById("roleText");
  let idx = 0;
  function swapRole() {
    if (!roleText) return;
    idx = (idx + 1) % roles.length;
    roleText.animate(
      [
        { opacity: 1, transform: "translateY(0px)" },
        { opacity: 0, transform: "translateY(-6px)" },
      ],
      { duration: 220, easing: "ease-in" }
    ).onfinish = () => {
      roleText.textContent = roles[idx];
      roleText.animate(
        [
          { opacity: 0, transform: "translateY(6px)" },
          { opacity: 1, transform: "translateY(0px)" },
        ],
        { duration: 260, easing: "ease-out" }
      );
    };
  }
  if (roleText && roles.length > 1) setInterval(swapRole, 2600);

  // Project search + featured filter
  const search = document.getElementById("projectSearch");
  const featuredBtn = document.getElementById("onlyFeatured");
  const cards = Array.from(document.querySelectorAll("#projectGrid .project"));
  let featuredOnly = false;

  function applyFilters() {
    const q = (search?.value || "").trim().toLowerCase();
    for (const c of cards) {
      const title = c.getAttribute("data-title") || "";
      const stack = c.getAttribute("data-stack") || "";
      const isFeatured = (c.getAttribute("data-featured") || "0") === "1";
      const okQ = !q || title.includes(q) || stack.includes(q);
      const okF = !featuredOnly || isFeatured;
      c.style.display = okQ && okF ? "" : "none";
    }
  }

  if (search) search.addEventListener("input", applyFilters);
  if (featuredBtn) {
    featuredBtn.addEventListener("click", () => {
      featuredOnly = !featuredOnly;
      featuredBtn.style.borderColor = featuredOnly ? "rgba(34,211,238,.35)" : "";
      featuredBtn.style.background = featuredOnly ? "rgba(34,211,238,.10)" : "";
      applyFilters();
    });
  }

  // Subtle 3D tilt effect
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!prefersReduced) {
    const tilts = Array.from(document.querySelectorAll(".tilt"));
    const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

    for (const el of tilts) {
      el.addEventListener("mousemove", (ev) => {
        const r = el.getBoundingClientRect();
        const px = (ev.clientX - r.left) / r.width;
        const py = (ev.clientY - r.top) / r.height;
        const rx = clamp((0.5 - py) * 10, -10, 10);
        const ry = clamp((px - 0.5) * 10, -10, 10);
        el.style.setProperty("--mx", `${px * 100}%`);
        el.style.setProperty("--my", `${py * 100}%`);
        el.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-1px)`;
      });
      el.addEventListener("mouseleave", () => {
        el.style.transform = "";
      });
    }
  }
})();
