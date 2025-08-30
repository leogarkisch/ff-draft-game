from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import pytz
import statistics
import os
import shutil
import json
import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///draft_game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Admin password
ADMIN_PASSWORD = 'ff2025admin'

# Add abs function to Jinja templates
app.jinja_env.globals.update(abs=abs)

db = SQLAlchemy(app)

# Set the deadline for submissions (Thursday 8/28 at 11:59pm ET)
# DEADLINE = datetime(2025, 8, 28, 23, 59, 0, tzinfo=pytz.timezone('US/Eastern'))
# For testing - disable automatic deadline
DEADLINE_ENABLED = False

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    guess = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    draft_position = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))  # Supports both IPv4 and IPv6

class DeletedPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    guess = db.Column(db.Integer, nullable=False)
    original_timestamp = db.Column(db.DateTime, nullable=False)
    deleted_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_reason = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))  # Track IP for deleted players too

class GameState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(20), default='setup')  # setup, submission, results, selecting, completed
    winner_id = db.Column(db.Integer)
    target_number = db.Column(db.Float)
    average_guess = db.Column(db.Float)
    num_teams = db.Column(db.Integer, default=12)  # Default to 12 teams for fantasy football
    submission_deadline = db.Column(db.DateTime)  # When submissions close
    dev_mode = db.Column(db.Boolean, default=False)  # Allow duplicate submissions for testing
    league_name = db.Column(db.String(100), default='Fantasy Football League')  # Customizable league name
    is_simulation = db.Column(db.Boolean, default=False)  # True for simulation mode, False for real run
    is_initialized = db.Column(db.Boolean, default=False)  # Whether game has been properly set up

class LeagueMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Backup Configuration
BACKUP_DIR = 'backups'
MAX_BACKUPS = 50  # Keep last 50 backups

def get_client_ip():
    """Get the client's IP address, accounting for proxies and load balancers"""
    # Check for X-Forwarded-For header (common with proxies/load balancers)
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # Check for X-Real-IP header (another common proxy header)
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    # Fallback to Flask's remote_addr
    else:
        ip = request.remote_addr
    
    return ip

def ensure_backup_directory():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_backup(reason="manual"):
    """Create a backup of the current database state"""
    try:
        ensure_backup_directory()
        
        # Create timestamp for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{reason}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Copy the database file
        db_path = 'instance/draft_game.db'
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            
            # Also create a JSON export for easier inspection
            json_filename = f"backup_{timestamp}_{reason}.json"
            json_path = os.path.join(BACKUP_DIR, json_filename)
            export_data_to_json(json_path)
            
            # Clean up old backups
            cleanup_old_backups()
            
            print(f"Backup created: {backup_filename}")
            return backup_filename
        else:
            print("Database file not found for backup")
            return None
    except Exception as e:
        print(f"Backup failed: {str(e)}")
        return None

def export_data_to_json(json_path):
    """Export current database state to JSON for easy inspection"""
    try:
        data = {
            'timestamp': datetime.now().isoformat(),
            'players': [],
            'deleted_players': [],
            'game_state': None
        }
        
        # Export players
        players = Player.query.all()
        for player in players:
            data['players'].append({
                'id': player.id,
                'name': player.name,
                'email': player.email,
                'guess': player.guess,
                'timestamp': player.timestamp.isoformat() if player.timestamp else None,
                'draft_position': player.draft_position,
                'ip_address': player.ip_address
            })
        
        # Export deleted players
        deleted_players = DeletedPlayer.query.all()
        for player in deleted_players:
            data['deleted_players'].append({
                'id': player.id,
                'original_id': player.original_id,
                'name': player.name,
                'email': player.email,
                'guess': player.guess,
                'original_timestamp': player.original_timestamp.isoformat() if player.original_timestamp else None,
                'deleted_timestamp': player.deleted_timestamp.isoformat() if player.deleted_timestamp else None,
                'deleted_reason': player.deleted_reason,
                'ip_address': player.ip_address
            })
        
        # Export game state
        game_state = GameState.query.first()
        if game_state:
            data['game_state'] = {
                'id': game_state.id,
                'phase': game_state.phase,
                'winner_id': game_state.winner_id,
                'target_number': game_state.target_number,
                'average_guess': game_state.average_guess,
                'num_teams': game_state.num_teams
            }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"JSON export failed: {str(e)}")

