#!/usr/bin/env python3
"""
AI Agent Monitoring Dashboard
Real-time monitoring of all agent activities, metrics, and health
"""
import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)

# Configuration
WORKSPACE = Path("/home/keith/chat-copilot/ai-agents")
LOGS_DIR = WORKSPACE / "logs"
CACHE_DIR = WORKSPACE / "cache"
REPORTS_DIR = WORKSPACE / "reports"

class AgentDashboard:
    """Monitor and display agent status"""

    def __init__(self):
        self.agents = [
            "sales_dev",
            "financial",
            "market_intel",
            "customer_intel",
            "customer_success",
            "operations",
            "content_marketing",
            "product_manager",
            "devops",
            "qa_testing"
        ]

    def get_agent_status(self) -> List[Dict]:
        """Get current status of all agents"""
        status_list = []

        for agent in self.agents:
            agent_dir = CACHE_DIR / agent.replace("_", "_")

            # Find most recent cache file
            cache_files = list(agent_dir.glob("*.json")) if agent_dir.exists() else []

            if cache_files:
                latest_file = max(cache_files, key=lambda x: x.stat().st_mtime)
                last_run = datetime.fromtimestamp(latest_file.stat().st_mtime)
                status = "active" if (datetime.now() - last_run).seconds < 3600 else "idle"
            else:
                last_run = None
                status = "not_started"

            status_list.append({
                "name": agent.replace("_", " ").title(),
                "agent_id": agent,
                "status": status,
                "last_run": last_run.isoformat() if last_run else None,
                "cache_files": len(cache_files)
            })

        return status_list

    def get_recent_metrics(self, limit: int = 50) -> List[Dict]:
        """Get recent metrics from log file"""
        metrics_file = LOGS_DIR / "metrics.jsonl"

        if not metrics_file.exists():
            return []

        metrics = []
        with open(metrics_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    metrics.append(json.loads(line))
                except:
                    continue

        return metrics

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary dashboard metrics"""
        metrics = self.get_recent_metrics(500)

        summary = {
            "leads_generated_today": 0,
            "weekly_arr": 0,
            "healthy_services": 0,
            "tests_passed": 0,
            "blog_posts_created": 0,
            "at_risk_customers": 0,
            "expansion_opportunities": 0
        }

        # Aggregate latest values
        for metric in reversed(metrics):
            metric_name = metric.get("metric")
            if metric_name in summary and summary[metric_name] == 0:
                summary[metric_name] = metric.get("value", 0)

        return summary

    def get_recent_reports(self) -> List[Dict]:
        """Get list of recent reports"""
        reports = []

        if REPORTS_DIR.exists():
            for report_file in sorted(REPORTS_DIR.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                reports.append({
                    "name": report_file.name,
                    "type": "daily" if "daily" in report_file.name else "weekly",
                    "date": datetime.fromtimestamp(report_file.stat().st_mtime).isoformat(),
                    "size": report_file.stat().st_size
                })

        return reports

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        status_list = self.get_agent_status()

        active_agents = len([a for a in status_list if a["status"] == "active"])
        total_agents = len(status_list)

        return {
            "overall_health": "healthy" if active_agents >= total_agents * 0.7 else "degraded",
            "active_agents": active_agents,
            "total_agents": total_agents,
            "health_percentage": round((active_agents / total_agents) * 100, 1)
        }

# Initialize dashboard
dashboard = AgentDashboard()

@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("dashboard.html")

@app.route("/api/status")
def api_status():
    """API endpoint for agent status"""
    return jsonify({
        "agents": dashboard.get_agent_status(),
        "system_health": dashboard.get_system_health()
    })

@app.route("/api/metrics")
def api_metrics():
    """API endpoint for metrics"""
    return jsonify({
        "summary": dashboard.get_summary_metrics(),
        "recent": dashboard.get_recent_metrics(100)
    })

@app.route("/api/reports")
def api_reports():
    """API endpoint for reports"""
    return jsonify({
        "reports": dashboard.get_recent_reports()
    })

@app.route("/api/report/<report_name>")
def api_report_content(report_name):
    """Get specific report content"""
    report_file = REPORTS_DIR / report_name

    if report_file.exists():
        with open(report_file, 'r') as f:
            return jsonify({
                "name": report_name,
                "content": f.read()
            })
    else:
        return jsonify({"error": "Report not found"}), 404

if __name__ == "__main__":
    print("🎯 AI Agent Dashboard Starting...")
    print("📊 Access dashboard at: http://localhost:11050")
    print("")

    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    app.run(host="0.0.0.0", port=11050, debug=True)
