(()=>{'use strict';function button(el,fn){if(!el)return;el.setAttribute('role','button');el.tabIndex=0;el.addEventListener('click',fn);el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fn(e)}})}function init(){document.querySelectorAll('.navbar').forEach(nav=>{const open=nav.querySelector('.menu-open-button'),close=nav.querySelector('.menu-close-button'),menu=nav.querySelector('.nav-menu-content');if(!menu)return;const set=(v,focus=true)=>{nav.classList.toggle('fexiva-nav-open',v);open?.setAttribute('aria-expanded',String(v));if(focus)(v?close:open)?.focus()};button(open,()=>set(true));button(close,()=>set(false));set(false,false);nav.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('fexiva-nav-open'))set(false)});menu.querySelectorAll('a[href]').forEach(a=>a.addEventListener('click',()=>set(false,false)));window.addEventListener('resize',()=>{if(innerWidth>=992)set(false,false)})});document.querySelectorAll('.w-tabs').forEach((tabs,index)=>{const links=[...tabs.querySelectorAll(':scope > .w-tab-menu .w-tab-link')],panes=[...tabs.querySelectorAll(':scope > .w-tab-content > .w-tab-pane')];const set=key=>{links.forEach((a,i)=>{const active=a.dataset.wTab===key;a.classList.toggle('w--current',active);a.setAttribute('aria-selected',String(active));a.tabIndex=active?0:-1});panes.forEach(p=>{const active=p.dataset.wTab===key;p.classList.toggle('w--tab-active',active);p.hidden=!active})};links.forEach((a,i)=>{a.setAttribute('role','tab');a.id='fexiva-tab-'+index+'-'+i;const p=panes.find(p=>p.dataset.wTab===a.dataset.wTab);if(p){p.id=a.id+'-pane';p.setAttribute('role','tabpanel');p.setAttribute('aria-labelledby',a.id);a.setAttribute('aria-controls',p.id)}a.addEventListener('click',e=>{e.preventDefault();set(a.dataset.wTab)});a.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End','Enter',' '].includes(e.key)){e.preventDefault();let n=e.key==='Home'?0:e.key==='End'?links.length-1:e.key==='ArrowLeft'?(i+links.length-1)%links.length:e.key==='ArrowRight'?(i+1)%links.length:i;set(links[n].dataset.wTab);links[n].focus()}})});tabs.querySelector('.w-tab-menu')?.setAttribute('role','tablist');set(tabs.dataset.current||links[0]?.dataset.wTab)});document.querySelectorAll('.faq-item').forEach((item,i)=>{const q=item.querySelector('.faq-question'),a=item.querySelector('.faq-answer');if(!q||!a)return;a.id='fexiva-faq-'+i;item.setAttribute('aria-controls',a.id);const set=v=>{item.classList.toggle('fexiva-open',v);item.setAttribute('aria-expanded',String(v));a.hidden=!v};button(item,()=>set(!item.classList.contains('fexiva-open')));set(false)});document.querySelectorAll('.w-slider').forEach(s=>{const slides=[...s.querySelectorAll('.w-slider-mask > .w-slide')];if(!slides.length)return;let n=0;const show=i=>{n=(i+slides.length)%slides.length;slides.forEach((x,j)=>{x.classList.toggle('fexiva-active',j===n);x.hidden=j!==n});};button(s.querySelector('.w-slider-arrow-left'),()=>show(n-1));button(s.querySelector('.w-slider-arrow-right'),()=>show(n+1));show(0)});document.querySelectorAll('.section_header a[href]').forEach(a=>{if(a.href.replace(/\/$/,'')===location.href.split(/[?#]/)[0].replace(/\/$/,'')){a.classList.add('w--current');a.setAttribute('aria-current','page')}})}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()})();

// Static site only: prevent any personal data from being sent to a missing backend.
document.addEventListener('submit',function(e){const f=e.target;if(!f.matches('form[data-static-form]'))return;e.preventDefault();let p=f.querySelector('.fexiva-static-status');if(!p){p=document.createElement('p');p.className='fexiva-static-status';p.setAttribute('role','status');f.append(p)}p.hidden=false;p.textContent='This preview is not connected to a submission service. No data has been sent.';});

document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-static-submit]').forEach(b=>{b.type='submit'});});

// Offline entrance, scroll reveal, number counters, and accessible transitions.
(()=>{'use strict';function motion(){const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;const selectors='[hero-title],[page-load-1],[page-load-2],[page-load-3],[page-load-4],[reveal-anim-1],[reveal-anim-2],[reveal-anim-3],[reveal-anim-4],[reveal-anim-5],[reveal-2s]';if(!reduced&&'IntersectionObserver'in window){document.documentElement.classList.add('fx-motion-ready');const observer=new IntersectionObserver(entries=>{entries.forEach(({target,isIntersecting})=>{if(!isIntersecting)return;target.classList.remove('fx-wait');target.classList.add('fx-enter');observer.unobserve(target)})},{rootMargin:'0px 0px 30px 0px',threshold:0});document.querySelectorAll(selectors).forEach(el=>{if(el.closest('a')||el.closest('[hidden]'))return;const attr=[...el.attributes].find(x=>/^(page-load|reveal-anim)-[1-5]$/.test(x.name));el.style.setProperty('--fx-delay',((attr?Number(attr.name.slice(-1)):1)-1)*70+'ms');if(el.getBoundingClientRect().top<innerHeight)el.classList.add('fx-enter');else{el.classList.add('fx-wait');observer.observe(el)}});const count=new IntersectionObserver(entries=>{entries.forEach(({target,isIntersecting})=>{if(!isIntersecting)return;count.unobserve(target);const el=target.firstElementChild||target, original=el.textContent.trim(),m=original.match(/^([^0-9.-]*)([0-9.,-]+)(.*)$/);if(!m)return;const n=Number(m[2].replace(/,/g,''));if(!Number.isFinite(n))return;const decimals=(m[2].split('.')[1]||'').length, start=performance.now();function tick(t){const p=Math.min((t-start)/1800,1),v=n*(1-Math.pow(1-p,3));el.textContent=p===1?original:m[1]+(m[2].includes(',')?v.toLocaleString('en-US',{minimumFractionDigits:decimals,maximumFractionDigits:decimals}):v.toFixed(decimals))+m[3];if(p<1)requestAnimationFrame(tick)}requestAnimationFrame(tick)})},{threshold:.1});document.querySelectorAll('[data-counter]').forEach(x=>count.observe(x))}document.querySelectorAll('.w-slider').forEach(s=>{const slides=[...s.querySelectorAll('.w-slider-mask > .w-slide')],nav=s.querySelector('.w-slider-nav');if(!slides.length)return;let touch=0;const active=()=>slides.findIndex(x=>x.classList.contains('fexiva-active'));const change=()=>{slides.forEach((x,i)=>{x.classList.toggle('fx-slide-enter',i===active());if(nav?.children[i]){nav.children[i].classList.toggle('w-active',i===active());nav.children[i].setAttribute('aria-pressed',String(i===active()))}})};if(nav){nav.replaceChildren();slides.forEach((_,i)=>{let d=document.createElement('button');d.type='button';d.className='w-slider-dot';d.setAttribute('aria-label','Show testimonial '+(i+1));d.addEventListener('click',()=>{let steps=(i-active()+slides.length)%slides.length;while(steps--)s.querySelector('.w-slider-arrow-right')?.click()});nav.append(d)})}new MutationObserver(change).observe(s.querySelector('.w-slider-mask'),{subtree:true,attributes:true,attributeFilter:['hidden']});change();s.addEventListener('touchstart',e=>{touch=e.changedTouches[0].clientX},{passive:true});s.addEventListener('touchend',e=>{const delta=e.changedTouches[0].clientX-touch;if(Math.abs(delta)>45)s.querySelector(delta>0?'.w-slider-arrow-left':'.w-slider-arrow-right')?.click()},{passive:true})});document.querySelectorAll('.w-tab-content,.faq-item').forEach(x=>{new MutationObserver(entries=>entries.forEach(({target})=>{if(!target.hidden){target.classList.remove('fx-slide-enter');void target.offsetWidth;target.classList.add('fx-slide-enter')}})).observe(x,{subtree:true,attributes:true,attributeFilter:['hidden']})});}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',motion);else motion()})();


// Original Fexiva Lottie artwork, progressively enhanced when internet is available.
// The existing local SVG/CSS illustrations remain visible until each animation is ready.
(() => {
  'use strict';
  const origin = 'https://cdn.prod.website-files.com/6aa7a9e9eb79fb41eaaa8184/';
  const artwork = {
    'saving-chart': '6ac7cfba2f4070164c7c432f_03-saving-chart.json',
    'global-transfer': '6ac7cfc021341b8f42f24ed3_11-global-transfer.json',
    'card-stack': '6ac7d5fad2ef10eade1e86a2_02-card-stack.json',
    'add-card': '6ac7cfc131ec8a5fb05bbf18_01-add-card.json',
    'accounts-home': '6ac7cfc06b0fa2c1f901e5b5_10-accounts-home.json',
    'instant-swap': '6ac7cfbebc4dd4ef4a1aebeb_08-instant-swap.json',
    'virtual-cards': '6ac7cfc1f09bec2a6cdccf45_12-virtual-cards.json',
    'transactions': '6ac7cfbf71fb8d75504aafce_09-transactions.json',
    'integration-network': '6aa9192d57dd0d71a7e71b4f_cortexa-integration%20(1).json',
    'home-balance': '6ac7cfbea290be8d55604f57_07-home-balance.json',
    'transfer-amount': '6ac7cfbe2a9c9db0e77bfc38_06-transfer-amount.json',
    'transfer-completed': '6ac7cfbbb04500c9ba1cbcb6_05-transfer-completed.json',
    'history-chart': '6ac7cfbaf09bec2a6cdccca0_04-history-chart.json'
  };
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const players = new Set();
  let playerPromise;
  function getPlayer() {
    if (window.lottie && typeof window.lottie.loadAnimation === 'function') return Promise.resolve(window.lottie);
    if (!playerPromise) playerPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js';
      script.async = true;
      const timer = setTimeout(() => {
        script.remove();
        reject(new Error('Lottie player timed out'));
      }, 10000);
      script.onload = () => {
        clearTimeout(timer);
        if (window.lottie && typeof window.lottie.loadAnimation === 'function') resolve(window.lottie);
        else reject(new Error('Lottie player unavailable'));
      };
      script.onerror = () => {
        clearTimeout(timer);
        script.remove();
        reject(new Error('Lottie player could not load'));
      };
      document.head.append(script);
    });
    return playerPromise;
  }
  async function enhance(element) {
    if (motionPreference.matches || element.dataset.originalAnimationState) return;
    element.dataset.originalAnimationState = 'loading';
    let host, animation, timeout;
    let previousPosition;
    const fallback = Array.from(element.children).map(child => [child, child.style.visibility]);
    let stopped = false;
    const restore = () => {
      if (stopped) return;
      stopped = true;
      clearTimeout(timeout);
      if (animation) { players.delete(animation); try { animation.destroy(); } catch (_) {} }
      if (host) host.remove();
      fallback.forEach(([child, visibility]) => { child.style.visibility = visibility; });
      if (previousPosition !== undefined) element.style.position = previousPosition;
      element.dataset.originalAnimationState = 'fallback';
    };
    try {
      const lottie = await getPlayer();
      if (motionPreference.matches || !element.isConnected) { restore(); return; }
      if (getComputedStyle(element).position === 'static') {
        previousPosition = element.style.position;
        element.style.position = 'relative';
      }
      host = document.createElement('div');
      host.className = 'fx-original-lottie';
      host.setAttribute('aria-hidden', 'true');
      host.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;visibility:hidden;pointer-events:none;overflow:hidden;';
      element.append(host);
      animation = lottie.loadAnimation({
        container: host,
        renderer: 'svg',
        loop: true,
        autoplay: false,
        path: origin + artwork[element.dataset.offlineAnimation],
        rendererSettings: { preserveAspectRatio: 'xMidYMid meet' }
      });
      players.add(animation);
      timeout = setTimeout(restore, 15000);
      animation.addEventListener('data_failed', restore);
      animation.addEventListener('error', restore);
      animation.addEventListener('DOMLoaded', () => {
        if (stopped) return;
        clearTimeout(timeout);
        if (motionPreference.matches) { restore(); return; }
        host.style.visibility = 'visible';
        fallback.forEach(([child]) => { child.style.visibility = 'hidden'; });
        element.dataset.originalAnimationState = 'ready';
        animation.goToAndPlay(0, true);
      });
    } catch (_) { restore(); }
  }
  function initialize() {
    if (motionPreference.matches) return;
    const elements = Array.from(document.querySelectorAll('[data-offline-animation]')).filter(element => Object.prototype.hasOwnProperty.call(artwork, element.dataset.offlineAnimation));
    if (!elements.length) return;
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          observer.unobserve(entry.target);
          enhance(entry.target);
        });
      }, { rootMargin: '400px 0px' });
      elements.forEach(element => observer.observe(element));
    } else elements.forEach(enhance);
  }
  motionPreference.addEventListener?.('change', event => {
    players.forEach(animation => { if (event.matches) animation.pause(); else animation.play(); });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
})();
