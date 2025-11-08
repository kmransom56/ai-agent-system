#!/usr/bin/env python3
"""
Base Agent Class - Foundation for all specialized AI agents
Provides common functionality: logging, memory management, MCP integration
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio

# Add parent directory to path for MCP server imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/keith/chat-copilot/ai-agents/logs/agents.log'),
        logging.StreamHandler()
    ]
)

class BaseAgent:
    """Base class for all AI agents"""

    def __init__(self, name: str, role: str, config: Optional[Dict] = None):
        self.name = name
        self.role = role
        self.config = config or {}
        self.logger = logging.getLogger(f"Agent.{name}")
        self.start_time = datetime.now()

        # Initialize agent workspace
        self.workspace = Path("/home/keith/chat-copilot/ai-agents")
        self.logs_dir = self.workspace / "logs"
        self.cache_dir = self.workspace / "cache" / name.lower().replace(" ", "_")

        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"🤖 {self.name} initialized - Role: {self.role}")

    def save_context(self, context_id: str, data: Dict[str, Any]) -> None:
        """Save context data to cache"""
        cache_file = self.cache_dir / f"{context_id}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "data": data
            }, f, indent=2)
        self.logger.debug(f"💾 Saved context: {context_id}")

    def load_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Load context data from cache"""
        cache_file = self.cache_dir / f"{context_id}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
            self.logger.debug(f"📂 Loaded context: {context_id}")
            return data.get("data")
        return None

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task - override in specialized agents"""
        raise NotImplementedError("Specialized agents must implement execute_task()")

    async def run(self) -> Dict[str, Any]:
        """Main execution loop - override in specialized agents"""
        raise NotImplementedError("Specialized agents must implement run()")

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate execution report"""
        duration = (datetime.now() - self.start_time).total_seconds()

        report = f"""
{'=' * 70}
Agent Execution Report
{'=' * 70}
Agent: {self.name}
Role: {self.role}
Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} seconds
Status: {'✅ Complete' if results.get('success') else '❌ Failed'}
{'=' * 70}

Results:
{json.dumps(results, indent=2)}
"""
        return report

    def log_metric(self, metric_name: str, value: Any) -> None:
        """Log performance metric"""
        metrics_file = self.logs_dir / "metrics.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "metric": metric_name,
                "value": value
            }) + "\n")

if __name__ == "__main__":
    # Test base agent
    agent = BaseAgent("TestAgent", "testing")
    agent.logger.info("Base agent initialized successfully")
    print(agent.generate_report({"success": True, "test": "passed"}))
