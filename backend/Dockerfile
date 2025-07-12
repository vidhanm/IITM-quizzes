# Use an official Python image as the base
FROM python:3.10-slim AS backend

# Install Node.js (for building frontend)
RUN apt-get update && apt-get install -y nodejs npm

# Set workdir for backend
WORKDIR /app

# Copy backend code
COPY ./backend/ /app/

# Copy frontend code into the image
COPY ./frontend/ /frontend/

# Build frontend
WORKDIR /frontend
RUN npm install && npm run build

# Move built frontend to backend's dist folder
WORKDIR /app
RUN rm -rf dist && cp -r /backend/dist ./dist

# Install backend dependencies
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Create a startup script to handle environment variables
RUN echo '#!/bin/bash\n\
# Create .env file in the backend directory\n\
if [ ! -z "$OPENROUTER_API_KEY" ]; then\n\
    echo "OPENROUTER_API_KEY=$OPENROUTER_API_KEY" > /app/.env\n\
    echo "Environment variables set successfully in /app/.env"\n\
else\n\
    echo "Warning: OPENROUTER_API_KEY not set"\n\
fi\n\
\n\
# Run the Flask app\n\
exec python main.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the port your Flask app runs on
EXPOSE 5000

# Use the start script
CMD ["/app/start.sh"]