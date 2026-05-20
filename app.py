from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
app = Flask(__name__); app.secret_key='cs104-esports-demo'; DB_PATH=Path(__file__).with_name('database.db')
def get_db():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; conn.execute('PRAGMA foreign_keys=ON'); return conn
def q(sql,args=(),one=False):
    with get_db() as conn:
        rows=conn.execute(sql,args).fetchall(); return (rows[0] if rows else None) if one else rows
def ex(sql,args=()):
    with get_db() as conn: conn.execute(sql,args); conn.commit()
@app.route('/')
def dashboard():
    stats={k:q(f'SELECT COUNT(*) c FROM {k}',one=True)['c'] for k in ['teams','players','tournaments','matches']}
    recent_matches=q('''SELECT m.match_id,t.team_name,tr.tournament_name,m.opponent_team,m.match_date,m.our_score,m.opponent_score,m.result FROM matches m JOIN teams t ON m.team_id=t.team_id JOIN tournaments tr ON m.tournament_id=tr.tournament_id ORDER BY m.match_date DESC LIMIT 8''')
    roster=q('''SELECT p.player_id,p.gamer_tag,p.real_name,p.role,p.rank_level,t.team_name FROM players p JOIN teams t ON p.team_id=t.team_id ORDER BY t.team_name,p.role LIMIT 12''')
    team_wins=q('''SELECT t.team_name,SUM(CASE WHEN m.result='Win' THEN 1 ELSE 0 END) wins,COUNT(m.match_id) total FROM teams t LEFT JOIN matches m ON t.team_id=m.team_id GROUP BY t.team_id ORDER BY wins DESC''')
    return render_template('dashboard.html',stats=stats,recent_matches=recent_matches,roster=roster,team_wins=team_wins,active='dashboard')
@app.route('/players')
def players():
    rows=q('SELECT p.*,t.team_name FROM players p JOIN teams t ON p.team_id=t.team_id ORDER BY p.player_id DESC'); teams=q('SELECT * FROM teams ORDER BY team_name')
    return render_template('players.html',rows=rows,teams=teams,edit=None,active='players')
@app.route('/players/create',methods=['POST'])
def create_player():
    ex('INSERT INTO players(team_id,gamer_tag,real_name,role,rank_level,join_date,status) VALUES(?,?,?,?,?,?,?)',tuple(request.form[f] for f in ['team_id','gamer_tag','real_name','role','rank_level','join_date','status'])); flash('เพิ่มนักแข่งเรียบร้อย'); return redirect(url_for('players'))
@app.route('/players/<int:id>/edit')
def edit_player(id):
    rows=q('SELECT p.*,t.team_name FROM players p JOIN teams t ON p.team_id=t.team_id ORDER BY p.player_id DESC'); teams=q('SELECT * FROM teams ORDER BY team_name'); edit=q('SELECT * FROM players WHERE player_id=?',(id,),True)
    return render_template('players.html',rows=rows,teams=teams,edit=edit,active='players')
@app.route('/players/<int:id>/update',methods=['POST'])
def update_player(id):
    ex('UPDATE players SET team_id=?,gamer_tag=?,real_name=?,role=?,rank_level=?,join_date=?,status=? WHERE player_id=?',tuple(request.form[f] for f in ['team_id','gamer_tag','real_name','role','rank_level','join_date','status'])+(id,)); flash('แก้ไขข้อมูลนักแข่งเรียบร้อย'); return redirect(url_for('players'))
