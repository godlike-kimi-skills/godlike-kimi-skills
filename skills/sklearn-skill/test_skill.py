"""
Scikit-Learn Skill - 测试模块
"""

import unittest
import os
import tempfile
import numpy as np
from unittest.mock import patch, MagicMock

# 导入被测试模块
import sys
sys.path.insert(0, os.path.dirname(__file__))
from main import SklearnSkill, create_skill


class TestSklearnSkill(unittest.TestCase):
    """SklearnSkill测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "random_state": 42,
            "test_size": 0.2,
            "model_path": self.temp_dir
        }
        import json
        self.config_path = os.path.join(self.temp_dir, "config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        
        # 生成测试数据
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.y_class = np.random.randint(0, 3, 100)
        self.y_reg = np.random.randn(100)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        skill = SklearnSkill(self.config_path)
        self.assertEqual(skill.random_state, 42)
        self.assertEqual(skill.test_size, 0.2)
        self.assertEqual(skill.model_path, self.temp_dir)
    
    def test_default_initialization(self):
        """测试默认初始化"""
        skill = SklearnSkill()
        self.assertIsNotNone(skill.random_state)
        self.assertIsNotNone(skill.classifiers)
        self.assertIsNotNone(skill.regressors)
    
    def test_load_config(self):
        """测试配置加载"""
        skill = SklearnSkill(self.config_path)
        self.assertEqual(skill.config["random_state"], 42)
    
    def test_classifier_mapping(self):
        """测试分类器映射"""
        skill = SklearnSkill()
        expected_classifiers = [
            "random_forest", "gradient_boosting", "svm",
            "logistic_regression", "knn", "naive_bayes",
            "decision_tree", "adaboost"
        ]
        for clf in expected_classifiers:
            self.assertIn(clf, skill.classifiers)
    
    def test_regressor_mapping(self):
        """测试回归器映射"""
        skill = SklearnSkill()
        expected_regressors = [
            "random_forest", "gradient_boosting", "svr",
            "linear", "ridge", "lasso", "knn",
            "decision_tree", "adaboost"
        ]
        for reg in expected_regressors:
            self.assertIn(reg, skill.regressors)
    
    def test_clusterer_mapping(self):
        """测试聚类器映射"""
        skill = SklearnSkill()
        expected_clusterers = ["kmeans", "dbscan", "agglomerative", "spectral", "gmm"]
        for clu in expected_clusterers:
            self.assertIn(clu, skill.clusterers)
    
    def test_train_classifier(self):
        """测试训练分类器"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_classifier(self.X, self.y_class, "random_forest", n_estimators=10)
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict'))
    
    def test_train_regressor(self):
        """测试训练回归器"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_regressor(self.X, self.y_reg, "random_forest", n_estimators=10)
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict'))
    
    def test_train_cluster(self):
        """测试训练聚类"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_cluster(self.X, "kmeans", n_clusters=3)
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'labels_'))
    
    def test_evaluate_classifier(self):
        """测试分类评估"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_classifier(self.X, self.y_class, "random_forest", n_estimators=10)
        metrics = skill.evaluate_model(model, self.X, self.y_class, "classification")
        
        self.assertIn("accuracy", metrics)
        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("f1_score", metrics)
    
    def test_evaluate_regressor(self):
        """测试回归评估"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_regressor(self.X, self.y_reg, "random_forest", n_estimators=10)
        metrics = skill.evaluate_model(model, self.X, self.y_reg, "regression")
        
        self.assertIn("mse", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn("mae", metrics)
        self.assertIn("r2_score", metrics)
    
    def test_cross_validate(self):
        """测试交叉验证"""
        skill = SklearnSkill(self.config_path)
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        
        results = skill.cross_validate(model, self.X, self.y_class, cv=3)
        
        self.assertIn("scores", results)
        self.assertIn("mean", results)
        self.assertIn("std", results)
        self.assertEqual(len(results["scores"]), 3)
    
    def test_preprocess_data(self):
        """测试数据预处理"""
        skill = SklearnSkill(self.config_path)
        X_transformed, preprocessor = skill.preprocess_data(self.X, "standard")
        
        self.assertEqual(X_transformed.shape, self.X.shape)
        self.assertIsNotNone(preprocessor)
    
    def test_split_data(self):
        """测试数据分割"""
        skill = SklearnSkill(self.config_path)
        X_train, X_test, y_train, y_test = skill.split_data(self.X, self.y_class)
        
        self.assertEqual(len(X_train), 80)
        self.assertEqual(len(X_test), 20)
        self.assertEqual(len(y_train), 80)
        self.assertEqual(len(y_test), 20)
    
    def test_save_load_model(self):
        """测试模型保存和加载"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_classifier(self.X, self.y_class, "random_forest", n_estimators=10)
        
        # 保存
        filepath = skill.save_model(model, "test_model.pkl")
        self.assertTrue(os.path.exists(filepath))
        
        # 加载
        loaded_model = skill.load_model("test_model.pkl")
        self.assertIsNotNone(loaded_model)
    
    def test_get_feature_importance(self):
        """测试特征重要性"""
        skill = SklearnSkill(self.config_path)
        model = skill.train_classifier(self.X, self.y_class, "random_forest", n_estimators=10)
        
        importance = skill.get_feature_importance(model)
        self.assertEqual(len(importance), 5)
    
    def test_unknown_classifier(self):
        """测试未知分类器"""
        skill = SklearnSkill(self.config_path)
        with self.assertRaises(ValueError):
            skill.train_classifier(self.X, self.y_class, "unknown_classifier")
    
    def test_create_skill(self):
        """测试创建skill"""
        skill = create_skill(self.config_path)
        self.assertIsInstance(skill, SklearnSkill)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import json
            config = {"random_state": 42, "model_path": temp_dir}
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            skill = SklearnSkill(config_path)
            
            # 生成数据
            np.random.seed(42)
            X = np.random.randn(100, 5)
            y = np.random.randint(0, 2, 100)
            
            # 分割数据
            X_train, X_test, y_train, y_test = skill.split_data(X, y)
            
            # 预处理
            X_train_scaled, scaler = skill.preprocess_data(X_train, "standard")
            X_test_scaled, _ = skill.preprocess_data(X_test, "standard", fit=False, preprocessor=scaler)
            
            # 训练模型
            model = skill.train_classifier(X_train_scaled, y_train, "random_forest", n_estimators=10)
            
            # 评估
            metrics = skill.evaluate_model(model, X_test_scaled, y_test, "classification")
            
            self.assertIn("accuracy", metrics)
            self.assertGreaterEqual(metrics["accuracy"], 0)
            self.assertLessEqual(metrics["accuracy"], 1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSklearnSkill))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
