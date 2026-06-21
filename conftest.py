import sys
from pathlib import Path

# Ensure the local src/ takes precedence over any installed copy of the package.
sys.path.insert(0, str(Path(__file__).parent / "src"))
