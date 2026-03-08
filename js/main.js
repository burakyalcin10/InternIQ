// ========== InternIQ Main JavaScript ==========

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initAnimations();
  initMobileMenu();

  // Page-specific
  if (document.getElementById('listings-container')) {
    renderListings(internshipListings);
    initFilters();
  }
  if (document.getElementById('companies-container')) {
    renderCompanies(companyData);
  }
  if (document.getElementById('chat-messages')) {
    initMockInterview();
  }
  if (document.getElementById('cv-output')) {
    initCVTailoring();
  }
  if (document.getElementById('roadmap-container')) {
    renderRoadmap(weeklyRoadmap);
  }
});

// ========== Navbar ==========
function initNavbar() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.style.borderBottomColor = window.scrollY > 30
      ? 'rgba(255,255,255,0.1)'
      : 'rgba(255,255,255,0.07)';
  });
}

// ========== Mobile Menu ==========
function initMobileMenu() {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', () => links.classList.toggle('open'));
  links.querySelectorAll('a').forEach(a =>
    a.addEventListener('click', () => links.classList.remove('open'))
  );
}

// ========== Scroll Animations ==========
function initAnimations() {
  const observer = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
  );
  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// ========== Listings ==========
function renderListings(listings) {
  const container = document.getElementById('listings-container');
  if (!container) return;

  container.innerHTML = listings.map(l => {
    const matchClass = l.matchScore >= 85 ? 'match-high' : l.matchScore >= 70 ? 'match-mid' : 'match-low';
    return `
    <div class="listing-row" data-type="${l.type}">
      <div class="listing-main">
        <div class="listing-icon">${l.logo}</div>
        <div>
          <div class="listing-title">${l.position}</div>
          <div class="listing-company">${l.company}</div>
        </div>
      </div>
      <span class="listing-loc">${l.location}</span>
      <span class="listing-type">${l.type}</span>
      <span class="listing-match ${matchClass}">${l.matchScore}%</span>
    </div>`;
  }).join('');
}

// ========== Filters ==========
function initFilters() {
  const search = document.getElementById('filter-search');
  const type = document.getElementById('filter-type');
  const btn = document.getElementById('filter-btn');
  const apply = () => {
    const s = (search?.value || '').toLowerCase();
    const t = type?.value || 'all';
    renderListings(internshipListings.filter(l => {
      const ms = !s || l.position.toLowerCase().includes(s) || l.company.toLowerCase().includes(s) || l.tags.some(tag => tag.toLowerCase().includes(s));
      const mt = t === 'all' || l.type === t;
      return ms && mt;
    }));
  };
  btn?.addEventListener('click', apply);
  search?.addEventListener('input', apply);
  type?.addEventListener('change', apply);
}

// ========== Companies ==========
function renderCompanies(companies) {
  const container = document.getElementById('companies-container');
  if (!container) return;

  container.innerHTML = companies.map(c => `
    <div class="company-card">
      <div class="company-top">
        <div class="company-avatar">${c.logo}</div>
        <div>
          <div class="company-name">${c.name}</div>
          <div class="company-type">${c.industry} · ${c.employees} çalışan</div>
        </div>
      </div>
      <div class="company-stat-row">
        <div class="c-stat"><span class="c-stat-val">${c.rating}</span><span class="c-stat-label">Rating</span></div>
        <div class="c-stat"><span class="c-stat-val">${c.employees}</span><span class="c-stat-label">Çalışan</span></div>
        <div class="c-stat"><span class="c-stat-val">${c.techStack.length}+</span><span class="c-stat-label">Stack</span></div>
      </div>
      <div class="company-info"><strong>Kültür:</strong> ${c.culture}</div>
      <div class="company-info"><strong>Mülakat:</strong> ${c.interviewStyle}</div>
      <div class="company-info" style="color:var(--text-3); font-size:0.8rem; margin-top:8px;">${c.recentNews}</div>
      <div class="tag-row">${c.techStack.map(t => `<span class="tag">${t}</span>`).join('')}</div>
    </div>
  `).join('');
}

