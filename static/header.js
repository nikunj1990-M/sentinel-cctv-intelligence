// Shared header/nav bar for the Sentinel dashboard pages (map, cameras, audit).
async function renderHeader(containerId, activePage) {
  const container = document.getElementById(containerId);
  let user;
  try {
    const res = await fetch("/me");
    if (!res.ok) { window.location.href = "/login.html"; return; }
    user = await res.json();
  } catch (e) {
    window.location.href = "/login.html";
    return;
  }
  const pages = [
    { key: "map", label: "Map", href: "/" },
    { key: "cameras", label: "Cameras", href: "/cameras.html" },
  ];
  if (user.role === "admin") {
    pages.push({ key: "audit", label: "Audit Log", href: "/audit.html" });
  }
  const navHtml = pages.map(p =>
    `<a class="nav" href="${p.href}" style="${p.key === activePage ? "color:#fff;font-weight:600" : ""}">${p.label}</a>`
  ).join("");
  container.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #232c3d;margin-bottom:12px">
      <div>${navHtml}</div>
      <div style="font-size:12px;color:#8aa0b6">
        ${user.username} (${user.role}) <a id="logoutLink" href="#" style="color:#ff6b6b;margin-left:8px">Logout</a>
      </div>
    </div>`;
  document.getElementById("logoutLink").addEventListener("click", async (e) => {
    e.preventDefault();
    await fetch("/logout", { method: "POST" });
    window.location.href = "/login.html";
  });
  return user;
}
