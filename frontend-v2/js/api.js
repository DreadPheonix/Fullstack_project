const API = {
  async predict(message) {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const result = await response.json();

    if (!response.ok) {
      const detail = result.detail;
      const error = detail && typeof detail === 'object'
        ? detail.error || detail.message
        : detail;
      throw new Error(error || `Prediction API request failed (${response.status})`);
    }

    if (
      !result ||
      !['ham', 'spam'].includes(result.label) ||
      typeof result.confidence !== 'number' ||
      !Number.isFinite(result.confidence) ||
      result.confidence < 0 ||
      result.confidence > 1
    ) {
      throw new Error('Prediction API returned an invalid response.');
    }

    return result;
  }
};

window.API = API;
