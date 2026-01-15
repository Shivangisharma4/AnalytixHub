"""
Database models and operations for storing and analyzing todo service features.
Supports both SQLite (local development) and PostgreSQL (production).
"""
import os
import json
import sqlite3
from typing import List, Dict, Optional, Union, Any
from contextlib import contextmanager
from datetime import datetime
from dotenv import load_dotenv
from base_scraper import ServiceFeatures

# Conditional PostgreSQL import
try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    psycopg2 = None

# Load environment variables
load_dotenv()


class DatabaseManager:
    """Manages database for todo service features with support for SQLite and PostgreSQL"""

    def __init__(self, db_path: str = None):
        self.database_url = os.environ.get('DATABASE_URL')
        self.db_path = db_path or os.environ.get('DB_PATH', "todo_services.db")
        self.is_postgres = self.database_url is not None and POSTGRES_AVAILABLE
        self.pg_pool = None
        
        if self.is_postgres:
            print("Using PostgreSQL database")
            self.placeholder = "%s"
            self.init_pg_pool()
        else:
            if self.database_url and not POSTGRES_AVAILABLE:
                print("Warning: DATABASE_URL set but psycopg2 not available. Using SQLite.")
            print(f"Using SQLite database at {self.db_path}")
            self.placeholder = "?"
            
        self.init_database()

    def init_pg_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pg_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, dsn=self.database_url
            )
        except Exception as e:
            print(f"Error initializing PostgreSQL pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self.is_postgres:
            conn = self.pg_pool.getconn()
            conn.autocommit = False
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                self.pg_pool.putconn(conn)
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute a query and return a cursor"""
        # Adapt placeholders if needed (already handled by self.placeholder)
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            cursor.execute(query, params or ())
            return cursor

    def init_database(self):
        """Initialize database schema"""
        # ID column definition differs
        id_col = "SERIAL PRIMARY KEY" if self.is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        json_type = "JSONB" if self.is_postgres else "TEXT"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Categories table (must be created before services for foreign key)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS categories (
                    id {id_col},
                    name TEXT UNIQUE NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    description TEXT,
                    feature_schema {json_type},
                    ranking_contexts {json_type},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Services table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS services (
                    id {id_col},
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    pricing TEXT,
                    platforms TEXT,
                    category_id INTEGER REFERENCES categories(id),
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Features table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS features (
                    id {id_col},
                    service_id INTEGER NOT NULL,
                    feature_name TEXT NOT NULL,
                    is_available BOOLEAN NOT NULL,
                    FOREIGN KEY (service_id) REFERENCES services(id),
                    UNIQUE(service_id, feature_name)
                )
            """)

            # Additional features table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS additional_features (
                    id {id_col},
                    service_id INTEGER NOT NULL,
                    feature_name TEXT NOT NULL,
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            """)

            # Feature weights table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS feature_weights (
                    id {id_col},
                    context TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(context, feature_name)
                )
            """)

            # Rankings table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS rankings (
                    id {id_col},
                    context TEXT NOT NULL,
                    service_id INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    score REAL NOT NULL,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (service_id) REFERENCES services(id),
                    UNIQUE(context, service_id)
                )
            """)

            # Create indexes (PostgreSQL already has IF NOT EXISTS support)
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_name ON services(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_category ON services(category_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_service ON features(service_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_context ON rankings(context)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug)")
            except:
                # Some older PostgreSQL might not support IF NOT EXISTS for indexes
                pass

    def save_service_features(self, features: ServiceFeatures) -> int:
        """Save or update a service and its features"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()

            # Check if service exists
            cursor.execute(f"SELECT id FROM services WHERE name = {p}", (features.name,))
            row = cursor.fetchone()

            if row:
                service_id = row['id']
                cursor.execute(f"""
                    UPDATE services SET url={p}, pricing={p}, platforms={p}, last_updated={p} WHERE id={p}
                """, (features.url, features.pricing, json.dumps(features.platforms), datetime.now(), service_id))
            else:
                cursor.execute(f"""
                    INSERT INTO services (name, url, pricing, platforms, last_updated)
                    VALUES ({p}, {p}, {p}, {p}, {p})
                    RETURNING id
                """ if self.is_postgres else f"""
                    INSERT INTO services (name, url, pricing, platforms, last_updated)
                    VALUES ({p}, {p}, {p}, {p}, {p})
                """, (features.name, features.url, features.pricing,
                      json.dumps(features.platforms), datetime.now()))
                
                if self.is_postgres:
                    service_id = cursor.fetchone()['id']
                else:
                    service_id = cursor.lastrowid

            # Save features
            feature_map = {
                'free_tier': features.free_tier,
                'collaboration': features.collaboration,
                'reminders': features.reminders,
                'due_dates': features.due_dates,
                'tags_labels': features.tags_labels,
                'subtasks': features.subtasks,
                'attachments': features.attachments,
                'offline_mode': features.offline_mode,
                'calendar_view': features.calendar_view,
                'integrations': features.integrations,
                'api_available': features.api_available,
            }

            # Handle UPSERT for features
            for feature_name, is_available in feature_map.items():
                if self.is_postgres:
                    cursor.execute(f"""
                        INSERT INTO features (service_id, feature_name, is_available)
                        VALUES ({p}, {p}, {p})
                        ON CONFLICT (service_id, feature_name) 
                        DO UPDATE SET is_available = EXCLUDED.is_available
                    """, (service_id, feature_name, is_available))
                else:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO features (service_id, feature_name, is_available)
                        VALUES ({p}, {p}, {p})
                    """, (service_id, feature_name, is_available))

            # Clear and save additional features
            cursor.execute(f"DELETE FROM additional_features WHERE service_id = {p}", (service_id,))
            if features.additional_features:
                for f in features.additional_features:
                    cursor.execute(f"""
                        INSERT INTO additional_features (service_id, feature_name)
                        VALUES ({p}, {p})
                    """, (service_id, f))

            return service_id

    def get_all_services(self, category_slug: str = None) -> List[Dict]:
        """Get all services with their features as a map, optionally filtered by category"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            if category_slug:
                # Get category id first
                cursor.execute(f"SELECT id FROM categories WHERE slug = {p}", (category_slug,))
                cat_row = cursor.fetchone()
                if cat_row:
                    cat_id = cat_row['id'] if self.is_postgres else cat_row[0]
                    cursor.execute(f"SELECT * FROM services WHERE category_id = {p} ORDER BY name", (cat_id,))
                else:
                    return []
            else:
                cursor.execute("SELECT * FROM services ORDER BY name")
            
            services = [dict(row) for row in cursor.fetchall()]

            for service in services:
                service['features'] = self.get_features_for_service(service['id'])
                service['additional_features'] = self.get_additional_features(service['id'])
                # Parse platforms from JSON string
                if isinstance(service['platforms'], str):
                    try:
                        service['platforms'] = json.loads(service['platforms'])
                    except:
                        pass
            return services

    def get_service_with_features(self, name: str) -> Optional[Dict]:
        """Get a specific service with all its features and details"""
        service = self.get_service_by_name(name)
        if not service:
            return None
        
        service['features'] = self.get_features_for_service(service['id'])
        service['additional_features'] = self.get_additional_features(service['id'])
        if isinstance(service['platforms'], str):
            try:
                service['platforms'] = json.loads(service['platforms'])
            except:
                pass
        return service

    def get_service_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific service by name"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM services WHERE name = {p}", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_feature_comparison(self) -> Dict:
        """Get a feature comparison matrix for all services"""
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute("""
                SELECT s.name, f.feature_name, f.is_available
                FROM services s
                JOIN features f ON s.id = f.service_id
                ORDER BY s.name, f.feature_name
            """)

            comparison = {}
            for row in cursor.fetchall():
                name = row['name']
                if name not in comparison:
                    comparison[name] = {}
                comparison[name][row['feature_name']] = bool(row['is_available'])

            return comparison

    def set_feature_weights(self, context: str, weights: Dict[str, float]):
        """Set feature weights for a specific context"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor()
            else:
                cursor = conn.cursor()
                
            # Clear existing weights for this context
            cursor.execute(f"DELETE FROM feature_weights WHERE context = {p}", (context,))

            # Insert new weights
            for feature_name, weight in weights.items():
                if self.is_postgres:
                    cursor.execute(f"""
                        INSERT INTO feature_weights (context, feature_name, weight)
                        VALUES ({p}, {p}, {p})
                        ON CONFLICT (context, feature_name) DO UPDATE SET weight = EXCLUDED.weight
                    """, (context, feature_name, weight))
                else:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO feature_weights (context, feature_name, weight)
                        VALUES ({p}, {p}, {p})
                    """, (context, feature_name, weight))

    def get_feature_weights(self, context: str) -> Dict[str, float]:
        """Get feature weights for a context"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute(f"""
                SELECT feature_name, weight FROM feature_weights WHERE context = {p}
            """, (context,))
            return {row['feature_name']: row['weight'] for row in cursor.fetchall()}

    def calculate_rankings(self, context: str, weights: Optional[Dict[str, float]] = None) -> List[Dict]:
        """Calculate and save rankings for a specific context"""
        if weights:
            self.set_feature_weights(context, weights)
        else:
            weights = self.get_feature_weights(context)
            if not weights:
                all_features = ['free_tier', 'collaboration', 'reminders', 'due_dates',
                               'tags_labels', 'subtasks', 'attachments', 'offline_mode',
                               'calendar_view', 'integrations', 'api_available']
                weights = {f: 1.0 for f in all_features}

        # Get all services and calculate scores
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
                
            cursor.execute("""
                SELECT s.id, s.name, f.feature_name, f.is_available 
                FROM services s
                LEFT JOIN features f ON s.id = f.service_id
                ORDER BY s.name
            """)
            rows = cursor.fetchall()

        # Group features by service
        services_map = {}
        for row in rows:
            s_id = row['id']
            if s_id not in services_map:
                services_map[s_id] = {'name': row['name'], 'features': {}}
            if row['feature_name']:
                services_map[s_id]['features'][row['feature_name']] = bool(row['is_available'])

        scores = []
        for service_id, data in services_map.items():
            features = data['features']
            score = 0.0
            for feature_name, weight in weights.items():
                if features.get(feature_name, False):
                    score += weight

            scores.append({
                'service_id': service_id,
                'service_name': data['name'],
                'score': score
            })

        scores.sort(key=lambda x: x['score'], reverse=True)
        for i, item in enumerate(scores, 1):
            item['rank'] = i

        # Save rankings to database
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor()
            else:
                cursor = conn.cursor()
                
            for item in scores:
                if self.is_postgres:
                    cursor.execute(f"""
                        INSERT INTO rankings (context, service_id, rank, score, calculated_at)
                        VALUES ({p}, {p}, {p}, {p}, {p})
                        ON CONFLICT (context, service_id) DO UPDATE SET 
                            rank = EXCLUDED.rank, 
                            score = EXCLUDED.score, 
                            calculated_at = EXCLUDED.calculated_at
                    """, (context, item['service_id'], item['rank'], item['score'], datetime.now()))
                else:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO rankings (context, service_id, rank, score, calculated_at)
                        VALUES ({p}, {p}, {p}, {p}, {p})
                    """, (context, item['service_id'], item['rank'], item['score'], datetime.now()))

        return scores

    def get_rankings(self, context: str) -> List[Dict]:
        """Get rankings for a specific context"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute(f"""
                SELECT r.rank, r.score, s.name as service_name
                FROM rankings r
                JOIN services s ON r.service_id = s.id
                WHERE r.context = {p}
                ORDER BY r.rank
            """, (context,))
            return [dict(row) for row in cursor.fetchall()]

    def get_features_for_service(self, service_id: int) -> Dict[str, bool]:
        """Get core features for a specific service"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute(f"SELECT feature_name, is_available FROM features WHERE service_id = {p}", (service_id,))
            return {row['feature_name']: bool(row['is_available']) for row in cursor.fetchall()}

    def get_additional_features(self, service_id: int) -> List[str]:
        """Get additional features for a specific service"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute(f"SELECT feature_name FROM additional_features WHERE service_id = {p}", (service_id,))
            return [row['feature_name'] for row in cursor.fetchall()]

    def get_service_rankings(self, service_id: int) -> Dict[str, Dict]:
        """Get rankings for a service across all contexts"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute(f"SELECT context, rank, score FROM rankings WHERE service_id = {p}", (service_id,))
            return {row['context']: {'rank': row['rank'], 'score': row['score']} for row in cursor.fetchall()}

    # ==================== Category Methods ====================

    def add_category(self, name: str, slug: str, description: str = None, 
                     feature_schema: Dict = None, ranking_contexts: Dict = None) -> int:
        """Add a new category"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            feature_json = json.dumps(feature_schema) if feature_schema else None
            contexts_json = json.dumps(ranking_contexts) if ranking_contexts else None
            
            if self.is_postgres:
                cursor.execute(f"""
                    INSERT INTO categories (name, slug, description, feature_schema, ranking_contexts)
                    VALUES ({p}, {p}, {p}, {p}, {p})
                    ON CONFLICT (slug) DO UPDATE SET 
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        feature_schema = EXCLUDED.feature_schema,
                        ranking_contexts = EXCLUDED.ranking_contexts
                    RETURNING id
                """, (name, slug, description, feature_json, contexts_json))
                return cursor.fetchone()['id']
            else:
                cursor.execute(f"""
                    INSERT OR REPLACE INTO categories (name, slug, description, feature_schema, ranking_contexts)
                    VALUES ({p}, {p}, {p}, {p}, {p})
                """, (name, slug, description, feature_json, contexts_json))
                return cursor.lastrowid

    def get_categories(self) -> List[Dict]:
        """Get all categories"""
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM categories ORDER BY name")
            categories = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for cat in categories:
                if cat.get('feature_schema') and isinstance(cat['feature_schema'], str):
                    try:
                        cat['feature_schema'] = json.loads(cat['feature_schema'])
                    except:
                        pass
                if cat.get('ranking_contexts') and isinstance(cat['ranking_contexts'], str):
                    try:
                        cat['ranking_contexts'] = json.loads(cat['ranking_contexts'])
                    except:
                        pass
            
            return categories

    def get_category_by_slug(self, slug: str) -> Optional[Dict]:
        """Get a category by its slug"""
        p = self.placeholder
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM categories WHERE slug = {p}", (slug,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            cat = dict(row)
            # Parse JSON fields
            if cat.get('feature_schema') and isinstance(cat['feature_schema'], str):
                try:
                    cat['feature_schema'] = json.loads(cat['feature_schema'])
                except:
                    pass
            if cat.get('ranking_contexts') and isinstance(cat['ranking_contexts'], str):
                try:
                    cat['ranking_contexts'] = json.loads(cat['ranking_contexts'])
                except:
                    pass
            
            return cat

    def assign_service_to_category(self, service_id: int, category_id: int):
        """Assign a service to a category"""
        p = self.placeholder
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE services SET category_id = {p} WHERE id = {p}", (category_id, service_id))

    def export_to_json(self, output_file: str):
        """Export all data to JSON file"""
        data = {
            'services': self.get_all_services(),
            'feature_comparison': self.get_feature_comparison(),
            'exported_at': datetime.now().isoformat()
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Default feature weights for different contexts (kept for reference and initialization)
DEFAULT_WEIGHTS = {
    'personal_use': {
        'free_tier': 2.0,
        'reminders': 2.0,
        'due_dates': 1.5,
        'tags_labels': 1.5,
        'subtasks': 1.0,
        'attachments': 1.0,
        'offline_mode': 1.5,
        'calendar_view': 1.0,
        'collaboration': 0.5,
        'integrations': 1.0,
        'api_available': 0.5,
    },
    'team_collaboration': {
        'collaboration': 3.0,
        'integrations': 2.0,
        'api_available': 1.5,
        'attachments': 1.5,
        'tags_labels': 1.0,
        'subtasks': 1.5,
        'due_dates': 1.0,
        'calendar_view': 1.0,
        'reminders': 1.0,
        'free_tier': 0.5,
        'offline_mode': 0.5,
    },
    'enterprise': {
        'collaboration': 2.5,
        'api_available': 2.5,
        'integrations': 2.0,
        'attachments': 1.5,
        'security': 2.0,
        'admin_controls': 2.0,
        'tags_labels': 1.0,
        'subtasks': 1.0,
        'due_dates': 1.0,
        'calendar_view': 0.5,
        'offline_mode': 0.5,
        'free_tier': 0.0,
    },
    'minimalist': {
        'free_tier': 2.0,
        'due_dates': 2.0,
        'reminders': 1.5,
        'offline_mode': 1.0,
        'tags_labels': 0.5,
        'subtasks': 0.5,
        'attachments': 0.5,
        'calendar_view': 0.5,
        'collaboration': 0.0,
        'integrations': 0.5,
        'api_available': 0.0,
    }
}
