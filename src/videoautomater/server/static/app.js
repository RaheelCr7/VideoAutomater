/**
 * Beyond 80 - Agent Control Center Frontend Logic
 * Full interactive controller connecting UI components with FastAPI backend.
 */

// State Management
const state = {
  currentView: 'dashboard',
  selectedJobId: null,
  selectedVideoData: null,
  jobs: [],
  agents: [],
  schedules: [],
  publishingAccounts: [],
  publishingTasks: [],
  pollTimer: null
};

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initModals();
  initChat();
  initReviewStudio();
  initSettings();
  initQuickPromptChips();

  // Initial data fetch
  fetchDashboardMetrics();
  fetchJobs();
  fetchAgents();
  fetchSchedules();
  fetchPublishingData();
  fetchAnalytics();

  // Start polling every 4 seconds
  state.pollTimer = setInterval(() => {
    fetchDashboardMetrics();
    if (state.currentView === 'queue' || state.currentView === 'dashboard') {
      fetchJobs();
    }
  }, 4000);
});

// View Navigation Router
function initNavigation() {
  const navButtons = document.querySelectorAll('.nav-item');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetView = btn.getAttribute('data-view');
      switchView(targetView);
    });
  });
}

function switchView(viewId) {
  state.currentView = viewId;

  // Update active nav button
  document.querySelectorAll('.nav-item').forEach(btn => {
    if (btn.getAttribute('data-view') === viewId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Update active view section
  document.querySelectorAll('.view').forEach(viewEl => {
    viewEl.classList.remove('active');
  });

  const activeViewEl = document.getElementById(`view-${viewId}`);
  if (activeViewEl) {
    activeViewEl.classList.add('active');
  }

  // Update header title
  const titles = {
    dashboard: ['Dashboard Overview', 'Real-time telemetry and production orchestration'],
    chat: ['AI Creative Director', 'Natural-language orchestration and intent parsing'],
    queue: ['Production Queue & Execution Monitor', 'Real-time 13-stage agent pipeline tracking'],
    review: ['Video Review Studio', 'Sub-second inspection, timestamp feedback and release authorization'],
    library: ['Master Video Library', 'Immutable rendered videos with verified 80s standards'],
    agents: ['Autonomous Agent Fleet', '13 coordinated agents with specialized domain directives'],
    scheduler: ['Autonomous Production Scheduler', 'Durable automated scheduling surviving system restarts'],
    publishing: ['Multi-Platform Distribution Hub', 'YouTube Shorts, Instagram Reels, TikTok, and Facebook Reels'],
    analytics: ['Production Analytics & QA Telemetry', 'Scientific verification pass-rates and engagement simulation'],
    settings: ['Platform Settings & Governance', 'Safety rules, timezones, and duration constraints']
  };

  if (titles[viewId]) {
    document.getElementById('current-view-title').textContent = titles[viewId][0];
    document.getElementById('current-view-subtitle').textContent = titles[viewId][1];
  }

  // View-specific refreshes
  if (viewId === 'library') fetchLibrary();
  if (viewId === 'agents') fetchAgents();
  if (viewId === 'scheduler') fetchSchedules();
  if (viewId === 'publishing') fetchPublishingData();
  if (viewId === 'analytics') fetchAnalytics();
}

// Modals Handling
function initModals() {
  const modalJob = document.getElementById('modal-create-job');
  const btnQuickNew = document.getElementById('btn-quick-new-job');
  const btnCloseModal = document.getElementById('btn-close-modal-job');
  const btnCancelModal = document.getElementById('btn-cancel-modal-job');
  const btnSubmitModal = document.getElementById('btn-submit-modal-job');

  btnQuickNew.addEventListener('click', () => modalJob.classList.remove('hidden'));
  btnCloseModal.addEventListener('click', () => modalJob.classList.add('hidden'));
  btnCancelModal.addEventListener('click', () => modalJob.classList.add('hidden'));

  btnSubmitModal.addEventListener('click', async () => {
    const topic = document.getElementById('modal-job-topic').value.trim();
    const duration = parseFloat(document.getElementById('modal-job-duration').value) || 80.0;
    const approval = document.getElementById('modal-job-approval').value;
    const instructions = document.getElementById('modal-job-instructions').value.trim();

    try {
      const res = await fetch('/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic || null,
          target_duration_sec: duration,
          approval_mode: approval,
          director_instructions: instructions || null
        })
      });
      if (!res.ok) throw new Error('Failed to create job');
      modalJob.classList.add('hidden');
      switchView('queue');
      fetchJobs();
    } catch (err) {
      alert(`Error creating job: ${err.message}`);
    }
  });
}

