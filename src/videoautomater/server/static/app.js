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

  // Account Modal
  const modalAccount = document.getElementById('modal-create-account');
  const btnNewAccount = document.getElementById('btn-new-account');
  const btnCloseModalAcc = document.getElementById('btn-close-modal-account');
  const btnCancelModalAcc = document.getElementById('btn-cancel-modal-account');
  const btnSubmitModalAcc = document.getElementById('btn-submit-modal-account');
  const selectAccMode = document.getElementById('modal-account-mode');
  const credsGroup = document.getElementById('modal-account-creds-group');

  btnNewAccount?.addEventListener('click', () => modalAccount?.classList.remove('hidden'));
  btnCloseModalAcc?.addEventListener('click', () => modalAccount?.classList.add('hidden'));
  btnCancelModalAcc?.addEventListener('click', () => modalAccount?.classList.add('hidden'));

  selectAccMode?.addEventListener('change', () => {
    if (selectAccMode.value === 'production') {
      credsGroup?.classList.remove('hidden');
    } else {
      credsGroup?.classList.add('hidden');
    }
  });

  btnSubmitModalAcc?.addEventListener('click', async () => {
    const platform = document.getElementById('modal-account-platform').value;
    const accountName = document.getElementById('modal-account-name').value.trim();
    const mode = selectAccMode.value;
    const token = document.getElementById('modal-account-token')?.value.trim() || '';

    if (!accountName) {
      alert('Please enter an account name or channel handle.');
      return;
    }

    try {
      const res = await fetch('/api/publishing/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: platform,
          account_name: accountName,
          is_simulated: mode === 'simulated',
          credentials: token ? { token: token } : null
        })
      });
      if (!res.ok) throw new Error('Failed to register account');
      modalAccount.classList.add('hidden');
      document.getElementById('modal-account-name').value = '';
      if (document.getElementById('modal-account-token')) document.getElementById('modal-account-token').value = '';
      fetchPublishingData();
      alert(`Connected ${accountName} (${platform}) successfully!`);
    } catch (err) {
      alert(`Error connecting account: ${err.message}`);
    }
  });

  // Dispatch Publication Modal
  document.getElementById('btn-close-modal-dispatch')?.addEventListener('click', () => closePublishDispatchModal());
  document.getElementById('btn-cancel-modal-dispatch')?.addEventListener('click', () => closePublishDispatchModal());
  document.getElementById('btn-submit-modal-dispatch')?.addEventListener('click', async () => {
    const jobId = document.getElementById('modal-dispatch-job').value;
    const accountId = document.getElementById('modal-dispatch-account').value;
    const title = document.getElementById('modal-dispatch-title').value.trim();
    const desc = document.getElementById('modal-dispatch-desc').value.trim();
    const rawTags = document.getElementById('modal-dispatch-tags').value.trim();
    const tags = rawTags ? rawTags.split(',').map(t => t.trim()).filter(Boolean) : [];

    if (!jobId || !accountId) {
      alert('Please select both an episode and a destination account.');
      return;
    }

    try {
      if (accountId === 'ALL') {
        const res = await fetch(`/api/publishing/authorize-and-publish?job_id=${encodeURIComponent(jobId)}`, {
          method: 'POST'
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Dispatch failed');
        }
        const data = await res.json();
        closePublishDispatchModal();
        fetchPublishingData();
        fetchDashboardMetrics();
        alert(`SUCCESS! Dispatched to all ${data.results?.length || 4} channels successfully!`);
      } else {
        const res = await fetch('/api/publishing/publish', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            job_id: jobId,
            account_id: accountId,
            title: title,
            description: desc,
            tags: tags,
            auto_authorize: true
          })
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Publishing failed');
        }
        const data = await res.json();
        closePublishDispatchModal();
        fetchPublishingData();
        fetchDashboardMetrics();
        alert(`🚀 BROADCAST SUCCESSFUL!\n\nDestination: ${data.platform}\nTransmission ID: ${data.remote_video_id || 'stream_ok'}\nLive URL: ${data.published_url || 'N/A'}`);
      }
    } catch (err) {
      alert(`Broadcast Dispatch Error: ${err.message}`);
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
    if (!state.jobs || state.jobs.length === 0) {
      const jobsRes = await fetch('/api/jobs');
      if (jobsRes.ok) state.jobs = await jobsRes.json();
    }

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
    renderPublishingHero();
  } catch (err) {
    console.error('Error fetching publishing data:', err);
  }
}

