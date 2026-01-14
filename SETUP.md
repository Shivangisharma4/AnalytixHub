# Complete Setup Guide

## Todo Service Rankings - Full Stack Application

This guide will help you set up and run both the scraper and the web dashboard.

---

## Quick Start

### 1. Install Python Dependencies

```bash
cd todo_features_scraper
pip install -r requirements.txt
```

### 2. Scrape Data & Generate Rankings

```bash
python main.py all
```

This will:
- Scrape all todo services
- Generate rankings for all contexts
- Export data to JSON files
- Create `todo_services.db` database

### 3. Install Web Dependencies

```bash
cd web
npm install
```

### 4. Run the Web Dashboard

```bash
npm run dev
```

Open http://localhost:3000

---

## Project Structure

```
todo_features_scraper/
├── main.py                # Main CLI script
├── base_scraper.py        # Base scraper class
├── scrapers.py            # Service-specific scrapers
├── database.py            # Database operations
├── ranking_system.py      # Ranking logic
├── requirements.txt       # Python dependencies
├── README.md             # CLI documentation
│
├── web/                   # Next.js web dashboard
│   ├── app/              # Next.js app directory
│   │   ├── api/          # API routes
│   │   ├── globals.css   # Global styles
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Home page
│   ├── components/       # React components
│   ├── lib/             # Utilities (database)
│   ├── package.json     # Node dependencies
│   └── README.md        # Web documentation
│
├── todo_services.db      # SQLite database (created after scraping)
├── todo_services_data.json    # Exported data
└── rankings_report.json       # Exported rankings
```

---

## CLI Commands

### Scraper Commands

```bash
# Scrape all services
python main.py scrape

# Scrape a single service
python main.py scrape-single --service "Todoist"

# List available services
python main.py list

# Generate rankings
python main.py rank

# Show feature comparison
python main.py compare

# Show service summary
python main.py summary --service "Todoist"

# Get interactive recommendations
python main.py recommend

# Export data to JSON
python main.py export

# Run full pipeline (scrape + rank + export)
python main.py all
```

---

## Web Dashboard

### Views

1. **Overview**: Quick stats, charts, and recommendations
2. **Rankings**: Detailed rankings by use case
3. **Compare**: Side-by-side feature comparison
4. **Services**: All services with search

### API Endpoints

```
GET /api/services          # All services or specific service
GET /api/rankings          # All rankings or by context
GET /api/compare           # Feature comparison matrix
GET /api/recommend         # Personalized recommendations
```

---

## Deployment to Vercel

### Option 1: Full Stack (Recommended for Production)

For production, you'll want to use an external database instead of SQLite:

1. **Set up a database** (Vercel Postgres, Neon, Supabase, etc.)
2. **Update `web/lib/db.ts`** to use your database
3. **Deploy to Vercel**:
   ```bash
   cd web
   vercel deploy
   ```

### Option 2: Static Site (Simpler)

For static hosting (GitHub Pages, Netlify):

1. **Pre-generate data**:
   ```bash
   python main.py export
   ```

2. **Create static JSON API** by moving exported files to `public/`

3. **Update API routes** to serve static files instead of database queries

4. **Build and deploy**:
   ```bash
   cd web
   npm run build
   # Deploy .next folder or use static export
   ```

---

## Updating Data

To refresh the data:

```bash
# From the root directory
python main.py all

# Then restart the web server
cd web
npm run dev
```

---

## Customization

### Add New Services

Edit `scrapers.py`:

```python
class NewServiceScraper(BaseScraper):
    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()
        return ServiceFeatures(
            name="New Service",
            url=self.url,
            # ... fill in features
        )

# Register in SCRAPERS dict
SCRAPERS = {
    # ... existing services
    'New Service': lambda: NewServiceScraper('https://newservice.com', 'New Service'),
}
```

### Adjust Ranking Weights

Edit `database.py`:

```python
DEFAULT_WEIGHTS = {
    'your_context': {
        'feature1': 2.0,
        'feature2': 1.5,
        # ...
    }
}
```

---

## Troubleshooting

### Database Issues

```bash
# Reset database
rm todo_services.db
python main.py all
```

### Web Dashboard Issues

```bash
# Clear Next.js cache
cd web
rm -rf .next
npm run dev
```

### Scraping Issues

- Check your internet connection
- Some sites may block scraping
- Try running with delay between requests

---

## Tech Stack

**Scraper:**
- Python 3.8+
- requests, BeautifulSoup4
- SQLite

**Web Dashboard:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Recharts

---

## License

Educational use only. Respect website terms of service.
