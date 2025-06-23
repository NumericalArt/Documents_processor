#!/usr/bin/env python3
"""
Documents Processor Cleanup Utility

A utility for cleaning temporary files from processing directories with selective cleaning options.

Usage:
    python cleanup_utility.py                    # Interactive mode (default)
    python cleanup_utility.py --all              # Clean all directories automatically
    python cleanup_utility.py --preview          # Preview mode - show what would be deleted
    python cleanup_utility.py --backup           # Create backup before cleaning
    python cleanup_utility.py --help             # Show help message

Target Directories:
    - images/             - All processed and extracted images (unified storage)
    - media_for_processing/ - Temporary media files
    - tables/             - Extracted CSV tables from spreadsheets
"""

import os
import shutil
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Target directories for cleanup
TARGET_DIRECTORIES = {
    'images': 'All processed and extracted images (unified storage)',
    'media_for_processing': 'Temporary media files',
    'tables': 'Extracted CSV tables from spreadsheets'
}

class CleanupUtility:
    """Main cleanup utility class for managing temporary file cleanup operations."""
    
    def __init__(self):
        self.backup_dir = None
        self.total_files = 0
        self.total_size = 0
        self.deleted_files = 0
        self.deleted_size = 0
        
    def get_directory_info(self, directory):
        """Get information about files in a directory."""
        if not os.path.exists(directory):
            return 0, 0, []
            
        files = []
        total_files = 0
        total_size = 0
        
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        files.append((filepath, size))
                        total_files += 1
                        total_size += size
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
                        
        except (OSError, PermissionError):
            # Skip directories that can't be accessed
            pass
            
        return total_files, total_size, files
    
    def format_size(self, size_bytes):
        """Convert bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def scan_directories(self):
        """Scan all target directories and collect file information."""
        print("🔍 Scanning directories...")
        print("=" * 60)
        
        directory_info = {}
        self.total_files = 0
        self.total_size = 0
        
        for directory, description in TARGET_DIRECTORIES.items():
            file_count, total_size, files = self.get_directory_info(directory)
            directory_info[directory] = {
                'description': description,
                'file_count': file_count,
                'total_size': total_size,
                'files': files
            }
            
            # Display directory information
            status = "📁" if os.path.exists(directory) else "❌"
            print(f"{status} {directory:<25} | {file_count:>3} files | {self.format_size(total_size):>8}")
            if file_count > 0:
                print(f"   └─ {description}")
                
            self.total_files += file_count
            self.total_size += total_size
        
        print("=" * 60)
        print(f"📊 TOTAL: {self.total_files} files, {self.format_size(self.total_size)}")
        print()
        
        return directory_info
    
    def select_directories_interactive(self, directory_info):
        """Interactive directory selection interface."""
        if self.total_files == 0:
            print("✅ No files to clean! All directories are already empty.")
            return []
            
        print("📋 Select directories to clean:")
        print("   (Press Enter to toggle, 'a' for all, 'n' for none, 'd' when done)")
        print()
        
        # Create selection state (default: all selected)
        selections = {}
        for directory in TARGET_DIRECTORIES.keys():
            info = directory_info.get(directory, {})
            file_count = info.get('file_count', 0)
            selections[directory] = file_count > 0  # Only select directories with files
        
        while True:
            # Display current selections
            print("\033[2J\033[H", end="")  # Clear screen
            print("📋 Directory Selection:")
            print("=" * 60)
            
            selected_files = 0
            selected_size = 0
            
            for i, (directory, description) in enumerate(TARGET_DIRECTORIES.items(), 1):
                info = directory_info.get(directory, {})
                file_count = info.get('file_count', 0)
                total_size = info.get('total_size', 0)
                
                if file_count == 0:
                    status = "⚪"  # No files
                    color = "\033[90m"  # Gray
                elif selections[directory]:
                    status = "✅"  # Selected
                    color = "\033[92m"  # Green
                    selected_files += file_count
                    selected_size += total_size
                else:
                    status = "❌"  # Not selected
                    color = "\033[91m"  # Red
                
                print(f"{color}{i}. {status} {directory:<25} | {file_count:>3} files | {self.format_size(total_size):>8}\033[0m")
                if file_count > 0:
                    print(f"   └─ {description}")
            
            print("=" * 60)
            print(f"📊 SELECTED: {selected_files} files, {self.format_size(selected_size)}")
            print()
            print("Commands: [1-3] toggle directory | [a] all | [n] none | [d] done | [q] quit")
            
            try:
                choice = input("➤ ").strip().lower()
                
                if choice == 'd':
                    break
                elif choice == 'q':
                    print("🚫 Cleanup cancelled.")
                    sys.exit(0)
                elif choice == 'a':
                    for directory in TARGET_DIRECTORIES.keys():
                        info = directory_info.get(directory, {})
                        selections[directory] = info.get('file_count', 0) > 0
                elif choice == 'n':
                    for directory in TARGET_DIRECTORIES.keys():
                        selections[directory] = False
                elif choice.isdigit():
                    idx = int(choice) - 1
                    directories = list(TARGET_DIRECTORIES.keys())
                    if 0 <= idx < len(directories):
                        directory = directories[idx]
                        info = directory_info.get(directory, {})
                        if info.get('file_count', 0) > 0:
                            selections[directory] = not selections[directory]
                        
            except (KeyboardInterrupt, EOFError):
                print("\n🚫 Cleanup cancelled.")
                sys.exit(0)
        
        # Return selected directories
        selected = [dir for dir, selected in selections.items() if selected]
        return selected
    
    def create_backup(self, selected_directories, directory_info):
        """Create backup of files before deletion."""
        if not selected_directories:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"cleanup_backup_{timestamp}"
        
        print(f"💾 Creating backup in '{self.backup_dir}'...")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            for directory in selected_directories:
                info = directory_info.get(directory, {})
                files = info.get('files', [])
                
                if files:
                    backup_subdir = os.path.join(self.backup_dir, directory)
                    os.makedirs(backup_subdir, exist_ok=True)
                    
                    for filepath, size in files:
                        try:
                            # Create relative path structure in backup
                            rel_path = os.path.relpath(filepath, directory)
                            backup_path = os.path.join(backup_subdir, rel_path)
                            backup_dir = os.path.dirname(backup_path)
                            
                            if backup_dir:
                                os.makedirs(backup_dir, exist_ok=True)
                            
                            shutil.copy2(filepath, backup_path)
                            
                        except (OSError, shutil.Error) as e:
                            print(f"⚠️  Backup failed for {filepath}: {e}")
            
            print(f"✅ Backup created successfully in '{self.backup_dir}'")
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            response = input("Continue without backup? (y/N): ").strip().lower()
            if response != 'y':
                print("🚫 Cleanup cancelled.")
                sys.exit(0)
    
    def preview_cleanup(self, selected_directories, directory_info):
        """Show preview of what would be deleted."""
        print("👁️  PREVIEW MODE - Files that would be deleted:")
        print("=" * 60)
        
        total_preview_files = 0
        total_preview_size = 0
        
        for directory in selected_directories:
            info = directory_info.get(directory, {})
            files = info.get('files', [])
            
            if files:
                print(f"📁 {directory}/")
                for filepath, size in files[:10]:  # Show first 10 files
                    rel_path = os.path.relpath(filepath, directory)
                    print(f"   🗑️  {rel_path} ({self.format_size(size)})")
                
                if len(files) > 10:
                    remaining = len(files) - 10
                    print(f"   ... and {remaining} more files")
                
                total_preview_files += len(files)
                total_preview_size += sum(size for _, size in files)
                print()
        
        print("=" * 60)
        print(f"📊 TOTAL TO DELETE: {total_preview_files} files, {self.format_size(total_preview_size)}")
        
        return total_preview_files > 0
    
    def delete_files(self, selected_directories, directory_info):
        """Delete files from selected directories."""
        print("🗑️  Starting cleanup...")
        
        self.deleted_files = 0
        self.deleted_size = 0
        
        for directory in selected_directories:
            info = directory_info.get(directory, {})
            files = info.get('files', [])
            
            if files:
                print(f"🧹 Cleaning {directory}/ ({len(files)} files)...")
                
                for filepath, size in files:
                    try:
                        os.remove(filepath)
                        self.deleted_files += 1
                        self.deleted_size += size
                        
                        # Progress indicator for large operations
                        if self.deleted_files % 50 == 0:
                            print(f"   ⏳ Deleted {self.deleted_files} files...")
                            
                    except (OSError, FileNotFoundError) as e:
                        print(f"⚠️  Failed to delete {filepath}: {e}")
                
                # Clean up empty directories
                try:
                    for root, dirs, files in os.walk(directory, topdown=False):
                        if not files and not dirs:
                            os.rmdir(root)
                except OSError:
                    pass  # Directory not empty or permission error
        
        print(f"✅ Cleanup complete! Deleted {self.deleted_files} files ({self.format_size(self.deleted_size)})")
    
    def confirm_deletion(self, selected_directories, directory_info):
        """Get user confirmation before deletion."""
        if not selected_directories:
            print("ℹ️  No directories selected for cleanup.")
            return False
            
        print("\n⚠️  DELETION CONFIRMATION")
        print("=" * 60)
        
        total_files = 0
        total_size = 0
        
        for directory in selected_directories:
            info = directory_info.get(directory, {})
            file_count = info.get('file_count', 0)
            dir_size = info.get('total_size', 0)
            
            print(f"🗑️  {directory}: {file_count} files ({self.format_size(dir_size)})")
            total_files += file_count
            total_size += dir_size
        
        print("=" * 60)
        print(f"📊 TOTAL TO DELETE: {total_files} files ({self.format_size(total_size)})")
        
        if self.backup_dir:
            print(f"💾 Backup will be created in: {self.backup_dir}")
        
        print()
        response = input("❓ Proceed with deletion? (type 'DELETE' to confirm): ").strip()
        
        return response == 'DELETE'
    
    def run_interactive(self, preview_only=False, create_backup=False):
        """Run the utility in interactive mode."""
        print("🧹 Documents Processor Cleanup Utility")
        print("=" * 60)
        
        # Scan directories
        directory_info = self.scan_directories()
        
        if self.total_files == 0:
            return
        
        # Select directories
        selected_directories = self.select_directories_interactive(directory_info)
        
        if not selected_directories:
            print("ℹ️  No directories selected for cleanup.")
            return
        
        # Preview mode
        if preview_only:
            self.preview_cleanup(selected_directories, directory_info)
            return
        
        # Show preview
        has_files = self.preview_cleanup(selected_directories, directory_info)
        if not has_files:
            return
        
        # Confirm deletion
        if not self.confirm_deletion(selected_directories, directory_info):
            print("🚫 Cleanup cancelled.")
            return
        
        # Create backup if requested
        if create_backup:
            self.create_backup(selected_directories, directory_info)
        
        # Delete files
        self.delete_files(selected_directories, directory_info)
        
        # Final summary
        if self.backup_dir:
            print(f"💾 Backup available in: {self.backup_dir}")
    
    def run_automatic(self, preview_only=False, create_backup=False):
        """Run the utility in automatic mode (clean all directories)."""
        print("🧹 Documents Processor Cleanup Utility (Automatic Mode)")
        print("=" * 60)
        
        # Scan directories
        directory_info = self.scan_directories()
        
        if self.total_files == 0:
            return
        
        # Select all directories with files
        selected_directories = []
        for directory, info in directory_info.items():
            if info['file_count'] > 0:
                selected_directories.append(directory)
        
        if not selected_directories:
            print("ℹ️  No files found to clean.")
            return
        
        # Preview
        print("🎯 Automatic cleanup mode - all directories with files will be cleaned:")
        has_files = self.preview_cleanup(selected_directories, directory_info)
        
        if preview_only:
            return
        
        if not has_files:
            return
        
        # Create backup if requested
        if create_backup:
            self.create_backup(selected_directories, directory_info)
        
        # Delete files
        self.delete_files(selected_directories, directory_info)
        
        # Final summary
        if self.backup_dir:
            print(f"💾 Backup available in: {self.backup_dir}")

def main():
    """Main entry point for the cleanup utility."""
    parser = argparse.ArgumentParser(
        description="Documents Processor Cleanup Utility - Clean temporary processing files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_utility.py                    # Interactive mode
  python cleanup_utility.py --all              # Clean all directories
  python cleanup_utility.py --preview          # Preview what would be deleted
  python cleanup_utility.py --all --backup     # Clean all with backup
  python cleanup_utility.py --preview --all    # Preview all directories

Target Directories:
  images/              - All processed and extracted images (unified storage)
  media_for_processing/ - Temporary media files  
  tables/              - Extracted CSV tables from spreadsheets
        """
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Clean all directories automatically (no interactive selection)'
    )
    
    parser.add_argument(
        '--preview', 
        action='store_true',
        help='Preview mode - show what would be deleted without deleting'
    )
    
    parser.add_argument(
        '--backup', 
        action='store_true',
        help='Create backup before deleting files'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        help='Interactive mode (default behavior)'
    )
    
    args = parser.parse_args()
    
    # Create cleanup utility instance
    utility = CleanupUtility()
    
    try:
        if args.all:
            utility.run_automatic(
                preview_only=args.preview,
                create_backup=args.backup
            )
        else:
            utility.run_interactive(
                preview_only=args.preview,
                create_backup=args.backup
            )
            
    except KeyboardInterrupt:
        print("\n🚫 Cleanup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()