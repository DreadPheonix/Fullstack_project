/**
 * SMS Shield v2 - Core Analytical Workspace Controller
 * Handles 60/40 Split-Pane workspace, sample dropdown, dynamic analysis card, and theme switching.
 */

// 1. Toast Notification Helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-item toast-${type}`;
  const text = document.createElement('span');
  text.textContent = message;
  toast.appendChild(text);
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 2500);
}

// 2. Sample Messages Map (For the sleek dropdown)
const SAMPLE_MESSAGES = {
  lottery: 'URGENT: You have won a $1,500 Walmart gift card! Claim your reward within 2 hours by texting WIN to 48210. Terms apply.',
  bank: 'Security Notice: Your Chase Bank debit card is temporarily locked due to unusual activity. Verify your identity at http://chase-security-check.net immediately.',
  gift: 'Congratulations! You are selected to receive a free Apple iPad. Reply FREE now or visit bit.ly/claim-apple-deal to receive your prize today.',
  tax: 'FINAL NOTICE: IRS has reported an overdue tax payment of $340.20. Pay today to avoid penalty. Visit irs-direct-settlement.org/pay',
  meeting: 'Hi Payal, are we still meeting in Lab 3 at 4:30 PM to review our presentation slides with Professor Sharma?',
  class: 'Reminder: Tomorrow morning class for Web Development will begin at 9:00 AM instead of 10:00 AM in Room 204.',
  otp: 'Your Google verification code is 829144. Do not share this one-time code with anyone.',
  delivery: 'Your package containing Computer Science textbooks has been shipped and is scheduled for delivery today by 5 PM.'
};

// 3. Dropdown Selection Handler
function handleSampleSelect(sampleKey) {
  const textarea = document.getElementById('sms-textarea');
  if (!textarea || !sampleKey) return;

  const text = SAMPLE_MESSAGES[sampleKey];
  if (text) {
    textarea.value = text;
    updateCharCount();
    textarea.focus();
    showToast('Sample loaded into input console', 'info');
  }
}

// 4. Load Sample Directly (from History rows)
function loadDirectSample(text) {
  const textarea = document.getElementById('sms-textarea');
  if (textarea) {
    switchTab('detector');
    textarea.value = text;
    updateCharCount();
    textarea.focus();
    showToast('Loaded message into inspector', 'info');
  }
}

// 5. Character Counter (Max 5,000 Chars)
function updateCharCount() {
  const textarea = document.getElementById('sms-textarea');
  const countText = document.getElementById('char-count');
  const progressBar = document.getElementById('char-bar');
  if (!textarea || !countText || !progressBar) return;

  const length = textarea.value.length;
  countText.textContent = `${length.toLocaleString()} / 5,000 characters`;

  const percent = Math.min(100, (length / 5000) * 100);
  progressBar.style.width = `${percent}%`;

  if (percent > 90) {
    progressBar.className = 'char-progress-bar danger';
  } else if (percent > 70) {
    progressBar.className = 'char-progress-bar warning';
  } else {
    progressBar.className = 'char-progress-bar';
  }
}

// 6. Clear Input & Reset to Default Placeholder State
function clearSMSInput() {
  const textarea = document.getElementById('sms-textarea');
  const dropdown = document.getElementById('sample-dropdown');
  if (textarea) {
    textarea.value = '';
    updateCharCount();
  }
  if (dropdown) {
    dropdown.value = '';
  }
  dismissResult();
  showToast('Workspace cleared', 'info');
}

// 7. Paste Clipboard Content
async function pasteClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    const textarea = document.getElementById('sms-textarea');
    if (textarea && text) {
      textarea.value = text;
      updateCharCount();
      showToast('Pasted from clipboard', 'info');
    }
  } catch (err) {
    showToast('Please paste manually using Ctrl+V', 'info');
  }
}

