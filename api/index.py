import os
import sys
from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras

# Add the script directory to the Python path to import templates
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'script'))

app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(__file__), '..', 'script', 'templates'),
           static_folder=os.path.join(os.path.dirname(__file__), '..', 'script', 'static'))

# Database configuration
DEFAULT_DB_URL = os.getenv("CRDB_URL") or "postgresql://smriti:14IoOzwofyHsi1RhXlnC2g@transaction-flow-16380.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=require"
DEFAULT_TABLE = os.getenv("CRDB_TABLE") or "public.merkle"

def connect(db_url: str):
    """Connect to CockroachDB"""
    conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.set_session(autocommit=True)
    return conn

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
    return render_template('index.html')

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

# This is the entry point for Vercel
def handler(request):
    return app(request.environ, lambda *args: None)