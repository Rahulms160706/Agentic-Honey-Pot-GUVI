"""
Debug UPI validation
"""
upi = "1234567890@paytm"
valid_providers = ['paytm', 'phonepe', 'googlepay', 'ybl', 'okaxis', 
                 'oksbi', 'okicici', 'okhdfc', 'upi', 'apl', 'axl', 'ibl', 'barodampay']

upi_lower = upi.lower()
provider = upi_lower.split('@')[-1]

print(f"Original UPI: {upi}")
print(f"Lowercased UPI: {upi_lower}")
print(f"Provider: {provider}")
print(f"Provider length: {len(provider)}")
print(f"Provider contains dot: {'.' in provider}")

# Check if provider matches
matches = any(p in provider for p in valid_providers)
print(f"Provider matches known list: {matches}")

# Alternative check
alt_check = len(provider) > 2 and '.' in provider
print(f"Alternative check (len > 2 and has dot): {alt_check}")

# Final result
result = matches or alt_check
print(f"Final result (should be added): {result}")
