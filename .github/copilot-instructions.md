# Fantasy Football Draft Game - Repository Instructions

## Project Overview

This is a web-based fantasy football draft game implementing the "2/3 of the average" game theory concept with a Chicago Bears theme. Players submit numbers between 0-100, and the winner is closest to 2/3 of the average of all submissions. Built with Flask and SQLite, deployed on Railway.

## Project Structure

- `app.py` - Main Flask application with all routes, game logic, and admin panel
- `instance/draft_game.db` - SQLite database (auto-created)
- `templates/` - Jinja2 HTML templates with Chicago Bears styling
- `static/` - CSS, JavaScript, and image assets
- `backups/` - Automatic database/JSON backups with timestamps
- `run.sh` - Local development script (validated working)
- `requirements.txt` - Python dependencies for Railway deployment
- `railway.toml` - Railway deployment configuration

## Development Workflow

### Local Development
Always use `./run.sh` for local development - it handles:
- Directory validation and navigation
- Process cleanup (kills existing Flask processes on port 5000)
- Virtual environment setup
- Dependency installation
- Database initialization
- Development server startup with debug mode

### Database Management
- SQLite database auto-creates on first run
- Automatic backups before major operations (in `/backups/` with timestamps)
- Three phases: Registration, Submission, Results
- Admin panel at `/admin` (password: `ff2025admin`)

### Deployment
- Deploy to Railway using `railway up`
- **CRITICAL**: Always backup data before deployment (Railway has ephemeral storage)
- Use git commits to preserve state: `git add . && git commit -m "backup before deploy"`

## Chicago Bears Branding Requirements

- **Colors**: Navy blue (#0B162A), orange (#C83803), white
- **Typography**: Bold headers, clean sans-serif body text
- **UI Elements**: Orange accent buttons, navy backgrounds
- **Icons**: Football/Bears themed where appropriate
- **Messaging**: Professional but enthusiastic Bears references

## Code Standards

- **Python**: PEP 8 style, clear function names, comprehensive error handling
- **HTML**: Semantic structure, accessibility considerations
- **CSS**: Mobile-first responsive design, Bears color scheme
- **JavaScript**: Vanilla JS preferred, progressive enhancement
- **Database**: SQLAlchemy ORM, proper migrations for schema changes

## Security Considerations

- Admin authentication required for sensitive operations
- Input validation on all form submissions
- CSRF protection on state-changing operations
- Backup system prevents data loss

## Key Features

- **Game Phases**: Registration → Submission → Results
- **Admin Controls**: Phase management, participant oversight, game reset
- **Backup System**: Automatic timestamped backups before major changes
- **Mobile Responsive**: Works on all device sizes
- **Railway Deployment**: Cloud hosting with proper configuration

## Important Notes

- This is a single-round game implementation
- Railway uses ephemeral storage - always backup before deploying
- Database resets when Railway container restarts unless data is committed to git
- Admin panel allows phase advancement and participant management
- Game state is preserved through automatic backup system
