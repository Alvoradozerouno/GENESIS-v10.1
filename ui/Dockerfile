# GENESIS UI - Nginx serving static HTML
FROM nginx:alpine

LABEL maintainer="GENESIS Team"
LABEL description="GENESIS Sovereign AI Dashboard"
LABEL version="10.1"

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf 2>/dev/null || true

# Copy UI files
COPY index.html /usr/share/nginx/html/index.html
COPY assets/ /usr/share/nginx/html/assets/ 2>/dev/null || true

# Set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
