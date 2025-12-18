"""
Typed exceptions for DataSetIQ API errors.

All exceptions include marketing messages to guide users toward solutions.
"""

from typing import Optional


class DataSetIQError(Exception):
    """Base exception for all DataSetIQ errors."""

    def __init__(
        self,
        status_code: Optional[int],
        code: str,
        message: str,
        marketing_text: Optional[str] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.marketing_text = marketing_text
        
        # Build full error message
        full_message = f"[{code}] {message}"
        if marketing_text:
            full_message += f"\n\n{marketing_text}"
        
        super().__init__(full_message)


class AuthenticationError(DataSetIQError):
    """Raised when API key is missing or invalid (401)."""

    def __init__(self, message: str = "Authentication required"):
        marketing = (
            "🔑 GET YOUR FREE API KEY:\n"
            "   → https://www.datasetiq.com/dashboard/api-keys\n\n"
            "📊 FREE PLAN INCLUDES:\n"
            "   • 25 requests/minute\n"
            "   • 25 AI insights/month\n"
            "   • Access to 40M+ time series\n\n"
            "💡 Set your key:\n"
            "   import datasetiq as iq\n"
            "   iq.set_api_key('your-key-here')"
        )
        super().__init__(401, "UNAUTHORIZED", message, marketing)


class ForbiddenError(DataSetIQError):
    """Raised when trying to access premium features (403)."""

    def __init__(self, message: str = "Premium access required"):
        marketing = (
            "🚀 UPGRADE FOR PREMIUM ACCESS:\n"
            "   → https://www.datasetiq.com/pricing\n\n"
            "✨ PREMIUM BENEFITS:\n"
            "   • Unlimited data exports\n"
            "   • 500 AI insights/month (Pro)\n"
            "   • Priority support\n"
            "   • Advanced analytics tools"
        )
        super().__init__(403, "FORBIDDEN", message, marketing)


class RateLimitError(DataSetIQError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        current: Optional[int] = None,
        reset_epoch_sec: Optional[int] = None,
    ):
        self.limit = limit
        self.current = current
        self.reset_epoch_sec = reset_epoch_sec
        
        marketing = (
            "⚡ RATE LIMIT REACHED:\n"
            f"   {current}/{limit} requests this minute\n\n"
            "🚀 INCREASE YOUR LIMITS:\n"
            "   → https://www.datasetiq.com/pricing\n\n"
            "📈 HIGHER TIER LIMITS:\n"
            "   • Starter: 50 RPM\n"
            "   • Pro: 100 RPM\n"
            "   • Team: 250 RPM/member"
        )
        super().__init__(429, "RATE_LIMITED", message, marketing)


class QuotaExceededError(DataSetIQError):
    """Raised when monthly quota is exceeded (429 with QUOTA_EXCEEDED code)."""

    def __init__(
        self,
        metric: str,
        current: int,
        limit: int,
        message: Optional[str] = None,
    ):
        self.metric = metric
        self.current = current
        self.limit = limit
        
        if not message:
            message = f"Monthly quota exceeded for {metric}: {current}/{limit}"
        
        marketing = (
            "📊 MONTHLY QUOTA EXCEEDED:\n"
            f"   {metric}: {current}/{limit} used\n\n"
            "🎯 UPGRADE FOR MORE:\n"
            "   → https://www.datasetiq.com/pricing\n\n"
            "💎 HIGHER QUOTAS:\n"
            "   • Starter: 50 advanced insights/month\n"
            "   • Pro: 500 advanced insights/month\n"
            "   • Team: 1000+ (scales with seats)"
        )
        super().__init__(429, "QUOTA_EXCEEDED", message, marketing)


class NotFoundError(DataSetIQError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        marketing = (
            "🔍 SERIES NOT FOUND\n\n"
            "💡 TIP: Search for series first:\n"
            "   import datasetiq as iq\n"
            "   results = iq.search('unemployment rate')\n"
            "   print(results[['id', 'title']])\n\n"
            "📚 Browse all datasets:\n"
            "   → https://www.datasetiq.com/datasets"
        )
        super().__init__(404, "NOT_FOUND", message, marketing)


class ServiceError(DataSetIQError):
    """Raised for server errors (5xx) or service unavailable."""

    def __init__(
        self,
        status_code: int = 503,
        code: str = "SERVICE_UNAVAILABLE",
        message: str = "Service temporarily unavailable",
    ):
        marketing = (
            "⚠️  SERVICE ISSUE\n\n"
            "Our team has been automatically notified.\n"
            "Please retry in a few moments.\n\n"
            "📧 If this persists, contact:\n"
            "   → support@datasetiq.com"
        )
        super().__init__(status_code, code, message, marketing)


class IngestionPendingError(DataSetIQError):
    """Raised when dataset is being ingested (202)."""

    def __init__(self, message: str = "Dataset ingestion in progress"):
        marketing = (
            "⏳ DATASET BEING PREPARED\n\n"
            "This dataset is being ingested into our system.\n"
            "Full data will be available in 1-2 minutes.\n\n"
            "💡 Please retry this request shortly."
        )
        super().__init__(202, "INGESTION_PENDING", message, marketing)


class ValidationError(DataSetIQError):
    """Raised for invalid input parameters (400)."""

    def __init__(self, message: str):
        super().__init__(400, "VALIDATION_ERROR", message, None)
