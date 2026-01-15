#!/usr/bin/env python3
"""
Migration script to copy data from local SQLite to Railway PostgreSQL.
Run this locally with DATABASE_URL pointing to Railway PostgreSQL.
"""
import os
import sqlite3
import json
from datetime import datetime

# Conditional PostgreSQL import
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 is required. Install with: pip install psycopg2-binary")
    exit(1)

def migrate_data(sqlite_path: str, postgres_url: str):
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(postgres_url)
    pg_cursor = pg_conn.cursor()
    
    print(f"Connected to SQLite: {sqlite_path}")
    print(f"Connected to PostgreSQL")
    
    try:
        # Migrate services
        print("\n--- Migrating services ---")
        sqlite_cursor.execute("SELECT * FROM services")
        services = sqlite_cursor.fetchall()
        
        service_id_map = {}  # old_id -> new_id
        
        for service in services:
            # Check if service already exists
            pg_cursor.execute("SELECT id FROM services WHERE name = %s", (service['name'],))
            existing = pg_cursor.fetchone()
            
            if existing:
                print(f"  Service '{service['name']}' already exists, skipping...")
                service_id_map[service['id']] = existing[0]
                continue
            
            pg_cursor.execute("""
                INSERT INTO services (name, url, pricing, platforms, scraped_at, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                service['name'],
                service['url'],
                service['pricing'],
                service['platforms'],
                service['scraped_at'],
                service['last_updated']
            ))
            new_id = pg_cursor.fetchone()[0]
            service_id_map[service['id']] = new_id
            print(f"  Migrated service: {service['name']} (old_id={service['id']} -> new_id={new_id})")
        
        # Migrate features
        print("\n--- Migrating features ---")
        sqlite_cursor.execute("SELECT * FROM features")
        features = sqlite_cursor.fetchall()
        
        for feature in features:
            old_service_id = feature['service_id']
            new_service_id = service_id_map.get(old_service_id)
            
            if not new_service_id:
                print(f"  Warning: No mapping for service_id {old_service_id}, skipping feature")
                continue
            
            # Check if feature already exists
            pg_cursor.execute(
                "SELECT id FROM features WHERE service_id = %s AND feature_name = %s",
                (new_service_id, feature['feature_name'])
            )
            if pg_cursor.fetchone():
                continue
            
            pg_cursor.execute("""
                INSERT INTO features (service_id, feature_name, is_available)
                VALUES (%s, %s, %s)
                ON CONFLICT (service_id, feature_name) DO UPDATE SET is_available = EXCLUDED.is_available
            """, (new_service_id, feature['feature_name'], bool(feature['is_available'])))
        
        print(f"  Migrated {len(features)} features")
        
        # Migrate additional_features
        print("\n--- Migrating additional features ---")
        sqlite_cursor.execute("SELECT * FROM additional_features")
        additional = sqlite_cursor.fetchall()
        
        for af in additional:
            old_service_id = af['service_id']
            new_service_id = service_id_map.get(old_service_id)
            
            if not new_service_id:
                continue
            
            pg_cursor.execute("""
                INSERT INTO additional_features (service_id, feature_name)
                VALUES (%s, %s)
            """, (new_service_id, af['feature_name']))
        
        print(f"  Migrated {len(additional)} additional features")
        
        # Migrate feature_weights
        print("\n--- Migrating feature weights ---")
        sqlite_cursor.execute("SELECT * FROM feature_weights")
        weights = sqlite_cursor.fetchall()
        
        for weight in weights:
            pg_cursor.execute("""
                INSERT INTO feature_weights (context, feature_name, weight, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (context, feature_name) DO UPDATE SET weight = EXCLUDED.weight
            """, (weight['context'], weight['feature_name'], weight['weight'], weight['created_at']))
        
        print(f"  Migrated {len(weights)} feature weights")
        
        # Migrate rankings
        print("\n--- Migrating rankings ---")
        sqlite_cursor.execute("SELECT * FROM rankings")
        rankings = sqlite_cursor.fetchall()
        
        for ranking in rankings:
            old_service_id = ranking['service_id']
            new_service_id = service_id_map.get(old_service_id)
            
            if not new_service_id:
                continue
            
            pg_cursor.execute("""
                INSERT INTO rankings (context, service_id, rank, score, calculated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (context, service_id) DO UPDATE SET rank = EXCLUDED.rank, score = EXCLUDED.score
            """, (ranking['context'], new_service_id, ranking['rank'], ranking['score'], ranking['calculated_at']))
        
        print(f"  Migrated {len(rankings)} rankings")
        
        # Commit all changes
        pg_conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify
        pg_cursor.execute("SELECT COUNT(*) FROM services")
        count = pg_cursor.fetchone()[0]
        print(f"   PostgreSQL now has {count} services")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    import sys
    
    sqlite_path = "todo_services.db"
    postgres_url = os.environ.get("DATABASE_URL")
    
    if not postgres_url:
        print("Error: DATABASE_URL environment variable not set")
        print("Usage: DATABASE_URL='postgresql://...' python migrate_to_postgres.py")
        sys.exit(1)
    
    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite database not found at {sqlite_path}")
        sys.exit(1)
    
    migrate_data(sqlite_path, postgres_url)