@app.route('/players/<int:id>/delete',methods=['POST'])
def delete_player(id): ex('DELETE FROM players WHERE player_id=?',(id,)); flash('ลบข้อมูลนักแข่งเรียบร้อย'); return redirect(url_for('players'))
@app.route('/teams')
def teams(): return render_template('simple_crud.html',title='จัดการทีม',table='teams',pk='team_id',fields=['team_name','game_title','coach_name','founded_date','region'],rows=q('SELECT * FROM teams ORDER BY team_id DESC'),active='teams')
@app.route('/teams/create',methods=['POST'])
def teams_create(): ex('INSERT INTO teams(team_name,game_title,coach_name,founded_date,region) VALUES(?,?,?,?,?)',tuple(request.form[f] for f in ['team_name','game_title','coach_name','founded_date','region'])); flash('บันทึกทีมเรียบร้อย'); return redirect(url_for('teams'))
@app.route('/teams/<int:id>/delete',methods=['POST'])
def teams_delete(id): ex('DELETE FROM teams WHERE team_id=?',(id,)); flash('ลบทีมเรียบร้อย'); return redirect(url_for('teams'))
@app.route('/gear')
def gear(): return render_template('gear.html',rows=q('SELECT g.*,p.gamer_tag FROM gear g JOIN players p ON g.player_id=p.player_id ORDER BY gear_id DESC'),players=q('SELECT player_id,gamer_tag FROM players ORDER BY gamer_tag'),active='gear')
@app.route('/gear/create',methods=['POST'])
def gear_create(): ex('INSERT INTO gear(player_id,gear_type,brand,model,serial_no,purchase_date) VALUES(?,?,?,?,?,?)',tuple(request.form[f] for f in ['player_id','gear_type','brand','model','serial_no','purchase_date'])); flash('เพิ่มอุปกรณ์เรียบร้อย'); return redirect(url_for('gear'))
@app.route('/gear/<int:id>/delete',methods=['POST'])
def gear_delete(id): ex('DELETE FROM gear WHERE gear_id=?',(id,)); flash('ลบอุปกรณ์เรียบร้อย'); return redirect(url_for('gear'))
@app.route('/tournaments')
def tournaments(): return render_template('simple_crud.html',title='จัดการรายการแข่งขัน',table='tournaments',pk='tournament_id',fields=['tournament_name','game_title','start_date','end_date','prize_pool','location'],rows=q('SELECT * FROM tournaments ORDER BY start_date DESC'),active='tournaments')
@app.route('/tournaments/create',methods=['POST'])
def tournaments_create(): ex('INSERT INTO tournaments(tournament_name,game_title,start_date,end_date,prize_pool,location) VALUES(?,?,?,?,?,?)',tuple(request.form[f] for f in ['tournament_name','game_title','start_date','end_date','prize_pool','location'])); flash('เพิ่มรายการแข่งขันเรียบร้อย'); return redirect(url_for('tournaments'))
@app.route('/tournaments/<int:id>/delete',methods=['POST'])
def tournaments_delete(id): ex('DELETE FROM tournaments WHERE tournament_id=?',(id,)); flash('ลบรายการแข่งขันเรียบร้อย'); return redirect(url_for('tournaments'))
@app.route('/matches')
def matches(): return render_template('matches.html',rows=q('SELECT m.*,t.team_name,tr.tournament_name FROM matches m JOIN teams t ON m.team_id=t.team_id JOIN tournaments tr ON m.tournament_id=tr.tournament_id ORDER BY match_date DESC'),teams=q('SELECT * FROM teams ORDER BY team_name'),tournaments=q('SELECT * FROM tournaments ORDER BY tournament_name'),active='matches')
@app.route('/matches/create',methods=['POST'])
def matches_create(): ex('INSERT INTO matches(team_id,tournament_id,opponent_team,match_date,our_score,opponent_score,result,note) VALUES(?,?,?,?,?,?,?,?)',tuple(request.form[f] for f in ['team_id','tournament_id','opponent_team','match_date','our_score','opponent_score','result','note'])); flash('เพิ่มผลการแข่งขันเรียบร้อย'); return redirect(url_for('matches'))
@app.route('/matches/<int:id>/delete',methods=['POST'])
def matches_delete(id): ex('DELETE FROM matches WHERE match_id=?',(id,)); flash('ลบผลการแข่งขันเรียบร้อย'); return redirect(url_for('matches'))
if __name__=='__main__': app.run(debug=True)
