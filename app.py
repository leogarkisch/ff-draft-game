from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import pytz
import statistics
import os

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

class GameState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(20), default='submission')  # submission, results, selecting, completed
    winner_id = db.Column(db.Integer)
    target_number = db.Column(db.Float)
    average_guess = db.Column(db.Float)

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
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    # Check game phase instead of deadline
    game_state = GameState.query.first()
    if not game_state:
        # Initialize game state
        game_state = GameState(phase='submission')
        db.session.add(game_state)
        db.session.commit()
    
    if game_state.phase != 'submission':
        return redirect(url_for('results'))
    
    # Get current submissions for display
    players = Player.query.order_by(Player.timestamp.desc()).all()
    
    return render_template('index.html', game_state=game_state, players=players)

@app.route('/submit', methods=['POST'])
def submit_guess():
    # Check game phase instead of deadline
    game_state = GameState.query.first()
    if not game_state or game_state.phase != 'submission':
        flash('Submission period has ended!', 'error')
        return redirect(url_for('results'))
    
    name = request.form.get('name')
    email = request.form.get('email')
    guess = request.form.get('guess')
    
    if not all([name, email, guess]):
        flash('All fields are required!', 'error')
        return redirect(url_for('index'))
    
    try:
        guess = int(guess)
        if guess < 0 or guess > 1000:
            flash('Guess must be between 0 and 1000!', 'error')
            return redirect(url_for('index'))
    except ValueError:
        flash('Please enter a valid number!', 'error')
        return redirect(url_for('index'))
    
    # Check if email already submitted
    existing = Player.query.filter_by(email=email).first()
    if existing:
        flash('This email has already submitted a guess!', 'error')
        return redirect(url_for('index'))
    
    player = Player(name=name, email=email, guess=guess)
    db.session.add(player)
    db.session.commit()
    
    flash('Your guess has been submitted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/results')
def results():
    players = Player.query.all()
    
    if not players:
        return render_template('results.html', players=[], winner=None, target=None)
    
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
                         draft_order=draft_order, draft_positions_selected=draft_positions_selected)

@app.route('/admin')
def admin():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    players = Player.query.all()
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
    
    return render_template('admin.html', 
                         players=players, 
                         game_state=game_state, 
                         average=average, 
                         target=target,
                         winner=winner)

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
    
    if game_state.phase == 'submission' and players:
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
    return redirect(url_for('admin'))

@app.route('/admin/reset_game', methods=['POST'])
def reset_game():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    # Clear all data and start fresh
    Player.query.delete()
    GameState.query.delete()
    
    # Create fresh game state
    game_state = GameState(phase='submission')
    db.session.add(game_state)
    db.session.commit()
    
    flash('Game completely reset!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/simulate', methods=['POST'])
def simulate_game():
    # Check authentication first
    auth_redirect = require_admin_auth()
    if auth_redirect:
        return auth_redirect
    
    num_players = int(request.form.get('num_players', 8))
    
    # Clear existing data
    Player.query.delete()
    GameState.query.delete()
    
    # Create fresh game state
    game_state = GameState(phase='submission')
    db.session.add(game_state)
    
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
        
        flash(f'{player.name} selected draft position {position}', 'success')
        
        # Check if all positions selected
        all_selected = all(p.draft_position for p in players)
        if all_selected:
            game_state.phase = 'completed'
            db.session.commit()
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