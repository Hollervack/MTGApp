# Installation and Configuration

## System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Git (to clone the repository)

## Installation

### 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd MTGDeckConstructorApp
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Application

1. Copy the example configuration file:
   ```bash
   cp config.json.example config.json
   ```

2. Edit `config.json` according to your needs:
   ```json
   {
     "data_path": "data/",
     "cache_path": "cache/",
     "log_level": "INFO",
     "scryfall_api_delay": 0.1
   }
   ```

### 5. Run the Application

```bash
python main.py
```

## Advanced Configuration

### Path Configuration

- `data_path`: Directory where card data is stored
- `cache_path`: Directory for image cache
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `scryfall_api_delay`: Delay between API calls (in seconds)

### Cache Configuration

The application uses a cache system for card images:

- Images are automatically downloaded the first time
- They are stored locally for quick access
- The cache can be cleared by deleting the `cache/` folder

## Troubleshooting

### Error: "No module named 'tkinter'"

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**On CentOS/RHEL:**
```bash
sudo yum install tkinter
# or on newer versions:
sudo dnf install python3-tkinter
```

### Internet Connection Error

The application requires internet connection to:
- Download card data from Scryfall
- Download card images

Make sure you have a stable internet connection.

### Performance Issues

If the application is slow:
1. Verify you have enough available RAM
2. Consider increasing the `scryfall_api_delay` in the configuration
3. Clear the image cache if it's too full

## Uninstallation

To completely uninstall the application:

1. Deactivate the virtual environment:
   ```bash
   deactivate
   ```

2. Delete the project directory:
   ```bash
   rm -rf MTGDeckConstructorApp
   ```

3. Optionally, delete the virtual environment:
   ```bash
   rm -rf venv
   ```