function getActiveMasterJob() {
  if (state.selectedJobId) {
    const j = state.jobs.find(item => item.id === state.selectedJobId);
    if (j) return j;
  }
  const completed = state.jobs.find(item => item.status === 'COMPLETED');
  if (completed) return completed;
  return state.jobs[0] || null;
}

function renderPublishingHero() {
  const heroCard = document.getElementById('pub-hero-card');
  if (!heroCard) return;

  const job = getActiveMasterJob();
  const accCountEl = document.getElementById('pub-account-count');
  if (accCountEl) {
    accCountEl.textContent = (state.publishingAccounts || []).length;
  }

  if (!job) {
    document.getElementById('pub-hero-title').textContent = 'No Master Episodes in Library';
    document.getElementById('pub-hero-desc').textContent = 'Generate an episode from the AI Creative Director or wait for the Autonomous Scheduler.';
    return;
  }

  document.getElementById('pub-hero-title').textContent = job.topic || 'Beyond 80 Master Episode';
  document.getElementById('pub-hero-desc').textContent = job.script_summary || (job.script_data ? job.script_data.selected_hook : '80.0-second standard verified science documentary.');

  const statusBadge = document.getElementById('pub-hero-status');
  if (statusBadge) {
    statusBadge.textContent = job.review_status || 'PENDING_HUMAN_APPROVAL';
    statusBadge.className = `status-badge ${(job.review_status || '').toLowerCase()}`;
  }

  const thumbBox = document.getElementById('pub-hero-thumb');
  if (thumbBox && job.thumbnail_path) {
    const parts = job.thumbnail_path.split('/output/');
    if (parts.length > 1) {
      thumbBox.style.backgroundImage = `url('/media/${parts[1]}')`;
    }
  }
}

