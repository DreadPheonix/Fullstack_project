const SMS_SAMPLES = [
  {
    id: 1,
    type: 'spam',
    badge: '🚨 Lottery Scam',
    label: 'Lottery Winner £10,000',
    text: 'URGENT! You have won a guaranteed £1,000 cash prize or a £2,000 holiday reward! To claim your jackpot now, text WIN to 87121 immediately. Terms apply.'
  },
  {
    id: 2,
    type: 'spam',
    badge: '💳 Bank Phishing',
    label: 'Bank Account Blocked',
    text: 'ALERT: Your SBI Debit Card ending in 4092 has been temporarily suspended due to unusual activity. Click http://bit.ly/sbi-verify-kyc now to update KYC within 24 hours.'
  },
  {
    id: 3,
    type: 'spam',
    badge: '🎁 Free Offer',
    label: 'Free iPhone 15 Gift',
    text: 'Congratulations! You have been selected as today\'s lucky winner for a brand new Apple iPhone 15 Pro. Call 0800 123 4567 or reply FREE to claim your free reward!'
  },
  {
    id: 4,
    type: 'spam',
    badge: '⚠️ Urgent Action',
    label: 'Tax Refund Available',
    text: 'FINAL NOTICE: HMRC has calculated your annual tax refund of $482.50. Please visit https://hmrc-refund-gov.com/verify to enter your bank details for direct deposit.'
  },
  {
    id: 5,
    type: 'ham',
    badge: '✅ Normal Ham',
    label: 'Dinner & Meeting',
    text: 'Hey Priyanjal! Are we still meeting at the library at 5 PM for the Machine Learning lab presentation preparation? Let me know.'
  },
  {
    id: 6,
    type: 'ham',
    badge: '✅ Normal Ham',
    label: 'Class Schedule',
    text: 'Hi Payal, Professor Sharma announced that tomorrow\'s Full Stack Development lab class will start at 10:30 AM in Lab 3. Please bring your project report.'
  },
  {
    id: 7,
    type: 'ham',
    badge: '🔐 Real OTP',
    label: 'Official OTP Code',
    text: 'Your Google Account verification code is 492810. Do not share this OTP with anyone for your security.'
  },
  {
    id: 8,
    type: 'ham',
    badge: '📦 Delivery Alert',
    label: 'Amazon Delivery',
    text: 'Your Amazon package containing "Python Data Science Handbook" is out for delivery today and will arrive by 6:00 PM.'
  }
];

// Helper to render samples into any target container
function renderSampleChips(containerId, onSelect) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';
  SMS_SAMPLES.forEach(sample => {
    const chip = document.createElement('button');
    chip.type = 'button';
    const isSpam = sample.type === 'spam';

    chip.className = `text-[11px] px-2.5 py-1 rounded-lg border font-semibold transition-all flex items-center gap-1.5 ${
      isSpam
        ? 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/40'
        : 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900/60 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 dark:hover:bg-emerald-900/40'
    }`;

    chip.innerHTML = `
      <span>${isSpam ? '🚨' : '💬'}</span>
      <span>${sample.label}</span>
    `;

    chip.addEventListener('click', () => {
      if (typeof onSelect === 'function') {
        onSelect(sample.text);
      }
    });

    container.appendChild(chip);
  });
}
