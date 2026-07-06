/* BCMAEP site behavior: progress tracking (localStorage only), sample-item quizzes,
   knowledge-check enhancements, and responsive navigation. No network calls. */
(function () {
  'use strict';

  var STORE_KEY = 'bcmaep.progress.v1';
  var MODULE_COUNT = 15;

  function readProgress() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      var data = raw ? JSON.parse(raw) : {};
      return (data && typeof data === 'object') ? data : {};
    } catch (e) { return {}; }
  }

  function writeProgress(data) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); } catch (e) { /* storage unavailable */ }
  }

  function moduleIds() {
    var ids = [];
    for (var i = 1; i <= MODULE_COUNT; i++) ids.push('m' + String(i).padStart(2, '0'));
    return ids;
  }

  function completedCount(progress) {
    return moduleIds().filter(function (id) { return progress[id]; }).length;
  }

  function firstIncomplete(progress) {
    var ids = moduleIds();
    for (var i = 0; i < ids.length; i++) {
      if (!progress[ids[i]]) return i + 1;
    }
    return null;
  }

  function rootPrefix() {
    return document.body.classList.contains('page-lesson') ? '../' : '';
  }

  function moduleHref(n) {
    return rootPrefix() + 'modules/module-' + String(n).padStart(2, '0') + '.html';
  }

  // ------------------------------------------------------------------
  // Render progress state into the page
  // ------------------------------------------------------------------
  function renderProgress() {
    var progress = readProgress();
    var done = completedCount(progress);
    var pct = Math.round((done / MODULE_COUNT) * 100);

    // Sidebar checkmarks
    document.querySelectorAll('.snav-module[data-module]').forEach(function (a) {
      a.classList.toggle('is-complete', !!progress[a.getAttribute('data-module')]);
    });

    // Sidebar progress bar
    var bar = document.getElementById('snav-progress-bar');
    var text = document.getElementById('snav-progress-text');
    if (bar) bar.style.width = pct + '%';
    if (text) text.textContent = done + ' of ' + MODULE_COUNT + ' modules complete';

    // Curriculum page panel
    var fill = document.getElementById('progress-fill');
    var summary = document.getElementById('progress-summary');
    if (fill) fill.style.width = pct + '%';
    if (summary) {
      summary.textContent = done === 0
        ? 'No modules completed yet. Progress is stored in this browser only.'
        : done + ' of ' + MODULE_COUNT + ' modules complete (' + pct + '%).';
    }

    // Curriculum module checks
    document.querySelectorAll('[data-check]').forEach(function (el) {
      var isDone = !!progress[el.getAttribute('data-check')];
      el.textContent = isDone ? 'Completed' : '';
      el.classList.toggle('is-complete', isDone);
    });

    // Continue buttons
    var next = firstIncomplete(progress);
    ['continue-btn', 'hero-continue'].forEach(function (id) {
      var btn = document.getElementById(id);
      if (!btn) return;
      if (next === null) {
        btn.textContent = 'All modules complete: open the capstone';
        btn.setAttribute('href', rootPrefix() + 'capstone.html');
      } else if (done > 0 || id === 'continue-btn') {
        btn.textContent = done > 0 ? ('Continue with module ' + next) : 'Start module 1';
        btn.setAttribute('href', moduleHref(next));
      }
    });

    // Mark-complete button state on lesson pages
    document.querySelectorAll('[data-complete]').forEach(function (btn) {
      var id = btn.getAttribute('data-complete');
      var isDone = !!progress[id];
      btn.classList.toggle('is-complete', isDone);
      var n = parseInt(id.slice(1), 10);
      btn.textContent = isDone ? ('Module ' + n + ' completed') : ('Mark module ' + n + ' as complete');
      var status = btn.parentElement.querySelector('.lesson-complete-status');
      if (status) status.textContent = isDone ? 'Saved in this browser. Select again to undo.' : '';
    });
  }

  // ------------------------------------------------------------------
  // Mark complete
  // ------------------------------------------------------------------
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('[data-complete]');
    if (!btn) return;
    var progress = readProgress();
    var id = btn.getAttribute('data-complete');
    if (progress[id]) delete progress[id]; else progress[id] = true;
    writeProgress(progress);
    renderProgress();
  });

  // ------------------------------------------------------------------
  // Export / import / reset progress (curriculum page)
  // ------------------------------------------------------------------
  var exportBtn = document.getElementById('progress-export');
  if (exportBtn) {
    exportBtn.addEventListener('click', function () {
      var blob = new Blob([JSON.stringify({ key: STORE_KEY, progress: readProgress() }, null, 2)], { type: 'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'bcmaep-progress.json';
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    });
  }

  var importBtn = document.getElementById('progress-import');
  if (importBtn) {
    importBtn.addEventListener('click', function () {
      var input = document.createElement('input');
      input.type = 'file';
      input.accept = 'application/json,.json';
      input.addEventListener('change', function () {
        var file = input.files && input.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function () {
          try {
            var data = JSON.parse(String(reader.result));
            var progress = (data && data.progress && typeof data.progress === 'object') ? data.progress : null;
            if (!progress) throw new Error('bad format');
            writeProgress(progress);
            renderProgress();
          } catch (e) {
            var summary = document.getElementById('progress-summary');
            if (summary) summary.textContent = 'Import failed: the file was not a valid progress export.';
          }
        };
        reader.readAsText(file);
      });
      input.click();
    });
  }

  var resetBtn = document.getElementById('progress-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      if (resetBtn.getAttribute('data-armed') === '1') {
        writeProgress({});
        resetBtn.removeAttribute('data-armed');
        resetBtn.textContent = 'Reset';
        renderProgress();
      } else {
        resetBtn.setAttribute('data-armed', '1');
        resetBtn.textContent = 'Select again to confirm reset';
        setTimeout(function () {
          resetBtn.removeAttribute('data-armed');
          resetBtn.textContent = 'Reset';
        }, 4000);
      }
    });
  }

  // ------------------------------------------------------------------
  // Sample-item quizzes (assessment page)
  // ------------------------------------------------------------------
  document.querySelectorAll('.quiz-item').forEach(function (item) {
    var correct = item.getAttribute('data-correct');
    var feedback = item.querySelector('.quiz-feedback');
    var verdict = item.querySelector('.quiz-verdict');
    item.querySelectorAll('.quiz-option').forEach(function (opt) {
      opt.addEventListener('click', function () {
        var chosen = opt.getAttribute('data-key');
        item.querySelectorAll('.quiz-option').forEach(function (o) {
          o.classList.remove('is-chosen');
          o.classList.toggle('is-correct', o.getAttribute('data-key') === correct);
        });
        opt.classList.add('is-chosen');
        item.classList.add('is-answered');
        if (feedback) feedback.hidden = false;
        if (verdict) {
          verdict.textContent = (chosen === correct)
            ? 'Correct: ' + correct + '.'
            : 'Not correct. You selected ' + chosen + '; the correct answer is ' + correct + '.';
          verdict.className = 'quiz-verdict ' + ((chosen === correct) ? 'is-right' : 'is-wrong');
        }
      });
    });
  });

  // ------------------------------------------------------------------
  // Sidebar toggle (small screens)
  // ------------------------------------------------------------------
  var toggle = document.getElementById('nav-toggle');
  var sidebarEl = document.getElementById('sidebar');
  function closeNav() {
    document.body.classList.remove('nav-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }
  if (toggle && sidebarEl) {
    toggle.addEventListener('click', function (ev) {
      ev.stopPropagation();
      var open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Click on the scrim (anywhere outside the sidebar) closes the menu.
    document.addEventListener('click', function (ev) {
      if (!document.body.classList.contains('nav-open')) return;
      if (sidebarEl.contains(ev.target) || toggle.contains(ev.target)) return;
      closeNav();
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') closeNav();
    });
  }

  renderProgress();
})();
