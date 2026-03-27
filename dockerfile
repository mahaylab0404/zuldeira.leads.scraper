# 1. Use the specialized Apify Python Playwright image
FROM apify/actor-python-playwright:3.11

# 2. Copy all files into the container 
# We use --chown to ensure the 'myuser' account can access them
COPY --chown=myuser:myuser . ./

# 3. Install your Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 4. Install only the Chromium browser
RUN playwright install chromium

# 5. Start the engine
# Note: We don't use a relative path here to keep it clean
CMD ["python3", "-m", "src"]
