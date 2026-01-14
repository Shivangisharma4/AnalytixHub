# Todo Service Feature Scraper & Ranking System

A comprehensive web scraping tool that extracts features from popular todo list services and provides intelligent rankings based on different use cases.

## Features

- **Web Scraping**: Automatically extracts features from popular todo services
- **Database Storage**: SQLite database for persistent storage
- **Smart Ranking System**: Ranks services based on different contexts (personal, team, enterprise, minimalist)
- **Feature Comparison**: Side-by-side comparison matrix
- **Interactive Recommendations**: Get personalized service recommendations
- **Data Export**: Export all data to JSON format

## Supported Services

- Todoist
- Trello
- Any.do
- Microsoft To Do
- Notion
- Asana
- ClickUp

## Installation

1. **Clone or download the project**

2. **Install dependencies**:
```bash
cd todo_features_scraper
pip install -r requirements.txt
```

## Usage

### Quick Start - Run Everything

```bash
python main.py all
```

This will:
1. Scrape all services
2. Generate rankings
3. Export data to JSON

### Individual Commands

#### 1. Scrape Services

```bash
# Scrape all services
python main.py scrape

# Scrape a single service
python main.py scrape-single --service "Todoist"

# List available services
python main.py list
```

#### 2. Generate Rankings

```bash
python main.py rank
```

This displays rankings for:
- **Personal Use**: Best for individuals
- **Team Collaboration**: Best for teams
- **Enterprise**: Best for large organizations
- **Minimalist**: Best for simple task management

#### 3. Feature Comparison

```bash
python main.py compare
```

Shows a matrix comparing all features across services.

#### 4. Service Summary

```bash
python main.py summary --service "Todoist"
```

Displays detailed information about a specific service.

#### 5. Get Recommendations

```bash
python main.py recommend
```

Interactive tool to find the best service based on your requirements.

#### 6. Export Data

```bash
python main.py export
```

Exports:
- `todo_services_data.json` - All features and data
- `rankings_report.json` - Rankings across all contexts

## Project Structure

```
todo_features_scraper/
├── main.py                 # Main CLI script
├── base_scraper.py        # Base scraper class
├── scrapers.py            # Individual service scrapers
├── database.py            # Database operations
├── ranking_system.py      # Ranking and comparison logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── todo_services.db      # SQLite database (created automatically)
├── todo_services_data.json  # Exported data
└── rankings_report.json  # Exported rankings
```

## Tracked Features

The scraper tracks the following features for each service:

- **Free Tier**: Whether a free version is available
- **Collaboration**: Team sharing and collaboration features
- **Reminders**: Notification and reminder capabilities
- **Due Dates**: Task due date management
- **Tags/Labels**: Organization and categorization
- **Subtasks**: Nested task support
- **Attachments**: File attachment support
- **Offline Mode**: Works without internet
- **Calendar View**: Calendar interface
- **Integrations**: Integration with other apps
- **API Availability**: Developer API access

Plus additional unique features for each service.

## Ranking System

The ranking system uses weighted scoring based on use case:

### Personal Use
Weights: Free tier (2.0), Reminders (2.0), Due dates (1.5), Offline mode (1.5)

### Team Collaboration
Weights: Collaboration (3.0), Integrations (2.0), API (1.5), Attachments (1.5)

### Enterprise
Weights: Collaboration (2.5), API (2.5), Integrations (2.0), Security (2.0)

### Minimalist
Weights: Free tier (2.0), Due dates (2.0), Reminders (1.5), Simple UI (1.5)

## Database Schema

### Tables

**services**: Basic service information
**features**: Boolean features for each service
**additional_features**: Text-based unique features
**feature_weights**: Weights for different ranking contexts
**rankings**: Cached ranking results

## Examples

### Example 1: Find Best Personal Todo App

```bash
python main.py recommend
# Select: 1 (Personal Use)
# Free tier: y
# Collaboration: n
# Offline mode: y
```

### Example 2: Compare Todoist vs Trello

```bash
python main.py scrape
python main.py compare
```

### Example 3: Detailed Service Analysis

```bash
python main.py summary --service "Notion"
```

## Extending the Scraper

### Adding a New Service

1. Create a new scraper class in `scrapers.py`:

```python
class NewServiceScraper(BaseScraper):
    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()
        return ServiceFeatures(
            name="New Service",
            url=self.url,
            # ... fill in features
        )
```

2. Register it in the `SCRAPERS` dictionary:

```python
SCRAPERS = {
    # ... existing services
    'New Service': lambda: NewServiceScraper('https://newservice.com', 'New Service'),
}
```

### Adding Custom Ranking Contexts

Edit `DEFAULT_WEIGHTS` in `database.py`:

```python
DEFAULT_WEIGHTS = {
    'my_context': {
        'feature1': 2.0,
        'feature2': 1.5,
        # ...
    }
}
```

## Troubleshooting

### Scraping Issues

- **Slow connection**: Increase timeout in `base_scraper.py`
- **Blocked by website**: The scraper uses basic headers; some sites may require Selenium
- **Missing features**: Update keyword lists in scraper classes

### Database Issues

```bash
# Reset database
rm todo_services.db
python main.py all
```

## Legal & Ethical Notes

- This tool scrapes publicly available information only
- Respect robots.txt and rate limits
- Some services may prohibit scraping in their ToS
- Consider using official APIs when available
- For educational and research purposes

## Future Enhancements

- [ ] Web dashboard for visualization
- [ ] Historical price tracking
- [ ] User review integration
- [ ] API endpoint for rankings
- [ ] Selenium/Playwright for dynamic sites
- [ ] Automated scheduled scraping
- [ ] Machine learning recommendation engine

## Contributing

To add more services:
1. Fork the project
2. Add scraper class
3. Submit pull request

## License

Educational use only. Respect website terms of service.

## Author

Built for competitor analysis and feature comparison research.
