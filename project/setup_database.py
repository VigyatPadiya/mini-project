import mysql.connector
import bcrypt

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Your MySQL password (XAMPP default is empty)
}

def create_database():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS youtube_downloader")
        print("Database 'youtube_downloader' created or already exists")
        
        # Use the database
        cursor.execute("USE youtube_downloader")
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Table 'users' created or already exists")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                video_title VARCHAR(255) NOT NULL,
                video_url TEXT NOT NULL,
                quality VARCHAR(20) NOT NULL,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("Table 'downloads' created or already exists")
        
        # Check if default users exist
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
        if cursor.fetchone()[0] == 0:
            # Create default admin
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)", 
                          ('admin', admin_password.decode('utf-8'), True))
            print("Admin user created - username: admin, password: admin123")
            
            # Create a test user
            user_password = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                          ('user', user_password.decode('utf-8')))
            print("Test user created - username: user, password: user123")
        
        conn.commit()
        print("Database setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    create_database()