"""
Database configuration for the CV-to-Job Matching System.
This module provides database functionality for storing uploaded CVs and analysis results.
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database handler for the CV-to-Job Matching System."""
    
    def __init__(self, db_path=None):
        """Initialize the database connection.
        
        Args:
            db_path (str, optional): Path to the SQLite database file.
                If None, uses the default path or environment variable.
        """
        if db_path is None:
            db_path = os.environ.get('DATABASE_URL', 'cv_analyzer.db')
            
        # For SQLite, ensure the directory exists
        if db_path != ':memory:' and not db_path.startswith('postgresql://'):
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            
        self.db_path = db_path
        self.connection = None
        self._initialize_db()
    
    def _get_connection(self):
        """Get a database connection.
        
        Returns:
            sqlite3.Connection: Database connection object.
        """
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                logger.error(f"Database connection error: {e}")
                raise
        return self.connection
    
    def _initialize_db(self):
        """Initialize the database schema if it doesn't exist."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create analyses table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                cv_filename TEXT NOT NULL,
                job_title TEXT,
                match_percentage REAL,
                feedback_report TEXT,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Create users table for future authentication
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def save_analysis(self, cv_filename, job_title, match_percentage, feedback_report):
        """Save analysis results to the database.
        
        Args:
            cv_filename (str): Name of the CV file.
            job_title (str): Job title from the job description.
            match_percentage (float): Overall match percentage.
            feedback_report (dict): Feedback report generated by the system.
            
        Returns:
            str: ID of the saved analysis.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            analysis_id = str(uuid.uuid4())
            created_at = datetime.now().isoformat()
            
            cursor.execute(
                '''
                INSERT INTO analyses (id, cv_filename, job_title, match_percentage, feedback_report, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (analysis_id, cv_filename, job_title, match_percentage, json.dumps(feedback_report), created_at)
            )
            
            conn.commit()
            logger.info(f"Analysis saved with ID: {analysis_id}")
            return analysis_id
        except sqlite3.Error as e:
            logger.error(f"Error saving analysis: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def get_analysis(self, analysis_id):
        """Retrieve analysis results from the database.
        
        Args:
            analysis_id (str): ID of the analysis to retrieve.
            
        Returns:
            dict: Analysis data or None if not found.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM analyses WHERE id = ?',
                (analysis_id,)
            )
            
            row = cursor.fetchone()
            if row:
                analysis = dict(row)
                analysis['feedback_report'] = json.loads(analysis['feedback_report'])
                return analysis
            return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving analysis: {e}")
            return None
    
    def get_recent_analyses(self, limit=10):
        """Retrieve recent analyses from the database.
        
        Args:
            limit (int, optional): Maximum number of analyses to retrieve.
            
        Returns:
            list: List of recent analyses.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                SELECT id, cv_filename, job_title, match_percentage, created_at
                FROM analyses
                ORDER BY created_at DESC
                LIMIT ?
                ''',
                (limit,)
            )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving recent analyses: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")

# Singleton instance
_db_instance = None

def get_db():
    """Get the database instance.
    
    Returns:
        Database: Database instance.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
