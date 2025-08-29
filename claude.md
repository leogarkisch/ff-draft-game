# Claude Memory File - Chicago Bears Fantasy Football Draft Order Game

## 🐻 CRITICAL: CHICAGO BEARS BRANDING IS PARAMOUNT 🐻

**NEVER FORGET**: This entire application MUST use Chicago Bears colors as the primary theme throughout ALL design elements:

- **Navy**: #0B162A (--bears-navy) - Main headers, borders, primary elements
- **Orange**: #C83803 (--bears-orange) - Accents, highlights, secondary elements  
- **Light Blue**: #1E3A5F (--bears-light-blue) - Hover states, tertiary elements
- **Light Orange**: #E85A2B (--bears-light-orange) - Light accents, subtitles

**DO NOT** use generic Bootstrap blue (#007bff) or any other primary colors! ALL primary/secondary colors throughout the app should be Bears themed.

## Project Overview

This is a Flask web application for a fantasy football draft order selection game using the "2/3 of the average" game theory concept. Players submit number guesses, and whoever gets closest to 2/3 of the average wins first pick of draft position.

## Technical Stack

- **Backend**: Flask with SQLAlchemy
- **Database**: SQLite (game.db)
- **Frontend**: Bootstrap + Custom CSS (Chicago Bears themed)
- **Deployment**: Local development server on port 5001

## Key Features Implemented

### Core Game Mechanics
- Number guessing game (0-1000 range)
- 2/3 of average calculation for winner determination
- Draft position selection in order of closeness to target
- Snake draft visualization
- Timezone-aware deadline system

### Admin Features
- Game phase management (submission → results → selecting → completed)
- Dev mode toggle for testing
- Manual game reset functionality
- Database backup/restore system
- League name customization
- Quick test data population

### UI/UX Features
- **Chicago Bears themed design** (Navy/Orange color scheme)
- Light/Dark mode toggle with auto-detection
- Responsive design for mobile/desktop
- Dynamic strategy explanations based on league size
- Real-time countdown timer
- Submission confirmation system

## Database Schema

### GameState Table
- `id`: Primary key
- `phase`: Current game phase (submission/results/selecting/completed)
- `target_number`: Calculated 2/3 of average
- `winner_id`: ID of winning player
- `deadline`: Submission deadline (timezone-aware)
- `dev_mode`: Boolean for development testing
- `league_name`: Customizable league name

### Player Table
- `id`: Primary key
- `name`: Player name
- `email`: ESPN account email
- `guess`: Number guess (0-1000)
- `timestamp`: Submission time
- `draft_position`: Selected draft position
- `distance_from_target`: Calculated distance from target

## File Structure

### Core Application Files
- `app.py` - Main Flask application with all routes
- `init_db.py` - Database initialization script
- `run.sh` - Development server startup script

### Templates (Jinja2)
- `base.html` - Base template with navigation and theme toggle
- `index.html` - Main game page with submission form
- `results.html` - Game results and winner display
- `draft_selection.html` - Interactive draft position selection
- `snake_draft.html` - Snake draft pattern visualization
- `admin.html` - Admin control panel
- `admin_backups.html` - Database backup management
- `submission_confirmed.html` - Confirmation page

### Static Assets
- `static/style.css` - **CHICAGO BEARS THEMED** CSS with comprehensive design system
- `static/script.js` - Theme toggle and countdown functionality

## CSS Architecture & Maintenance Guidelines

### CSS Consolidation Best Practices
- **AVOID BLOAT**: Never let CSS exceed ~300 lines without consolidation
- **REMOVE REDUNDANCY**: Don't create utility classes that Bootstrap already provides (margins, padding, text alignment, flex utilities)
- **CONSOLIDATE SELECTORS**: Group similar styles together with comma-separated selectors
- **MINIMIZE DUPLICATES**: Don't repeat property declarations across multiple rules
- **COMPACT SYNTAX**: Use shorthand properties and group related styles on single lines where appropriate
- **BOOTSTRAP UTILIZATION**: Leverage existing Bootstrap classes instead of creating custom utilities

### File Structure & Organization

### Theme System
- CSS custom properties for Bears colors
- Auto light/dark mode detection + manual toggle
- Comprehensive Bootstrap utility overrides
- Consistent spacing and typography utilities

### Component Classes
- `.info-card` - Main content cards with Bears navy headers
- `.status-card` - Status indicators with color-coded borders
- `.game-example-card` - Example content with light blue accents
- `.strategy-card` - Navy background with orange borders
- `.submissions-card` - Table-based cards with Bears headers
- `.inline-form` utilities for consistent form layouts

## Critical Implementation Notes

### Bears Color Usage
- **All headers**: Bears navy background (#0B162A) with white text
- **All borders**: Bears navy or orange depending on context
- **Accent elements**: Bears orange (#C83803)
- **Hover states**: Orange border transitions
- **Text hierarchy**: Navy for headings, orange for highlights

### Dark Mode Considerations
- All colors use CSS variables for theme compatibility
- Text colors properly switch between light/dark variants
- No hardcoded colors in templates (all moved to CSS)
- Shadow and border colors adapt to theme

### Development Workflow
1. Kill existing processes: `lsof -ti:5001 | xargs kill -9 2>/dev/null || true`
2. Initialize database: `source venv/bin/activate && python init_db.py`
3. Start server: `python app.py` (runs on localhost:5001)

## Recent Changes & Maintenance

### CSS Consolidation (Latest Priority)
- **CRITICAL**: CSS file was bloated at 1119 lines with significant redundancy
- **FIXED**: Consolidated down to 202 lines (82% reduction) by:
  - Combining duplicate selectors and properties
  - Removing redundant utility classes that Bootstrap already provides
  - Consolidating theme declarations and removing duplication
  - Grouping related styles together with compact syntax
  - **REMEMBER**: Always keep CSS lean and consolidated. Avoid duplicate declarations and redundant utility classes. Most spacing/layout utilities already exist in Bootstrap.

### Chicago Bears Color Scheme Enforcement
- Moved all embedded CSS from templates to main stylesheet
- Eliminated all inline styles in favor of utility classes
- Created comprehensive design system with Bears branding
- Fixed dark text on dark background issues
- Organized CSS with clear section headers and comments

### UI Improvements
- Standardized all front page cards with consistent styling
- Implemented proper visual hierarchy
- Enhanced responsive design
- Added comprehensive utility classes for layout/typography
- Ensured Bears colors dominate throughout

### Features Added
- League name customization
- Submission confirmation workflow
- Enhanced admin controls
- Better error handling and validation
- Improved mobile responsiveness

## Testing & Debugging

### Common Issues
- **Dark text on dark backgrounds**: Fixed by moving to CSS variables
- **Color inconsistencies**: Resolved by enforcing Bears color scheme
- **Timezone errors**: Fixed with proper pytz handling
- **Database migration**: Handled with backup/restore system

### Admin Quick Actions
- Toggle dev mode for testing without affecting live game
- Reset game state while preserving league configuration
- Create manual backups before major changes
- Quick populate test data for development

## Future Considerations

- Maintain Bears branding in ALL new features
- Test theme toggle functionality with each update
- Ensure responsive design for new components
- Keep CSS organized and commented
- Preserve database backup functionality

---

*Remember: CHICAGO BEARS COLORS ARE NON-NEGOTIABLE! 🐻*
