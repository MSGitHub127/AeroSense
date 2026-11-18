/**
 * AeroSense - Accessible Client-side Application Logic
 * Integrates Web Speech API, Real-Time Dosimetry, and AI Air Advisory.
 */
(() => {
  'use strict';

  let currentProfileId = null;
  let currentDossierMarkdown = '';
  let speechSynthesizer = window.speechSynthesis;
  let currentUtterance = null;
  let isSpeaking = false;

  const announceStatus = (message) => {
    const announcer = document.getElementById('status-announcer');
    if (announcer) {
      announcer.textContent = message;
    }
  };

  const getSessionToken = async () => {
    let token = sessionStorage.getItem('aerosense_session');
    if (!token) {
      try {
        const res = await fetch('/api/session', { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          token = data.session_token;
          sessionStorage.setItem('aerosense_session', token);
        }
      } catch (err) {
        console.warn('Session initialization fallback:', err);
      }
    }
    return token;
  };

  // --- Voice Narration (Web Speech API) ---
  const toggleSpeechNarration = () => {
    const btn = document.getElementById('btn-narrate');
    if (!speechSynthesizer) {
      alert('Text-to-Speech is not supported in this browser.');
      return;
    }

    if (isSpeaking) {
      speechSynthesizer.cancel();
      isSpeaking = false;
      if (btn) {
        btn.textContent = '🔊 Read Advisory Aloud';
        btn.setAttribute('aria-pressed', 'false');
      }
      announceStatus('Audio narration stopped.');
      return;
    }

    const narrationSource = document.getElementById('advisory-results');
    if (!narrationSource || narrationSource.style.display === 'none') {
      announceStatus('Please generate an action plan before listening to narration.');
      return;
    }

    const textToRead = narrationSource.innerText || narrationSource.textContent;
    currentUtterance = new SpeechSynthesisUtterance(textToRead.slice(0, 3000));
    currentUtterance.rate = 1.0;
    currentUtterance.pitch = 1.0;

    currentUtterance.onend = () => {
      isSpeaking = false;
      if (btn) {
        btn.textContent = '🔊 Read Advisory Aloud';
        btn.setAttribute('aria-pressed', 'false');
      }
      announceStatus('Audio narration finished.');
    };

    currentUtterance.onerror = () => {
      isSpeaking = false;
      if (btn) {
        btn.textContent = '🔊 Read Advisory Aloud';
        btn.setAttribute('aria-pressed', 'false');
      }
    };

    speechSynthesizer.speak(currentUtterance);
    isSpeaking = true;
    if (btn) {
      btn.textContent = '⏹️ Stop Narration';
      btn.setAttribute('aria-pressed', 'true');
    }
    announceStatus('Audio narration playing.');
  };

  // --- Form Submission & Advisory Formulation ---
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    const btnSubmit = document.getElementById('btn-generate-plan');
    btnSubmit.disabled = true;
    btnSubmit.textContent = 'Synthesizing Plan...';
    announceStatus('Synthesizing your personalized air quality advisory...');

    const vulnerableCheckboxes = document.querySelectorAll('input[name="vulnerable"]:checked');
    const vulnerable_members = Array.from(vulnerableCheckboxes).map(cb => cb.value);

    const aqiInput = document.getElementById('baseline-aqi').value;
    const payload = {
      household_name: document.getElementById('household-name').value.trim() || 'My Household',
      location_city: document.getElementById('location-city').value.trim() || 'Delhi',
      home_type: document.getElementById('home-type').value,
      cooking_fuel: document.getElementById('cooking-fuel').value,
      commute_mode: document.getElementById('commute-mode').value,
      has_hepa_purifier: document.getElementById('has-hepa').checked,
      vulnerable_members: vulnerable_members,
      baseline_aqi: aqiInput ? parseInt(aqiInput, 10) : null,
    };

    try {
      const token = await getSessionToken();
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/advisory', {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to synthesize advisory.');
      }

      const advisory = await res.json();
      currentProfileId = advisory.profile_id;
      currentDossierMarkdown = advisory.action_plan_markdown;
      renderAdvisoryResults(advisory);
      announceStatus('Air action plan generated successfully. Impact metrics and routines displayed below.');
    } catch (err) {
      alert(`Error generating advisory: ${err.message}`);
      announceStatus(`Error: ${err.message}`);
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.textContent = 'Generate Family Air Action Plan';
    }
  };

  // --- Render Results ---
  const renderAdvisoryResults = (data) => {
    const resultsContainer = document.getElementById('advisory-results');
    resultsContainer.style.display = 'block';

    // 1. Direct Impact Metrics
    document.getElementById('metric-lung-dose').textContent = `${data.impact.daily_pm25_lung_dose_avoided_ug.toLocaleString()} µg`;
    document.getElementById('metric-cigs').textContent = `${data.impact.equivalent_cigarettes_avoided.toLocaleString()}`;
    document.getElementById('metric-co2').textContent = `${data.impact.annual_co2_saved_kg.toLocaleString()} kg`;
    document.getElementById('metric-risk').textContent = `${data.impact.respiratory_risk_reduction_pct}%`;

    // 2. Diurnal Timeline
    const timelineEl = document.getElementById('diurnal-timeline-list');
    timelineEl.innerHTML = '';
    data.routines.diurnal_windows.forEach(w => {
      let severityClass = 'moderate';
      if (w.aqi_category.toLowerCase().includes('hazardous') || w.predicted_pm25 > 150) {
        severityClass = 'severe';
      } else if (w.aqi_category.toLowerCase().includes('optimal') || w.predicted_pm25 < 60) {
        severityClass = 'optimal';
      }

      const item = document.createElement('div');
      item.className = `timeline-item ${severityClass}`;
      item.innerHTML = `
        <div class="time-badge">${w.time_range}</div>
        <div>
          <span class="aqi-pill ${severityClass}">${w.predicted_pm25} µg/m³</span>
        </div>
        <div>
          <strong>${w.aqi_category}</strong>
          <p style="font-size:0.875rem; color:var(--text-secondary); margin-top:0.25rem;">
            ✅ <em>Safe:</em> ${w.recommended_activities.join(', ')}<br/>
            ⚠️ <em>Avoid:</em> ${w.activities_to_avoid.join(', ')}
          </p>
        </div>
      `;
      timelineEl.appendChild(item);
    });

    // 3. Optimized Routines
    const routinesList = document.getElementById('routines-list');
    routinesList.innerHTML = '';
    const routines = [
      data.routines.commute_routine,
      data.routines.school_routine,
      data.routines.exercise_routine,
      data.routines.ventilation_routine,
    ];

    routines.forEach(r => {
      const card = document.createElement('div');
      card.className = 'routine-card';
      card.innerHTML = `
        <div class="routine-header">
          <span class="routine-title">${r.activity_name}</span>
          <span class="routine-badge">Saved ${r.pm25_exposure_saved_pct}% Exposure</span>
        </div>
        <p style="margin-bottom:0.5rem;">
          <del style="color:var(--text-muted);">${r.standard_time}</del> ➡️ 
          <strong style="color:var(--color-clean);">${r.optimized_time}</strong>
        </p>
        <p style="font-size:0.9rem; color:var(--text-secondary);">${r.reasoning}</p>
      `;
      routinesList.appendChild(card);
    });

    // 4. IAQ Hacks
    const hacksList = document.getElementById('iaq-hacks-list');
    hacksList.innerHTML = '';
    data.iaq_hacks.hacks.forEach(h => {
      const hackEl = document.createElement('div');
      hackEl.className = 'hack-item';
      hackEl.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
          <h3 style="font-size:1.15rem; color:#ffffff;">${h.hack_name}</h3>
          <span class="routine-badge" style="background:#059669;">~${h.pm25_reduction_pct}% PM2.5 Cut</span>
        </div>
        <div class="hack-meta">
          <span><strong>Category:</strong> ${h.category}</span>
          <span><strong>Difficulty:</strong> ${h.difficulty}</span>
          <span><strong>Estimated Cost:</strong> $${h.estimated_cost_usd.toFixed(2)}</span>
        </div>
        <p><strong>Required Equipment:</strong> ${h.equipment_needed.join(', ')}</p>
        <ol class="hack-steps">
          ${h.step_by_step_instructions.map(s => `<li>${s}</li>`).join('')}
        </ol>
      `;
      hacksList.appendChild(hackEl);
    });

    // 5. Sustainable Alternatives Table
    const tableBody = document.getElementById('alternatives-tbody');
    tableBody.innerHTML = '';
    data.alternatives.alternatives.forEach(alt => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight:700; text-transform:capitalize;">${alt.habit_category}</td>
        <td><del>${alt.current_habit}</del></td>
        <td style="color:var(--color-clean); font-weight:600;">${alt.recommended_alternative}</td>
        <td>${alt.annual_co2_kg_saved.toLocaleString()} kg</td>
        <td>${alt.local_pm25_averted_grams.toLocaleString()} g</td>
        <td>${alt.cost_implication}</td>
      `;
      tableBody.appendChild(tr);
    });

    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
  };

  // --- Download Markdown Dossier ---
  const downloadDossier = () => {
    if (!currentProfileId) {
      alert('Please generate an advisory plan first.');
      return;
    }
    window.location.href = `/api/advisory/${currentProfileId}/dossier`;
  };

  // --- Conversational Q&A ---
  const handleConsultation = async (e) => {
    e.preventDefault();
    if (!currentProfileId) {
      alert('Please generate an air action plan first so AeroSense can contextualize advice.');
      return;
    }

    const input = document.getElementById('consult-question');
    const question = input.value.trim();
    if (!question) return;

    const chatList = document.getElementById('chat-history');
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-bubble user';
    userMsg.textContent = question;
    chatList.appendChild(userMsg);
    input.value = '';

    const assistantMsg = document.createElement('div');
    assistantMsg.className = 'chat-bubble assistant';
    assistantMsg.textContent = 'AeroSense is consulting atmospheric and health models...';
    chatList.appendChild(assistantMsg);

    try {
      const res = await fetch(`/api/advisory/${currentProfileId}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error('Failed to get consultation.');
      const data = await res.json();
      assistantMsg.textContent = data.answer;
      announceStatus('AeroSense replied to your question.');
    } catch (err) {
      assistantMsg.textContent = `Error: ${err.message}`;
    }
  };

  // --- Vision Inspection ---
  const handleVisionInspection = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('vision-file');
    if (!fileInput.files || fileInput.files.length === 0) {
      alert('Please select an image file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('prompt', 'Inspect outdoor haze level, estimated visibility, and safety precautions.');

    const visionResult = document.getElementById('vision-result');
    visionResult.style.display = 'block';
    visionResult.textContent = 'Analyzing image with Multimodal AI...';

    try {
      const res = await fetch('/api/vision/inspect', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Vision analysis failed.');
      const data = await res.json();
      visionResult.textContent = data.analysis;
      announceStatus('Vision analysis completed.');
    } catch (err) {
      visionResult.textContent = `Error: ${err.message}`;
    }
  };

  // --- Event Listeners Setup ---
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('profile-form');
    if (form) form.addEventListener('submit', handleProfileSubmit);

    const btnNarrate = document.getElementById('btn-narrate');
    if (btnNarrate) btnNarrate.addEventListener('click', toggleSpeechNarration);

    const btnDownload = document.getElementById('btn-download-dossier');
    if (btnDownload) btnDownload.addEventListener('click', downloadDossier);

    const consultForm = document.getElementById('consult-form');
    if (consultForm) consultForm.addEventListener('submit', handleConsultation);

    const visionForm = document.getElementById('vision-form');
    if (visionForm) visionForm.addEventListener('submit', handleVisionInspection);
  });
})();
