# Todo Service Rankings - Web Dashboard

Interactive web dashboard for comparing and ranking todo list services.

## Features

- **Overview Page**: Quick stats, charts, and top services
- **Rankings View**: Detailed rankings by use case (Personal, Team, Enterprise, Minimalist)
- **Comparison Tool**: Side-by-side feature comparison with filters
- **Service Cards**: Detailed information for each service
- **Smart Recommendations**: AI-powered recommendations based on your requirements
- **Interactive Charts**: Radar charts and bar charts for visual comparison
- **Search & Filters**: Find the perfect service for your needs

## Tech Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Database**: SQLite (better-sqlite3)
- **Icons**: React Icons
- **Deployment**: Vercel/Netlify ready

## Development

### Prerequisites

1. Make sure you have scraped data first:
```bash
cd ..
python main.py all
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

4. Open http://localhost:3000

## Project Structure

```
web/
├── app/
│   ├── api/
│   │   ├── services/      # Service data endpoints
│   │   ├── rankings/      # Rankings endpoints
│   │   ├── compare/       # Feature comparison endpoint
│   │   └── recommend/     # Recommendation endpoint
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/
│   ├── Dashboard.tsx      # Main dashboard
│   ├── Header.tsx         # Navigation header
│   ├── RankingsView.tsx   # Rankings display
│   ├── ComparisonView.tsx # Feature comparison
│   ├── ServiceCards.tsx   # Service cards
│   ├── RecommendationPanel.tsx  # Recommendation tool
│   └── FeatureChart.tsx   # Charts and visualizations
├── lib/
│   └── db.ts              # Database utilities
└── package.json
```

## API Endpoints

### GET /api/services
Get all services or a specific service.
- Query params: `?name=Todoist`

### GET /api/rankings
Get rankings for all contexts or specific context.
- Query params: `?context=personal_use`

### GET /api/compare
Get feature comparison matrix for all services.

### GET /api/recommend
Get personalized recommendations.
- Query params:
  - `context`: personal_use, team_collaboration, enterprise, minimalist
  - `free_tier`: true/false
  - `collaboration`: true/false
  - `offline_mode`: true/false
  - `api_available`: true/false

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Configure build settings:
   - Root Directory: `web`
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Important**: For SQLite to work, you need to handle the database:
   - Option A: Use Vercel Postgres instead of SQLite
   - Option B: Deploy with Docker to include the database file
   - Option C: Use serverless functions with external database

### Netlify

1. Create `netlify.toml`:
```toml
[build]
  base = "web/"
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

2. Connect your Git repository to Netlify

### GitHub Pages (Static Export)

For static hosting, you'll need to:
1. Convert to static export (no API routes)
2. Pre-generate JSON files
3. Serve static data instead of database queries

## Environment Variables

No environment variables needed for local development.

For production with external database:
- `DATABASE_URL`: Connection string for your database

## Updating Data

To refresh the data:
```bash
cd ..
python main.py all
```

Then restart the web server to see updated data.

## Customization

### Adding New Services

Edit `../scrapers.py` to add new services, then re-scrape.

### Changing Feature Weights

Edit `../database.py` DEFAULT_WEIGHTS to adjust ranking criteria.

### Styling

Edit `tailwind.config.ts` for theme customization.

## Performance

- Static generation where possible
- Database queries optimized with indexes
- Charts use responsive containers
- Lazy loading for large datasets

## License

Same as parent project.
