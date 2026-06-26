from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db
from functools import wraps

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('user_role') not in roles:
                flash('Access denied.', 'error')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── Dashboard ──────────────────────────────────────────────
@main_bp.route('/')
@login_required
def dashboard():
    db = get_db()
    stats = {
        'total_resources': db.execute("SELECT COUNT(*) FROM resources WHERE status='available'").fetchone()[0],
        'pending_requests': db.execute("SELECT COUNT(*) FROM aid_requests WHERE status='pending'").fetchone()[0],
        'open_shelters': db.execute("SELECT COUNT(*) FROM shelters WHERE status='open'").fetchone()[0],
        'total_volunteers': db.execute("SELECT COUNT(*) FROM volunteers WHERE availability='available'").fetchone()[0],
    }
    recent_requests = db.execute(
        '''SELECT ar.*, u.name as requester_name FROM aid_requests ar
           JOIN users u ON ar.requester_id=u.id
           ORDER BY ar.created_at DESC LIMIT 5''').fetchall()
    critical_requests = db.execute(
        "SELECT COUNT(*) FROM aid_requests WHERE urgency='critical' AND status='pending'").fetchone()[0]
    return render_template('dashboard.html', stats=stats, recent_requests=recent_requests, critical=critical_requests)

# ── Resources ──────────────────────────────────────────────
@main_bp.route('/resources')
@login_required
def resources():
    db = get_db()
    rtype = request.args.get('type', '')
    status = request.args.get('status', '')
    query = '''SELECT r.*, u.name as registered_by_name FROM resources r
               LEFT JOIN users u ON r.registered_by=u.id WHERE 1=1'''
    params = []
    if rtype:
        query += ' AND r.type=?'; params.append(rtype)
    if status:
        query += ' AND r.status=?'; params.append(status)
    query += ' ORDER BY r.created_at DESC'
    items = db.execute(query, params).fetchall()
    return render_template('resources.html', resources=items, filter_type=rtype, filter_status=status)

