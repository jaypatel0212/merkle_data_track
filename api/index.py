import os
import sys
from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
           template_folder=os.path.join(BASE_DIR, 'script', 'templates'),
           static_folder=os.path.join(BASE_DIR, 'script', 'static'))

# Database configuration - use environment variables
DEFAULT_DB_URL = os.getenv("CRDB_URL")
DEFAULT_TABLE = os.getenv("CRDB_TABLE", "public.merkle")

if not DEFAULT_DB_URL:
    raise ValueError("CRDB_URL environment variable is required")

def connect(db_url: str):
    """Connect to CockroachDB"""
    try:
        conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.set_session(autocommit=True)
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

def query_rows(conn, table: str, creator: str, limit: int):
    """Query aggregated rows from the database"""
    sql = f"""
        SELECT
          to_address,
          SUM(value) as total_value,
          COUNT(*) as claim_count,
          creator
        FROM {table}
        WHERE lower(creator) = lower(%s)
        GROUP BY to_address, creator
        ORDER BY total_value DESC
        LIMIT %s
    """
    with conn.cursor() as cur:
        cur.execute(sql, (creator, limit))
        return cur.fetchall()

def count_rows(conn, table: str, creator: str) -> int:
    """Count total rows for a creator"""
    sql = f"SELECT count(1) AS cnt FROM {table} WHERE lower(creator) = lower(%s)"
    with conn.cursor() as cur:
        cur.execute(sql, (creator,))
        r = cur.fetchone()
        return int(r.get("cnt") if isinstance(r, dict) else r[0])

def get_unique_address_count(conn, table: str, creator: str) -> int:
    """Count unique addresses for a creator"""
    sql = f"SELECT COUNT(DISTINCT to_address) AS unique_cnt FROM {table} WHERE lower(creator) = lower(%s)"
    with conn.cursor() as cur:
        cur.execute(sql, (creator,))
        r = cur.fetchone()
        return int(r.get("unique_cnt") if isinstance(r, dict) else r[0])

def get_total_value_sum(conn, table: str, creator: str) -> float:
    """Get total value sum for a creator"""
    sql = f"SELECT SUM(value) AS total_sum FROM {table} WHERE lower(creator) = lower(%s)"
    with conn.cursor() as cur:
        cur.execute(sql, (creator,))
        r = cur.fetchone()
        return float(r.get("total_sum") if isinstance(r, dict) else r[0]) or 0.0

@app.route('/')
def index():
    """Main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template error: {str(e)}<br>Template folder: {app.template_folder}", 500

@app.route('/query', methods=['POST'])
def query_merkle():
    """Handle the query request"""
    try:
        data = request.get_json()
        creator = data.get('creator', '').strip()
        limit = int(data.get('limit', 50))
        
        if not creator:
            return jsonify({'error': 'Creator address is required'}), 400
        
        # Connect to database
        conn = connect(DEFAULT_DB_URL)
        
        try:
            # Get aggregated statistics
            total_claims = count_rows(conn, DEFAULT_TABLE, creator)
            unique_addresses = get_unique_address_count(conn, DEFAULT_TABLE, creator)
            total_value_sum = get_total_value_sum(conn, DEFAULT_TABLE, creator)
            rows = query_rows(conn, DEFAULT_TABLE, creator, limit)
            
            # Convert rows to list of dictionaries for JSON response
            result_rows = []
            for row in rows:
                result_rows.append({
                    'to_address': str(row.get('to_address', '')).strip(),
                    'total_value': float(row.get('total_value', 0)),
                    'claim_count': int(row.get('claim_count', 0)),
                    'creator': str(row.get('creator', '')).strip()
                })
            
            return jsonify({
                'success': True,
                'creator': creator,
                'total_claims': total_claims,
                'unique_addresses': unique_addresses,
                'total_value_sum': total_value_sum,
                'preview_rows': len(result_rows),
                'data': result_rows
            })
            
        except Exception as e:
            return jsonify({'error': f'Query failed: {str(e)}'}), 500
        finally:
            try:
                conn.close()
            except Exception:
                pass
                
    except Exception as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'template_folder': app.template_folder})