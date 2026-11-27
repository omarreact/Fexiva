"""Create a staging-only mirror from the original Fexiva template.
The production tree is not modified by this program.
"""
import base64, hashlib, json, mimetypes, os, re, functools, threading, tempfile
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops, ImageStat

ORIGIN="https://fexiva.webflow.io/"
ROOT=Path("parity-candidate")
QA=Path("parity-evidence")
ROOT.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
HOSTS={"fexiva.webflow.io","cdn.prod.website-files.com","assets.website-files.com","uploads-ssl.webflow.com","d3e54v103j8qbb.cloudfront.net","unpkg.com","fonts.googleapis.com","fonts.gstatic.com","ajax.googleapis.com","cdn.jsdelivr.net","cdnjs.cloudflare.com"}
s=requests.Session()
s.headers["User-Agent"]="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
report={"source":ORIGIN,"routes":[],"resources":{},"animations":[],"failures":[],"online_checks":[],"mode":"online-http","form_backend":"not configured; submission blocked to protect visitor data","comparisons":[]}
cache={}
def save():
    (QA/"report.json").write_text(json.dumps(report,indent=2))
def fetch(url, allow404=False):
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname not in HOSTS:
        raise ValueError("Unexpected source URL: "+url)
    if url in cache:
        return cache[url]
    r=s.get(url,timeout=35,allow_redirects=False)
    if r.is_redirect:
        raise ValueError("Unexpected redirect: "+url)
    if not (r.ok or (allow404 and r.status_code==404)):
        r.raise_for_status()
    if len(r.content)>30_000_000:
        raise ValueError("Resource too large: "+url)
    cache[url]=r
    return r
def relative(path,page):
    return os.path.relpath(path,page.parent).replace(os.sep,"/")
def resource(value):
    return bool(value) and not value.startswith(("data:","#","blob:","javascript:"))
def data_uri(data,kind):
    return "data:"+kind.split(";")[0]+";base64,"+base64.b64encode(data).decode()
def css(text,base,dest):
    def repl(m):
        val=m.group(2).strip()
        return 'url("'+relative(localize(urljoin(base,val)),dest)+'")' if resource(val) else m.group(0)
    text=re.sub(r"""url\(\s*(['"]?)(.*?)\1\s*\)""",repl,text,flags=re.I)
    return re.sub(r"""@import\s+["']([^"']+)["']""",lambda m:'@import "'+relative(localize(urljoin(base,m.group(1))),dest)+'"',text,flags=re.I)
def localize(url):
    url=url.split("#")[0]
    if url in report["resources"]:
        return ROOT/report["resources"][url]["path"]
    r=fetch(url)
    kind=r.headers.get("Content-Type","").split(";")[0]
    name=re.sub(r"[^A-Za-z0-9._-]","-",unquote(Path(urlsplit(url).path).name) or "resource")
    ext=Path(name).suffix.lower()
    if kind=="text/css":
        folder,ext="css",".css"
    elif ext==".js" or "javascript" in kind:
        folder,ext="js",".js"
    elif ext in (".woff",".woff2",".otf",".ttf") or "font" in kind:
        folder="fonts"
    else:
        folder="media"
    ext=ext or mimetypes.guess_extension(kind) or ".bin"
    dest=ROOT/"assets"/folder/(hashlib.sha256(url.encode()).hexdigest()[:12]+"-"+Path(name).stem[:85]+ext)
    dest.parent.mkdir(parents=True,exist_ok=True)
    report["resources"][url]={"path":str(dest.relative_to(ROOT)),"source_sha256":hashlib.sha256(r.content).hexdigest()}
    if folder=="css":
        dest.write_text(css(r.text,url,dest),encoding="utf-8")
    else:
        dest.write_bytes(r.content)
    return dest
def lottie(url):
    r=fetch(url)
    doc=r.json()
    if not all(k in doc for k in ("layers","fr","ip","op")):
        raise ValueError("Invalid Lottie: "+url)
    for a in doc.get("assets",[]):
        if a.get("p") and not a["p"].startswith("data:"):
            image=fetch(urljoin(url,a.get("u","")+a["p"]))
            a.update(p=data_uri(image.content,image.headers.get("Content-Type","image/png")),u="",e=1)
    dest=ROOT/"assets"/"animations"/(hashlib.sha256(url.encode()).hexdigest()[:12]+"-"+re.sub(r"[^A-Za-z0-9._-]","-",unquote(Path(urlsplit(url).path).name)))
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(doc,separators=(",",":")),encoding="utf-8")
    return dest
paths=[Path("index.html"),Path("404.html")]+sorted(Path("inner-pages").rglob("*.html"))
assert len(paths)==33, "Unexpected local page count"
routes={("/" if p.name=="index.html" else "/"+str(p).removeprefix("inner-pages/").removesuffix(".html")):p for p in paths}
def nav(value,base,dest):
    if not resource(value) or value.startswith(("mailto:","tel:")):
        return value
    u=urlsplit(urljoin(base,value))
    if u.hostname!="fexiva.webflow.io":
        return value
    route=(u.path.rstrip("/") or "/").removesuffix(".html")
    if route=="/index":
        route="/"
    if route in routes:
        return relative(ROOT/routes[route],dest)+("?" + u.query if u.query else "")+("#"+u.fragment if u.fragment else "")
    return value
