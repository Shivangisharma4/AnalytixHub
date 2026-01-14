"""
Individual scrapers for popular todo list services.
Each scraper is tailored to extract features from specific services.
"""
from base_scraper import BaseScraper, ServiceFeatures
from bs4 import BeautifulSoup


class TodoistScraper(BaseScraper):
    """Scraper for Todoist features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="Todoist",
            url=self.url,
            free_tier=True,
            pricing=self.extract_pricing(soup),
            platforms=self.extract_platforms(soup),
            collaboration=self.check_feature_mention(soup, ['share', 'team', 'collabora', 'assign']),
            reminders=self.check_feature_mention(soup, ['reminder', 'notification']),
            due_dates=True,
            tags_labels=self.check_feature_mention(soup, ['tag', 'label']),
            subtasks=self.check_feature_mention(soup, ['subtask', 'section', 'task']),
            attachments=self.check_feature_mention(soup, ['attach', 'file', 'upload']),
            offline_mode=self.check_feature_mention(soup, ['offline', 'work offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar', 'schedule view']),
            integrations=self.check_feature_mention(soup, ['integrate', 'zapier', 'google calendar']),
            api_available=True,
            additional_features=self.extract_additional_features(soup, [
                'Karma points', 'Natural language input', 'Templates',
                'Project templates', 'Productivity trends'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


class TrelloScraper(BaseScraper):
    """Scraper for Trello features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="Trello",
            url=self.url,
            free_tier=True,
            pricing=self.extract_pricing(soup),
            platforms=self.extract_platforms(soup),
            collaboration=self.check_feature_mention(soup, ['board', 'team', 'member', 'share']),
            reminders=True,  # Trello has due date notifications
            due_dates=True,
            tags_labels=self.check_feature_mention(soup, ['label', 'tag']),
            subtasks=self.check_feature_mention(soup, ['checklist', 'subtask']),
            attachments=True,  # Core Trello feature
            offline_mode=self.check_feature_mention(soup, ['offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar', 'calendar power-up']),
            integrations=self.check_feature_mention(soup, ['power-up', 'integrate', 'butler']),
            api_available=True,
            additional_features=self.extract_additional_features(soup, [
                'Kanban boards', 'Power-ups', 'Butler automation',
                'Custom fields', 'Board templates'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


class AnyDoScraper(BaseScraper):
    """Scraper for Any.do features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="Any.do",
            url=self.url,
            free_tier=True,
            pricing=self.extract_pricing(soup),
            platforms=self.extract_platforms(soup),
            collaboration=self.check_feature_mention(soup, ['share', 'assign', 'collabora']),
            reminders=True,
            due_dates=True,
            tags_labels=self.check_feature_mention(soup, ['category', 'tag']),
            subtasks=self.check_feature_mention(soup, ['subtask']),
            attachments=self.check_feature_mention(soup, ['attach', 'file']),
            offline_mode=self.check_feature_mention(soup, ['offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar', 'calendar integration']),
            integrations=self.check_feature_mention(soup, ['integrate', 'sync', 'google calendar']),
            api_available=self.check_feature_mention(soup, ['api', 'developer']),
            additional_features=self.extract_additional_features(soup, [
                'Voice entry', 'Gesture planning', 'WhatsApp integration',
                'Smart grocery lists', 'Location-based reminders'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


class MicrosoftToDoScraper(BaseScraper):
    """Scraper for Microsoft To Do features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="Microsoft To Do",
            url=self.url,
            free_tier=True,
            pricing="Free",
            platforms=self.extract_platforms(soup),
            collaboration=self.check_feature_mention(soup, ['share', 'team', 'group']),
            reminders=True,
            due_dates=True,
            tags_labels=self.check_feature_mention(soup, ['tag', 'category']),
            subtasks=self.check_feature_mention(soup, ['step', 'subtask']),
            attachments=self.check_feature_mention(soup, ['attach', 'file']),
            offline_mode=self.check_feature_mention(soup, ['offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar', 'outlook calendar']),
            integrations=self.check_feature_mention(soup, ['outlook', 'office 365', 'teams']),
            api_available=self.check_feature_mention(soup, ['graph api', 'microsoft graph']),
            additional_features=self.extract_additional_features(soup, [
                'My Day feature', 'Outlook integration', 'Office 365 integration',
                'Smart suggestions', 'Task syncing across devices'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


class NotionScraper(BaseScraper):
    """Scraper for Notion tasks/features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="Notion",
            url=self.url,
            free_tier=True,
            pricing=self.extract_pricing(soup),
            platforms=self.extract_platforms(soup),
            collaboration=True,  # Core feature
            reminders=self.check_feature_mention(soup, ['reminder', 'notification']),
            due_dates=True,
            tags_labels=self.check_feature_mention(soup, ['tag', 'property', 'database']),
            subtasks=True,  # Can create nested pages
            attachments=True,
            offline_mode=self.check_feature_mention(soup, ['offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar view', 'database view']),
            integrations=self.check_feature_mention(soup, ['integrate', 'api', 'connect']),
            api_available=True,
            additional_features=self.extract_additional_features(soup, [
                'Databases', 'Wikis', 'Docs', 'Templates',
                'Kanban boards', 'Timeline view', 'Gallery view',
                'AI assistant', 'Web clipper'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


class AsanaScraper(BaseScraper):
    """Scraper for Asana features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="Asana",
            url=self.url,
            free_tier=True,
            pricing=self.extract_pricing(soup),
            platforms=self.extract_platforms(soup),
            collaboration=True,
            reminders=True,
            due_dates=True,
            tags_labels=self.check_feature_mention(soup, ['tag', 'custom field']),
            subtasks=self.check_feature_mention(soup, ['subtask']),
            attachments=True,
            offline_mode=self.check_feature_mention(soup, ['offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar', 'timeline']),
            integrations=self.check_feature_mention(soup, ['integrate', 'app']),
            api_available=True,
            additional_features=self.extract_additional_features(soup, [
                'Timeline view', 'Portfolio management', 'Forms',
                'Workload management', 'Goal tracking', 'Automations'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


class ClickUpScraper(BaseScraper):
    """Scraper for ClickUp features"""

    def scrape(self) -> ServiceFeatures:
        soup = self.fetch_page()

        return ServiceFeatures(
            name="ClickUp",
            url=self.url,
            free_tier=True,
            pricing=self.extract_pricing(soup),
            platforms=self.extract_platforms(soup),
            collaboration=True,
            reminders=True,
            due_dates=True,
            tags_labels=True,
            subtasks=True,
            attachments=True,
            offline_mode=self.check_feature_mention(soup, ['offline']),
            calendar_view=self.check_feature_mention(soup, ['calendar', 'calendar view']),
            integrations=True,
            api_available=True,
            additional_features=self.extract_additional_features(soup, [
                'Multiple views', 'Custom statuses', 'Docs',
                'Whiteboards', 'Mind maps', 'Automations',
                'Time tracking', 'Goals'
            ])
        )

    def extract_additional_features(self, soup: BeautifulSoup, features: list) -> list:
        found = []
        text = soup.get_text().lower()
        for feature in features:
            if feature.lower() in text or any(word in text for word in feature.lower().split()):
                found.append(feature)
        return found


# Registry of all scrapers
SCRAPERS = {
    'Todoist': lambda: TodoistScraper('https://todoist.com', 'Todoist'),
    'Trello': lambda: TrelloScraper('https://trello.com', 'Trello'),
    'Any.do': lambda: AnyDoScraper('https://any.do', 'Any.do'),
    'Microsoft To Do': lambda: MicrosoftToDoScraper('https://todo.microsoft.com', 'Microsoft To Do'),
    'Notion': lambda: NotionScraper('https://notion.so', 'Notion'),
    'Asana': lambda: AsanaScraper('https://asana.com', 'Asana'),
    'ClickUp': lambda: ClickUpScraper('https://clickup.com', 'ClickUp'),
}
