import json
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DATABASE_PATH


class MemoryAgent:
    """Conversation Memory Agent - Stores and retrieves client context."""

    def __init__(self):
        self.db_path = DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                name TEXT,
                language TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contact TIMESTAMP,
                lead_score TEXT,
                notes TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                key TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                platform TEXT DEFAULT 'instagram',
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                product TEXT,
                amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        """)

        conn.commit()
        conn.close()

    def _get_conn(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def save_client(self, client_id: str, name: str = None, language: str = None):
        """Create or update a client profile."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO clients (client_id, name, language, last_contact)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(client_id) DO UPDATE SET
                name = COALESCE(?, name),
                language = COALESCE(?, language),
                last_contact = ?
        """,
            (
                client_id,
                name,
                language,
                datetime.now(),
                name,
                language,
                datetime.now(),
            ),
        )

        conn.commit()
        conn.close()

    def get_client(self, client_id: str) -> dict:
        """Get client profile."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "client_id": row[0],
                "name": row[1],
                "language": row[2],
                "created_at": row[3],
                "last_contact": row[4],
                "lead_score": row[5],
                "notes": row[6],
            }
        return None

    def save_detail(self, client_id: str, key: str, value: str):
        """Save a specific detail about a client."""
        self.save_client(client_id)  # Ensure client exists

        conn = self._get_conn()
        cursor = conn.cursor()

        # Check if key exists, update or insert
        cursor.execute(
            """
            SELECT id FROM client_details
            WHERE client_id = ? AND key = ?
        """,
            (client_id, key),
        )

        if cursor.fetchone():
            cursor.execute(
                """
                UPDATE client_details SET value = ?, created_at = ?
                WHERE client_id = ? AND key = ?
            """,
                (value, datetime.now(), client_id, key),
            )
        else:
            cursor.execute(
                """
                INSERT INTO client_details (client_id, key, value)
                VALUES (?, ?, ?)
            """,
                (client_id, key, value),
            )

        conn.commit()
        conn.close()

    def get_detail(self, client_id: str, key: str) -> str:
        """Get a specific detail about a client."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT value FROM client_details
            WHERE client_id = ? AND key = ?
            ORDER BY created_at DESC LIMIT 1
        """,
            (client_id, key),
        )

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None

    def get_all_details(self, client_id: str) -> dict:
        """Get all stored details for a client."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT key, value FROM client_details
            WHERE client_id = ?
        """,
            (client_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        return {row[0]: row[1] for row in rows}

    def save_message(self, client_id: str, role: str, content: str, platform: str = "instagram"):
        """Save a conversation message."""
        self.save_client(client_id)

        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversations (client_id, role, content, platform)
            VALUES (?, ?, ?, ?)
        """,
            (client_id, role, content, platform),
        )

        conn.commit()
        conn.close()

    def get_history(self, client_id: str, limit: int = 20) -> list:
        """Get conversation history for a client."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT role, content, timestamp FROM conversations
            WHERE client_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """,
            (client_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        # Return in chronological order
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in reversed(rows)
        ]

    def get_context(self, client_id: str) -> dict:
        """Get full context for a client before responding."""
        client = self.get_client(client_id)
        details = self.get_all_details(client_id)
        history = self.get_history(client_id, limit=10)
        orders = self.get_orders(client_id)

        context = {
            "client": client,
            "details": details,
            "recent_history": history,
            "orders": orders,
            "summary": self._generate_context_summary(client, details, history, orders),
        }

        return context

    def _generate_context_summary(self, client, details, history, orders) -> str:
        """Generate a human-readable context summary."""
        parts = []

        if client:
            if client.get("name"):
                parts.append(f"Client: {client['name']}")
            if client.get("language"):
                parts.append(f"Language: {client['language']}")
            if client.get("lead_score"):
                parts.append(f"Lead score: {client['lead_score']}")

        if details:
            for key, value in details.items():
                parts.append(f"{key}: {value}")

        if orders:
            parts.append(f"Orders: {len(orders)} total")
            if orders:
                last_order = orders[0]
                parts.append(f"Last order: {last_order.get('product')} ({last_order.get('status')})")

        if history:
            parts.append(f"Conversation history: {len(history)} messages")

        return " | ".join(parts) if parts else "New client, no history"

    def save_order(self, client_id: str, product: str, amount: float, status: str = "pending"):
        """Save an order for a client."""
        self.save_client(client_id)

        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO orders (client_id, product, amount, status)
            VALUES (?, ?, ?, ?)
        """,
            (client_id, product, amount, status),
        )

        conn.commit()
        conn.close()

    def get_orders(self, client_id: str) -> list:
        """Get order history for a client."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT product, amount, status, created_at FROM orders
            WHERE client_id = ?
            ORDER BY created_at DESC
        """,
            (client_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "product": row[0],
                "amount": row[1],
                "status": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    def update_lead_score(self, client_id: str, score: str):
        """Update the lead score for a client."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE clients SET lead_score = ? WHERE client_id = ?
        """,
            (score, client_id),
        )

        conn.commit()
        conn.close()

    def search_clients(self, query: str) -> list:
        """Search clients by name or details."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT c.* FROM clients c
            LEFT JOIN client_details d ON c.client_id = d.client_id
            WHERE c.name LIKE ? OR c.client_id LIKE ? OR d.value LIKE ?
        """,
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "client_id": row[0],
                "name": row[1],
                "language": row[2],
                "last_contact": row[4],
                "lead_score": row[5],
            }
            for row in rows
        ]
