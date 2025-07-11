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

# Expose the port your Flask app runs on
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]