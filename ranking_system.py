"""
Ranking and comparison system for todo services.
Analyzes features and provides rankings based on different use cases.
"""
from typing import List, Dict, Optional
from database import DatabaseManager, DEFAULT_WEIGHTS
import json


class RankingSystem:
    """Analyzes and ranks todo services based on different contexts"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def generate_all_rankings(self):
        """Generate rankings for all predefined contexts"""
        print("Generating rankings for all contexts...")

        for context, weights in DEFAULT_WEIGHTS.items():
            print(f"  Calculating rankings for: {context}")
            rankings = self.db.calculate_rankings(context, weights)
            print(f"    Top service: {rankings[0]['service_name']} (score: {rankings[0]['score']:.1f})")

        print("\n✓ All rankings generated successfully!")

    def display_rankings(self, context: str, top_n: int = 10):
        """Display rankings for a specific context"""
        rankings = self.db.get_rankings(context)

        if not rankings:
            print(f"No rankings found for context: {context}")
            return

        print(f"\n{'='*60}")
        print(f"TOP {top_n} TODO SERVICES FOR: {context.upper().replace('_', ' ')}")
        print(f"{'='*60}\n")

        for i, item in enumerate(rankings[:top_n], 1):
            print(f"{i:2d}. {item['service_name']:20s} - Score: {item['score']:.1f}")

    def display_feature_comparison(self, services: Optional[List[str]] = None):
        """Display a feature comparison matrix"""
        comparison = self.db.get_feature_comparison()

        if services:
            comparison = {k: v for k, v in comparison.items() if k in services}

        if not comparison:
            print("\nNo services to compare.")
            return

        # Define feature order for display
        feature_order = [
            'free_tier', 'collaboration', 'reminders', 'due_dates',
            'tags_labels', 'subtasks', 'attachments', 'offline_mode',
            'calendar_view', 'integrations', 'api_available'
        ]

        feature_labels = {
            'free_tier': 'Free Tier',
            'collaboration': 'Collaboration',
            'reminders': 'Reminders',
            'due_dates': 'Due Dates',
            'tags_labels': 'Tags/Labels',
            'subtasks': 'Subtasks',
            'attachments': 'Attachments',
            'offline_mode': 'Offline Mode',
            'calendar_view': 'Calendar View',
            'integrations': 'Integrations',
            'api_available': 'API'
        }

        print(f"\n{'='*80}")
        print("FEATURE COMPARISON MATRIX")
        print(f"{'='*80}\n")

        # Print header
        header = f"{'Feature':<20}"
        for service in comparison.keys():
            header += f"{service[:15]:>17}"
        print(header)
        print("-" * 80)

        # Print each feature
        for feature in feature_order:
            if feature in feature_labels:
                row = f"{feature_labels[feature]:<20}"
                for service_name, features in comparison.items():
                    has_feature = features.get(feature, False)
                    symbol = "✓" if has_feature else "✗"
                    row += f"{symbol:>17}"
                print(row)

    def get_service_summary(self, service_name: str) -> Optional[Dict]:
        """Get a detailed summary of a service"""
        service = self.db.get_service_by_name(service_name)
        if not service:
            print(f"\nService '{service_name}' not found.")
            return None

        features = self.db.get_features_for_service(service['id'])
        additional_features = self.db.get_additional_features(service['id'])
        rankings = self.db.get_service_rankings(service['id'])

        summary = {
            'service': service,
            'features': features,
            'additional_features': additional_features,
            'rankings': rankings
        }

        return summary

    def display_service_summary(self, service_name: str):
        """Display a detailed summary of a service"""
        summary = self.get_service_summary(service_name)
        if not summary:
            return

        service = summary['service']
        features = summary['features']
        additional = summary['additional_features']
        rankings = summary['rankings']

        print(f"\n{'='*60}")
        print(f"SERVICE SUMMARY: {service['name'].upper()}")
        print(f"{'='*60}\n")

        print(f"URL: {service['url']}")
        print(f"Pricing: {service['pricing']}")
        print(f"Platforms: {service['platforms']}")

        print(f"\nCore Features:")
        feature_labels = {
            'free_tier': 'Free Tier',
            'collaboration': 'Collaboration',
            'reminders': 'Reminders',
            'due_dates': 'Due Dates',
            'tags_labels': 'Tags/Labels',
            'subtasks': 'Subtasks',
            'attachments': 'Attachments',
            'offline_mode': 'Offline Mode',
            'calendar_view': 'Calendar View',
            'integrations': 'Integrations',
            'api_available': 'API'
        }

        for feature, label in feature_labels.items():
            status = "✓" if features.get(feature, False) else "✗"
            print(f"  {status} {label}")

        if additional:
            print(f"\nAdditional Features:")
            for feat in additional[:10]:  # Show first 10
                print(f"  • {feat}")
            if len(additional) > 10:
                print(f"  ... and {len(additional) - 10} more")

        if rankings:
            print(f"\nRankings by Context:")
            for context, data in sorted(rankings.items(), key=lambda x: x[1]['rank']):
                print(f"  #{data['rank']} - {context.replace('_', ' ')} (score: {data['score']:.1f})")

    def recommend_service(self, requirements: Dict[str, bool], context: str = 'personal_use') -> List[Dict]:
        """Recommend services based on specific requirements"""
        comparison = self.db.get_feature_comparison()

        scored_services = []

        for service_name, features in comparison.items():
            # Check if service meets all requirements
            meets_requirements = all(
                features.get(feature, False) == required
                for feature, required in requirements.items()
            )

            if meets_requirements:
                # Get score for context
                rankings = self.db.get_rankings(context)
                for ranking in rankings:
                    if ranking['service_name'] == service_name:
                        scored_services.append({
                            'name': service_name,
                            'score': ranking['score'],
                            'rank': ranking['rank']
                        })
                        break

        # Sort by score
        scored_services.sort(key=lambda x: x['score'], reverse=True)

        return scored_services

    def export_rankings_report(self, output_file: str = "rankings_report.json"):
        """Export a comprehensive rankings report"""
        report = {
            'generated_at': str(datetime.now()),
            'contexts': {}
        }

        # Get rankings for all contexts
        for context in DEFAULT_WEIGHTS.keys():
            rankings = self.db.get_rankings(context)
            report['contexts'][context] = rankings

        # Add feature comparison
        report['feature_comparison'] = self.db.get_feature_comparison()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n✓ Rankings report exported to: {output_file}")


from datetime import datetime
