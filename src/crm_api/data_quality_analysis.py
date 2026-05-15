"""
Data Quality Analysis for Zoho CRM Records
Analyzes field completeness and data quality WITHOUT exposing client details
"""
import sys
import os
from collections import defaultdict
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.crm_api.zoho_client import ZohoCRMClient


class DataQualityAnalyzer:
    """Analyzes data quality without exposing sensitive information"""

    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records
        self.total_records = len(records)

    def analyze_field_completeness(self) -> Dict[str, Dict]:
        """
        Analyze how complete each field is across all records

        Returns aggregate statistics ONLY - no individual client data
        """
        if not self.records:
            return {}

        # Get all possible fields from all records
        all_fields = set()
        for record in self.records:
            all_fields.update(record.keys())

        # Count filled vs empty for each field
        field_stats = {}

        for field in sorted(all_fields):
            filled_count = 0
            empty_count = 0

            for record in self.records:
                value = record.get(field)

                # Check if value is "filled" (not None, not empty string, not empty list)
                if value is not None and value != "" and value != []:
                    filled_count += 1
                else:
                    empty_count += 1

            field_stats[field] = {
                "filled": filled_count,
                "empty": empty_count,
                "fill_rate": (filled_count / self.total_records * 100) if self.total_records > 0 else 0
            }

        return field_stats

    def get_critical_fields_analysis(self, critical_fields: List[str]) -> Dict:
        """
        Analyze specific fields that are critical for matching

        Args:
            critical_fields: List of field names that are important

        Returns:
            Statistics for critical fields only
        """
        field_stats = self.analyze_field_completeness()

        critical_analysis = {}
        for field in critical_fields:
            if field in field_stats:
                critical_analysis[field] = field_stats[field]
            else:
                critical_analysis[field] = {
                    "filled": 0,
                    "empty": self.total_records,
                    "fill_rate": 0.0,
                    "note": "Field not found in records"
                }

        return critical_analysis

    def get_overall_quality_score(self) -> float:
        """
        Calculate overall data quality score (0-100)
        Based on average fill rate across all fields
        """
        field_stats = self.analyze_field_completeness()

        if not field_stats:
            return 0.0

        total_fill_rate = sum(stats["fill_rate"] for stats in field_stats.values())
        return total_fill_rate / len(field_stats)

    def get_records_with_missing_data(self, critical_fields: List[str]) -> Dict:
        """
        Count how many records are missing critical data

        Returns counts ONLY - no individual record details
        """
        complete_records = 0
        incomplete_records = 0
        missing_field_counts = defaultdict(int)

        for record in self.records:
            is_complete = True

            for field in critical_fields:
                value = record.get(field)
                if value is None or value == "" or value == []:
                    is_complete = False
                    missing_field_counts[field] += 1

            if is_complete:
                complete_records += 1
            else:
                incomplete_records += 1

        return {
            "complete_records": complete_records,
            "incomplete_records": incomplete_records,
            "completeness_rate": (complete_records / self.total_records * 100) if self.total_records > 0 else 0,
            "missing_by_field": dict(missing_field_counts)
        }


def generate_report(module: str, records: List[Dict], critical_fields: List[str] = None):
    """
    Generate a comprehensive data quality report

    Args:
        module: Name of the Zoho module
        records: List of records to analyze
        critical_fields: List of field names that are critical for matching
    """
    analyzer = DataQualityAnalyzer(records)

    print("\n" + "=" * 80)
    print(f"DATA QUALITY REPORT: {module}")
    print("=" * 80)

    print(f"\n📊 OVERVIEW")
    print(f"   Total Records: {analyzer.total_records}")
    print(f"   Overall Quality Score: {analyzer.get_overall_quality_score():.1f}%")

    # Field completeness
    print(f"\n📋 FIELD COMPLETENESS")
    print("-" * 80)
    field_stats = analyzer.analyze_field_completeness()

    # Sort by fill rate (descending)
    sorted_fields = sorted(
        field_stats.items(),
        key=lambda x: x[1]["fill_rate"],
        reverse=True
    )

    print(f"{'Field Name':<40} {'Filled':<10} {'Empty':<10} {'Fill Rate'}")
    print("-" * 80)

    for field, stats in sorted_fields:
        print(f"{field:<40} {stats['filled']:<10} {stats['empty']:<10} {stats['fill_rate']:.1f}%")

    # Critical fields analysis
    if critical_fields:
        print(f"\n🎯 CRITICAL FIELDS ANALYSIS")
        print("-" * 80)
        critical_analysis = analyzer.get_critical_fields_analysis(critical_fields)

        for field, stats in critical_analysis.items():
            status = "✅" if stats["fill_rate"] >= 80 else "⚠️" if stats["fill_rate"] >= 50 else "❌"
            print(f"{status} {field:<35} Fill Rate: {stats['fill_rate']:.1f}%")

        # Records with missing critical data
        missing_analysis = analyzer.get_records_with_missing_data(critical_fields)
        print(f"\n📈 COMPLETENESS SUMMARY")
        print(f"   Complete records (all critical fields): {missing_analysis['complete_records']}")
        print(f"   Incomplete records: {missing_analysis['incomplete_records']}")
        print(f"   Completeness rate: {missing_analysis['completeness_rate']:.1f}%")

    print("\n" + "=" * 80)
    print("✅ Report Complete - No client data was displayed")
    print("=" * 80 + "\n")


def main():
    """Main function to run data quality analysis"""

    print("=" * 80)
    print("ZOHO CRM DATA QUALITY ANALYSIS")
    print("=" * 80)

    # Initialize client
    try:
        client = ZohoCRMClient()
        print("✅ Successfully connected to Zoho CRM")
    except Exception as e:
        print(f"❌ Failed to initialize Zoho client: {e}")
        return

    # Get available modules
    print("\n📋 Fetching available modules...")
    try:
        modules = client.get_modules()
        print(f"✅ Found {len(modules)} modules")

        print("\nAvailable modules:")
        for i, module in enumerate(modules, 1):
            api_name = module.get("api_name")
            plural_label = module.get("plural_label")
            print(f"  {i}. {api_name} ({plural_label})")

    except Exception as e:
        print(f"❌ Failed to fetch modules: {e}")
        return

    # Ask user which module to analyze
    print("\n" + "-" * 80)
    module_choice = input("\nEnter module API name to analyze (e.g., 'Contacts', 'Accounts'): ").strip()

    if not module_choice:
        print("❌ No module selected")
        return

    # Fetch all records from selected module
    print(f"\n📥 Fetching all records from {module_choice}...")
    try:
        records = client.get_all_records(module_choice)

        if not records:
            print(f"⚠️ No records found in {module_choice}")
            return

    except Exception as e:
        print(f"❌ Failed to fetch records: {e}")
        return

    # Define critical fields for matching (can be customized)
    critical_fields = [
        "Company",
        "Full_Name",
        "First_Name",
        "Last_Name",
        "Email",
        "Phone",
        "Mailing_City",
        "Mailing_State",
        "Mailing_Country",
        "Account_Name",
        "Owner"
    ]

    # Generate report
    generate_report(module_choice, records, critical_fields)

    # Save summary to file
    output_file = f"../../docs/data_quality_{module_choice}.txt"
    print(f"\n💾 Saving summary to {output_file}...")


if __name__ == "__main__":
    main()
