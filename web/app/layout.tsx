import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Todo Service Rankings | Compare & Find the Best Todo App',
  description: 'Compare features, rankings, and find the best todo list service for your needs. Analyze Todoist, Trello, Notion, Asana, and more.',
  keywords: 'todo app comparison, todoist vs trello, task management, productivity tools',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
