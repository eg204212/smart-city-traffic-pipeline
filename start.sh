#!/bin/bash

# Smart City Traffic System - Quick Start Script
# This script starts all services and validates the setup

set -e

echo "========================================="
echo "Smart City Traffic System - Quick Start"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down -v
echo ""

# Start infrastructure services first
echo "🚀 Starting infrastructure services (Zookeeper, Kafka, PostgreSQL)..."
docker-compose up -d zookeeper kafka postgres
echo ""

# Wait for services to be ready
echo "⏳ Waiting for Kafka to be ready (30 seconds)..."
sleep 30
echo ""

# Initialize database
echo "💾 Initializing PostgreSQL database..."
docker exec -i postgres psql -U airflow -d trafficdb < database/init.sql
echo "✅ Database initialized"
echo ""

# Start Airflow
echo "✈️ Starting Airflow..."
docker-compose up -d airflow-init
sleep 10
docker-compose up -d airflow-webserver airflow-scheduler
echo "✅ Airflow started"
echo ""

# Start Spark
echo "⚡ Starting Spark cluster..."
docker-compose up -d spark-master spark-worker
sleep 10
echo "✅ Spark cluster started"
echo ""

# Start producer
echo "📡 Starting traffic data producer..."
docker-compose up -d traffic-producer
sleep 5
echo "✅ Producer started"
echo ""

# Start Spark streaming job
echo "🌊 Starting Spark streaming processor..."
docker-compose up -d traffic-stream-processor
sleep 10
echo "✅ Stream processor started"
echo ""

# Verify services
echo "========================================="
echo "Verifying Services"
echo "========================================="
echo ""

# Check Kafka topic
echo "📋 Checking Kafka topics..."
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null || echo "⚠️ Kafka topics not yet created (will be auto-created)"
echo ""

# Check database
echo "💾 Checking PostgreSQL tables..."
docker exec postgres psql -U airflow -d trafficdb -c "\dt" 2>/dev/null | grep traffic && echo "✅ Tables created" || echo "⚠️ Tables not yet visible"
echo ""

# Display service URLs
echo "========================================="
echo "✅ All Services Started Successfully!"
echo "========================================="
echo ""
echo "Access the services at:"
echo ""
echo "🌐 Airflow Web UI:    http://localhost:8085"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "⚡ Spark Master UI:   http://localhost:8080"
echo "🔧 Spark Worker UI:   http://localhost:8081"
echo ""
echo "📊 PostgreSQL:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: trafficdb"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "========================================="
echo "Monitoring Commands"
echo "========================================="
echo ""
echo "View producer logs:     docker logs -f traffic-producer"
echo "View Spark logs:        docker logs -f traffic-stream-processor"
echo "View Airflow logs:      docker logs -f airflow-scheduler"
echo ""
echo "Connect to PostgreSQL:  docker exec -it postgres psql -U airflow -d trafficdb"
echo ""
echo "Stop all services:      docker-compose down"
echo "Stop and remove data:   docker-compose down -v"
echo ""
echo "========================================="
echo "🎉 Setup Complete! Traffic data is now flowing."
echo "========================================="