// 8. Check Message & Generate Eye-Level Analysis Verdict (Right Column)
async function checkSMSMessage() {
  const textarea = document.getElementById('sms-textarea');
  if (!textarea) return;
  const text = textarea.value.trim();

  if (!text) {
    showToast('Please enter or select an SMS message first', 'error');
    textarea.focus();
    return;
  }

  if (!window.API || typeof window.API.predict !== 'function') {
    showToast('Prediction API client is unavailable. Reload the page and try again.', 'error');
    return;
  }

  const button = document.getElementById('btn-check-message');
  const buttonLabel = button ? button.querySelector('[data-label]') : null;
  if (button) button.disabled = true;
  if (buttonLabel) buttonLabel.textContent = 'ANALYZING...';
  dismissResult();

  try {
    const prediction = await window.API.predict(text);
    const isSpam = prediction.label === 'spam';
    const confidencePercent = Number((prediction.confidence * 100).toFixed(1));

    const placeholder = document.getElementById('analysis-placeholder');
    const resultCard = document.getElementById('analysis-result-card');
    if (placeholder) placeholder.classList.add('hidden');
    if (resultCard) resultCard.classList.remove('hidden');

    const banner = document.getElementById('result-banner');
    const title = document.getElementById('result-title');
    const desc = document.getElementById('result-desc');
    const badgeIcon = document.getElementById('result-badge-icon');
    const dot = document.getElementById('verdict-dot');
    const confidence = document.getElementById('result-confidence');
    const confBar = document.getElementById('result-confidence-bar');
    const classification = document.getElementById('result-keywords');

    if (isSpam) {
      banner.className = 'p-4 rounded-xl bg-[#FEE2E2] dark:bg-[#7F1D1D] border border-[#FCA5A5] dark:border-[#991B1B] flex items-center justify-between gap-3';
      title.textContent = 'SPAM DETECTED';
      title.className = 'text-xl font-black text-[#DC2626] dark:text-[#F87171] mt-0.5 tracking-tight';
      desc.textContent = 'The machine-learning model classified this message as spam.';
      desc.className = 'text-xs mt-0.5 text-[#DC2626] dark:text-[#F87171] font-medium leading-snug';
      badgeIcon.innerHTML = '<i class="fas fa-triangle-exclamation text-2xl text-[#DC2626] dark:text-[#F87171]"></i>';
      dot.className = 'w-2.5 h-2.5 rounded-full bg-[#DC2626] dark:bg-[#F87171]';
      confBar.className = 'h-full bg-[#DC2626] dark:bg-[#F87171] rounded-full transition-all duration-500';
    } else {
      banner.className = 'p-4 rounded-xl bg-[#DCFCE7] dark:bg-[#14532D] border border-[#86EFAC] dark:border-[#166534] flex items-center justify-between gap-3';
      title.textContent = 'LEGITIMATE (HAM)';
      title.className = 'text-xl font-black text-[#16A34A] dark:text-[#4ADE80] mt-0.5 tracking-tight';
      desc.textContent = 'The machine-learning model classified this message as ham.';
      desc.className = 'text-xs mt-0.5 text-[#16A34A] dark:text-[#4ADE80] font-medium leading-snug';
      badgeIcon.innerHTML = '<i class="fas fa-circle-check text-2xl text-[#16A34A] dark:text-[#4ADE80]"></i>';
      dot.className = 'w-2.5 h-2.5 rounded-full bg-[#16A34A] dark:bg-[#4ADE80]';
      confBar.className = 'h-full bg-[#16A34A] dark:bg-[#4ADE80] rounded-full transition-all duration-500';
    }

    confidence.textContent = `${confidencePercent.toFixed(1)}%`;
    confBar.style.width = `${confidencePercent}%`;
    classification.replaceChildren();

    const label = document.createElement('span');
    label.className = `text-xs font-semibold px-2.5 py-1 rounded-md ${
      isSpam
        ? 'bg-[#FEE2E2] dark:bg-[#7F1D1D] text-[#DC2626] dark:text-[#F87171] border border-[#FCA5A5] dark:border-[#991B1B]'
        : 'bg-[#DCFCE7] dark:bg-[#14532D] text-[#16A34A] dark:text-[#4ADE80] border border-[#86EFAC] dark:border-[#166534]'
    }`;
    label.textContent = `#${prediction.label}`;
    classification.appendChild(label);

    showToast(`Model prediction: ${isSpam ? 'SPAM' : 'HAM'}`, isSpam ? 'error' : 'success');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unexpected prediction API error.';
    showToast(`Could not analyze this message: ${message}`, 'error');
  } finally {
    if (button) button.disabled = false;
    if (buttonLabel) buttonLabel.textContent = 'CHECK MESSAGE';
  }
}

// 9. Dismiss Result Card (Returns Right Column to Default Placeholder State)
function dismissResult() {
  const placeholder = document.getElementById('analysis-placeholder');
  const resultCard = document.getElementById('analysis-result-card');
  if (placeholder) placeholder.classList.remove('hidden');
  if (resultCard) resultCard.classList.add('hidden');
}

// 10. Copy Verdict Report
function copyVerdictReport() {
  const textarea = document.getElementById('sms-textarea');
  const title = document.getElementById('result-title');
  const conf = document.getElementById('result-confidence');

  const text = textarea ? textarea.value : '';
  const verdict = title ? title.textContent : 'UNKNOWN';
  const confidence = conf ? conf.textContent : '0%';

  const report = `[SMS Shield Report]\nVerdict: ${verdict}\nConfidence: ${confidence}\nMessage: "${text}"`;
  navigator.clipboard.writeText(report).then(() => {
    showToast('Report copied to clipboard', 'info');
  });
}

// 11. Sidebar Navigation Tabs
function switchTab(tabId) {
  const tabs = ['detector', 'history', 'team'];
  tabs.forEach(tab => {
    const btn = document.getElementById(`tab-btn-${tab}`);
    const section = document.getElementById(`tab-content-${tab}`);

    if (tab === tabId) {
      if (btn) {
        btn.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-bold bg-[#18181B] text-[#FFFFFF] dark:bg-[#F4F4F5] dark:text-[#18181B] shadow-sm transition-all text-left';
      }
      if (section) section.classList.remove('hidden');
    } else {
      if (btn) {
        btn.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium text-[#71717A] dark:text-[#A1A1AA] hover:text-[#18181B] dark:hover:text-[#F4F4F5] hover:bg-[#F4F4F5] dark:hover:bg-[#3F3F46] transition-all text-left';
      }
      if (section) section.classList.add('hidden');
    }
  });
}

// 12. Theme Toggle & Icon Update
function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme_v2', isDark ? 'dark' : 'light');
  updateThemeIcon(isDark);
  showToast(isDark ? 'Switched to Dark Mode' : 'Switched to Light Mode', 'info');
}

function updateThemeIcon(isDark) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.className = isDark ? 'fas fa-sun text-xs text-[#F4F4F5]' : 'fas fa-moon text-xs text-[#18181B]';
  }
}

// 13. Initialize on Page Load
document.addEventListener('DOMContentLoaded', () => {
  const isDark = document.documentElement.classList.contains('dark');
  updateThemeIcon(isDark);

  // Textarea input listener for dynamic char counting
  const textarea = document.getElementById('sms-textarea');
  if (textarea) {
    textarea.addEventListener('input', updateCharCount);
    updateCharCount();
  }
});
