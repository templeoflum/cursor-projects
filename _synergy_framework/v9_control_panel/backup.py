import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.backup_dir = self.base_dir / "backups"
        self.backup_log = self.backup_dir / "backup_log.json"
        self.scripts = [
            "01_build.py",
            "02_connect.py",
            "03_focus.py",
            "04_participate.py",
            "05_manage.py"
        ]
        self._initialize_backup_dir()

    def _initialize_backup_dir(self):
        """Create backup directory and log file if they don't exist"""
        self.backup_dir.mkdir(exist_ok=True)
        if not self.backup_log.exists():
            self._save_log({})

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _load_log(self) -> Dict:
        """Load the backup log"""
        try:
            with open(self.backup_log) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load backup log: {e}")
            return {}

    def _save_log(self, log_data: Dict):
        """Save the backup log"""
        try:
            with open(self.backup_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save backup log: {e}")

    def create_backup(self, note: Optional[str] = None) -> bool:
        """Create a backup of all scripts"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_info = {
                "timestamp": timestamp,
                "note": note,
                "files": {}
            }

            # Create timestamp directory
            backup_path = self.backup_dir / timestamp
            backup_path.mkdir(exist_ok=True)

            # Backup each script
            for script in self.scripts:
                script_path = self.base_dir / script
                if script_path.exists():
                    # Calculate hash
                    file_hash = self._calculate_hash(script_path)
                    
                    # Copy file
                    shutil.copy2(script_path, backup_path / script)
                    
                    # Store file info
                    backup_info["files"][script] = {
                        "hash": file_hash,
                        "size": script_path.stat().st_size
                    }

            # Update log
            log_data = self._load_log()
            log_data[timestamp] = backup_info
            self._save_log(log_data)

            logger.info(f"Backup created successfully: {timestamp}")
            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def restore_backup(self, timestamp: str) -> bool:
        """Restore scripts from a backup"""
        try:
            log_data = self._load_log()
            if timestamp not in log_data:
                raise ValueError(f"Backup {timestamp} not found")

            backup_path = self.backup_dir / timestamp
            if not backup_path.exists():
                raise ValueError(f"Backup directory {timestamp} not found")

            # Restore each script
            for script in self.scripts:
                backup_script = backup_path / script
                if backup_script.exists():
                    shutil.copy2(backup_script, self.base_dir / script)

            logger.info(f"Backup {timestamp} restored successfully")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def list_backups(self) -> List[Dict]:
        """List all backups with their details"""
        try:
            log_data = self._load_log()
            return [
                {
                    "timestamp": ts,
                    "note": info.get("note"),
                    "file_count": len(info["files"])
                }
                for ts, info in log_data.items()
            ]
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    def get_backup_details(self, timestamp: str) -> Optional[Dict]:
        """Get detailed information about a specific backup"""
        try:
            log_data = self._load_log()
            return log_data.get(timestamp)
        except Exception as e:
            logger.error(f"Failed to get backup details: {e}")
            return None 