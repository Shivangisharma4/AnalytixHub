'use client';

import { FiHome, FiAward, FiColumns, FiGrid, FiSearch, FiChevronDown } from 'react-icons/fi';
import { Category } from '@/lib/db';

type View = 'overview' | 'rankings' | 'compare' | 'services';

interface HeaderProps {
  view: View;
  setView: (view: View) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  categories: Category[];
  selectedCategory: Category | null;
  setSelectedCategory: (category: Category) => void;
}

const navItems = [
  { id: 'overview' as View, label: 'Overview', icon: FiHome },
  { id: 'rankings' as View, label: 'Rankings', icon: FiAward },
  { id: 'compare' as View, label: 'Compare', icon: FiColumns },
  { id: 'services' as View, label: 'Services', icon: FiGrid },
];

export default function Header({
  view,
  setView,
  searchQuery,
  setSearchQuery,
  categories,
  selectedCategory,
  setSelectedCategory
}: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-bold text-primary-600 shrink-0">
              ServiceRank
            </h1>

            <div className="relative group">
              <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors">
                {selectedCategory?.name || 'Loading...'}
                <FiChevronDown size={14} className="text-gray-400" />
              </button>

              <div className="absolute top-full left-0 mt-1 w-56 bg-white border border-gray-200 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <div className="p-1">
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setSelectedCategory(cat)}
                      className={`
                        w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors
                        ${selectedCategory?.id === cat.id
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-600 hover:bg-gray-50'
                        }
                      `}
                    >
                      {cat.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <nav className="hidden lg:flex items-center gap-1">
              {navItems.map(item => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setView(item.id)}
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-lg font-medium transition-colors
                      ${view === item.id
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon size={18} />
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search services..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-48 xl:w-64"
              />
            </div>

            <a
              href="https://github.com/Shivangisharma4/AnalytixHub"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary whitespace-nowrap"
            >
              GitHub
            </a>
          </div>
        </div>

        {/* Mobile nav */}
        <nav className="lg:hidden flex items-center gap-2 py-2 overflow-x-auto">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setView(item.id)}
                className={`
                  flex items-center gap-2 px-3 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors
                  ${view === item.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50'
                  }
                `}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
