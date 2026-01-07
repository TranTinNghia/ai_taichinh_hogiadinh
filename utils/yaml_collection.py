import yaml
import re
from pathlib import Path

class YamlCollection:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.yaml"
        self.config_path = Path(config_path)
        self._config = None
        self.load_config()
    
    def load_config(self):
        with open(self.config_path, "r", encoding = "utf-8") as file:
            self._config = yaml.safe_load(file)
    
    def get_config(self):
        return self._config
    
    def get_database_config(self):
        return self._config.get("database", {})
    
    def get_ui_config(self):
        return self._config.get("ui", {})
    
    def get_lm_config(self):
        return self._config.get("lm", {})
    
    def _parse_jdbc_url(self, jdbc_url):
        if not jdbc_url:
            return None, None, None
        
        url = jdbc_url.replace("jdbc:sqlserver://", "")
        
        host_port_match = re.match(r"([^:;]+):(\d+)", url)
        if host_port_match:
            host = host_port_match.group(1)
            port = host_port_match.group(2)
        else:
            host = None
            port = None
        
        db_match = re.search(r"databaseName=([^;]+)", url)
        database = db_match.group(1) if db_match else None
        
        return host, port, database
    
    def get_database_host(self):
        db_config = self.get_database_config()
        if "url" in db_config:
            host, _, _ = self._parse_jdbc_url(db_config.get("url"))
            return host
        return db_config.get("host")
    
    def get_database_port(self):
        db_config = self.get_database_config()
        if "url" in db_config:
            _, port, _ = self._parse_jdbc_url(db_config.get("url"))
            return port
        return db_config.get("port")
    
    def get_database_name(self):
        db_config = self.get_database_config()
        if "url" in db_config:
            _, _, database = self._parse_jdbc_url(db_config.get("url"))
            return database
        return db_config.get("name")
    
    def get_database_user(self):
        return self.get_database_config().get("user")
    
    def get_database_password(self):
        return self.get_database_config().get("password")
    
    def get_ui_host(self):
        return self.get_ui_config().get("host")
    
    def get_ui_port(self):
        return self.get_ui_config().get("port")
    
    def get_lm_api_key(self):
        return self.get_lm_config().get("api_key")
    
    def get_lm_base_url(self):
        return self.get_lm_config().get("base_url", "https://generativelanguage.googleapis.com/v1")
    
    def get_lm_endpoint(self):
        model = self.get_lm_model()
        if model:
            return f"/models/{model}:generateContent"
        return None
    
    def get_lm_model(self):
        return self.get_lm_config().get("model")
    
    def get_lm_system_prompt(self):
        return self.get_lm_config().get("system_prompt")
    
    def reload(self):
        self.load_config()

