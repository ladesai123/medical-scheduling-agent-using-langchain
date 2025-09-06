"""
Simple .env file loader when python-dotenv is not available.
"""
import os


def load_dotenv(env_file=".env"):
    """Load environment variables from a .env file."""
    try:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        os.environ[key] = value
            return True
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
    return False


if __name__ == "__main__":
    # Test the function
    print("Testing simple dotenv loader...")
    result = load_dotenv()
    print(f"Load result: {result}")
    print(f"OPENAI_API_KEY found: {'OPENAI_API_KEY' in os.environ}")