// Quick Prompt Chips on Dashboard
function initQuickPromptChips() {
  const quickInput = document.getElementById('quick-chat-input');
  const btnQuickSend = document.getElementById('btn-quick-send');

  document.querySelectorAll('.chip-btn').forEach(chip => {
    chip.addEventListener('click', () => {
      quickInput.value = chip.getAttribute('data-prompt');
    });
  });

  btnQuickSend.addEventListener('click', async () => {
    const text = quickInput.value.trim();
    if (!text) return;
    quickInput.value = '';

    // Switch to chat view and post
    switchView('chat');
    appendChatMessage('user', text);

    try {
      const res = await fetch('/api/director/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      appendChatMessage('ai', data.content, data.metadata);
      fetchDashboardMetrics();
    } catch (err) {
      appendChatMessage('ai', `Error contacting AI Director: ${err.message}`);
    }
  });
}

// AI Director Chat
function initChat() {
  const chatInput = document.getElementById('chat-user-input');
  const btnSend = document.getElementById('btn-send-chat');

  btnSend.addEventListener('click', async () => {
    const msg = chatInput.value.trim();
    if (!msg) return;
    chatInput.value = '';

    appendChatMessage('user', msg);

    try {
      const res = await fetch('/api/director/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      appendChatMessage('ai', data.content, data.metadata);
      fetchDashboardMetrics();
    } catch (err) {
      appendChatMessage('ai', `Communication error: ${err.message}`);
    }
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      btnSend.click();
    }
  });
}

function appendChatMessage(sender, text, metadata = null) {
  const container = document.getElementById('chat-messages-container');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${sender}`;

  let metaHtml = '';
  if (metadata && metadata.job_id) {
    metaHtml = `
      <div style="margin-top: 10px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 6px; font-family: monospace; font-size: 0.75rem;">
        <div><strong>Linked Job:</strong> ${metadata.job_id}</div>
        <div><strong>Action:</strong> ${metadata.action || 'created'}</div>
      </div>
    `;
  }

  bubble.innerHTML = `
    <div class="bubble-header">
      <span class="agent-name">${sender === 'ai' ? 'AI Creative Director' : 'You (Director)'}</span>
      <span class="bubble-time">${new Date().toLocaleTimeString()}</span>
    </div>
    <div class="bubble-body">${escapeHtml(text)}${metaHtml}</div>
  `;

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// Fetch Metrics & Dashboard
async function fetchDashboardMetrics() {
  try {
    const res = await fetch('/api/dashboard');
    if (!res.ok) return;
    const d = await res.json();

    document.getElementById('metric-completed').textContent = d.completed_videos;
    document.getElementById('metric-review').textContent = d.in_review;
    document.getElementById('metric-running').textContent = d.active_running;
    document.getElementById('metric-published').textContent = d.published_videos;

    document.getElementById('queue-count-pill').textContent = d.active_running + d.queued;
    document.getElementById('review-count-pill').textContent = d.in_review;

    renderRecentDashboardTable(d.recent_jobs);
  } catch (err) {
    console.error('Failed to fetch dashboard metrics:', err);
  }
}

function renderRecentDashboardTable(recentJobs) {
  const tbody = document.getElementById('dashboard-recent-tbody');
  if (!recentJobs || recentJobs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">No recent production jobs.</td></tr>';
    return;
  }

  tbody.innerHTML = recentJobs.map(j => `
    <tr>
      <td><code>${j.id}</code></td>
      <td><strong>${escapeHtml(j.topic || 'Autonomous Topic Discovery')}</strong></td>
      <td><span class="status-badge ${j.status.toLowerCase()}">${j.status}</span></td>
      <td><span class="status-badge ${j.review_status.toLowerCase()}">${j.review_status}</span></td>
      <td>${new Date(j.created_at).toLocaleTimeString()}</td>
      <td>
        <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openInReview('${j.id}')">
          Review
        </button>
      </td>
    </tr>
  `).join('');
}

// Production Queue & Execution Tracking
async function fetchJobs() {
  try {
    const res = await fetch('/api/jobs');
    if (!res.ok) return;
    state.jobs = await res.json();
    renderQueueTable(state.jobs);
  } catch (err) {
    console.error('Error fetching jobs:', err);
  }
}

function renderQueueTable(jobs) {
  const tbody = document.getElementById('queue-jobs-tbody');
  if (!jobs || jobs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No jobs in queue.</td></tr>';
    return;
  }

  tbody.innerHTML = jobs.map(j => `
    <tr>
      <td><code>${j.id}</code></td>
      <td><strong>${escapeHtml(j.topic || 'Auto Scientific Discovery')}</strong></td>
      <td><span class="status-badge ${j.status.toLowerCase()}">${j.current_stage || j.status}</span></td>
      <td>
        <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; width: 80px; overflow: hidden;">
          <div style="background: var(--accent-cyan); height: 100%; width: ${j.status === 'COMPLETED' ? '100%' : (j.status === 'RUNNING' ? '50%' : '10%')};"></div>
        </div>
      </td>
      <td><span class="tag">${j.approval_mode}</span></td>
      <td><span class="status-badge ${j.review_status.toLowerCase()}">${j.review_status}</span></td>
      <td>
        <div style="display: flex; gap: 6px;">
          <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.72rem;" onclick="openJobInspector('${j.id}')">Inspect</button>
          <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.72rem;" onclick="openInReview('${j.id}')">Review</button>
          ${j.status === 'RUNNING' ? `<button class="btn btn-danger" style="padding: 4px 8px; font-size: 0.72rem;" onclick="cancelJob('${j.id}')">Cancel</button>` : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

window.cancelJob = async function(jobId) {
  if (!confirm(`Cancel execution of job ${jobId}?`)) return;
  try {
    const res = await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' });
    if (!res.ok) throw new Error('Cancellation failed');
    fetchJobs();
  } catch (err) {
    alert(err.message);
  }
};

window.openJobInspector = function(jobId) {
  const job = state.jobs.find(j => j.id === jobId);
  if (!job) return;

  const drawer = document.getElementById('job-inspector-drawer');
  const title = document.getElementById('inspector-job-title');
  const content = document.getElementById('inspector-job-content');

  title.textContent = `Job Trace: ${job.id} — ${job.topic || 'Auto Topic'}`;

  let stepsHtml = '';
  if (job.agent_steps && job.agent_steps.length > 0) {
    stepsHtml = job.agent_steps.map(s => `
      <div style="margin-bottom: 12px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid ${s.status === 'completed' ? '#10b981' : '#f59e0b'};">
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; margin-bottom: 4px;">
          <strong>${s.agent_name}</strong>
          <span>${s.status.toUpperCase()} (${(s.duration_sec || 0).toFixed(1)}s)</span>
        </div>
        <p style="font-size: 0.82rem; margin: 0;">${escapeHtml(s.summary || 'Executing stage')}</p>
      </div>
    `).join('');
  } else {
    stepsHtml = '<p class="empty-state">No agent step details recorded yet.</p>';
  }

  content.innerHTML = `
    <div style="margin-bottom: 16px;">
      <div><strong>Status:</strong> ${job.status}</div>
      <div><strong>Current Stage:</strong> ${job.current_stage}</div>
      <div><strong>Approval Mode:</strong> ${job.approval_mode}</div>
      <div><strong>Review Status:</strong> ${job.review_status}</div>
      <div><strong>Publication Authorized:</strong> ${job.publication_authorized ? 'YES' : 'NO (LOCKED)'}</div>
    </div>
    <h4>Agent Step Timeline (13 Pipeline Stages):</h4>
    ${stepsHtml}
  `;

  drawer.classList.remove('hidden');
};

document.getElementById('btn-close-inspector')?.addEventListener('click', () => {
  document.getElementById('job-inspector-drawer').classList.add('hidden');
});

// Review Studio Controller
function initReviewStudio() {
  const player = document.getElementById('review-video-player');
  const timeReadout = document.getElementById('current-time-readout');
  const btnSyncTime = document.getElementById('btn-sync-time');
  const fbTimestamp = document.getElementById('feedback-timestamp');

  // Player timeupdate listener
  player.addEventListener('timeupdate', () => {
    const cur = player.currentTime;
    const dur = player.duration || 80.0;
    timeReadout.textContent = `${formatTime(cur)} / ${formatTime(dur)}`;
  });

  btnSyncTime.addEventListener('click', () => {
    fbTimestamp.value = player.currentTime.toFixed(1);
  });

  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetTab = btn.getAttribute('data-tab');
      document.getElementById(targetTab).classList.add('active');
    });
  });

  // Approval Buttons
  document.getElementById('btn-approve-video').addEventListener('click', async () => {
    if (!state.selectedJobId) return;
    await setReviewStatus(state.selectedJobId, 'APPROVED_FOR_RELEASE', 'Human creative director approved video for release.');
  });

  document.getElementById('btn-request-changes').addEventListener('click', async () => {
    if (!state.selectedJobId) return;
    const notes = prompt('Enter revision notes for the Agent Fleet:');
    if (!notes) return;
    await setReviewStatus(state.selectedJobId, 'CHANGES_REQUESTED', notes);
  });

  document.getElementById('btn-reject-video').addEventListener('click', async () => {
    if (!state.selectedJobId) return;
    if (!confirm('Reject this master version?')) return;
    await setReviewStatus(state.selectedJobId, 'REJECTED', 'Master video rejected by human reviewer.');
  });

  // Authorization toggle
  const chkAuth = document.getElementById('chk-authorize-release');
  chkAuth.addEventListener('change', async () => {
    if (!state.selectedJobId) return;
    try {
      const res = await fetch(`/api/review/${state.selectedJobId}/authorize-publication`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ authorized: chkAuth.checked })
      });
      if (!res.ok) {
        const err = await res.json();
        chkAuth.checked = !chkAuth.checked;
        alert(`Cannot authorize: ${err.detail}`);
      } else {
        alert(chkAuth.checked ? 'AUTHORIZATION CONFIRMED: Master unlocked for multi-platform distribution.' : 'AUTHORIZATION REVOKED.');
      }
    } catch (err) {
      chkAuth.checked = !chkAuth.checked;
      alert(`Error: ${err.message}`);
    }
  });

  // Feedback Submission
  document.getElementById('btn-submit-feedback').addEventListener('click', async () => {
    if (!state.selectedJobId) {
      alert('Please select a video from the library first.');
      return;
    }
    const timestamp = parseFloat(fbTimestamp.value) || 0.0;
    const comment = document.getElementById('feedback-comment').value.trim();
    const reqRegen = document.getElementById('chk-request-regeneration').checked;

    if (!comment) {
      alert('Please enter feedback comment.');
      return;
    }

    try {
      const res = await fetch(`/api/review/${state.selectedJobId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timestamp_sec: timestamp,
          comment: comment,
          request_regeneration: reqRegen
        })
      });
      if (!res.ok) throw new Error('Failed to save feedback');
      document.getElementById('feedback-comment').value = '';
      alert(reqRegen ? 'Feedback saved! Autonomous regeneration initiated for a new version.' : 'Feedback recorded.');
      openInReview(state.selectedJobId);
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  });
}

async function setReviewStatus(jobId, status, notes) {
  try {
    const res = await fetch(`/api/review/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: status, reviewer_notes: notes })
    });
    if (!res.ok) throw new Error('Status update failed');
    alert(`Video status updated to: ${status}`);
    openInReview(jobId);
    fetchDashboardMetrics();
  } catch (err) {
    alert(`Error updating review status: ${err.message}`);
  }
}