def cleanup_old_backups():
    """Remove old backups to keep only the most recent MAX_BACKUPS"""
    try:
        # Get all backup files sorted by creation time
        backup_files = glob.glob(os.path.join(BACKUP_DIR, "backup_*.db"))
        backup_files.sort(key=os.path.getctime, reverse=True)
        
        # Remove old backups
        for old_backup in backup_files[MAX_BACKUPS:]:
            os.remove(old_backup)
            # Also remove corresponding JSON file
            json_file = old_backup.replace('.db', '.json')
            if os.path.exists(json_file):
                os.remove(json_file)
                
    except Exception as e:
        print(f"Cleanup failed: {str(e)}")

def get_backup_list():
    """Get list of available backups with metadata"""
    try:
        ensure_backup_directory()
        backup_files = glob.glob(os.path.join(BACKUP_DIR, "backup_*.db"))
        backups = []

        for backup_file in sorted(backup_files, key=os.path.getctime, reverse=True):
            filename = os.path.basename(backup_file)
            # Parse filename: backup_YYYYMMDD_HHMMSS_reason.db
            parts = filename.replace('.db', '').split('_')
            if len(parts) >= 3:
                date_str = parts[1]
                time_str = parts[2]
                reason = '_'.join(parts[3:]) if len(parts) > 3 else 'manual'

                # Format display date
                try:
                    backup_datetime = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                    display_date = backup_datetime.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    display_date = "Unknown"

                backups.append({
                    'filename': filename,
                    'display_date': display_date,
                    'reason': reason,
                    'size': os.path.getsize(backup_file),
                    'path': backup_file
                })

        return backups
    except Exception as e:
        print(f"Failed to get backup list: {str(e)}")
        return []

def restore_backup(backup_filename):
    """Restore database from a backup file"""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return False, "Backup file not found"
        
        # Create a backup of current state before restoring
        create_backup("pre_restore")
        
        # Close database connections
        db.session.close()
        
        # Copy backup over current database
        db_path = 'instance/draft_game.db'
        shutil.copy2(backup_path, db_path)
        
        # Recreate database connection
        db.create_all()
        
        return True, f"Successfully restored from {backup_filename}"
        
    except Exception as e:
        return False, f"Restore failed: {str(e)}"

