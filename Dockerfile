FROM nginx:1.25.5-alpine
RUN apk update && apk upgrade --no-cache
# Set environment variables
ENV NGINX_ENV=production \
    NGINX_USER=portfolio

# Create non-root user and group
RUN addgroup -S $NGINX_USER && \
    adduser -S -G $NGINX_USER $NGINX_USER && \
    chown -R $NGINX_USER:$NGINX_USER /var/cache/nginx && \
    chown -R $NGINX_USER:$NGINX_USER /var/run && \
    touch /var/run/nginx.pid && \
    chown -R $NGINX_USER:$NGINX_USER /var/run/nginx.pid

# Remove default configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories
RUN mkdir -p /usr/share/nginx/html/assets

# Copy website files
COPY *.html/ /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/
COPY /assets/terraform/terraform.zip /usr/share/nginx/html/assets/terraform.zip

# Create security.txt
RUN mkdir -p /usr/share/nginx/html/.well-known && \
    echo -e "Contact: mailto:daniel.rada1891@gmail.com\nEncryption: https://keys.openpgp.org/search?q=daniel.rada1891%40gmail.com\nPolicy: https://danielrada.com/security-policy" > /usr/share/nginx/html/.well-known/security.txt

# Set permissions - FIXED: Added missing && operator
RUN chown -R $NGINX_USER:$NGINX_USER /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \; && \
    chmod 444 /usr/share/nginx/html/.well-known/security.txt && \
    chown -R $NGINX_USER:$NGINX_USER /usr/share/nginx/html/assets

# Remove unnecessary packages
RUN apk del apk-tools && \
    rm -rf /var/cache/apk/*

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1

# Expose port 80
EXPOSE 80

# Run as non-root user
USER $NGINX_USER

# Start Nginx with security enhancements
CMD ["nginx", "-g", "daemon off; error_log /dev/stderr info;"]
