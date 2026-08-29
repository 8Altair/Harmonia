import {
  AudioLines,
  BookOpenText,
  FolderKanban,
  History,
  House,
  MoonStar,
  Settings,
  Sun,
  Volume2,
} from "lucide-react";

const navigationItems = [
  { label: "Workspace", icon: House, active: true },
  { label: "Projects", icon: FolderKanban },
  { label: "History", icon: History },
  { label: "Glossary", icon: BookOpenText },
  { label: "Voices", icon: Volume2 },
  { label: "Settings", icon: Settings },
];

function Sidebar({ theme, onThemeChange }) {
  const darkModeEnabled = theme === "dark";

  return (
    <aside className="sidebar">
      <div className="brand-card">
        <div className="brand-mark" aria-hidden="true">
          <AudioLines size={26} />
        </div>
        <div>
          <p className="brand-eyebrow">Harmonia</p>
          <h1 className="brand-title">Language pipeline</h1>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Workspace navigation">
        {navigationItems.map(({ label, icon: Icon, active }) => (
          <button
            key={label}
            type="button"
            className={`sidebar-nav__item${active ? " sidebar-nav__item--active" : ""}`}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-toggle">
        <div className="sidebar-toggle__label">
          {darkModeEnabled ? <MoonStar size={22} /> : <Sun size={22} />}
          <p>Dark Mode</p>
        </div>
        <button
          type="button"
          className={`toggle-pill${darkModeEnabled ? " toggle-pill--active" : ""}`}
          aria-label="Toggle dark mode"
          aria-pressed={darkModeEnabled}
          onClick={() => onThemeChange(darkModeEnabled ? "light" : "dark")}
        >
          <span />
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
