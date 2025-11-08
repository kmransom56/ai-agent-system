#!/usr/bin/env python3
"""
Financial Planning Agent - Automated Financial Tracking
Monitors ARR, MRR, burn rate, generates investor reports
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_agent import BaseAgent

class FinancialPlanningAgent(BaseAgent):
    """AI agent for financial planning and reporting"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(
            name="Financial Planning Agent",
            role="Financial Operations",
            config=config or {}
        )

        # Load GTM financial projections
        self.gtm_plans_dir = Path("/home/keith/chat-copilot/go-to-market-plans")
        self.master_plan = self.load_master_projections()

        # Financial targets
        self.year_1_arr_target = 85_700_000  # $85.7M from master plan
        self.year_2_arr_target = 292_600_000  # $292.6M
        self.year_3_arr_target = 524_400_000  # $524.4M

        self.logger.info(f"💰 Financial targets loaded - Year 1: ${self.year_1_arr_target:,.0f}")

    def load_master_projections(self) -> Dict:
        """Load financial projections from master GTM plan"""
        master_file = self.gtm_plans_dir / "MASTER-EXECUTIVE-SUMMARY.md"

        if not master_file.exists():
            self.logger.warning("Master GTM plan not found")
            return {}

        # Parse key financial metrics
        projections = {
            "verticals": {
                "healthcare": {"y1": 40_500_000, "y2": 153_000_000, "y3": 265_500_000},
                "retail": {"y1": 21_600_000, "y2": 80_100_000, "y3": 138_600_000},
                "restaurant": {"y1": 4_200_000, "y2": 14_800_000, "y3": 32_500_000},
                "banking": {"y1": 2_500_000, "y2": 7_500_000, "y3": 23_000_000},
                "education": {"y1": 4_200_000, "y2": 8_400_000, "y3": 15_800_000},
                "manufacturing": {"y1": 5_000_000, "y2": 10_000_000, "y3": 15_000_000},
                "msp": {"y1": 1_600_000, "y2": 6_400_000, "y3": 12_800_000},
                "hospitality": {"y1": 3_500_000, "y2": 6_800_000, "y3": 10_000_000},
                "franchise": {"y1": 2_500_000, "y2": 5_000_000, "y3": 9_400_000},
                "dns_saas": {"y1": 100_000, "y2": 600_000, "y3": 1_800_000}
            },
            "total": {
                "y1": 85_700_000,
                "y2": 292_600_000,
                "y3": 524_400_000
            }
        }

        return projections

    async def weekly_financial_update(self) -> Dict[str, Any]:
        """Generate weekly financial dashboard"""
        self.logger.info("📊 Generating weekly financial update")

        try:
            # Calculate current metrics
            current_arr = await self.calculate_current_arr()
            current_mrr = current_arr / 12
            customers = await self.get_customer_count()

            # Calculate variance from plan
            variance = await self.calculate_variance(current_arr)

            # Generate key metrics
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "current_arr": current_arr,
                "current_mrr": current_mrr,
                "target_arr_y1": self.year_1_arr_target,
                "variance_dollars": current_arr - self.year_1_arr_target,
                "variance_percent": ((current_arr / self.year_1_arr_target) - 1) * 100 if self.year_1_arr_target > 0 else 0,
                "customers": customers,
                "arpc": current_arr / customers if customers > 0 else 0,  # Average Revenue Per Customer
                "burn_rate": await self.calculate_burn_rate(),
                "runway_months": await self.calculate_runway(),
                "cash_balance": await self.get_cash_balance()
            }

            # Vertical breakdown
            vertical_performance = await self.analyze_vertical_performance()
            metrics["vertical_breakdown"] = vertical_performance

            # Save context
            self.save_context(
                f"financial_update_{datetime.now().strftime('%Y%m%d')}",
                metrics
            )

            # Log metrics
            self.log_metric("weekly_arr", current_arr)
            self.log_metric("weekly_customers", customers)

            self.logger.info(f"✅ Financial update complete - ARR: ${current_arr:,.0f}")

            return {
                "success": True,
                "metrics": metrics,
                "alerts": await self.generate_financial_alerts(metrics),
                "recommendations": await self.generate_recommendations(metrics)
            }

        except Exception as e:
            self.logger.error(f"❌ Financial update failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def calculate_current_arr(self) -> float:
        """Calculate current Annual Recurring Revenue"""
        # In production, query from billing system/CRM
        # For now, simulate based on phase

        # Check cached value
        cached = self.load_context("current_arr")
        if cached:
            return cached.get("arr", 0)

        # Simulate startup phase - starting from $0, ramping up
        # Assume we're in Month 3 of operations
        month = 3
        ramp_factor = month / 12  # 25% through Year 1

        # Conservative ramp: 10% of Year 1 target by Month 3
        current_arr = self.year_1_arr_target * 0.10

        return current_arr

    async def get_customer_count(self) -> int:
        """Get current customer count"""
        # In production, query from CRM
        # Simulate based on ARR
        arr = await self.calculate_current_arr()

        # Assume average ACV of $500K (from GTM plan)
        avg_acv = 500_000
        customers = int(arr / avg_acv) if avg_acv > 0 else 0

        return max(3, customers)  # Minimum 3 customers (Arby's, BWW, Sonic)

    async def calculate_burn_rate(self) -> float:
        """Calculate monthly burn rate"""
        # In production, pull from accounting system
        # Simulate based on team size and infrastructure costs

        # Assume Year 1 investment: $35M over 12 months = ~$2.9M/month
        monthly_burn = 2_900_000

        return monthly_burn

    async def calculate_runway(self) -> float:
        """Calculate runway in months"""
        cash_balance = await self.get_cash_balance()
        burn_rate = await self.calculate_burn_rate()

        if burn_rate > 0:
            runway = cash_balance / burn_rate
        else:
            runway = float('inf')

        return runway

    async def get_cash_balance(self) -> float:
        """Get current cash balance"""
        # In production, pull from bank accounts
        # Simulate Series A funding: $45M raised, 3 months burn

        series_a = 45_000_000
        months_elapsed = 3
        burn_rate = await self.calculate_burn_rate()

        cash_balance = series_a - (burn_rate * months_elapsed)

        return max(0, cash_balance)

    async def calculate_variance(self, current_arr: float) -> Dict[str, float]:
        """Calculate variance from GTM plan"""
        # Determine which quarter we're in
        month = 3  # Assume Month 3
        expected_arr_by_month = {
            1: self.year_1_arr_target * 0.05,
            2: self.year_1_arr_target * 0.08,
            3: self.year_1_arr_target * 0.12,
            6: self.year_1_arr_target * 0.30,
            9: self.year_1_arr_target * 0.55,
            12: self.year_1_arr_target
        }

        expected_arr = expected_arr_by_month.get(month, self.year_1_arr_target * (month / 12))

        return {
            "expected_arr": expected_arr,
            "actual_arr": current_arr,
            "variance_dollars": current_arr - expected_arr,
            "variance_percent": ((current_arr / expected_arr) - 1) * 100 if expected_arr > 0 else 0
        }

    async def analyze_vertical_performance(self) -> Dict[str, Any]:
        """Analyze performance by vertical"""
        # In production, query from CRM with vertical tagging
        # Simulate based on master projections

        verticals = {}
        for vertical, targets in self.master_plan.get("verticals", {}).items():
            # Simulate current performance (Month 3)
            current = targets["y1"] * 0.10  # 10% of Year 1 target

            verticals[vertical] = {
                "current_arr": current,
                "target_y1": targets["y1"],
                "target_y2": targets["y2"],
                "target_y3": targets["y3"],
                "progress_percent": (current / targets["y1"]) * 100 if targets["y1"] > 0 else 0
            }

        return verticals

    async def generate_financial_alerts(self, metrics: Dict) -> List[str]:
        """Generate financial alerts and warnings"""
        alerts = []

        # Runway alert
        if metrics["runway_months"] < 6:
            alerts.append(f"🚨 CRITICAL: Only {metrics['runway_months']:.1f} months runway remaining")

        # Variance alert
        if metrics["variance_percent"] < -20:
            alerts.append(f"⚠️  WARNING: {metrics['variance_percent']:.1f}% below target")

        # Burn rate alert
        if metrics["burn_rate"] > 3_500_000:
            alerts.append(f"⚠️  High burn rate: ${metrics['burn_rate']:,.0f}/month")

        return alerts

    async def generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []

        if metrics["variance_percent"] < -10:
            recommendations.append("📈 Accelerate sales hiring to close gap to target")
            recommendations.append("🎯 Focus on high-ARR verticals (Healthcare, Retail)")

        if metrics["runway_months"] < 12:
            recommendations.append("💰 Begin Series B fundraising process")

        if metrics.get("arpc", 0) < 400_000:
            recommendations.append("💎 Focus on enterprise customers to increase ARPC")

        return recommendations

    async def run(self) -> Dict[str, Any]:
        """Main execution - called by orchestrator"""
        return await self.weekly_financial_update()

async def main():
    """Test financial planning agent"""
    agent = FinancialPlanningAgent()
    results = await agent.run()
    print(agent.generate_report(results))

if __name__ == "__main__":
    asyncio.run(main())
