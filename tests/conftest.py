import sys
import os

# Add the src directory to the system path so that the deep_research package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))) 