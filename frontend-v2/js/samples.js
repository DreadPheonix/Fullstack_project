/**
 * SMS Shield v2 - Sample Test Datasets
 * Uses exact user-provided color values for Ham and Spam highlights.
 */

const SMS_SAMPLES = [
  {
    id: 1,
    type: 'spam',
    category: 'Scam',
    label: 'Lottery Prize Alert',
    text: 'URGENT: You have won a $1,500 Walmart gift card! Claim your reward within 2 hours by texting WIN to 48210. Terms apply.'
  },
  {
    id: 2,
    type: 'spam',
    category: 'Phishing',
    label: 'Bank Account Blocked',
    text: 'Security Notice: Your Chase Bank debit card is temporarily locked due to unusual activity. Verify your identity at http://chase-security-check.net immediately.'
  },
  {
    id: 3,
    type: 'spam',
    category: 'Scam',
    label: 'Free Gift Card Offer',
    text: 'Congratulations! You are selected to receive a free Apple iPad. Reply FREE now or visit bit.ly/claim-apple-deal to receive your prize today.'
  },
  {
    id: 4,
    type: 'spam',
    category: 'Alert',
    label: 'Unpaid Tax Notice',
    text: 'FINAL NOTICE: IRS has reported an overdue tax payment of $340.20. Pay today to avoid penalty. Visit irs-direct-settlement.org/pay'
  },
  {
    id: 5,
    type: 'ham',
    category: 'Normal',
    label: 'Team Meeting',
    text: 'Hi Payal, are we still meeting in Lab 3 at 4:30 PM to review our presentation slides with Professor Sharma?'
  },
  {
    id: 6,
    type: 'ham',
    category: 'Normal',
    label: 'Class Schedule Update',
    text: 'Reminder: Tomorrow morning class for Web Development will begin at 9:00 AM instead of 10:00 AM in Room 204.'
  },
  {
    id: 7,
    type: 'ham',
    category: 'OTP',
    label: 'Google Security Code',
    text: 'Your Google verification code is 829144. Do not share this one-time code with anyone.'
  },
  {
    id: 8,
    type: 'ham',
    category: 'Delivery',
    label: 'Amazon Order Shipped',
    text: 'Your package containing Computer Science textbooks has been shipped and is scheduled for delivery today by 5 PM.'
  }
];

// Helper to render the sample buttons
function renderSampleChips(containerId, onSelect) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';
  SMS_SAMPLES.forEach(sample => {
    const btn = document.createElement('button');
    btn.type = 'button';
    const isSpam = sample.type === 'spam';

    // Exact palette styling:
    // Ham: Light (bg #DCFCE7, text #16A34A) | Dark (bg #14532D, text #4ADE80)
    // Spam: Light (bg #FEE2E2, text #DC2626) | Dark (bg #7F1D1D, text #F87171)
    btn.className = `text-xs px-3 py-1.5 rounded-lg font-semibold border transition-all flex items-center gap-1.5 ${
      isSpam
        ? 'bg-[#FEE2E2] dark:bg-[#7F1D1D] text-[#DC2626] dark:text-[#F87171] border-[#FCA5A5] dark:border-[#991B1B] hover:opacity-90'
        : 'bg-[#DCFCE7] dark:bg-[#14532D] text-[#16A34A] dark:text-[#4ADE80] border-[#86EFAC] dark:border-[#166534] hover:opacity-90'
    }`;

    btn.innerHTML = `
      <span>${isSpam ? '⚠️' : '💬'}</span>
      <span>${sample.label}</span>
    `;

    btn.onclick = () => {
      if (typeof onSelect === 'function') {
        onSelect(sample.text);
      }
    };

    container.appendChild(btn);
  });
}
