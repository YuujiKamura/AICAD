import os
import tempfile
import unittest

class TestBasicOperations(unittest.TestCase):
    def test_file_operations(self):
        # 一時ディレクトリを作成
        temp_dir = tempfile.mkdtemp()
        self.assertTrue(os.path.exists(temp_dir))
        
        # テストファイルを作成
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
            
        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(test_file))
        
        # ファイルの内容を読み取り
        with open(test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'test content')
        
        # ファイルを削除
        os.remove(test_file)
        self.assertFalse(os.path.exists(test_file))
        
        # ディレクトリを削除
        os.rmdir(temp_dir)
        self.assertFalse(os.path.exists(temp_dir))

if __name__ == '__main__':
    unittest.main() 