def build(route,p):
    url=urljoin(ORIGIN,route)
    response=fetch(url,route=="/404")
    soup=BeautifulSoup(response.text,"html.parser")
    assert soup.body and soup.title, "Invalid page: "+url
    dest=ROOT/p
    dest.parent.mkdir(parents=True,exist_ok=True)
    for tag in list(soup.find_all("script")):
        src=tag.get("src","")
        code=tag.string or tag.get_text()
        if "app-validator" in src or "review.js" in src or "__WF_REVIEW_BRIDGE" in code:
            tag.decompose()
            continue
        if src and "webfont" in src.lower():
            tag.decompose()
            continue
        if src:
            tag["src"]=relative(localize(urljoin(url,src)),dest)
            tag.attrs.pop("integrity",None)
            tag.attrs.pop("crossorigin",None)
        elif "WebFont.load" in code:
            families=re.findall(r'"([^"]+:[0-9,]+)"',code)
            if not families:
                raise ValueError("Unknown WebFont declaration")
            for family in families:
                font=localize("https://fonts.googleapis.com/css?family="+family.replace(" ","+"))
                link=soup.new_tag("link",rel="stylesheet",href=relative(font,dest))
                link["data-localized"]="true"
                tag.insert_before(link)
            tag.decompose()
    for tag in list(soup.find_all("link")):
        rel=tag.get("rel",[])
        if any(x in rel for x in ("preconnect","dns-prefetch","prefetch","prerender")):
            tag.decompose()
            continue
        href=tag.get("href")
        if resource(href) and not tag.has_attr("data-localized") and any(x in rel for x in ("stylesheet","icon","apple-touch-icon","preload","modulepreload")):
            tag["href"]=relative(localize(urljoin(url,href)),dest)
            tag.attrs.pop("integrity",None)
            tag.attrs.pop("crossorigin",None)
    for tag in soup.find_all(True):
        if tag.name!="script":
            for attr in ("src","poster"):
                val=tag.get(attr)
                if isinstance(val,str) and resource(val):
                    tag[attr]=relative(localize(urljoin(url,val)),dest)
        if tag.get("srcset") and not tag["srcset"].startswith("data:"):
            result=[]
            for item in tag["srcset"].split(","):
                bits=item.strip().split()
                if bits:
                    result.append(" ".join([relative(localize(urljoin(url,bits[0])),dest),*bits[1:]]))
            tag["srcset"]=", ".join(result)
        if tag.get("style"):
            tag["style"]=css(tag["style"],url,dest)
        if tag.name=="a" and tag.get("href"):
            tag["href"]=nav(tag["href"],url,dest)
        if tag.get("data-animation-type")=="lottie":
            src=urljoin(url,tag["data-src"])
            tag["data-src"]=relative(lottie(src),dest)
            report["animations"].append({"page":str(p),"url":src,"sha256":hashlib.sha256(cache[src].content).hexdigest()})
    for style in soup.find_all("style"):
        if style.string:
            style.string.replace_with(css(str(style.string),url,dest))
    guard=soup.new_tag("script")
    guard.string="document.addEventListener('submit',function(e){if(e.target.tagName==='FORM'){e.preventDefault();e.stopImmediatePropagation();let p=e.target.querySelector('[data-offline-notice]');if(!p){p=document.createElement('p');p.setAttribute('data-offline-notice','');p.setAttribute('role','status');e.target.append(p)}p.textContent='Form service has not been configured. No data was sent.'}},true);"
    soup.head.insert(0,guard)
    if p==Path("inner-pages/instructions.html"):
        style=soup.new_tag("style")
        style.string="@media(max-width:479px){.instructions-code,.w-code-block{max-width:100%;min-width:0;overflow-x:auto;white-space:pre-wrap;overflow-wrap:anywhere}}"
        soup.head.append(style)
    if p==Path("inner-pages/about.html"):
        style=soup.new_tag("style")
        style.string="@media(max-width:359px){.section_header,.section_header *{min-width:0}.section_header img{max-width:100%;height:auto}.heading-style-1,.heading-style-2,.heading-style-3{overflow-wrap:anywhere}}"
        soup.head.append(style)
    dest.write_text(str(soup),encoding="utf-8")
    if p==Path("index.html"):
        parts=ROOT/"parts"
        parts.mkdir(exist_ok=True)
        header=soup.select_one(".w-nav")
        footer=soup.select_one("footer")
        if header and footer:
            (parts/"header.html").write_text(str(header),encoding="utf-8")
            (parts/"footer.html").write_text(str(footer),encoding="utf-8")
    report["routes"].append({"path":str(p),"url":url,"status":response.status_code})