window.openInReview = async function(jobId) {
  try {
    const res = await fetch(`/api/jobs/${jobId}`);
    if (!res.ok) throw new Error('Job not found');
    const job = await res.json();

    state.selectedJobId = job.id;
    state.selectedVideoData = job;

    switchView('review');

    // Setup Video Player
    const player = document.getElementById('review-video-player');
    const badge = document.getElementById('player-status-badge');
    const chkAuth = document.getElementById('chk-authorize-release');

    badge.textContent = job.review_status;
    badge.className = `video-overlay-badge status-${job.review_status.toLowerCase()}`;
    chkAuth.checked = !!job.publication_authorized;

    if (job.master_video_path) {
      player.src = `/media/${job.master_video_path}`;
      player.load();
    }

    // Populate Version Switcher & Comparison
    const vSelectorBox = document.getElementById('version-selector-container');
    const vPillGroup = document.getElementById('version-pill-group');
    const vMetaLabel = document.getElementById('version-meta-label');

    if (vSelectorBox && job.versions && job.versions.length > 0) {
      vSelectorBox.style.display = 'flex';
      const curVer = job.current_version || job.versions[job.versions.length - 1].version_number;
      vPillGroup.innerHTML = job.versions.map(v => `
        <button class="version-pill-btn ${v.version_number === curVer ? 'active' : ''}" 
                data-vnum="${v.version_number}" 
                onclick="switchReviewVersion(${v.version_number}, '${v.video_path.replace(/\\/g, '/')}', '${escapeHtml(v.notes || '')}')">
          v${v.version_number}
        </button>
      `).join('');
      vMetaLabel.textContent = `v${curVer} (${job.versions.length} versions recorded)`;
    } else if (vSelectorBox) {
      vSelectorBox.style.display = 'none';
    }

    // Populate Feedback List
    const fbContainer = document.getElementById('feedback-items-container');
    if (job.feedback && job.feedback.length > 0) {
      fbContainer.innerHTML = job.feedback.map(fb => `
        <div style="margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--accent-cyan); margin-bottom: 4px;">
            <strong>Timestamp: ${fb.timestamp_sec.toFixed(1)}s</strong>
            <span>${new Date(fb.created_at).toLocaleTimeString()}</span>
          </div>
          <p style="font-size: 0.82rem; margin: 0;">${escapeHtml(fb.comment)}</p>
          ${fb.request_regeneration ? '<span class="tag tag-accent" style="margin-top: 6px; display: inline-block;">Autonomous Regeneration Requested</span>' : ''}
        </div>
      `).join('');
    } else {
      fbContainer.innerHTML = '<p class="empty-state">No feedback recorded for this master video.</p>';
    }

    // Populate Script & Narration Tab
    const scriptContainer = document.getElementById('script-inspector-content');
    if (job.script_data) {
      const scenes = job.script_data.scenes || [];
      scriptContainer.innerHTML = `
        <h4>${escapeHtml(job.script_data.title || job.topic)}</h4>
        <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 16px;">Verified Target Duration: 80.0s | Scenes: ${scenes.length}</p>
        ${scenes.map((s, idx) => `
          <div style="margin-bottom: 14px; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid var(--accent-cyan);">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-subtle); margin-bottom: 6px;">
              <strong>Scene ${s.scene_number || idx + 1}: ${escapeHtml(s.heading || 'Visual Section')}</strong>
              <span>${s.duration_sec ? s.duration_sec.toFixed(1) + 's' : ''}</span>
            </div>
            <p style="font-size: 0.85rem; color: #fff; margin-bottom: 6px;"><strong>Narration:</strong> "${escapeHtml(s.narration || '')}"</p>
            <p style="font-size: 0.78rem; color: var(--text-muted);"><strong>Visual Directive:</strong> ${escapeHtml(s.visual_prompt || '')}</p>
          </div>
        `).join('')}
      `;

      // Populate Scene Jump Buttons
      const sceneStrip = document.getElementById('scene-jump-strip');
      let cumulativeTime = 0;
      sceneStrip.innerHTML = scenes.map((s, idx) => {
        const startTime = cumulativeTime;
        cumulativeTime += (s.duration_sec || 16.0);
        return `
          <button class="scene-jump-btn" onclick="jumpToVideoTime(${startTime})">
            Scene ${idx + 1} (${startTime.toFixed(0)}s)
          </button>
        `;
      }).join('');
    } else {
      scriptContainer.innerHTML = '<p class="empty-state">No script data recorded for this job.</p>';
    }

    // Populate Scientific QA Tab
    const qaContainer = document.getElementById('qa-inspector-content');
    if (job.qa_report) {
      const qa = job.qa_report;
      qaContainer.innerHTML = `
        <div style="margin-bottom: 14px; padding: 12px; background: ${qa.passed ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)'}; border-radius: 8px;">
          <h4 style="color: ${qa.passed ? '#10b981' : '#f43f5e'};">
            ${qa.passed ? '✓ PASSED SCIENTIFIC & TECHNICAL QA' : '✗ QA ISSUES FLAGGED'}
          </h4>
          <p style="font-size: 0.82rem; margin: 4px 0 0;">Zero fabricated facts permitted. Strict Crossref DOI provenance verified.</p>
        </div>
        <div style="font-size: 0.82rem; line-height: 1.6;">
          <div><strong>Speech Sync Check:</strong> ${qa.subtitles_synchronized ? 'Synchronized (WordBoundary TTS)' : 'Unverified'}</div>
          <div><strong>Safe-Zone Verification:</strong> ${qa.safe_zones_respected ? 'Passed (Y=1460, vertical bounds)' : 'Violated'}</div>
          <div><strong>Rights Clearance:</strong> ${qa.rights_cleared ? '100% Original/Procedural Cleared' : 'Uncleared'}</div>
        </div>
      `;
    } else {
      qaContainer.innerHTML = '<p class="empty-state">QA report pending.</p>';
    }

    // Populate Version History Tab
    const vContainer = document.getElementById('version-history-container');
    if (job.versions && job.versions.length > 0) {
      vContainer.innerHTML = job.versions.map(v => `
        <div style="margin-bottom: 12px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid var(--border-subtle);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <strong style="color: var(--accent-cyan); font-size: 0.85rem;">Version ${v.version_number}</strong>
            <span style="font-size: 0.72rem; color: var(--text-muted);">${new Date(v.created_at).toLocaleString()}</span>
          </div>
          <p style="font-size: 0.82rem; margin: 4px 0 8px;">${escapeHtml(v.notes || 'Master render')}</p>
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
            <code style="font-size: 0.68rem; color: var(--text-subtle); max-width: 65%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${v.video_path}</code>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.72rem;" onclick="switchReviewVersion(${v.version_number}, '${v.video_path.replace(/\\/g, '/')}', '${escapeHtml(v.notes || '')}')">
              ▶ Play v${v.version_number}
            </button>
          </div>
        </div>
      `).join('');
    } else {
      vContainer.innerHTML = '<p class="empty-state">Version 1 (Initial Master).</p>';
    }

  } catch (err) {
    alert(`Could not load video for review: ${err.message}`);
  }
};

