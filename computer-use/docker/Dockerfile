FROM python:3.11-slim

# Install system dependencies for browser automation
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements-computer-use.txt .
RUN pip install --no-cache-dir -r requirements-computer-use.txt

# Set up display
ENV DISPLAY=:99
ENV RESOLUTION=1920x1080x24

# Create startup script
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 $RESOLUTION &\n\
fluxbox &\n\
x11vnc -display :99 -forever -shared -rfbport 5900 &\n\
websockify --web /usr/share/novnc 6080 localhost:5900 &\n\
exec "$@"' > /start.sh && chmod +x /start.sh

# Copy application files
COPY . /app

# Expose VNC web interface
EXPOSE 6080

# Start services and keep container running
ENTRYPOINT ["/start.sh"]
CMD ["python", "computer_use_server.py"]
