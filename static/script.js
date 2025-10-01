document.addEventListener("DOMContentLoaded", () => {

  // Settings modal
  const settings = document.querySelector(".settings");
  const settingsMenu = document.querySelector(".settings-menu"); // the actual dropdown content

  settings.addEventListener("click", () => settings.classList.toggle("active"));

  // Prevent clicks inside menu from closing it
  settingsMenu?.addEventListener("click", (e) => e.stopPropagation());

  // Theme toggle
  const toggleTheme = document.getElementById("toggle-theme");
  toggleTheme?.addEventListener("click", () => {
    const html = document.documentElement;
    const newTheme = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", newTheme);
    fetch("/update_theme", { method: "POST", body: new URLSearchParams({ theme: newTheme }) });
  });

  // Update cookies
  const updateCookies = document.getElementById("update-cookies");
  updateCookies?.addEventListener("click", () => {
    const user_id = document.getElementById("cookie-id").value;
    const PHPSESSID = document.getElementById("cookie-sess").value;
    fetch("/update_cookies", { method: "POST", body: new URLSearchParams({ user_id, PHPSESSID }) })
      .then(res => res.json())
      .then(res => alert("Cookies updated!"));
  });

  // Episode buttons with service selection
  document.querySelectorAll(".episode-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const url = btn.dataset.url;
      const frameDiv = document.getElementById("service-frame");
      frameDiv.innerHTML = `<div class="loading-spinner"></div>`;
      const res = await fetch("/episode?url=" + encodeURIComponent(url));
      const data = await res.json();
      frameDiv.innerHTML = "";

      function createIframe(src) {
        const iframe = document.createElement("iframe");
        iframe.src = src;
        iframe.width = "100%";
        iframe.height = "450px";
        iframe.allowFullscreen = true;
        iframe.setAttribute("allowfullscreen", "true");
        frameDiv.innerHTML = "";
        frameDiv.appendChild(iframe);

        // Fullscreen button
        const fullBtn = document.createElement("button");
        fullBtn.textContent = "Fullscreen";
        fullBtn.style.marginTop = "10px";
        fullBtn.style.padding = "8px 12px";
        fullBtn.style.borderRadius = "8px";
        fullBtn.style.border = "none";
        fullBtn.style.background = "#9b59b6";
        fullBtn.style.color = "#fff";
        fullBtn.addEventListener("click", () => {
          if (iframe.requestFullscreen) iframe.requestFullscreen();
          else if (iframe.webkitRequestFullscreen) iframe.webkitRequestFullscreen();
          else if (iframe.msRequestFullscreen) iframe.msRequestFullscreen();
        });
        frameDiv.appendChild(fullBtn);
      }

      if (data.links.length > 1) {
        const select = document.createElement("select");
        select.style.padding = "10px";
        select.style.borderRadius = "12px";
        select.style.marginBottom = "10px";
        data.links.forEach(link => {
          const option = document.createElement("option");
          option.value = link.url;
          option.textContent = link.host;
          select.appendChild(option);
        });
        const playBtn = document.createElement("button");
        playBtn.textContent = "Play Selected";
        playBtn.style.marginLeft = "10px";
        playBtn.style.padding = "10px 15px";
        playBtn.style.borderRadius = "12px";
        playBtn.style.border = "none";
        playBtn.style.background = "#9b59b6";
        playBtn.style.color = "#fff";
        playBtn.addEventListener("click", () => createIframe(select.value));
        frameDiv.appendChild(select);
        frameDiv.appendChild(playBtn);
      } else if (data.links.length === 1) {
        createIframe(data.links[0].url);
      }
    });
  });

});