window.quickPublishAll = async function() {
  const job = getActiveMasterJob();
  if (!job) {
    alert('No master video found to publish. Please create an episode first.');
    return;
  }

  const btn = document.getElementById('btn-hero-quick-publish');
  const originalText = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '🚀 Dispatching across 4 channels...';
  }

  try {
    const res = await fetch(`/api/publishing/authorize-and-publish?job_id=${encodeURIComponent(job.id)}`, {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Multi-channel publishing failed');
    }
    const data = await res.json();
    await fetchPublishingData();
    fetchDashboardMetrics();

    const urls = (data.results || []).map(r => `• ${r.platform}: ${r.published_url || r.error || 'Done'}`).join('\n');
    alert(`🎉 MULTI-PLATFORM BROADCAST COMPLETE!\n\nEpisode: ${job.topic}\nStatus: PUBLISHED & VERIFIED\n\nActive Broadcast Destinations:\n${urls}`);
  } catch (err) {
    alert(`Broadcast Error: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  }
};

window.publishToSingleAccount = async function(accountId) {
  const job = getActiveMasterJob();
  if (!job) {
    alert('No master video available to publish.');
    return;
  }
  const account = state.publishingAccounts.find(a => a.id === accountId);
  const accName = account ? `${account.account_name} (${account.platform})` : accountId;

  if (!confirm(`Publish "${job.topic || job.id}" to ${accName}?`)) return;

  try {
    const res = await fetch('/api/publishing/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: job.id,
        account_id: accountId,
        // Empty title: the server builds hook-first metadata from the job's research brief.
        title: '',
        description: '',
        tags: [],
        auto_authorize: true
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Publishing failed');
    }
    const data = await res.json();
    await fetchPublishingData();
    fetchDashboardMetrics();
    alert(`SUCCESS! Published to ${data.platform}!\n\nURL: ${data.published_url}`);
  } catch (err) {
    alert(`Publishing Error: ${err.message}`);
  }
};

function getPlatformSvg(platform) {
  if (platform === 'youtube_shorts') {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="#fff"><path d="M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z"/></svg>`;
  } else if (platform === 'instagram_reels') {
    return `<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`;
  } else if (platform === 'tiktok') {
    return `<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.24 1.07-.14 1.61.24 1.64 1.82 2.89 3.5 2.76 1.47-.04 2.7-1.07 3.01-2.48.16-.76.15-1.55.15-2.33V.02z"/></svg>`;
  } else if (platform === 'facebook_reels') {
    return `<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`;
  }
  return `<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/></svg>`;
}

function renderAccounts(accounts) {
  const container = document.getElementById('pub-accounts-container');
  if (!container) return;

  if (!accounts || accounts.length === 0) {
    container.innerHTML = `
      <div class="dashboard-panel" style="grid-column: span 2; padding: 24px; text-align: center;">
        <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 14px;">No broadcast channels currently connected. Link your studio outlets:</p>
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
          <button class="btn btn-primary" onclick="registerDefaultAccounts()">⚡ Quick-Link 4 Studio Channels</button>
          <button class="btn btn-outline" onclick="openNewAccountModal()">+ Connect Custom Channel</button>
        </div>
      </div>
    `;
    return;
  }

  container.innerHTML = accounts.map(a => {
    let platformLabel = 'YouTube Shorts';
    let specText = '4K/60fps • Shorts Algorithm Ingest';

    if (a.platform === 'youtube_shorts') {
      platformLabel = 'YouTube Shorts';
      specText = '4K/60fps • Shorts Algorithm Ingest';
    } else if (a.platform === 'instagram_reels') {
      platformLabel = 'Instagram Reels';
      specText = 'Meta Graph API • 320kbps Audio';
    } else if (a.platform === 'tiktok') {
      platformLabel = 'TikTok';
      specText = 'ByteDance Open API • 9:16 Full Bleed';
    } else if (a.platform === 'facebook_reels') {
      platformLabel = 'Facebook Reels';
      specText = 'Meta Page Stream • High Priority';
    }

    return `
      <div class="pub-account-card">
        <div class="pub-account-left">
          <div class="platform-avatar-box ${a.platform}">
            ${getPlatformSvg(a.platform)}
          </div>
          <div class="pub-account-info">
            <div class="pub-account-title-row">
              <span class="pub-account-title">${escapeHtml(a.account_name)}</span>
              ${a.account_handle ? `<span class="pub-account-handle-chip">${escapeHtml(a.account_handle)}</span>` : ''}
              ${a.metadata && a.metadata.channel_url ? `<a href="${escapeHtml(a.metadata.channel_url)}" target="_blank" rel="noopener" class="channel-external-link" title="Open YouTube Channel">↗</a>` : ''}
              <span class="verified-icon" title="Studio Verified">✓</span>
            </div>
            <div class="pub-account-handle">${platformLabel} • ${specText}</div>
            <div class="pub-account-telemetry">
              <span class="status-beacon-live ${a.is_simulated ? '' : 'beacon-oauth'}">
                <span class="beacon-dot"></span>
                ${a.is_simulated ? 'ACTIVE PIPELINE' : 'LIVE GOOGLE API • OAUTH 2.0'}
              </span>
            </div>
          </div>
        </div>
        <div class="pub-account-actions">
          <button class="btn-pub-dispatch" onclick="publishToSingleAccount('${a.id}')">🚀 Broadcast</button>
          <button class="btn-pub-disconnect" onclick="deleteAccount('${a.id}')">Disconnect</button>
        </div>
      </div>
    `;
  }).join('');
}

window.deleteAccount = async function(accountId) {
  if (!confirm('Disconnect this broadcast channel?')) return;
  try {
    const res = await fetch(`/api/publishing/accounts/${accountId}`, { method: 'DELETE' });
    if (res.ok) {
      fetchPublishingData();
    } else {
      alert('Failed to disconnect account');
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
};

window.openNewAccountModal = function() {
  document.getElementById('modal-create-account')?.classList.remove('hidden');
};

window.closeNewAccountModal = function() {
  document.getElementById('modal-create-account')?.classList.add('hidden');
};

window.registerDefaultAccounts = async function() {
  const defaults = [
    { platform: 'youtube_shorts', name: 'Beyond80 Official Broadcast' },
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

window.openPublishDispatchModal = function() {
  const modal = document.getElementById('modal-dispatch-publish');
  if (!modal) return;

  const jobSelect = document.getElementById('modal-dispatch-job');
  const accSelect = document.getElementById('modal-dispatch-account');
  const titleInput = document.getElementById('modal-dispatch-title');
  const descInput = document.getElementById('modal-dispatch-desc');

  // Populate accounts
  if (!state.publishingAccounts || state.publishingAccounts.length === 0) {
    alert('Please connect at least one destination account first.');
    return;
  }
  accSelect.innerHTML = `
    <option value="ALL">🌟 ALL Channels (YouTube, IG, TikTok, FB)</option>
    ${state.publishingAccounts.map(a => `
      <option value="${a.id}">${escapeHtml(a.account_name)} (${a.platform.replace('_', ' ')})</option>
    `).join('')}
  `;

  // Populate jobs
  if (!state.jobs || state.jobs.length === 0) {
    alert('No episodes found in queue or library.');
    return;
  }
  jobSelect.innerHTML = state.jobs.map(j => `
    <option value="${j.id}">${escapeHtml(j.topic || j.id)} [${j.review_status}]</option>
  `).join('');

  const tagsInput = document.getElementById('modal-dispatch-tags');
  const updateFields = async () => {
    const selectedJob = state.jobs.find(j => j.id === jobSelect.value);
    if (!selectedJob) return;
    // Prefill with the hook-first metadata the server would publish; the director can still edit it.
    titleInput.value = '';
    descInput.value = '';
    if (tagsInput) tagsInput.value = '';
    try {
      const res = await fetch(`/api/publishing/metadata-preview?job_id=${encodeURIComponent(selectedJob.id)}`);
      if (!res.ok) return;
      const meta = await res.json();
      if (jobSelect.value !== selectedJob.id) return; // selection changed while loading
      titleInput.value = meta.title || '';
      descInput.value = meta.description || '';
      if (tagsInput) tagsInput.value = (meta.tags || []).join(', ');
    } catch (e) {
      console.warn('Metadata preview unavailable; the server will build it on publish.', e);
    }
  };
  jobSelect.onchange = updateFields;
  updateFields();

  modal.classList.remove('hidden');
};

window.closePublishDispatchModal = function() {
  document.getElementById('modal-dispatch-publish')?.classList.add('hidden');
};

function renderPublishingTasks(tasks) {
  const tbody = document.getElementById('pub-tasks-tbody');
  if (!tbody) return;

  if (!tasks || tasks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">No broadcast transmissions dispatched yet. Use "Direct Broadcast to All Channels" above.</td></tr>';
    return;
  }

  tbody.innerHTML = tasks.slice().reverse().map(t => {
    const account = (state.publishingAccounts || []).find(a => a.id === t.account_id);
    const accLabel = account ? account.account_name : (t.account_id ? t.account_id.substring(0, 15) : 'Studio Channel');

    let badgeClass = 'tag-accent';
    let iconSvg = '';
    if (t.platform === 'youtube_shorts') {
      badgeClass = 'tag-youtube';
      iconSvg = '▶ YouTube Shorts';
    } else if (t.platform === 'instagram_reels') {
      badgeClass = 'tag-instagram';
      iconSvg = '📷 Instagram Reels';
    } else if (t.platform === 'tiktok') {
      badgeClass = 'tag-tiktok';
      iconSvg = '🎵 TikTok';
    } else if (t.platform === 'facebook_reels') {
      badgeClass = 'tag-facebook';
      iconSvg = '📘 Facebook Reels';
    }

    return `
      <tr>
        <td><code style="font-size: 0.74rem; color: #94a3b8; font-weight: 600;">${t.id.replace('pub_task_', 'REL-')}</code></td>
        <td><span class="tag ${badgeClass}" style="font-weight: 700; font-size: 0.72rem;">${iconSvg}</span></td>
        <td><strong>${escapeHtml(accLabel)}</strong></td>
        <td><span style="color: #f1f5f9; font-weight: 500;">${escapeHtml(t.title || 'Master Episode')}</span></td>
        <td>
          <span class="status-beacon-live" style="font-size: 0.7rem;">
            <span class="beacon-dot"></span>
            ${t.status === 'COMPLETED' ? 'BROADCAST COMPLETE' : t.status}
          </span>
        </td>
        <td>
          ${t.published_url ? `
            <a href="${t.published_url}" target="_blank" class="broadcast-url-link">
              <span>Watch Video</span>
              <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3"/></svg>
            </a>
          ` : '—'}
        </td>
      </tr>
    `;
  }).join('');
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
