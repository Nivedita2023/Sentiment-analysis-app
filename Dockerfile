# *******************************************
# Stage 1: Builder
# *******************************************
FROM python:3.13-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install system dependencies only if needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# COPY only requirements to leverage caching
COPY ./flask_app/requirements.txt .

# Install dependencies  using pre-built binaries where possible
RUN pip install --prefix=/install --no-cache-dir --prefer-binary -r requirements.txt

# Download NLTK data inside builder stage (isolated)
RUN mkdir -p /nltk_data && \
    PYTHONPATH=/install/lib/python3.13/site-packages \
    python -m nltk.downloader -d /nltk_data stopwords wordnet

# Remove build tools to shrink builder layer
RUN apt-get purge -y build-essential gcc && apt-get autoremove -y


# *******************************************
# Stage 2: Final Image
# *******************************************
FROM python:3.13-slim-bookworm As final

# Set working directory
WORKDIR /app

# Copy installed python packages and NLTK data from builder
COPY --from=builder /install /usr/local
ENV NLTK_DATA=/usr/local/nltk_data
COPY --from=builder /nltk_data ${NLTK_DATA}

# Copy only necessary application files to reduce image size
COPY ./flask_app/app.py .
COPY ./flask_app/templates/ ./templates/
COPY ./models/ ./models/

# Add environment variable and Expose the port
ENV PORT=5000
EXPOSE 5000

# RUN the Flask app
CMD ["python", "app.py"]