@main_bp.route('/resources/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if session.get('user_role') == 'affected':
        flash('Only volunteers, NGOs, and authorities can register resources.', 'error')
        return redirect(url_for('main.resources'))
    if request.method == 'POST':
        db = get_db()
        db.execute('''INSERT INTO resources (name, type, quantity, unit, location, disaster_type, notes, registered_by)
                      VALUES (?,?,?,?,?,?,?,?)''',
                   (request.form['name'], request.form['type'], request.form['quantity'],
                    request.form['unit'], request.form['location'], request.form.get('disaster_type','general'),
                    request.form.get('notes',''), session['user_id']))
        db.commit()
        flash('Resource registered successfully.', 'success')
        return redirect(url_for('main.resources'))
    return render_template('add_resource.html')

@main_bp.route('/resources/<int:rid>/allocate', methods=['POST'])
@login_required
@role_required('authority', 'ngo')
def allocate_resource(rid):
    db = get_db()
    db.execute("UPDATE resources SET status='allocated' WHERE id=?", (rid,))
    db.commit()
    flash('Resource marked as allocated.', 'success')
    return redirect(url_for('main.resources'))

# ── Aid Requests ───────────────────────────────────────────
@main_bp.route('/requests')
@login_required
def aid_requests():
    db = get_db()
    if session['user_role'] == 'affected':
        items = db.execute(
            'SELECT * FROM aid_requests WHERE requester_id=? ORDER BY created_at DESC',
            (session['user_id'],)).fetchall()
    else:
        urgency = request.args.get('urgency', '')
        status = request.args.get('status', '')
        query = '''SELECT ar.*, u.name as requester_name FROM aid_requests ar
                   JOIN users u ON ar.requester_id=u.id WHERE 1=1'''
        params = []
        if urgency:
            query += ' AND ar.urgency=?'; params.append(urgency)
        if status:
            query += ' AND ar.status=?'; params.append(status)
        query += ' ORDER BY CASE ar.urgency WHEN "critical" THEN 1 WHEN "high" THEN 2 WHEN "medium" THEN 3 ELSE 4 END, ar.created_at DESC'
        items = db.execute(query, params).fetchall()
    return render_template('requests.html', requests=items)

@main_bp.route('/requests/new', methods=['GET', 'POST'])
@login_required
def new_request():
    if request.method == 'POST':
        db = get_db()
        db.execute('''INSERT INTO aid_requests (requester_id, resource_type, quantity_needed, urgency, location, description)
                      VALUES (?,?,?,?,?,?)''',
                   (session['user_id'], request.form['resource_type'], request.form['quantity'],
                    request.form['urgency'], request.form['location'], request.form.get('description', '')))
        db.commit()
        flash('Aid request submitted. Authorities have been notified.', 'success')
        return redirect(url_for('main.aid_requests'))
    return render_template('new_request.html')

@main_bp.route('/requests/<int:rid>/update', methods=['POST'])
@login_required
@role_required('authority', 'ngo')
def update_request(rid):
    new_status = request.form['status']
    db = get_db()
    db.execute('UPDATE aid_requests SET status=?, reviewed_by=? WHERE id=?',
               (new_status, session['user_id'], rid))
    db.commit()
    flash(f'Request {new_status}.', 'success')
    return redirect(url_for('main.aid_requests'))

# ── Shelters ───────────────────────────────────────────────
@main_bp.route('/shelters')
@login_required
def shelters():
    db = get_db()
    items = db.execute('SELECT * FROM shelters ORDER BY status, name').fetchall()
    return render_template('shelters.html', shelters=items)

@main_bp.route('/shelters/add', methods=['GET', 'POST'])
@login_required
@role_required('authority', 'ngo')
def add_shelter():
    if request.method == 'POST':
        db = get_db()
        db.execute('''INSERT INTO shelters (name, location, capacity, contact_name, contact_phone, facilities, managed_by)
                      VALUES (?,?,?,?,?,?,?)''',
                   (request.form['name'], request.form['location'], request.form['capacity'],
                    request.form['contact_name'], request.form['contact_phone'],
                    request.form.get('facilities', ''), session['user_id']))
        db.commit()
        flash('Shelter added successfully.', 'success')
        return redirect(url_for('main.shelters'))
    return render_template('add_shelter.html')

@main_bp.route('/shelters/<int:sid>/update', methods=['POST'])
@login_required
def update_shelter(sid):
    db = get_db()
    occupancy = int(request.form['occupancy'])
    shelter = db.execute('SELECT capacity FROM shelters WHERE id=?', (sid,)).fetchone()
    status = 'full' if occupancy >= shelter['capacity'] else 'open'
    db.execute('UPDATE shelters SET current_occupancy=?, status=? WHERE id=?', (occupancy, status, sid))
    db.commit()
    flash('Shelter updated.', 'success')
    return redirect(url_for('main.shelters'))

# ── Volunteers ─────────────────────────────────────────────
@main_bp.route('/volunteers')
@login_required
@role_required('authority', 'ngo')
def volunteers():
    db = get_db()
    items = db.execute(
        '''SELECT v.*, u.name, u.email, u.phone, u.location FROM volunteers v
           JOIN users u ON v.user_id=u.id ORDER BY v.availability, u.name''').fetchall()
    return render_template('volunteers.html', volunteers=items)

@main_bp.route('/volunteers/<int:vid>/assign', methods=['POST'])
@login_required
@role_required('authority', 'ngo')
def assign_volunteer(vid):
    db = get_db()
    db.execute('''UPDATE volunteers SET assigned_area=?, assigned_task=?, availability='assigned' WHERE id=?''',
               (request.form['area'], request.form['task'], vid))
    db.commit()
    flash('Volunteer assigned.', 'success')
    return redirect(url_for('main.volunteers'))
