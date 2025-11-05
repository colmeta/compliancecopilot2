#!/usr/bin/env python3
"""
Automated Render Deployment Script for CLARITY
Uses Render API to deploy the platform
"""

import os
import sys
import json
import requests
from typing import Dict, Any

class RenderDeployer:
    """Automate CLARITY deployment to Render."""
    
    def __init__(self, api_key: str):
        """Initialize with Render API key."""
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def check_connection(self) -> bool:
        """Test Render API connection."""
        try:
            response = requests.get(
                f"{self.base_url}/owners",
                headers=self.headers
            )
            if response.status_code == 200:
                print("✅ Render API connection successful")
                return True
            else:
                print(f"❌ Render API error: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_owner_id(self) -> str:
        """Get the owner ID for creating services."""
        response = requests.get(
            f"{self.base_url}/owners",
            headers=self.headers
        )
        owners = response.json()
        if owners:
            owner_id = owners[0]['owner']['id']
            print(f"✅ Owner ID: {owner_id}")
            return owner_id
        raise Exception("No owner found")
    
    def create_postgres_database(self, owner_id: str, name: str = "clarity-db") -> Dict[str, Any]:
        """Create PostgreSQL database."""
        print(f"\n📊 Creating PostgreSQL database: {name}")
        
        payload = {
            "name": name,
            "databaseName": "clarity",
            "databaseUser": "clarity",
            "plan": "starter",  # or "free"
            "region": "oregon",
            "ownerId": owner_id
        }
        
        response = requests.post(
            f"{self.base_url}/postgres",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            db = response.json()
            print(f"✅ Database created: {db['postgres']['id']}")
            return db['postgres']
        else:
            print(f"❌ Failed to create database: {response.status_code}")
            print(response.text)
            raise Exception("Database creation failed")
    
    def create_redis_instance(self, owner_id: str, name: str = "clarity-redis") -> Dict[str, Any]:
        """Create Redis instance."""
        print(f"\n🔴 Creating Redis instance: {name}")
        
        payload = {
            "name": name,
            "plan": "starter",  # or "free"
            "region": "oregon",
            "maxmemoryPolicy": "allkeys-lru",
            "ownerId": owner_id
        }
        
        response = requests.post(
            f"{self.base_url}/redis",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            redis = response.json()
            print(f"✅ Redis created: {redis['redis']['id']}")
            return redis['redis']
        else:
            print(f"❌ Failed to create Redis: {response.status_code}")
            print(response.text)
            raise Exception("Redis creation failed")
    
    def create_web_service(
        self,
        owner_id: str,
        repo_url: str,
        database_url: str,
        redis_url: str,
        env_vars: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create web service."""
        print(f"\n🌐 Creating web service")
        
        # Prepare environment variables
        all_env_vars = [
            {"key": "PYTHON_VERSION", "value": "3.11.6"},
            {"key": "FLASK_ENV", "value": "production"},
            {"key": "FLASK_DEBUG", "value": "false"},
            {"key": "DATABASE_URL", "value": database_url},
            {"key": "REDIS_URL", "value": redis_url},
            {"key": "CELERY_BROKER_URL", "value": redis_url},
            {"key": "CELERY_RESULT_BACKEND", "value": redis_url},
        ]
        
        # Add user-provided env vars
        for key, value in env_vars.items():
            all_env_vars.append({"key": key, "value": value})
        
        payload = {
            "type": "web_service",
            "name": "clarity-web",
            "ownerId": owner_id,
            "repo": repo_url,
            "branch": "main",
            "buildCommand": "./build-render.sh",
            "startCommand": "gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120",
            "plan": "starter",
            "region": "oregon",
            "envVars": all_env_vars,
            "autoDeploy": True
        }
        
        response = requests.post(
            f"{self.base_url}/services",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            service = response.json()
            print(f"✅ Web service created: {service['service']['id']}")
            print(f"🌍 URL: https://{service['service']['slug']}.onrender.com")
            return service['service']
        else:
            print(f"❌ Failed to create web service: {response.status_code}")
            print(response.text)
            raise Exception("Web service creation failed")
    
    def create_background_worker(
        self,
        owner_id: str,
        repo_url: str,
        database_url: str,
        redis_url: str,
        env_vars: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create background worker."""
        print(f"\n⚙️ Creating background worker")
        
        # Prepare environment variables
        all_env_vars = [
            {"key": "PYTHON_VERSION", "value": "3.11.6"},
            {"key": "DATABASE_URL", "value": database_url},
            {"key": "REDIS_URL", "value": redis_url},
            {"key": "CELERY_BROKER_URL", "value": redis_url},
            {"key": "CELERY_RESULT_BACKEND", "value": redis_url},
        ]
        
        # Add user-provided env vars
        for key, value in env_vars.items():
            all_env_vars.append({"key": key, "value": value})
        
        payload = {
            "type": "background_worker",
            "name": "clarity-worker",
            "ownerId": owner_id,
            "repo": repo_url,
            "branch": "main",
            "buildCommand": "./build-render.sh",
            "startCommand": "celery -A celery_worker.celery_app worker --loglevel=info --concurrency=2",
            "plan": "starter",
            "region": "oregon",
            "envVars": all_env_vars,
            "autoDeploy": True
        }
        
        response = requests.post(
            f"{self.base_url}/services",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            service = response.json()
            print(f"✅ Background worker created: {service['service']['id']}")
            return service['service']
        else:
            print(f"❌ Failed to create worker: {response.status_code}")
            print(response.text)
            raise Exception("Worker creation failed")
    
    def deploy_clarity(
        self,
        repo_url: str,
        google_api_key: str,
        flask_secret_key: str,
        openai_api_key: str = "",
        anthropic_api_key: str = "",
        groq_api_key: str = ""
    ):
        """Deploy complete CLARITY platform to Render."""
        print("🚀 Starting CLARITY deployment to Render")
        print("=" * 60)
        
        try:
            # Step 1: Check connection
            if not self.check_connection():
                return False
            
            # Step 2: Get owner ID
            owner_id = self.get_owner_id()
            
            # Step 3: Create PostgreSQL database
            database = self.create_postgres_database(owner_id)
            database_url = database['connectionInfo']['internalConnectionString']
            
            # Step 4: Create Redis instance
            redis = self.create_redis_instance(owner_id)
            redis_url = redis['connectionInfo']['internalConnectionString']
            
            # Wait for databases to provision
            print("\n⏳ Waiting for databases to provision (30 seconds)...")
            import time
            time.sleep(30)
            
            # Step 5: Prepare environment variables
            env_vars = {
                "FLASK_SECRET_KEY": flask_secret_key,
                "GOOGLE_API_KEY": google_api_key,
            }
            
            if openai_api_key:
                env_vars["OPENAI_API_KEY"] = openai_api_key
            if anthropic_api_key:
                env_vars["ANTHROPIC_API_KEY"] = anthropic_api_key
            if groq_api_key:
                env_vars["GROQ_API_KEY"] = groq_api_key
            
            # Step 6: Create web service
            web_service = self.create_web_service(
                owner_id, repo_url, database_url, redis_url, env_vars
            )
            
            # Step 7: Create background worker
            worker_service = self.create_background_worker(
                owner_id, repo_url, database_url, redis_url, env_vars
            )
            
            # Success!
            print("\n" + "=" * 60)
            print("🎉 CLARITY DEPLOYMENT SUCCESSFUL!")
            print("=" * 60)
            print(f"\n🌍 Your CLARITY platform is live at:")
            print(f"   https://{web_service['slug']}.onrender.com")
            print(f"\n📊 Services created:")
            print(f"   - Web Service: {web_service['name']}")
            print(f"   - Background Worker: {worker_service['name']}")
            print(f"   - PostgreSQL: clarity-db")
            print(f"   - Redis: clarity-redis")
            print(f"\n⏳ Build will take 5-8 minutes. Check Render dashboard for progress.")
            print(f"\n🔑 Next steps:")
            print(f"   1. Wait for build to complete")
            print(f"   2. Access your platform")
            print(f"   3. Register and generate API keys")
            print(f"   4. Share with clients!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            return False


def main():
    """Main deployment function."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║        🚀 CLARITY - Automated Render Deployment 🚀          ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Get Render API key
    render_api_key = os.getenv("RENDER_API_KEY")
    if not render_api_key:
        print("❌ RENDER_API_KEY environment variable not set")
        print("\nTo get your Render API key:")
        print("1. Go to https://dashboard.render.com/")
        print("2. Click your profile → Account Settings")
        print("3. Go to 'API Keys' tab")
        print("4. Create new API key")
        print("5. Set it: export RENDER_API_KEY='your-key'")
        print("\nThen run this script again:")
        print("   python deploy-to-render.py")
        sys.exit(1)
    
    # Get repository URL
    repo_url = os.getenv("GITHUB_REPO_URL")
    if not repo_url:
        print("❌ GITHUB_REPO_URL not set")
        print("\nSet your GitHub repository URL:")
        print("   export GITHUB_REPO_URL='https://github.com/yourusername/clarity'")
        sys.exit(1)
    
    # Get required API keys
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not set (required)")
        sys.exit(1)
    
    flask_secret_key = os.getenv("FLASK_SECRET_KEY")
    if not flask_secret_key:
        print("⚠️ FLASK_SECRET_KEY not set, generating random key...")
        import secrets
        flask_secret_key = secrets.token_hex(32)
        print(f"✅ Generated: {flask_secret_key}")
    
    # Optional API keys
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    
    # Create deployer and deploy
    deployer = RenderDeployer(render_api_key)
    success = deployer.deploy_clarity(
        repo_url=repo_url,
        google_api_key=google_api_key,
        flask_secret_key=flask_secret_key,
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        groq_api_key=groq_api_key
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