// ========== Mock Interview ==========
function initMockInterview() {
  const messagesDiv = document.getElementById('chat-messages');
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');
  const categoryBtns = document.querySelectorAll('.interview-category-btn');

  let currentQuestions = mockInterviewQuestions.technical;
  let questionIndex = 0;

  categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      categoryBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentQuestions = mockInterviewQuestions[btn.dataset.category] || mockInterviewQuestions.technical;
      questionIndex = 0;
      messagesDiv.innerHTML = '';
      addBot(`${btn.dataset.category === 'technical' ? 'Teknik' : 'Davranışsal'} mülakat modunu seçtiniz. "Başla" yazarak başlayın.`);
    });
  });

  addBot('Mock Interview\'a hoş geldiniz. Bir kategori seçin ve "Başla" yazarak mülakata başlayın.');

  function addBot(text) {
    const d = document.createElement('div');
    d.className = 'chat-msg bot';
    d.textContent = text;
    messagesDiv.appendChild(d);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function addUser(text) {
    const d = document.createElement('div');
    d.className = 'chat-msg user';
    d.textContent = text;
    messagesDiv.appendChild(d);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function handleSend() {
    const text = input.value.trim();
    if (!text) return;
    addUser(text);
    input.value = '';

    setTimeout(() => {
      if (text.toLowerCase() === 'başla' || text.toLowerCase() === 'basla') {
        questionIndex = 0;
        const q = currentQuestions[0];
        addBot(`Soru ${questionIndex + 1}/${currentQuestions.length} [${q.category} · ${q.difficulty}]\n\n${q.question}`);
      } else if (questionIndex < currentQuestions.length) {
        addBot(generateFeedback(text, currentQuestions[questionIndex]));
        questionIndex++;
        if (questionIndex < currentQuestions.length) {
          setTimeout(() => {
            const q = currentQuestions[questionIndex];
            addBot(`Soru ${questionIndex + 1}/${currentQuestions.length} [${q.category} · ${q.difficulty}]\n\n${q.question}`);
          }, 1200);
        } else {
          setTimeout(() => addBot('Tüm soruları tamamladınız. Tekrar "Başla" yazarak yeniden başlayabilirsiniz.'), 1200);
        }
      } else {
        addBot('"Başla" yazarak yeni bir mülakat başlatabilirsiniz.');
      }
    }, 600);
  }

  sendBtn?.addEventListener('click', handleSend);
  input?.addEventListener('keypress', e => { if (e.key === 'Enter') handleSend(); });
}

function generateFeedback(answer, question) {
  const len = answer.length;
  if (len < 20) return `Cevabınız çok kısa. ${question.category} alanında daha detaylı yanıt bekleniyor.`;
  if (len < 80) return `İyi bir başlangıç. Somut bir proje deneyimiyle desteklerseniz daha güçlü olur.`;
  return `Kapsamlı ve detaylı bir cevap. Mülakatta da bu netlikte ifade ederseniz güçlü bir izlenim bırakırsınız.`;
}

// ========== CV Tailoring ==========
function initCVTailoring() {
  const btn = document.getElementById('cv-submit');
  const textarea = document.getElementById('cv-textarea');
  const output = document.getElementById('cv-output');

  btn?.addEventListener('click', () => {
    if (!textarea?.value?.trim()) {
      showToast('Lütfen ilan açıklamasını yapıştırın.');
      return;
    }

    btn.textContent = 'Analiz ediliyor...';
    btn.disabled = true;

    setTimeout(() => {
      const score = Math.floor(Math.random() * 25) + 70;
      const borderColor = score >= 85 ? 'var(--green)' : 'var(--amber)';
      output.innerHTML = `
        <h3>Analiz Sonuçları</h3>
        <div class="cv-score-box">
          <div class="score-ring" style="border-color:${borderColor}; color:${borderColor};">${score}</div>
          <div>
            <div class="score-label">ATS Uyumluluk Skoru</div>
            <div class="score-sub">CV'niz bu ilan ile ${score}% eşleşiyor</div>
          </div>
        </div>
        <div style="font-size:0.85rem; font-weight:500; margin-bottom:10px;">Öneriler</div>
        ${cvSuggestions.map(s => `
          <div class="suggestion">
            <span class="s-icon">${s.icon}</span>
            <span>${s.text}</span>
          </div>
        `).join('')}
      `;
      btn.textContent = 'CV\'yi Analiz Et';
      btn.disabled = false;
    }, 1800);
  });
}

// ========== Roadmap ==========
function renderRoadmap(items) {
  const container = document.getElementById('roadmap-container');
  if (!container) return;

  container.innerHTML = items.map(item => `
    <div class="tl-item">
      <span class="tl-week">${item.week}</span>
      <h3>${item.title}</h3>
      <p>${item.description}</p>
      <div style="margin-top:10px;">
        <span class="bento-tag">${item.tech}</span>
      </div>
    </div>
  `).join('');
}

// ========== Toast ==========
function showToast(msg) {
  const existing = document.querySelector('.toast-msg');
  if (existing) existing.remove();
  const t = document.createElement('div');
  t.className = 'toast-msg';
  t.textContent = msg;
  t.style.cssText = `
    position:fixed; bottom:24px; right:24px; padding:12px 20px;
    border-radius:8px; background:var(--bg-elevated); border:1px solid var(--border);
    color:var(--text); font-size:0.85rem; z-index:9999;
    animation: fadeUp 0.25s ease-out;
  `;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 3000);
}
