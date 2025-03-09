from config.config_manager import ConfigManager
from flask import Flask

app = Flask(__name__)

# Initialize configuration
config_manager = ConfigManager()

# Get specific configurations
flask_config = config_manager.get_flask_config()
correlation_config = config_manager.get_correlation_config()
asset_config = config_manager.get_asset_config()

# Use in Flask app
app.config.update(flask_config) 