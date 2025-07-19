#!/usr/bin/env python3
"""
Cleanup Script for Render Files
Removes Render-specific configurations and files
"""

import os
import shutil
from pathlib import Path

class RenderCleanup:
    def __init__(self):
        self.removed_files = []
        self.removed_content = []
        
    def print_status(self, message, status="INFO"):
        """Print formatted status messages"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        # Remove emoji characters for Windows compatibility
        message = message.encode('ascii', 'ignore').decode('ascii')
        print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['RESET']} {message}")
    
    def remove_render_files(self):
        """Remove Render-specific files"""
        self.print_status("[CLEAN] Cleaning up Render files...", "INFO")
        
        # Files to remove
        render_files = [
            "render.yaml",
            "RENDER_DEPLOYMENT.md",
            "Procfile",
            "railway.json",
            "runtime.txt"
        ]
        
        for file_path in render_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.removed_files.append(file_path)
                    self.print_status(f"✅ Removed: {file_path}", "SUCCESS")
                except Exception as e:
                    self.print_status(f"❌ Failed to remove {file_path}: {e}", "ERROR")
            else:
                self.print_status(f"ℹ️  File not found: {file_path}", "INFO")
    
    def update_config_files(self):
        """Update configuration files to remove Render references"""
        self.print_status("[UPDATE] Updating configuration files...", "INFO")
        
        # Update CORS origins in config.py
        config_file = "app/core/config.py"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove Render-specific CORS origins
                old_content = content
                content = content.replace("https://smartshop-frontend.onrender.com", "")
                content = content.replace("https://smartshop-backend.onrender.com", "")
                content = content.replace("https://*.onrender.com", "")
                
                # Clean up empty lines and formatting
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    if line.strip() and not line.strip().startswith('"https://smartshop-'):
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines)
                
                if content != old_content:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.removed_content.append("Render CORS origins from config.py")
                    self.print_status("✅ Updated CORS origins in config.py", "SUCCESS")
                else:
                    self.print_status("ℹ️  No Render references found in config.py", "INFO")
                    
            except Exception as e:
                self.print_status(f"❌ Failed to update {config_file}: {e}", "ERROR")
    
    def update_documentation(self):
        """Update documentation to remove Render references"""
        self.print_status("[DOCS] Updating documentation...", "INFO")
        
        # Update README files
        readme_files = [
            "README.md",
            "docs/README.md",
            "docs/PROJECT_STRUCTURE.md"
        ]
        
        for readme_file in readme_files:
            if os.path.exists(readme_file):
                try:
                    with open(readme_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Remove Render deployment sections
                    old_content = content
                    
                    # Remove Render-specific deployment instructions
                    render_sections = [
                        "## 🚀 Deployment Options",
                        "### 3. Cloud Deployment",
                        "- **Railway**: Direct deployment from GitHub",
                        "- **Heroku**: Container deployment",
                        "- **AWS/GCP**: Container orchestration",
                        "- **Vercel**: Serverless deployment"
                    ]
                    
                    for section in render_sections:
                        if section in content:
                            # Find the section and remove it
                            lines = content.split('\n')
                            new_lines = []
                            skip_section = False
                            
                            for line in lines:
                                if any(section in line for section in render_sections):
                                    skip_section = True
                                    continue
                                elif skip_section and line.strip() and line.startswith('##'):
                                    skip_section = False
                                    new_lines.append(line)
                                elif not skip_section:
                                    new_lines.append(line)
                            
                            content = '\n'.join(new_lines)
                    
                    if content != old_content:
                        with open(readme_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.removed_content.append(f"Render references from {readme_file}")
                        self.print_status(f"✅ Updated {readme_file}", "SUCCESS")
                    else:
                        self.print_status(f"ℹ️  No Render references found in {readme_file}", "INFO")
                        
                except Exception as e:
                    self.print_status(f"❌ Failed to update {readme_file}: {e}", "ERROR")
    
    def create_vercel_readme(self):
        """Create a Vercel-specific README"""
        self.print_status("[CREATE] Creating Vercel README...", "INFO")
        
        vercel_readme_content = """# SmartShop - Vercel Deployment

## Quick Start

This project is configured for deployment on Vercel.

### Backend API
- FastAPI application deployed as serverless functions
- Uses `requirements-vercel.txt` for dependencies
- Configured with `vercel.json`

### Frontend
- React/Vite application
- Configured with `frontend/vercel.json`
- Builds to `dist` directory

## Deployment

1. **Deploy Backend**: Use the root directory
2. **Deploy Frontend**: Use the `frontend` directory
3. **Set Environment Variables**: Configure in Vercel dashboard

## Important Notes

- Uses mock scrapers (no browser automation)
- MongoDB connection is optional
- Optimized for serverless environment

See `VERCEL_DEPLOYMENT.md` for detailed instructions.
"""
        
        try:
            with open("README-VERCEL.md", 'w', encoding='utf-8') as f:
                f.write(vercel_readme_content)
            self.print_status("✅ Created README-VERCEL.md", "SUCCESS")
        except Exception as e:
            self.print_status(f"❌ Failed to create README-VERCEL.md: {e}", "ERROR")
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        self.print_status("[START] Starting Render cleanup process", "INFO")
        self.print_status("=" * 50, "INFO")
        
        self.remove_render_files()
        print()
        self.update_config_files()
        print()
        self.update_documentation()
        print()
        self.create_vercel_readme()
        print()
        
        self.print_summary()
    
    def print_summary(self):
        """Print cleanup summary"""
        self.print_status("=" * 50, "INFO")
        self.print_status("[SUMMARY] CLEANUP SUMMARY", "INFO")
        self.print_status("=" * 50, "INFO")
        
        if self.removed_files:
            self.print_status(f"[REMOVED] Removed {len(self.removed_files)} files:", "SUCCESS")
            for file_path in self.removed_files:
                self.print_status(f"   - {file_path}", "SUCCESS")
        else:
            self.print_status("ℹ️  No files removed", "INFO")
        
        if self.removed_content:
            self.print_status(f"[UPDATED] Updated {len(self.removed_content)} files:", "SUCCESS")
            for content in self.removed_content:
                self.print_status(f"   - {content}", "SUCCESS")
        else:
            self.print_status("ℹ️  No content updates", "INFO")
        
        print()
        self.print_status("[SUCCESS] Cleanup completed! Project is ready for Vercel deployment.", "SUCCESS")

def main():
    """Main function"""
    cleanup = RenderCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main() 