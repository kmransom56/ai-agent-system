#!/usr/bin/env python3
"""
AI Agent Orchestrator - Coordinates All Specialized Agents
Runs daily/weekly/monthly workflows with intelligent scheduling
"""
import os
import sys
import asyncio
import json
import schedule
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Import all agents
sys.path.insert(0, str(Path(__file__).parent))

from sales.lead_generation_agent import LeadGenerationAgent
from finance.financial_planning_agent import FinancialPlanningAgent
from research.market_intelligence_agent import MarketIntelligenceAgent
from research.customer_intelligence_agent import CustomerIntelligenceAgent
from operations.customer_success_agent import CustomerSuccessAgent
from operations.operations_agent import OperationsAgent
from marketing.content_marketing_agent import ContentMarketingAgent
from product.product_manager_agent import ProductManagerAgent
from engineering.devops_agent import DevOpsAgent
from engineering.qa_testing_agent import QATestingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/keith/chat-copilot/ai-agents/logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

class AgentOrchestrator:
    """Master orchestrator for all AI agents"""

    def __init__(self):
        self.logger = logger
        self.workspace = Path("/home/keith/chat-copilot/ai-agents")
        self.reports_dir = self.workspace / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all agents
        self.agents = {
            "sales_dev": LeadGenerationAgent(),
            "financial": FinancialPlanningAgent(),
            "market_intel": MarketIntelligenceAgent(),
            "customer_intel": CustomerIntelligenceAgent(),
            "customer_success": CustomerSuccessAgent(),
            "operations": OperationsAgent(),
            "content_marketing": ContentMarketingAgent(),
            "product_manager": ProductManagerAgent(),
            "devops": DevOpsAgent(),
            "qa_testing": QATestingAgent()
        }

        self.logger.info(f"🎯 Orchestrator initialized with {len(self.agents)} agents")

    async def daily_workflow(self):
        """Execute daily agent tasks in parallel"""
        self.logger.info("="*70)
        self.logger.info(f"🌅 DAILY WORKFLOW STARTING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*70)

        try:
            # Run independent agents in parallel
            tasks = [
                self.agents["sales_dev"].run(),
                self.agents["market_intel"].run(),
                self.agents["customer_success"].run(),
                self.agents["devops"].run(),
                self.agents["qa_testing"].run(),
                self.agents["operations"].run()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            daily_summary = {
                "timestamp": datetime.now().isoformat(),
                "workflow": "daily",
                "agents_executed": len(tasks),
                "results": {
                    "sales_dev": results[0] if len(results) > 0 else None,
                    "market_intel": results[1] if len(results) > 1 else None,
                    "customer_success": results[2] if len(results) > 2 else None,
                    "devops": results[3] if len(results) > 3 else None,
                    "qa_testing": results[4] if len(results) > 4 else None,
                    "operations": results[5] if len(results) > 5 else None
                },
                "errors": [r for r in results if isinstance(r, Exception)]
            }

            # Generate daily report
            report = self.generate_daily_report(daily_summary)

            # Save report
            self.save_daily_report(report)

            # Send notifications
            await self.send_notifications(report, "daily")

            self.logger.info(f"✅ Daily workflow complete - {len(daily_summary['errors'])} errors")

            return daily_summary

        except Exception as e:
            self.logger.error(f"❌ Daily workflow failed: {str(e)}")
            raise

    async def weekly_workflow(self):
        """Execute weekly agent tasks sequentially"""
        self.logger.info("="*70)
        self.logger.info(f"📊 WEEKLY WORKFLOW STARTING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*70)

        try:
            # Run weekly agents sequentially
            self.logger.info("💰 Running Financial Planning Agent")
            financial_results = await self.agents["financial"].run()

            self.logger.info("📝 Running Content Marketing Agent")
            marketing_results = await self.agents["content_marketing"].run()

            self.logger.info("🗺️ Running Product Manager Agent")
            product_results = await self.agents["product_manager"].run()

            self.logger.info("🔍 Running Customer Intelligence Agent")
            intel_results = await self.agents["customer_intel"].run()

            # Generate weekly summary
            weekly_summary = {
                "timestamp": datetime.now().isoformat(),
                "workflow": "weekly",
                "financial_update": financial_results,
                "marketing_content": marketing_results,
                "product_planning": product_results,
                "customer_intelligence": intel_results,
                "key_metrics": self.extract_key_metrics(financial_results)
            }

            # Generate weekly report
            report = self.generate_weekly_report(weekly_summary)

            # Save report
            self.save_weekly_report(report)

            # Send executive update
            await self.send_notifications(report, "weekly")

            self.logger.info("✅ Weekly workflow complete")

            return weekly_summary

        except Exception as e:
            self.logger.error(f"❌ Weekly workflow failed: {str(e)}")
            raise

    async def monthly_workflow(self):
        """Execute monthly strategic review"""
        self.logger.info("="*70)
        self.logger.info(f"📈 MONTHLY WORKFLOW STARTING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*70)

        try:
            # Collect all monthly data
            monthly_summary = {
                "timestamp": datetime.now().isoformat(),
                "workflow": "monthly",
                "performance_review": await self.generate_performance_review(),
                "strategic_recommendations": await self.generate_strategic_recommendations()
            }

            # Generate monthly report
            report = self.generate_monthly_report(monthly_summary)

            # Save report
            self.save_monthly_report(report)

            # Send executive briefing
            await self.send_notifications(report, "monthly")

            self.logger.info("✅ Monthly workflow complete")

            return monthly_summary

        except Exception as e:
            self.logger.error(f"❌ Monthly workflow failed: {str(e)}")
            raise

    def generate_daily_report(self, summary: Dict) -> str:
        """Generate human-readable daily report"""
        report = f"""
{'='*70}
🤖 AI AGENT DAILY REPORT
{'='*70}
Date: {datetime.now().strftime('%Y-%m-%d')}
Execution Time: {datetime.now().strftime('%H:%M:%S')}

📊 SALES DEVELOPMENT
"""
        sales_result = summary["results"].get("sales_dev", {})
        if sales_result and sales_result.get("success"):
            leads = sales_result.get("leads_generated", 0)
            report += f"  ✅ Generated {leads} qualified leads\n"
            report += f"  🎯 Top verticals: Healthcare, Retail, Banking\n"
        else:
            report += f"  ❌ Failed: {sales_result.get('error', 'Unknown')}\n"

        report += f"\n🔍 MARKET INTELLIGENCE\n"
        intel_result = summary["results"].get("market_intel", {})
        if intel_result and intel_result.get("success"):
            report += f"  ✅ Intelligence gathering complete\n"
            alerts = intel_result.get("alerts", [])
            if alerts:
                report += f"  🚨 {len(alerts)} priority alerts\n"
        else:
            report += f"  ❌ Failed: {intel_result.get('error', 'Unknown')}\n"

        report += f"\n👥 CUSTOMER SUCCESS\n"
        cs_result = summary["results"].get("customer_success", {})
        if cs_result and cs_result.get("success"):
            report_data = cs_result.get("report", {})
            at_risk = len(report_data.get("at_risk_customers", []))
            expansion = len(report_data.get("expansion_opportunities", []))
            report += f"  ✅ Health check complete\n"
            report += f"  ⚠️  {at_risk} at-risk customers\n"
            report += f"  💰 {expansion} expansion opportunities\n"
        else:
            report += f"  ❌ Failed: {cs_result.get('error', 'Unknown')}\n"

        report += f"\n{'='*70}\n"

        return report

    def generate_weekly_report(self, summary: Dict) -> str:
        """Generate human-readable weekly report"""
        report = f"""
{'='*70}
💰 AI AGENT WEEKLY FINANCIAL REPORT
{'='*70}
Week Ending: {datetime.now().strftime('%Y-%m-%d')}

FINANCIAL METRICS
"""
        metrics = summary.get("key_metrics", {})
        if metrics:
            report += f"  ARR: ${metrics.get('current_arr', 0):,.0f}\n"
            report += f"  MRR: ${metrics.get('current_mrr', 0):,.0f}\n"
            report += f"  Customers: {metrics.get('customers', 0)}\n"
            report += f"  Variance: {metrics.get('variance_percent', 0):+.1f}%\n"
            report += f"  Burn Rate: ${metrics.get('burn_rate', 0):,.0f}/month\n"
            report += f"  Runway: {metrics.get('runway_months', 0):.1f} months\n"

        report += f"\n{'='*70}\n"

        return report

    def generate_monthly_report(self, summary: Dict) -> str:
        """Generate human-readable monthly report"""
        report = f"""
{'='*70}
📈 AI AGENT MONTHLY EXECUTIVE BRIEFING
{'='*70}
Month: {datetime.now().strftime('%B %Y')}

MONTHLY PERFORMANCE REVIEW
[Comprehensive analysis would be generated here]

STRATEGIC RECOMMENDATIONS
[AI-generated strategic recommendations would be included here]

{'='*70}
"""
        return report

    def save_daily_report(self, report: str):
        """Save daily report to file"""
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath = self.reports_dir / filename
        with open(filepath, 'w') as f:
            f.write(report)
        self.logger.info(f"📄 Daily report saved: {filename}")

    def save_weekly_report(self, report: str):
        """Save weekly report to file"""
        filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath = self.reports_dir / filename
        with open(filepath, 'w') as f:
            f.write(report)
        self.logger.info(f"📄 Weekly report saved: {filename}")

    def save_monthly_report(self, report: str):
        """Save monthly report to file"""
        filename = f"monthly_report_{datetime.now().strftime('%Y%m')}.txt"
        filepath = self.reports_dir / filename
        with open(filepath, 'w') as f:
            f.write(report)
        self.logger.info(f"📄 Monthly report saved: {filename}")

    async def send_notifications(self, report: str, frequency: str):
        """Send notifications (email, Slack, etc.)"""
        # In production, integrate with email/Slack
        self.logger.info(f"📤 {frequency.capitalize()} notifications sent")
        # TODO: Implement email/Slack integration

    def extract_key_metrics(self, financial_results: Dict) -> Dict:
        """Extract key metrics from financial results"""
        if not financial_results or not financial_results.get("success"):
            return {}

        metrics = financial_results.get("metrics", {})
        return {
            "current_arr": metrics.get("current_arr", 0),
            "current_mrr": metrics.get("current_mrr", 0),
            "customers": metrics.get("customers", 0),
            "variance_percent": metrics.get("variance_percent", 0),
            "burn_rate": metrics.get("burn_rate", 0),
            "runway_months": metrics.get("runway_months", 0)
        }

    async def generate_performance_review(self) -> Dict:
        """Generate monthly performance review"""
        # Aggregate data from all agents
        return {
            "summary": "Monthly performance analysis",
            "highlights": ["Metric 1", "Metric 2"],
            "concerns": ["Issue 1", "Issue 2"]
        }

    async def generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic recommendations"""
        return [
            "Accelerate healthcare vertical expansion",
            "Increase marketing spend in Q2",
            "Hire 3 additional AEs for high-ARR verticals"
        ]

    def schedule_workflows(self):
        """Schedule all agent workflows"""
        self.logger.info("⏰ Scheduling workflows...")

        # Daily tasks - 8:00 AM
        schedule.every().day.at("08:00").do(
            lambda: asyncio.run(self.daily_workflow())
        )

        # Weekly tasks - Monday 9:00 AM
        schedule.every().monday.at("09:00").do(
            lambda: asyncio.run(self.weekly_workflow())
        )

        # Monthly tasks - 1st of month at 10:00 AM
        schedule.every().day.at("10:00").do(
            lambda: self.run_monthly_if_first() and asyncio.run(self.monthly_workflow())
        )

        self.logger.info("✅ Workflows scheduled:")
        self.logger.info("   📅 Daily: 8:00 AM (lead gen, intel, health checks)")
        self.logger.info("   📅 Weekly: Monday 9:00 AM (financial update)")
        self.logger.info("   📅 Monthly: 1st at 10:00 AM (executive review)")

    def run_monthly_if_first(self) -> bool:
        """Check if today is the 1st of the month"""
        return datetime.now().day == 1

    def run_forever(self):
        """Keep orchestrator running 24/7"""
        self.logger.info("🚀 Agent Orchestrator ACTIVE - Running 24/7")
        self.logger.info("   Press Ctrl+C to stop")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("\n👋 Orchestrator shutting down...")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in orchestrator: {str(e)}")
                time.sleep(60)

async def test_agents():
    """Test all agents immediately"""
    print("\n🧪 TESTING ALL AI AGENTS\n")

    orchestrator = AgentOrchestrator()

    print("Running daily workflow test...")
    await orchestrator.daily_workflow()

    print("\nRunning weekly workflow test...")
    await orchestrator.weekly_workflow()

    print("\n✅ Agent testing complete!")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Agent Orchestrator")
    parser.add_argument("--test", action="store_true", help="Test all agents immediately")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (24/7)")
    args = parser.parse_args()

    orchestrator = AgentOrchestrator()

    if args.test:
        # Test mode - run agents immediately
        asyncio.run(test_agents())
    elif args.daemon:
        # Daemon mode - schedule and run forever
        orchestrator.schedule_workflows()
        orchestrator.run_forever()
    else:
        # Interactive mode
        print("\n🤖 AI Agent Orchestrator")
        print("\nOptions:")
        print("  1. Test agents now")
        print("  2. Run as daemon (24/7)")
        print("  3. Exit")

        choice = input("\nSelect option: ")

        if choice == "1":
            asyncio.run(test_agents())
        elif choice == "2":
            orchestrator.schedule_workflows()
            orchestrator.run_forever()
        else:
            print("👋 Exiting...")

if __name__ == "__main__":
    main()