def qa():
    # Use a real HTTP origin and the same /Fexiva/ prefix as GitHub Pages.
    # No server is required for the actual hosted static website.
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp)/"Fexiva").symlink_to(ROOT.resolve(),target_is_directory=True)
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self,*args):
                pass
        server=ThreadingHTTPServer(("127.0.0.1",0),functools.partial(QuietHandler,directory=tmp))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        host="http://127.0.0.1:"+str(server.server_port)+"/Fexiva/"
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                for w in (320,390,768,1024,1440,1920):
                    ctx=browser.new_context(viewport={"width":w,"height":900},offline=False)
                    # Never transmit form data or analytics POSTs to the template owner.
                    ctx.route("**/*",lambda route: route.continue_() if route.request.method in ("GET","HEAD","OPTIONS") else route.abort())
                    for p in paths:
                        page=ctx.new_page()
                        errors,external,bad=[],[],[]
                        page.on("pageerror",lambda e:errors.append(str(e)))
                        page.on("request",lambda r:external.append(r.url) if not r.url.startswith(host) and r.url.startswith(("http:","https:")) else None)
                        page.on("requestfailed",lambda r:bad.append({"url":r.url,"kind":r.resource_type,"error":r.failure,"method":r.method}))
                        page.on("response",lambda r:bad.append({"url":r.url,"kind":r.request.resource_type,"status":r.status,"method":r.request.method}) if r.status>=400 else None)
                        page.goto(host+str(p),wait_until="load",timeout=45000)
                        page.wait_for_timeout(1600)
                        result=page.evaluate("""() => ({width:document.documentElement.scrollWidth,visible:!!document.body.innerText.trim(),broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src')),lottie_count:document.querySelectorAll('[data-animation-type=lottie]').length,rendered_lottie:document.querySelectorAll('[data-animation-type=lottie] svg,[data-animation-type=lottie] canvas').length,overflow:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+2&&getComputedStyle(e).position!=='fixed').slice(0,15).map(e=>({tag:e.tagName,cls:String(e.className).slice(0,150),right:Math.round(e.getBoundingClientRect().right)}))})""")
                        required=[x for x in bad if x["method"] in ("GET","HEAD") and (x["url"].startswith(host) or x["kind"] in ("image","stylesheet","font","script")) and not x["url"].startswith("https://challenges.cloudflare.com/")]
                        row={"page":str(p),"width":w,"result":result,"js_errors":errors,"external_requests":external,"network_failures":bad,"required_failures":required}
                        report["online_checks"].append(row)
                        if not result["visible"] or result["width"]>w+2 or result["broken"] or errors or required or result["rendered_lottie"]<result["lottie_count"]:
                            report["failures"].append(row)
                        if p in (Path("index.html"),Path("inner-pages/features.html"),Path("inner-pages/about.html")) and w in (390,1440):
                            name=p.stem+"-"+str(w)
                            page.screenshot(path=str(QA/(name+"-candidate.png")))
                            live=browser.new_page(viewport={"width":w,"height":900})
                            live.route("**/*",lambda route:route.continue_() if route.request.method in ("GET","HEAD","OPTIONS") else route.abort())
                            try:
                                live.goto(urljoin(ORIGIN,next(r for r,v in routes.items() if v==p)),wait_until="load",timeout=45000)
                                live.wait_for_timeout(1600)
                                live.screenshot(path=str(QA/(name+"-original.png")))
                                a=Image.open(QA/(name+"-candidate.png")).convert("RGB")
                                b=Image.open(QA/(name+"-original.png")).convert("RGB")
                                report["comparisons"].append({"page":str(p),"width":w,"mean_rgb_difference":ImageStat.Stat(ImageChops.difference(a,b)).mean,"note":"Animation phases may differ; manual visual review still required."})
                            except Exception as e:
                                report["failures"].append({"page":str(p),"live_comparison":str(e)})
                            finally:
                                live.close()
                        page.close()
                    ctx.close()
                    save()
                browser.close()
        finally:
            server.shutdown()

try:
    for route,p in routes.items():
        build(route,p)
        save()
    if len(report["animations"])!=13:
        raise ValueError("Original animation count changed: "+str(len(report["animations"])))
    qa()
    if report["failures"]:
        raise RuntimeError("Unresolved online or visual QA failures")
    (ROOT/"README.md").write_text("Fexiva online original-template parity candidate for GitHub Pages. Original scripts retained in dependency order and Lottie JSON is hosted locally. Form backend not configured; no visitor data is sent. Review QA evidence before release.\n")
except Exception as e:
    report["failures"].append(str(e))
    print(json.dumps({"summary": {"pages":len(report["routes"]),"animations":len(report["animations"]),"online_checks":len(report["online_checks"]),"failures":len(report["failures"])}, "first_failures":report["failures"][:5]},indent=2)[:18000])
    raise
finally:
    save()
