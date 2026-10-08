'use strict';

/* ── Hamburger nav toggle ─────────────────────────────────── */
(function () {
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
    // Animate hamburger → X
    const spans = toggle.querySelectorAll('span');
    if (open) {
      spans[0].style.transform = 'translateY(7px) rotate(45deg)';
      spans[1].style.opacity   = '0';
      spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
    } else {
      spans[0].style.transform = '';
      spans[1].style.opacity   = '';
      spans[2].style.transform = '';
    }
  });

  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!toggle.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.querySelectorAll('span').forEach(s => {
        s.style.transform = ''; s.style.opacity = '';
      });
    }
  });
})();


/* ── Auto-dismiss flash alerts (4 s) ─────────────────────── */
(function () {
  document.querySelectorAll('.alert').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s ease, transform .4s ease';
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(-6px)';
      setTimeout(function () { el.remove(); }, 420);
    }, 4000);
  });
})();


/* ── Client-side password match (register) ───────────────── */
(function () {
  const pw  = document.getElementById('password');
  const cpw = document.getElementById('confirm_password');
  if (!pw || !cpw) return;
  function check() {
    cpw.setCustomValidity(cpw.value && pw.value !== cpw.value ? 'Passwords do not match.' : '');
  }
  pw.addEventListener('input', check);
  cpw.addEventListener('input', check);
})();


/* ── Live client-side table search ───────────────────────── */
(function () {
  const input = document.querySelector('.search-bar input[name="q"]');
  const tbody = document.querySelector('.table tbody');
  if (!input || !tbody || input.value.trim()) return; // skip if server query active

  input.addEventListener('input', function () {
    const q = this.value.toLowerCase().trim();
    tbody.querySelectorAll('tr').forEach(function (row) {
      row.style.display = (!q || row.textContent.toLowerCase().includes(q)) ? '' : 'none';
    });
  });
})();


/* ── Mark active nav link ─────────────────────────────────── */
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function (a) {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
})();
