#!/bin/bash

# Build the image
echo "🏗️ Building portfolio image..."
docker build -t portfolio:latest .

# Stop and remove old container if exists
echo "🛑 Stopping and removing old container if exists..."
docker stop my-portfolio >/dev/null 2>&1
docker rm my-portfolio >/dev/null 2>&1

# Run new container and expose port 8080 → 80
echo "🐳 Running container on http://localhost:8080"
docker run -d -p 8080:80 --name my-portfolio portfolio:latest

# Wait for container to start
sleep 2

# Show logs
echo "🔍 Container logs:"
docker logs --tail 20 my-portfolio

# Health check
echo "🩺 Health check:"
curl -I http://localhost:8080

echo -e "\n✅ Portfolio is running at http://localhost:8080"
echo "💡 Test locally before connecting Cloudflare Tunnel"
