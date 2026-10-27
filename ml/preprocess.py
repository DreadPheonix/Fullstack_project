import re
import string
import html


ROUTINE_OTP_PATTERN = re.compile(
    r"\b(?:verification|security|one[\s-]?time)\s+(?:code|passcode|pin)\b",
    re.IGNORECASE,
)
ROUTINE_SHIPMENT_PATTERN = re.compile(
    r"\b(?:package|parcel|order)\b.*\b(?:shipped|dispatched|on its way|out for delivery)\b"
    r"|\b(?:package|parcel|order)\b.*\bdelivery\s+(?:is\s+)?(?:scheduled|expected)\b",
    re.IGNORECASE,
)
RISKY_MESSAGE_PATTERN = re.compile(
    r"https?://|www\.|\b(?:bit\.ly|tinyurl|t\.co)\b|"
    r"\b(?:claim|click|visit|pay|payment|fee|verify|confirm|urgent|immediately|"
    r"winner|won|prize|reward|free|locked|suspended)\b|"
    r"\b[\w-]+\.(?:com|net|org|info|xyz|biz|io|co|in)\b",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = html.unescape(text)
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'<.*?>+', ' ', text)
    text = re.sub(r'&(?:nbsp|amp|lt|gt|quot|apos);', ' ', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_routine_transactional_message(text: str) -> bool:
    if RISKY_MESSAGE_PATTERN.search(text):
        return False

    has_otp_code = ROUTINE_OTP_PATTERN.search(text) and re.search(r"\b\d{4,8}\b", text)
    return bool(has_otp_code or ROUTINE_SHIPMENT_PATTERN.search(text))
