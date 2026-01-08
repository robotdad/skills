"""
Test suite for safety.py module

Tests TempFileManager, SafeFileOperations, and DocumentTransaction
"""

import sys
from pathlib import Path

# Add parent directory to path to import docx_skill
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.safety import TempFileManager, SafeFileOperations, DocumentTransaction
import tempfile
import shutil


def test_temp_file_manager():
    """Test TempFileManager context manager and cleanup."""
    print("\n=== Testing TempFileManager ===")
    
    # Test basic temp file creation
    print("Test 1: Basic temp file creation and cleanup")
    temp_path = None
    with TempFileManager() as temp_mgr:
        temp_path = temp_mgr.create_temp_file("test.docx")
        print(f"  Created temp file: {temp_path}")
        assert temp_path.exists(), "Temp file should exist inside context"
        
        # Write some data
        temp_path.write_text("test content")
        assert temp_path.read_text() == "test content"
    
    # After context, file should be cleaned up
    assert not temp_path.exists(), "Temp file should be cleaned up after context"
    print("  ✓ Temp file cleaned up successfully")
    
    # Test copy to temp
    print("\nTest 2: Copy existing file to temp")
    source_file = Path(tempfile.mktemp(suffix=".txt"))
    source_file.write_text("original content")
    
    try:
        with TempFileManager() as temp_mgr:
            temp_copy = temp_mgr.copy_to_temp(source_file)
            print(f"  Copied to temp: {temp_copy}")
            assert temp_copy.exists(), "Temp copy should exist"
            assert temp_copy.read_text() == "original content"
            print("  ✓ Copy successful")
    finally:
        source_file.unlink()
    
    # Test cleanup on error
    print("\nTest 3: Cleanup on error")
    temp_path = None
    try:
        with TempFileManager(cleanup_on_error=True) as temp_mgr:
            temp_path = temp_mgr.create_temp_file("error.docx")
            print(f"  Created temp file: {temp_path}")
            raise ValueError("Simulated error")
    except ValueError:
        pass
    
    assert not temp_path.exists(), "Temp file should be cleaned up on error"
    print("  ✓ Cleanup on error successful")
    
    # Test preserve on success
    print("\nTest 4: Preserve temp files (cleanup_on_success=False)")
    temp_path = None
    temp_dir = None
    with TempFileManager(cleanup_on_success=False) as temp_mgr:
        temp_path = temp_mgr.create_temp_file("keep.docx")
        temp_dir = temp_mgr.get_temp_dir()
        print(f"  Created temp file: {temp_path}")
    
    assert temp_path.exists(), "Temp file should persist when cleanup_on_success=False"
    print("  ✓ Temp file preserved")
    
    # Manual cleanup
    if temp_dir and temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    print("\n✓ All TempFileManager tests passed!")


def test_safe_file_operations():
    """Test SafeFileOperations."""
    print("\n=== Testing SafeFileOperations ===")
    
    ops = SafeFileOperations()
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test write with overwrite protection
        print("Test 1: Write with overwrite protection")
        target = temp_dir / "test.txt"
        data = b"test content"
        
        ops.write_file(data, target, allow_overwrite=False)
        print(f"  Wrote file: {target}")
        assert target.exists()
        assert target.read_bytes() == data
        print("  ✓ Write successful")
        
        # Test overwrite protection
        print("\nTest 2: Overwrite protection")
        try:
            ops.write_file(b"new content", target, allow_overwrite=False)
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            print(f"  ✓ Correctly prevented overwrite: {e}")
        
        # Test overwrite with backup
        print("\nTest 3: Overwrite with backup")
        backup_path = target.with_suffix(target.suffix + '.bak')
        ops.write_file(b"new content", target, allow_overwrite=True, backup=True)
        
        assert target.read_bytes() == b"new content"
        assert backup_path.exists()
        assert backup_path.read_bytes() == b"test content"
        print(f"  ✓ Overwrite successful, backup created: {backup_path}")
        
        # Test read file
        print("\nTest 4: Read file")
        content = ops.read_file(target)
        assert content == b"new content"
        print("  ✓ Read successful")
        
        # Test copy file
        print("\nTest 5: Copy file")
        copy_target = temp_dir / "copy.txt"
        ops.copy_file(target, copy_target, allow_overwrite=False)
        assert copy_target.read_bytes() == b"new content"
        print(f"  ✓ Copy successful: {copy_target}")
        
        print("\n✓ All SafeFileOperations tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_document_transaction():
    """Test DocumentTransaction."""
    print("\n=== Testing DocumentTransaction ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create a test file
        test_file = temp_dir / "document.txt"
        test_file.write_text("original content")
        
        # Test successful transaction
        print("Test 1: Successful transaction with commit")
        with DocumentTransaction(test_file, backup=True) as txn:
            working_path = txn.get_working_path()
            print(f"  Working on: {working_path}")
            
            # Modify working copy
            working_path.write_text("modified content")
            
            # Commit changes
            txn.commit()
            print("  ✓ Transaction committed")
        
        # Verify changes persisted
        assert test_file.read_text() == "modified content"
        backup_path = test_file.with_suffix(test_file.suffix + '.bak')
        assert backup_path.exists()
        assert backup_path.read_text() == "original content"
        print("  ✓ Changes persisted, backup created")
        
        # Test rollback (no commit)
        print("\nTest 2: Rollback (no commit)")
        original_content = test_file.read_text()
        
        with DocumentTransaction(test_file) as txn:
            working_path = txn.get_working_path()
            working_path.write_text("should not persist")
            # No commit - should rollback
        
        # Verify original unchanged
        assert test_file.read_text() == original_content
        print("  ✓ Rollback successful (changes not persisted)")
        
        # Test error handling
        print("\nTest 3: Rollback on error")
        original_content = test_file.read_text()
        
        try:
            with DocumentTransaction(test_file) as txn:
                working_path = txn.get_working_path()
                working_path.write_text("error content")
                raise ValueError("Simulated error")
                txn.commit()  # Never reached
        except ValueError:
            pass
        
        # Verify original unchanged
        assert test_file.read_text() == original_content
        print("  ✓ Automatic rollback on error")
        
        # Test transaction with new file
        print("\nTest 4: Transaction with new file")
        new_file = temp_dir / "new_document.txt"
        
        with DocumentTransaction(new_file) as txn:
            working_path = txn.get_working_path()
            working_path.write_text("new file content")
            txn.commit()
        
        assert new_file.exists()
        assert new_file.read_text() == "new file content"
        print("  ✓ New file transaction successful")
        
        print("\n✓ All DocumentTransaction tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all safety tests."""
    print("=" * 60)
    print("DOCX Skill - Safety Module Tests")
    print("=" * 60)
    
    try:
        test_temp_file_manager()
        test_safe_file_operations()
        test_document_transaction()
        
        print("\n" + "=" * 60)
        print("✓ ALL SAFETY TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
