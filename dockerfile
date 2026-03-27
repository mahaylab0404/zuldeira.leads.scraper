# 1. Use the specialized Apify Python Playwright image
# This comes pre-loaded with the OS-level dependencies Playwright needs.
FROM apify/actor-python-playwright:3.11

# 2. Set the working directory to the standard Apify user path
WORKDIR /home/myuser

# 3. Copy requirements first to leverage Docker's cache layer
# The --chown flag is MANDATORY in 2026 to avoid permission errors.
COPY --chown=myuser:myuser requirements.txt ./

# 4. Install your Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your Zuldeira project files
COPY --chown=myuser:myuser . ./

# 6. Install ONLY the Chromium browser
# We don't need Firefox or WebKit for Google Maps; this keeps the build fast.
RUN playwright install chromium

# 7. Start the engine
# This runs the 'src' folder as a Python module.
CMD ["python3", "-m", "src"]
