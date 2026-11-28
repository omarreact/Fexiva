# Fexiva — offline HTML website

Extract the entire ZIP, then double-click `index.html`. No server, build, Node.js, PHP, installation, or internet connection is required for local pages, CSS, JavaScript, images, fonts, and browser-native motion. JavaScript must be enabled in your browser. Keep the folder structure intact.

33 retained HTML pages. Navigation uses relative file links; reusable header/footer reference fragments are not loaded dynamically. Original Switzer fonts are bundled; missing Plus Jakarta Sans is replaced with Switzer. The 13 missing Lottie files are replaced by purpose-specific inline animated SVG/CSS visuals (not exact originals). Scroll reveals, counters, tabs, menu, FAQ, slider arrows/dots/swipe, and reduced-motion preferences are implemented locally. External links still need internet. Contact and newsletter forms validate locally but do not submit to a server. No authentication backend is included. The original Webflow password page is omitted.

Actual file:// browser testing is restricted in the authoring environment; see the separate QA report for isolated local-content tests.

## Run on your local network (Windows)

1. Install Node.js LTS if it is not already installed.
2. Clone or download this repository and keep its folder structure intact.
3. Double-click `start.bat` in the website root, or run `npx --yes http-server@14.1.1 . -a 0.0.0.0 -p 8080 -c-1` from that folder.
4. Open `http://localhost:8080` on your PC. On another device connected to the same trusted LAN, open `http://YOUR-PC-IP:8080` using the IPv4 address printed by the launcher.
5. Keep the server window open; press Ctrl+C to stop it.

The first launch may require internet access to download the server package. If access from other devices fails, ensure both devices share the same network, client isolation is disabled, and Windows Firewall permits TCP port 8080 on the private network only. Do not expose the server to the public internet.

Optional firewall rule (PowerShell as Administrator):

```powershell
New-NetFirewallRule -DisplayName "Fexiva Local Server" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Private -RemoteAddress LocalSubnet
```