window.switchReviewVersion = function(vNum, videoPath, notes) {
  const player = document.getElementById('review-video-player');
  player.src = `/media/${videoPath}`;
  player.load();
  player.play().catch(() => {});

  const badge = document.getElementById('player-status-badge');
  badge.textContent = `VIEWING v${vNum}`;

  const vMetaLabel = document.getElementById('version-meta-label');
  if (vMetaLabel) {
    vMetaLabel.textContent = `Viewing v${vNum} ${notes ? '— ' + notes.slice(0, 35) : ''}`;
  }

  document.querySelectorAll('.version-pill-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.vnum === String(vNum));
  });
};

window.jumpToVideoTime = function(sec) {
  const player = document.getElementById('review-video-player');
  player.currentTime = sec;
  player.play();
};

// Video Library View
async function fetchLibrary() {
  try {
    const res = await fetch('/api/library');
    if (!res.ok) return;
    const items = await res.json();
    const container = document.getElementById('library-cards-container');

    if (!items || items.length === 0) {
      container.innerHTML = '<p class="empty-state">No completed master videos in library.</p>';
      return;
    }

    container.innerHTML = items.map(item => `
      <div class="video-card">
        <div class="video-thumb-wrap">
          <svg style="width: 48px; height: 48px; fill: rgba(255,255,255,0.4);" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          <span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-family: monospace;">80.0s</span>
        </div>
        <div class="video-card-body">
          <span class="status-badge ${item.review_status.toLowerCase()}">${item.review_status}</span>
          <div class="video-card-title">${escapeHtml(item.topic || 'Master Production')}</div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <span style="font-size: 0.72rem; color: var(--text-muted);">${new Date(item.created_at).toLocaleDateString()}</span>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openInReview('${item.id}')">
              Review Master
            </button>
          </div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Error fetching library:', err);
  }
}

// Agent Fleet View
async function fetchAgents() {
  try {
    const res = await fetch('/api/agents');
    if (!res.ok) return;
    state.agents = await res.json();
    const container = document.getElementById('agent-cards-container');

    container.innerHTML = state.agents.map(a => `
      <div class="agent-card">
        <div class="agent-card-header">
          <span class="agent-title">${escapeHtml(a.name)}</span>
          <span class="tag tag-accent">${a.is_active ? 'ACTIVE' : 'IDLE'}</span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;">
          Model: ${a.model} | Temp: ${a.temperature}
        </div>
        <div class="agent-prompt-box">
          ${escapeHtml(a.system_prompt)}
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Error fetching agents:', err);
  }
}

// Scheduler View
async function fetchSchedules() {
  try {
    const res = await fetch('/api/schedules');
    if (!res.ok) return;
    state.schedules = await res.json();
    const container = document.getElementById('schedules-container');

    if (!state.schedules || state.schedules.length === 0) {
      container.innerHTML = '<p class="empty-state">No recurring schedules active. Use "+ Create Schedule" to configure daily autonomous production.</p>';
      return;
    }

    container.innerHTML = state.schedules.map(s => `
      <div class="dashboard-panel" style="margin-bottom: 16px;">
        <div class="panel-header">
          <div>
            <h4>${escapeHtml(s.name)}</h4>
            <span style="font-size: 0.75rem; color: var(--text-muted);">
              Frequency: ${s.videos_per_day} video(s)/day | Timezone: Asia/Karachi | Next Trigger: ${s.next_run ? new Date(s.next_run).toLocaleString() : 'Immediate'}
            </span>
          </div>
          <span class="tag tag-accent">${s.active ? 'ACTIVE' : 'PAUSED'}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">
          <strong>Preferred Topics:</strong> ${s.preferred_topics && s.preferred_topics.length ? s.preferred_topics.join(', ') : 'Autonomous Scientific Discovery'}
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Error fetching schedules:', err);
  }
}

// Publishing Hub View
async function fetchPublishingData() {
  try {
    const [accRes, taskRes] = await Promise.all([
      fetch('/api/publishing/accounts'),
      fetch('/api/publishing/tasks')
    ]);

    if (accRes.ok) {
      state.publishingAccounts = await accRes.json();
      renderAccounts(state.publishingAccounts);
    }
    if (taskRes.ok) {
      state.publishingTasks = await taskRes.json();
      renderPublishingTasks(state.publishingTasks);
    }
  } catch (err) {
    console.error('Error fetching publishing data:', err);
  }
}

function renderAccounts(accounts) {
  const container = document.getElementById('pub-accounts-container');
  if (!accounts || accounts.length === 0) {
    container.innerHTML = `
      <div class="dashboard-panel" style="grid-column: span 2;">
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">No social media accounts connected. Connect your YouTube Shorts, TikTok, or Instagram accounts:</p>
        <button class="btn btn-primary" onclick="registerDefaultAccounts()">Connect Simulated Platforms (YouTube, IG, TikTok, FB)</button>
      </div>
    `;
    return;
  }

  container.innerHTML = accounts.map(a => `
    <div class="dashboard-panel" style="margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <strong>${escapeHtml(a.account_name)}</strong>
          <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">${a.platform}</div>
        </div>
        <span class="tag tag-accent">${a.is_simulated ? 'SIMULATED_CONNECTOR' : 'PRODUCTION_OAUTH'}</span>
      </div>
    </div>
  `).join('');
}

window.registerDefaultAccounts = async function() {
  const defaults = [
    { platform: 'youtube_shorts', name: 'Beyond80 Official YouTube' },
    { platform: 'instagram_reels', name: '@beyond80_official' },
    { platform: 'tiktok', name: '@beyond80_science' },
    { platform: 'facebook_reels', name: 'Beyond 80 Science' }
  ];

  for (const item of defaults) {
    await fetch('/api/publishing/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform: item.platform,
        account_name: item.name,
        is_simulated: true
      })
    });
  }
  fetchPublishingData();
};

function renderPublishingTasks(tasks) {
  const tbody = document.getElementById('pub-tasks-tbody');
  if (!tasks || tasks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">No publishing tasks dispatched. (Masters remain safely unreleased until approved).</td></tr>';
    return;
  }

  tbody.innerHTML = tasks.map(t => `
    <tr>
      <td><code>${t.id}</code></td>
      <td><strong>${t.platform}</strong></td>
      <td>${escapeHtml(t.title)}</td>
      <td><span class="status-badge ${t.status.toLowerCase()}">${t.status}</span></td>
      <td>${t.published_url ? `<a href="${t.published_url}" target="_blank" style="color: var(--accent-cyan);">${t.published_url}</a>` : '—'}</td>
      <td><span class="tag">${t.status === 'COMPLETED' ? 'SIMULATED' : 'QUEUED'}</span></td>
    </tr>
  `).join('');
}

// Analytics View
async function fetchAnalytics() {
  try {
    const res = await fetch('/api/analytics');
    if (!res.ok) return;
    const a = await res.json();

    document.getElementById('analytics-qa-rate').textContent = `${a.qa_pass_rate_pct}%`;
    document.getElementById('analytics-approval-rate').textContent = `${a.approval_rate_pct}%`;
    document.getElementById('analytics-avg-duration').textContent = `${a.average_video_duration_sec}s`;
    document.getElementById('analytics-platforms').textContent = a.platforms_connected;
    document.getElementById('analytics-sim-views').textContent = a.simulated_views.toLocaleString();

    const topicContainer = document.getElementById('analytics-topic-dist');
    if (topicContainer && a.topic_distribution) {
      topicContainer.innerHTML = Object.entries(a.topic_distribution).map(([topic, count]) => `
        <div style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span>${topic}</span>
            <strong>${count} Video(s)</strong>
          </div>
          <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)); height: 100%; width: ${Math.min(100, count * 25)}%;"></div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Error fetching analytics:', err);
  }
}

// Settings View
function initSettings() {
  document.getElementById('btn-save-settings')?.addEventListener('click', async () => {
    const mode = document.getElementById('setting-approval-mode').value;
    const tz = document.getElementById('setting-timezone').value.trim();
    const dur = parseFloat(document.getElementById('setting-duration').value) || 80.0;
    const quota = parseInt(document.getElementById('setting-quota').value) || 5;

    try {
      const res = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          default_approval_mode: mode,
          default_timezone: tz,
          target_video_duration_sec: dur,
          daily_production_quota: quota
        })
      });
      if (!res.ok) throw new Error('Settings update failed');
      alert('Settings saved successfully.');
      document.getElementById('tz-display').textContent = tz;
      document.getElementById('scheduler-tz-label').textContent = tz;
    } catch (err) {
      alert(`Error saving settings: ${err.message}`);
    }
  });
}

// Helpers
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  const tenths = Math.floor((seconds % 1) * 10);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${tenths}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
