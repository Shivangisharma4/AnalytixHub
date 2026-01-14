#!/usr/bin/env python3
"""
Main script to scrape todo service features and generate rankings.

Usage:
    python main.py scrape              # Scrape all services
    python main.py scrape-single NAME  # Scrape a single service
    python main.py rank                # Generate rankings
    python main.py compare             # Show feature comparison
    python main.py summary SERVICE     # Show service summary
    python main.py recommend           # Interactive recommendation
    python main.py export              # Export data to JSON
    python main.py all                 # Scrape + rank + export
"""
import sys
import argparse
from database import DatabaseManager
from ranking_system import RankingSystem
from scrapers import SCRAPERS


def scrape_all_services(db: DatabaseManager):
    """Scrape features from all registered services"""
    print("\n" + "="*60)
    print("SCRAPING ALL TODO SERVICES")
    print("="*60 + "\n")

    results = []
    for name, scraper_factory in SCRAPERS.items():
        print(f"Scraping {name}...")
        try:
            scraper = scraper_factory()
            features = scraper.scrape()
            service_id = db.save_service_features(features)
            results.append((name, True, service_id))
            print(f"  ✓ Success - saved features to database")
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"  ✗ Error: {e}")
        print()

    # Summary
    success_count = sum(1 for r in results if r[1])
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE: {success_count}/{len(results)} successful")
    print(f"{'='*60}\n")

    return results


def scrape_single_service(db: DatabaseManager, service_name: str):
    """Scrape a single service by name"""
    print(f"\nScraping {service_name}...")

    if service_name not in SCRAPERS:
        print(f"Error: Service '{service_name}' not found.")
        print(f"Available services: {', '.join(SCRAPERS.keys())}")
        return False

    try:
        scraper = SCRAPERS[service_name]()
        features = scraper.scrape()
        db.save_service_features(features)
        print(f"✓ Successfully scraped and saved {service_name}")
        return True
    except Exception as e:
        print(f"✗ Error scraping {service_name}: {e}")
        return False


def generate_rankings(db: DatabaseManager):
    """Generate rankings for all contexts"""
    ranking_system = RankingSystem(db)
    ranking_system.generate_all_rankings()

    # Display rankings for each context
    contexts = ['personal_use', 'team_collaboration', 'enterprise', 'minimalist']
    for context in contexts:
        ranking_system.display_rankings(context, top_n=5)


def show_comparison(db: DatabaseManager):
    """Show feature comparison matrix"""
    ranking_system = RankingSystem(db)
    ranking_system.display_feature_comparison()


def show_service_summary(db: DatabaseManager, service_name: str):
    """Show detailed summary of a service"""
    ranking_system = RankingSystem(db)
    ranking_system.display_service_summary(service_name)


def interactive_recommendation(db: DatabaseManager):
    """Interactive service recommendation"""
    ranking_system = RankingSystem(db)

    print("\n" + "="*60)
    print("SERVICE RECOMMENDATION SYSTEM")
    print("="*60 + "\n")

    # Select context
    print("Select your use case:")
    print("  1. Personal Use")
    print("  2. Team Collaboration")
    print("  3. Enterprise")
    print("  4. Minimalist/Simple")

    context_map = {
        '1': 'personal_use',
        '2': 'team_collaboration',
        '3': 'enterprise',
        '4': 'minimalist'
    }

    context_choice = input("\nEnter choice (1-4): ").strip()
    context = context_map.get(context_choice, 'personal_use')

    # Ask about key features
    print("\nMust-have features (enter y/n):")
    questions = {
        'free_tier': "  Free tier required? ",
        'collaboration': "  Team collaboration required? ",
        'offline_mode': "  Offline mode required? ",
        'api_available': "  API access required? "
    }

    requirements = {}
    for feature, question in questions.items():
        answer = input(question).strip().lower()
        requirements[feature] = answer in ['y', 'yes']

    # Get recommendations
    recommendations = ranking_system.recommend_service(requirements, context)

    print("\n" + "="*60)
    print(f"RECOMMENDED SERVICES FOR: {context.replace('_', ' ').upper()}")
    print("="*60 + "\n")

    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. {rec['name']} (Score: {rec['score']:.1f})")
    else:
        print("No services match your exact requirements. Try relaxing some constraints.")


def export_data(db: DatabaseManager):
    """Export database to JSON"""
    ranking_system = RankingSystem(db)

    print("\nExporting data...")

    # Export full database
    db.export_to_json("todo_services_data.json")

    # Export rankings report
    ranking_system.export_rankings_report("rankings_report.json")

    print("\n✓ Export complete!")


def run_full_pipeline(db: DatabaseManager):
    """Run complete pipeline: scrape -> rank -> export"""
    print("\n" + "="*60)
    print("RUNNING FULL PIPELINE")
    print("="*60)

    # Scrape
    scrape_all_services(db)

    # Rank
    print("\nGenerating rankings...")
    generate_rankings(db)

    # Export
    print("\nExporting data...")
    export_data(db)

    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)


def list_services():
    """List all available services to scrape"""
    print("\nAvailable services:")
    for name in SCRAPERS.keys():
        print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Todo Service Feature Scraper and Ranking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scrape              # Scrape all services
  python main.py scrape-single Todoist # Scrape single service
  python main.py rank                # Generate and display rankings
  python main.py compare             # Show feature comparison matrix
  python main.py summary Todoist     # Show detailed service summary
  python main.py recommend           # Interactive recommendation
  python main.py export              # Export all data to JSON
  python main.py all                 # Run full pipeline
  python main.py list                # List available services
        """
    )

    parser.add_argument('command', nargs='?',
                       choices=['scrape', 'scrape-single', 'rank', 'compare',
                               'summary', 'recommend', 'export', 'all', 'list'],
                       help='Command to run')

    parser.add_argument('--service', help='Service name (for scrape-single or summary)')

    args = parser.parse_args()

    # Initialize database
    db = DatabaseManager()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'scrape':
        scrape_all_services(db)

    elif args.command == 'scrape-single':
        if not args.service:
            print("Error: --service argument required for scrape-single")
            return
        scrape_single_service(db, args.service)

    elif args.command == 'rank':
        generate_rankings(db)

    elif args.command == 'compare':
        show_comparison(db)

    elif args.command == 'summary':
        if not args.service:
            print("Error: --service argument required for summary")
            return
        show_service_summary(db, args.service)

    elif args.command == 'recommend':
        interactive_recommendation(db)

    elif args.command == 'export':
        export_data(db)

    elif args.command == 'all':
        run_full_pipeline(db)

    elif args.command == 'list':
        list_services()


if __name__ == "__main__":
    main()