def require_admin_auth():
    """Check if user is authenticated as admin"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    return None

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            flash('Successfully logged in as admin!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid password!', 'error')
    
    game_state = GameState.query.first()
    return render_template('admin_login.html', game_state=game_state)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

def is_submissions_open(game_state):
    """Check if submissions are currently open based on game phase and deadline"""
    if game_state.phase != 'submission':
        return False
    
    if game_state.submission_deadline:
        now = datetime.now(pytz.UTC)
        # Ensure deadline is timezone-aware (stored as UTC in database)
        deadline = game_state.submission_deadline
        if deadline.tzinfo is None:
            deadline = pytz.UTC.localize(deadline)
        
        if now > deadline:
            return False
    
    return True

def get_deadline_info(game_state):
    """Get deadline information for display"""
    if not game_state.submission_deadline:
        return None, "No deadline set"
    
    et_tz = pytz.timezone('US/Eastern')
    deadline = game_state.submission_deadline
    
    # Ensure deadline is timezone-aware (stored as UTC in database)
    if deadline.tzinfo is None:
        deadline = pytz.UTC.localize(deadline)
    
    deadline_et = deadline.astimezone(et_tz)
    return deadline_et, deadline_et.strftime('%A, %B %d at %I:%M %p ET')

@app.route('/')
def index():
    # Check game state and initialization
    game_state = GameState.query.first()
    if not game_state:
        # Initialize game state
        game_state = GameState(phase='setup', is_initialized=False)
        db.session.add(game_state)
        db.session.commit()
    
    # If not initialized, show notice to use admin panel
    if not game_state.is_initialized:
        return render_template('not_initialized.html', game_state=game_state)
    
    # Check game phase redirects
    if game_state.phase == 'selecting':
        return redirect(url_for('draft_selection'))
    elif game_state.phase != 'submission':
        return redirect(url_for('results'))
    
    # Check if submissions are open
    submissions_open = is_submissions_open(game_state)
    deadline_dt, deadline_str = get_deadline_info(game_state)
    
    # Get current submissions for display
    players = Player.query.order_by(Player.timestamp.desc()).all()
    
    # Get league members for dropdown - exclude those who already submitted
    all_league_members = LeagueMember.query.filter_by(active=True).order_by(LeagueMember.name).all()
    submitted_names = {player.name for player in players}  # Set of names who already submitted
    league_members = [member for member in all_league_members if member.name not in submitted_names]
    
    return render_template('index.html', 
                         game_state=game_state, 
                         players=players, 
                         num_teams=game_state.num_teams,
                         league_name=game_state.league_name or 'Fantasy Football League',
                         league_members=league_members,
                         submissions_open=submissions_open,
                         deadline_str=deadline_str,
                         deadline_dt=deadline_dt)

@app.route('/snake-draft')
def snake_draft():
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState(phase='submission', num_teams=12)
        db.session.add(game_state)
        db.session.commit()
    
    return render_template('snake_draft.html', num_teams=game_state.num_teams, game_state=game_state)

@app.route('/submit', methods=['POST'])
def submit_guess():
    # Check game phase and deadline
    game_state = GameState.query.first()
    if not game_state or not is_submissions_open(game_state):
        flash('Submission period has ended!', 'error')
        return redirect(url_for('results'))
    
    name = request.form.get('name')
    email = request.form.get('email') or f"{name.lower().replace(' ', '.')}@placeholder.com"
    guess = request.form.get('guess')
    
    if not all([name, guess]):
        flash('Name and guess are required!', 'error')
        return redirect(url_for('index'))
    
    try:
        guess = int(guess)
        if guess < 0 or guess > 1000:
            flash('Guess must be between 0 and 1000!', 'error')
            return redirect(url_for('index'))
    except ValueError:
        flash('Please enter a valid number!', 'error')
        return redirect(url_for('index'))
    
    # Check if name already submitted (unless in dev mode)
    existing = Player.query.filter_by(name=name).first()
    if existing and not game_state.dev_mode:
        flash('This name has already submitted a guess!', 'error')
        return redirect(url_for('index'))
    
    # Get client IP address
    client_ip = get_client_ip()
    
    # Check for duplicate IP addresses (warn but allow)
    ip_submissions = Player.query.filter_by(ip_address=client_ip).all()
    if ip_submissions and not game_state.dev_mode:
        existing_names = [p.name for p in ip_submissions]
        flash(f'Note: Another submission from this IP address was already received from: {", ".join(existing_names)}', 'warning')
    
    # If dev mode and existing submission, update it instead of creating new
    if existing and game_state.dev_mode:
        existing.name = name
        existing.guess = guess
        existing.timestamp = datetime.now()
        existing.ip_address = client_ip
        player = existing
    else:
        player = Player(name=name, email=email, guess=guess, ip_address=client_ip)
        db.session.add(player)
    
    db.session.commit()
    
    # Create automatic backup after each submission
    create_backup("submission")
    
    # Redirect to confirmation page instead of index
    return redirect(url_for('submission_confirmed', player_id=player.id))

@app.route('/submission-confirmed/<int:player_id>')
def submission_confirmed(player_id):
    """Show submission confirmation page"""
    player = Player.query.get_or_404(player_id)
    game_state = GameState.query.first()
    total_submissions = Player.query.count()
    deadline_dt, deadline_str = get_deadline_info(game_state)
    
    # Get all players for current submissions display
    players = Player.query.order_by(Player.timestamp.desc()).all()
    
    return render_template('submission_confirmed.html',
                         player=player,
                         game_state=game_state,
                         players=players,
                         num_teams=game_state.num_teams if game_state else 12,
                         total_submissions=total_submissions,
                         deadline_str=deadline_str)

@app.route('/results')
def results():
    # Check if we should be in draft selection phase
    game_state = GameState.query.first()
    if game_state and game_state.phase == 'selecting':
        return redirect(url_for('draft_selection'))
    
    players = Player.query.all()
    
    if not players:
        return render_template('results.html', players=[], winner=None, target=None, game_state=game_state)
    
    # Calculate 2/3 of average
    guesses = [p.guess for p in players]
    average = statistics.mean(guesses)
    target = (2/3) * average
    
    # Find winner (closest to target)
    winner = min(players, key=lambda p: abs(p.guess - target))
    
    # Sort players by distance from target (best to worst)
    players_ranked = sorted(players, key=lambda p: abs(p.guess - target))
    
    # Check if draft positions have been selected
    draft_positions_selected = any(p.draft_position for p in players)
    draft_order = None
    if draft_positions_selected:
        # Get players with draft positions, sorted by position
        draft_order = sorted([p for p in players if p.draft_position], key=lambda p: p.draft_position)
    
    # Update game state
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState(phase='results', winner_id=winner.id, target_number=target, average_guess=average)
        db.session.add(game_state)
    else:
        game_state.phase = 'results'
        game_state.winner_id = winner.id
        game_state.target_number = target
        game_state.average_guess = average
    
    db.session.commit()
    
    return render_template('results.html', players=players_ranked, winner=winner, target=target, average=average, 
                         draft_order=draft_order, draft_positions_selected=draft_positions_selected, game_state=game_state)

@app.route('/admin')
def admin():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    players = Player.query.all()
    deleted_players = DeletedPlayer.query.order_by(DeletedPlayer.deleted_timestamp.desc()).all()
    game_state = GameState.query.first()
    
    if not game_state:
        game_state = GameState(phase='submission')
        db.session.add(game_state)
        db.session.commit()
    
    if players:
        guesses = [p.guess for p in players]
        average = statistics.mean(guesses) if guesses else 0
        target = (2/3) * average
    else:
        average = 0
        target = 0
    
    winner = None
    if game_state.winner_id:
        winner = Player.query.get(game_state.winner_id)
    
    # Create IP address count dictionary for highlighting duplicates
    ip_counts = {}
    for player in players:
        if player.ip_address:
            ip_counts[player.ip_address] = ip_counts.get(player.ip_address, 0) + 1
    
    # Get league members for display
    league_members = LeagueMember.query.filter_by(active=True).order_by(LeagueMember.name).all()
    
    return render_template('admin.html', 
                         players=players, 
                         deleted_players=deleted_players,
                         game_state=game_state, 
                         average=average, 
                         target=target,
                         winner=winner,
                         ip_counts=ip_counts,
                         league_members=league_members,
                         league_name=game_state.league_name or 'Fantasy Football League',
                         pytz=pytz)

@app.route('/admin/delete_submission/<int:player_id>', methods=['POST'])
def delete_submission(player_id):
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    player = Player.query.get_or_404(player_id)
    reason = request.form.get('reason', 'No reason provided')
    player_name = player.name  # Store name before deletion
    
    # Create a record in deleted players table
    deleted_player = DeletedPlayer(
        original_id=player.id,
        name=player.name,
        email=player.email,
        guess=player.guess,
        original_timestamp=player.timestamp,
        deleted_reason=reason,
        ip_address=player.ip_address
    )
    
    db.session.add(deleted_player)
    db.session.delete(player)
    db.session.commit()
    
    # Create backup after deletion
    create_backup("deletion")
    
    flash(f'Submission by {player_name} has been deleted. Reason: {reason}', 'warning')
    return redirect(url_for('admin'))

@app.route('/admin/advance_phase', methods=['POST'])
def advance_phase():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState(phase='submission')
        db.session.add(game_state)
    
    players = Player.query.all()
    
    if game_state.phase == 'submission':
        if players:
            # Calculate winner and advance to results
            guesses = [p.guess for p in players]
            average = statistics.mean(guesses)
            target = (2/3) * average
            
            # Find winner (closest to target)
            winner = min(players, key=lambda p: abs(p.guess - target))
            
            game_state.phase = 'results'
            game_state.winner_id = winner.id
            game_state.target_number = target
            game_state.average_guess = average
            flash(f'Advanced to results phase. Winner: {winner.name}', 'success')
        else:
            # No players submitted - advance anyway to draft selection
            game_state.phase = 'selecting'
            game_state.winner_id = None
            game_state.target_number = None
            game_state.average_guess = None
            flash('Advanced to draft selection phase (no submissions received)', 'warning')
        
    elif game_state.phase == 'results':
        # Advance to draft selection
        game_state.phase = 'selecting'
        flash('Advanced to draft selection phase', 'success')
        
    elif game_state.phase == 'selecting':
        # Reset game
        game_state.phase = 'submission'
        game_state.winner_id = None
        game_state.target_number = None
        game_state.average_guess = None
        # Clear all players for new game
        Player.query.delete()
        flash('Game reset to submission phase', 'success')
        
    elif game_state.phase == 'completed':
        # Reset game
        game_state.phase = 'submission'
        game_state.winner_id = None
        game_state.target_number = None
        game_state.average_guess = None
        # Clear all players for new game
        Player.query.delete()
        flash('Game reset for new round', 'success')
    
    db.session.commit()
    
    # Create backup after phase advancement
    create_backup("phase_advance")
    
    return redirect(url_for('admin'))

@app.route('/admin/reset_to_setup', methods=['POST'])
def admin_reset_to_setup():
    """Reset game to setup phase (admin only)"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
    
    # Reset to setup phase
    game_state.phase = 'setup'
    game_state.is_initialized = False
    game_state.winner_id = None
    game_state.target_number = None
    game_state.average_guess = None
    
    # Clear all players for new game
    Player.query.delete()
    
    db.session.commit()
    flash('Game reset to setup phase', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reset_game', methods=['POST'])
def reset_game():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    # Clear all data and start fresh
    Player.query.delete()
    DeletedPlayer.query.delete()
    GameState.query.delete()
    
    # Create fresh game state
    game_state = GameState(phase='submission')
    db.session.add(game_state)
    db.session.commit()
    
    flash('Game completely reset!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/initialize_game', methods=['POST'])
def admin_initialize_game():
    """Initialize the game with all settings (admin only)"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState()
        db.session.add(game_state)
    
    # Get form data
    league_name = request.form.get('league_name', 'Fantasy Football League').strip()
    num_teams = request.form.get('num_teams', type=int)
    is_simulation = request.form.get('is_simulation') == 'on'
    dev_mode = request.form.get('dev_mode') == 'on'
    
    # Validate num_teams
    if not num_teams or num_teams < 2 or num_teams > 20:
        flash('Number of teams must be between 2 and 20!', 'error')
        return redirect(url_for('admin'))
    
    # Update game state
    game_state.league_name = league_name
    game_state.num_teams = num_teams
    game_state.is_simulation = is_simulation
    game_state.dev_mode = dev_mode
    game_state.is_initialized = True
    game_state.phase = 'submission'
    
    # Clear existing players first
    Player.query.delete()
    
    # If simulation mode, auto-generate players
    if is_simulation:
        # Generate dummy players with realistic fantasy football names
        dummy_names = [
            ("Mike Johnson", "mike.johnson@email.com"),
            ("Sarah Davis", "sarah.davis@gmail.com"),
            ("Alex Thompson", "alex.thompson@yahoo.com"),
            ("Jessica Wilson", "jessica.wilson@hotmail.com"),
            ("Ryan Martinez", "ryan.martinez@email.com"),
            ("Ashley Brown", "ashley.brown@gmail.com"),
            ("David Lee", "david.lee@yahoo.com"),
            ("Amanda Taylor", "amanda.taylor@email.com"),
            ("Chris Anderson", "chris.anderson@gmail.com"),
            ("Lauren Garcia", "lauren.garcia@hotmail.com"),
            ("Justin Miller", "justin.miller@email.com"),
            ("Nicole Rodriguez", "nicole.rodriguez@gmail.com"),
            ("Brandon White", "brandon.white@yahoo.com"),
            ("Stephanie Clark", "stephanie.clark@email.com"),
            ("Kevin Lopez", "kevin.lopez@gmail.com"),
            ("Emily Carter", "emily.carter@email.com"),
            ("Tyler Moore", "tyler.moore@gmail.com"),
            ("Rachel Green", "rachel.green@yahoo.com"),
            ("Jason Scott", "jason.scott@hotmail.com"),
            ("Megan Turner", "megan.turner@email.com"),
            ("Derek Hall", "derek.hall@gmail.com"),
            ("Brittany Adams", "brittany.adams@yahoo.com"),
            ("Sean Parker", "sean.parker@email.com"),
            ("Vanessa King", "vanessa.king@gmail.com"),
            ("Logan Wright", "logan.wright@hotmail.com"),
            ("Kayla Mitchell", "kayla.mitchell@email.com"),
            ("Trevor Phillips", "trevor.phillips@gmail.com"),
            ("Samantha Young", "samantha.young@yahoo.com"),
            ("Marcus Allen", "marcus.allen@email.com"),
            ("Natalie Brooks", "natalie.brooks@gmail.com")
        ]
        
        import random
        
        # Add the specified number of players
        for i in range(min(num_teams, len(dummy_names))):
            name, email = dummy_names[i]
            # Generate strategic guesses (most people guess 200-400 in these games)
            guess = random.randint(150, 500)
            
            player = Player(name=name, email=email, guess=guess)
            db.session.add(player)
        
        # If more players requested than dummy names available, generate extras
        if num_teams > len(dummy_names):
            for i in range(len(dummy_names), num_teams):
                name = f"Player {i + 1}"
                email = f"player{i + 1}@testleague.com"
                guess = random.randint(150, 500)
                
                player = Player(name=name, email=email, guess=guess)
                db.session.add(player)
    
    # Handle submission deadline
    deadline_date = request.form.get('deadline_date')
    deadline_time = request.form.get('deadline_time')
    
    if deadline_date and deadline_time:
        import datetime
        import pytz
        
        # Parse the date and time
        deadline_datetime = datetime.datetime.strptime(f"{deadline_date} {deadline_time}", "%Y-%m-%d %H:%M")
        
        # Convert to ET timezone
        et_tz = pytz.timezone('US/Eastern')
        deadline_datetime = et_tz.localize(deadline_datetime)
        
        # Convert to UTC for storage
        utc_tz = pytz.UTC
        deadline_datetime_utc = deadline_datetime.astimezone(utc_tz)
        
        game_state.submission_deadline = deadline_datetime_utc
    
    db.session.commit()
    create_backup(f"Game initialized: {league_name}")
    
    mode_text = "simulation" if is_simulation else "real draft"
    players_text = f" with {num_teams} dummy players" if is_simulation else ""
    deadline_text = f" (deadline: {deadline_date} {deadline_time} ET)" if deadline_date and deadline_time else ""
    flash(f'Game initialized successfully for {league_name} ({mode_text}, {num_teams} teams){players_text}{deadline_text}!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/toggle_simulation_mode', methods=['POST'])
def admin_toggle_simulation_mode():
    """Toggle simulation mode (admin only)"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state:
        flash('No game state found', 'error')
        return redirect(url_for('admin'))
    
    # Toggle simulation mode
    game_state.is_simulation = not game_state.is_simulation
    db.session.commit()
    
    mode_text = "simulation" if game_state.is_simulation else "real draft"
    flash(f'Game mode changed to {mode_text}', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/toggle_dev_mode', methods=['POST'])
def toggle_dev_mode():
    """Toggle development mode on/off"""
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState(phase='submission', dev_mode=False)
        db.session.add(game_state)
    else:
        game_state.dev_mode = not game_state.dev_mode
    
    db.session.commit()
    create_backup(f"Toggled dev mode {'ON' if game_state.dev_mode else 'OFF'}")
    
    mode_status = "enabled" if game_state.dev_mode else "disabled"
    flash(f'Development mode {mode_status}!', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/update_league_name', methods=['POST'])
def update_league_name():
    """Update the league name"""
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    league_name = request.form.get('league_name', '').strip()
    
    if not league_name:
        flash('League name cannot be empty', 'error')
        return redirect(url_for('admin'))
    
    if len(league_name) > 100:
        flash('League name must be 100 characters or less', 'error')
        return redirect(url_for('admin'))
    
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState(phase='submission', league_name=league_name)
        db.session.add(game_state)
    else:
        game_state.league_name = league_name
    
    db.session.commit()
    create_backup(f"Updated league name to '{league_name}'")
    flash(f'League name updated to "{league_name}"', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/upload_league_members', methods=['POST'])
def upload_league_members():
    """Upload CSV file with league member names"""
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    if 'csv_file' not in request.files:
        flash('No file uploaded!', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('admin'))
    
    if not file.filename.lower().endswith('.csv'):
        flash('Please upload a CSV file!', 'error')
        return redirect(url_for('admin'))
    
    try:
        import csv
        import io
        
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        # Check if 'name' column exists
        if 'name' not in csv_input.fieldnames:
            flash('CSV file must have a "name" column!', 'error')
            return redirect(url_for('admin'))
        
        # Clear existing league members
        LeagueMember.query.delete()
        
        # Add new league members
        added_count = 0
        for row in csv_input:
            name = row['name'].strip()
            if name:  # Skip empty names
                # Check for duplicates
                existing = LeagueMember.query.filter_by(name=name).first()
                if not existing:
                    member = LeagueMember(name=name)
                    db.session.add(member)
                    added_count += 1
        
        db.session.commit()
        create_backup(f"Uploaded {added_count} league members")
        flash(f'Successfully uploaded {added_count} league member names!', 'success')
        
    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/clear_league_members', methods=['POST'])
def clear_league_members():
    """Clear all league member names"""
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    count = LeagueMember.query.count()
    LeagueMember.query.delete()
    db.session.commit()
    
    create_backup(f"Cleared {count} league members")
    flash(f'Cleared {count} league member names', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/add_player', methods=['POST'])
def add_player_to_draft():
    """Add a player directly to draft selection phase (for late arrivals)"""
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state or game_state.phase not in ['selecting', 'results']:
        flash('Can only add players during draft selection phase', 'error')
        return redirect(url_for('admin'))
    
    name = request.form.get('player_name', '').strip()
    email = request.form.get('player_email', '').strip()
    
    if not name or not email:
        flash('Both name and email are required', 'error')
        return redirect(url_for('admin'))
    
    # Check if player already exists
    existing_player = Player.query.filter_by(email=email).first()
    if existing_player:
        flash(f'Player with email {email} already exists', 'error')
        return redirect(url_for('admin'))
    
    # Add player with no guess (since they missed submission phase)
    new_player = Player(name=name, email=email, guess=None)
    db.session.add(new_player)
    db.session.commit()
    
    flash(f'Added {name} to draft selection', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/simulate', methods=['POST'])
def simulate_game():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    if not game_state:
        flash('Game must be initialized first', 'error')
        return redirect(url_for('admin'))
    
    # Use the game's configured number of teams
    num_players = game_state.num_teams
    
    # Clear existing players
    Player.query.delete()
    DeletedPlayer.query.delete()
    
    # Reset game state to submission phase
    game_state.phase = 'submission'
    game_state.winner_id = None
    game_state.target_number = None
    game_state.average_guess = None
    
    # Generate dummy players with realistic fantasy football names
    dummy_names = [
        ("Mike Johnson", "mike.johnson@email.com"),
        ("Sarah Davis", "sarah.davis@gmail.com"),
        ("Alex Thompson", "alex.thompson@yahoo.com"),
        ("Jessica Wilson", "jessica.wilson@hotmail.com"),
        ("Ryan Martinez", "ryan.martinez@email.com"),
        ("Ashley Brown", "ashley.brown@gmail.com"),
        ("David Lee", "david.lee@yahoo.com"),
        ("Amanda Taylor", "amanda.taylor@email.com"),
        ("Chris Anderson", "chris.anderson@gmail.com"),
        ("Lauren Garcia", "lauren.garcia@hotmail.com"),
        ("Justin Miller", "justin.miller@email.com"),
        ("Nicole Rodriguez", "nicole.rodriguez@gmail.com"),
        ("Brandon White", "brandon.white@yahoo.com"),
        ("Stephanie Clark", "stephanie.clark@email.com"),
        ("Kevin Lopez", "kevin.lopez@gmail.com"),
        ("Emily Carter", "emily.carter@email.com"),
        ("Tyler Moore", "tyler.moore@gmail.com"),
        ("Rachel Green", "rachel.green@yahoo.com"),
        ("Jason Scott", "jason.scott@hotmail.com"),
        ("Megan Turner", "megan.turner@email.com"),
        ("Derek Hall", "derek.hall@gmail.com"),
        ("Brittany Adams", "brittany.adams@yahoo.com"),
        ("Sean Parker", "sean.parker@email.com"),
        ("Vanessa King", "vanessa.king@gmail.com"),
        ("Logan Wright", "logan.wright@hotmail.com"),
        ("Kayla Mitchell", "kayla.mitchell@email.com"),
        ("Trevor Phillips", "trevor.phillips@gmail.com"),
        ("Samantha Young", "samantha.young@yahoo.com"),
        ("Marcus Allen", "marcus.allen@email.com"),
        ("Natalie Brooks", "natalie.brooks@gmail.com")
    ]
    
    import random
    
    # Add the specified number of players
    for i in range(min(num_players, len(dummy_names))):
        name, email = dummy_names[i]
        # Generate strategic guesses (most people guess 200-400 in these games)
        guess = random.randint(150, 500)
        
        player = Player(name=name, email=email, guess=guess)
        db.session.add(player)
    
    # If more players requested than dummy names available, generate extras
    if num_players > len(dummy_names):
        for i in range(len(dummy_names), num_players):
            name = f"Player {i + 1}"
            email = f"player{i + 1}@testleague.com"
            guess = random.randint(150, 500)
            
            player = Player(name=name, email=email, guess=guess)
            db.session.add(player)
    
    db.session.commit()
    
    flash(f'Simulation created with {num_players} dummy players!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/quick_test', methods=['POST'])
def quick_test():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    # Clear existing data
    Player.query.delete()
    DeletedPlayer.query.delete()
    GameState.query.delete()
    
    # Create game state in results phase with pre-calculated winner
    import random
    
    # Create 5 players with strategic guesses
    players_data = [
        ("Alice", "alice@test.com", 300),
        ("Bob", "bob@test.com", 250),
        ("Charlie", "charlie@test.com", 400),
        ("Diana", "diana@test.com", 350),
        ("Eve", "eve@test.com", 200)
    ]
    
    for name, email, guess in players_data:
        player = Player(name=name, email=email, guess=guess)
        db.session.add(player)
    
    # Calculate winner
    guesses = [p[2] for p in players_data]
    average = statistics.mean(guesses)  # 300
    target = (2/3) * average  # 200
    
    # Find winner (Eve with guess=200 is closest to target=200)
    winner_player = Player.query.filter_by(email="eve@test.com").first()
    if not winner_player:
        db.session.commit()
        winner_player = Player.query.filter_by(email="eve@test.com").first()
    
    game_state = GameState(phase='results', winner_id=winner_player.id, target_number=target, average_guess=average)
    db.session.add(game_state)
    db.session.commit()
    
    flash('Quick test scenario created! Eve should be the winner.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/backup', methods=['POST'])
def create_manual_backup():
    """Create a manual backup"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    backup_filename = create_backup("manual")
    if backup_filename:
        flash(f'Backup created: {backup_filename}', 'success')
    else:
        flash('Failed to create backup', 'error')
    return redirect(url_for('admin'))

@app.route('/admin/backups')
def list_backups():
    """Show backup management page"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    game_state = GameState.query.first()
    backups = get_backup_list()
    return render_template('admin_backups.html', backups=backups, game_state=game_state)

@app.route('/admin/restore/<backup_filename>', methods=['POST'])
def restore_from_backup(backup_filename):
    """Restore from a specific backup"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    success, message = restore_backup(backup_filename)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete_backup/<backup_filename>', methods=['POST'])
def delete_backup_file(backup_filename):
    """Delete a specific backup file"""
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        json_path = backup_path.replace('.db', '.json')
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
        if os.path.exists(json_path):
            os.remove(json_path)
            
        flash(f'Backup {backup_filename} deleted', 'success')
    except Exception as e:
        flash(f'Failed to delete backup: {str(e)}', 'error')
    
    return redirect(url_for('list_backups'))

@app.route('/draft_selection')
def draft_selection():
    """Show draft position selection interface"""
    game_state = GameState.query.first()
    if not game_state or game_state.phase != 'selecting':
        flash('Game not in selection phase', 'error')
        return redirect(url_for('index'))
    
    players = Player.query.all()
    if not players:
        flash('No players found', 'error')
        return redirect(url_for('index'))
    
    # Get winner and selection order
    winner = Player.query.get(game_state.winner_id) if game_state.winner_id else None
    
    # Sort players by distance from target (winner first, then by proximity)
    target = game_state.target_number
    selection_order = sorted(players, key=lambda p: abs(p.guess - target))
    
    # Get taken positions
    taken_positions = {p.draft_position: p.name for p in players if p.draft_position}
    
    # Find current picker (first without draft position)
    current_picker = None
    current_picker_index = 0
    for i, player in enumerate(selection_order):
        if not player.draft_position:
            current_picker = player
            current_picker_index = i
            break
    
    # Check if all selected
    all_selected = all(p.draft_position for p in players)
    
    return render_template('draft_selection.html',
                         game_state=game_state,
                         players=players,
                         winner=winner,
                         target=target,
                         average=game_state.average_guess,
                         selection_order=selection_order,
                         taken_positions=taken_positions,
                         current_picker=current_picker,
                         current_picker_index=current_picker_index,
                         total_players=len(players),
                         all_selected=all_selected)

@app.route('/select_draft_position', methods=['POST'])
def select_draft_position():
    """Handle draft position selection"""
    game_state = GameState.query.first()
    if not game_state or game_state.phase != 'selecting':
        flash('Game not in selection phase', 'error')
        return redirect(url_for('index'))
    
    player_id = request.form.get('player_id')
    position = request.form.get('position')
    
    if not player_id or not position:
        flash('Missing player or position', 'error')
        return redirect(url_for('draft_selection'))
    
    try:
        player = Player.query.get(int(player_id))
        position = int(position)
        
        if not player:
            flash('Player not found', 'error')
            return redirect(url_for('draft_selection'))
        
        # Check if position is already taken
        existing = Player.query.filter_by(draft_position=position).first()
        if existing:
            flash(f'Position {position} already taken by {existing.name}', 'error')
            return redirect(url_for('draft_selection'))
        
        # Check if player already selected
        if player.draft_position:
            flash(f'{player.name} already selected position {player.draft_position}', 'error')
            return redirect(url_for('draft_selection'))
        
        # Verify it's this player's turn
        players = Player.query.all()
        target = game_state.target_number
        selection_order = sorted(players, key=lambda p: abs(p.guess - target))
        
        current_picker = None
        for p in selection_order:
            if not p.draft_position:
                current_picker = p
                break
        
        if not current_picker or current_picker.id != player.id:
            flash('Not your turn to pick', 'error')
            return redirect(url_for('draft_selection'))
        
        # Make the selection
        player.draft_position = position
        db.session.commit()
        
        # Create backup after draft position selection
        create_backup("draft_selection")
        
        flash(f'{player.name} selected draft position {position}', 'success')
        
        # Check if all positions selected
        all_selected = all(p.draft_position for p in players)
        if all_selected:
            game_state.phase = 'completed'
            db.session.commit()
            # Create backup when draft is completed
            create_backup("draft_completed")
            flash('Draft order complete!', 'success')
        
        return redirect(url_for('draft_selection'))
        
    except (ValueError, TypeError):
        flash('Invalid player or position', 'error')
        return redirect(url_for('draft_selection'))

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            print("Database initialized successfully")
        print("Starting Flask app...")
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f"Error starting app: {e}")
        raise