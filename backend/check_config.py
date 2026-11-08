from app.core.config import settings

print("Application: ", settings.APP_NAME)
print("Version:", settings.APP_VERSION)
print("Debug:", settings.DEBUG)
print("Website:", settings.EBR_BASE_URL)
print("Timeout:", settings.REQUEST_TIMEOUT)