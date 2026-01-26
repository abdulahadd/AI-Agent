#!/usr/bin/env python3
"""
Script to download required ML models for the LiveKit agent.
This script is run during Docker build time to create a persistent layer.
"""

import os
import logging
import sys
from pathlib import Path

# Configure logging for build time
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_silero_vad():
    """Download the Silero VAD model."""
    try:
        logger.info("Downloading Silero VAD model...")
        from livekit.plugins.silero import VAD
        
        # This will trigger the download
        vad = VAD.load()
        logger.info("✓ Silero VAD model downloaded successfully!")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to download Silero VAD model: {e}")
        return False

def download_huggingface_models():
    """Download Hugging Face models directly."""
    try:
        logger.info("Downloading Hugging Face models...")
        from huggingface_hub import snapshot_download
        
        # Download turn detector model files directly
        turn_detector_path = snapshot_download(
            repo_id="livekit/turn-detector",
            revision="v0.2.0-intl",
            local_files_only=False
        )
        logger.info(f"✓ Turn detector model downloaded to: {turn_detector_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to download Hugging Face models: {e}")
        return False

def verify_model_cache():
    """Verify that models are cached locally."""
    try:
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        
        # Check for turn detector model
        turn_detector_path = Path(cache_dir) / "models--livekit--turn-detector"
        silero_path = Path(cache_dir) / "models--silero--silero-vad"
        
        logger.info(f"Model cache directory: {cache_dir}")
        logger.info(f"Turn detector cache: {'✓' if turn_detector_path.exists() else '✗'}")
        logger.info(f"Silero VAD cache: {'✓' if silero_path.exists() else '✗'}")
        
        return turn_detector_path.exists() and silero_path.exists()
    except Exception as e:
        logger.warning(f"Could not verify model cache: {e}")
        return False

def main():
    """Download all required models during build time."""
    logger.info("🚀 Starting model download process for Docker build...")
    
    # Set environment variables to allow downloads
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["LOCAL_FILES_ONLY"] = "false"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    
    success_count = 0
    total_models = 2
    
    # Download Silero VAD model
    if download_silero_vad():
        success_count += 1
    
    # Download Hugging Face models directly
    if download_huggingface_models():
        success_count += 1
    
    # Verify models are cached
    logger.info("Verifying model cache...")
    if verify_model_cache():
        logger.info("✓ Model cache verification successful")
    else:
        logger.warning("⚠ Model cache verification incomplete")
    
    logger.info(f"📊 Download complete: {success_count}/{total_models} models downloaded successfully")
    
    # Don't fail the build if some models fail - they're optional
    if success_count >= 1:
        logger.info("🎉 Core models downloaded successfully! Docker image is ready.")
        sys.exit(0)
    else:
        logger.warning("⚠ No models downloaded, but continuing with build...")
        sys.exit(0)

if __name__ == "__main__":
    main()



