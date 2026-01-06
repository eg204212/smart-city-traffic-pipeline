@echo off
REM Smart City Traffic System - Quick Start Script (Windows)
REM This script starts all services and validates the setup

echo =========================================
echo Smart City Traffic System - Quick Start
echo =========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo X Error: Docker is not running. Please start Docker Desktop.
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Stop any existing containers
echo Cleaning up existing containers...
docker-compose down -v
echo.

REM Start infrastructure services first
echo Starting infrastructure services (Zookeeper, Kafka, PostgreSQL)...
docker-compose up -d zookeeper kafka postgres
echo.

REM Wait for services to be ready
echo Waiting for Kafka to be ready (30 seconds)...
timeout /t 30 /nobreak >nul
echo.

REM Initialize database
echo Initializing PostgreSQL database...
docker exec -i postgres psql -U airflow -d trafficdb < database\init.sql
echo [OK] Database initialized
echo.

REM Start Airflow
echo Starting Airflow...
docker-compose up -d airflow-init
timeout /t 10 /nobreak >nul
docker-compose up -d airflow-webserver airflow-scheduler
echo [OK] Airflow started
echo.

REM Start Spark
echo Starting Spark cluster...
docker-compose up -d spark-master spark-worker
timeout /t 10 /nobreak >nul
echo [OK] Spark cluster started
echo.

REM Start producer
echo Starting traffic data producer...
docker-compose up -d traffic-producer
timeout /t 5 /nobreak >nul
echo [OK] Producer started
echo.

REM Start Spark streaming job
echo Starting Spark streaming processor...
docker-compose up -d traffic-stream-processor
timeout /t 10 /nobreak >nul
echo [OK] Stream processor started
echo.

REM Display service URLs
echo =========================================
echo [OK] All Services Started Successfully!
echo =========================================
echo.
echo Access the services at:
echo.
echo Airflow Web UI:    http://localhost:8085
echo    Username: admin
echo    Password: admin
echo.
echo Spark Master UI:   http://localhost:8080
echo Spark Worker UI:   http://localhost:8081
echo.
echo PostgreSQL:
echo    Host: localhost
echo    Port: 5432
echo    Database: trafficdb
echo    Username: airflow
echo    Password: airflow
echo.
echo =========================================
echo Monitoring Commands
echo =========================================
echo.
echo View producer logs:     docker logs -f traffic-producer
echo View Spark logs:        docker logs -f traffic-stream-processor
echo View Airflow logs:      docker logs -f airflow-scheduler
echo.
echo Connect to PostgreSQL:  docker exec -it postgres psql -U airflow -d trafficdb
echo.
echo Stop all services:      docker-compose down
echo Stop and remove data:   docker-compose down -v
echo.
echo =========================================
echo Setup Complete! Traffic data is now flowing.
echo =========================================

pause
