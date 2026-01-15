#!/usr/bin/env python3
"""
Seed script to add categories and migrate existing services.
Run with DATABASE_URL set to Railway PostgreSQL.
"""
import os
from database import DatabaseManager

# Todo Apps category with its feature schema and ranking contexts
TODO_CATEGORY = {
    "name": "Todo Apps",
    "slug": "todo",
    "description": "Task management and to-do list applications for personal and team productivity.",
    "feature_schema": {
        "free_tier": {"label": "Free Tier", "type": "boolean"},
        "collaboration": {"label": "Collaboration", "type": "boolean"},
        "reminders": {"label": "Reminders", "type": "boolean"},
        "due_dates": {"label": "Due Dates", "type": "boolean"},
        "tags_labels": {"label": "Tags/Labels", "type": "boolean"},
        "subtasks": {"label": "Subtasks", "type": "boolean"},
        "attachments": {"label": "Attachments", "type": "boolean"},
        "offline_mode": {"label": "Offline Mode", "type": "boolean"},
        "calendar_view": {"label": "Calendar View", "type": "boolean"},
        "integrations": {"label": "Integrations", "type": "boolean"},
        "api_available": {"label": "API", "type": "boolean"},
    },
    "ranking_contexts": {
        "personal_use": {"label": "Personal Use", "description": "Best for individual productivity"},
        "team_collaboration": {"label": "Team Collaboration", "description": "Best for team projects"},
        "enterprise": {"label": "Enterprise", "description": "Best for large organizations"},
        "minimalist": {"label": "Minimalist", "description": "Simple and focused"},
    }
}

# Additional sample categories
NOTE_TAKING_CATEGORY = {
    "name": "Note-taking Apps",
    "slug": "notes",
    "description": "Applications for taking notes, organizing thoughts, and knowledge management.",
    "feature_schema": {
        "free_tier": {"label": "Free Tier", "type": "boolean"},
        "markdown_support": {"label": "Markdown Support", "type": "boolean"},
        "sync": {"label": "Cloud Sync", "type": "boolean"},
        "offline_mode": {"label": "Offline Mode", "type": "boolean"},
        "tags": {"label": "Tags/Organization", "type": "boolean"},
        "search": {"label": "Full-text Search", "type": "boolean"},
        "collaboration": {"label": "Collaboration", "type": "boolean"},
        "export": {"label": "Export Options", "type": "boolean"},
        "plugins": {"label": "Plugins/Extensions", "type": "boolean"},
        "api_available": {"label": "API", "type": "boolean"},
    },
    "ranking_contexts": {
        "personal_use": {"label": "Personal Use", "description": "Best for personal notes"},
        "knowledge_base": {"label": "Knowledge Base", "description": "Best for building a knowledge base"},
        "team_wiki": {"label": "Team Wiki", "description": "Best for team documentation"},
    }
}

PASSWORD_MANAGER_CATEGORY = {
    "name": "Password Managers",
    "slug": "passwords",
    "description": "Secure password storage and management applications.",
    "feature_schema": {
        "free_tier": {"label": "Free Tier", "type": "boolean"},
        "encryption": {"label": "End-to-end Encryption", "type": "boolean"},
        "two_factor": {"label": "2FA Support", "type": "boolean"},
        "browser_extension": {"label": "Browser Extension", "type": "boolean"},
        "mobile_app": {"label": "Mobile App", "type": "boolean"},
        "password_generator": {"label": "Password Generator", "type": "boolean"},
        "secure_sharing": {"label": "Secure Sharing", "type": "boolean"},
        "breach_monitoring": {"label": "Breach Monitoring", "type": "boolean"},
        "family_plan": {"label": "Family Plan", "type": "boolean"},
    },
    "ranking_contexts": {
        "personal_use": {"label": "Personal Use", "description": "Best for individuals"},
        "family": {"label": "Family", "description": "Best for families"},
        "business": {"label": "Business", "description": "Best for businesses"},
    }
}


def seed_categories(db: DatabaseManager):
    """Seed the database with initial categories"""
    print("\n=== Seeding Categories ===\n")
    
    categories = [TODO_CATEGORY, NOTE_TAKING_CATEGORY, PASSWORD_MANAGER_CATEGORY]
    
    for cat in categories:
        category_id = db.add_category(
            name=cat["name"],
            slug=cat["slug"],
            description=cat["description"],
            feature_schema=cat["feature_schema"],
            ranking_contexts=cat["ranking_contexts"]
        )
        print(f"✅ Added category: {cat['name']} (id={category_id})")
    
    return db.get_categories()


def assign_existing_services_to_todo(db: DatabaseManager):
    """Assign all existing services to the Todo Apps category"""
    print("\n=== Assigning Services to Todo Apps Category ===\n")
    
    # Get the Todo category
    todo_cat = db.get_category_by_slug("todo")
    if not todo_cat:
        print("❌ Todo category not found!")
        return
    
    # Get all services without a category
    services = db.get_all_services()
    assigned_count = 0
    
    for service in services:
        if not service.get('category_id'):
            db.assign_service_to_category(service['id'], todo_cat['id'])
            print(f"  Assigned '{service['name']}' to Todo Apps")
            assigned_count += 1
    
    print(f"\n✅ Assigned {assigned_count} services to Todo Apps category")


def main():
    db = DatabaseManager()
    
    print(f"Connected to {'PostgreSQL' if db.is_postgres else 'SQLite'}")
    
    # Seed categories
    categories = seed_categories(db)
    print(f"\nTotal categories: {len(categories)}")
    
    # Assign existing services to Todo category
    assign_existing_services_to_todo(db)
    
    # Verify
    print("\n=== Verification ===")
    for cat in db.get_categories():
        services = db.get_all_services(category_slug=cat['slug'])
        print(f"  {cat['name']}: {len(services)} services")
    
    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    main()
