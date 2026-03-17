from app.db.database import get_session

# For backward compatibility, export get_session as get_db
get_db = get_session