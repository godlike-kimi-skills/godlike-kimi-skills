"""
Scikit-Learn Skill - 使用示例
"""

import sys
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import SklearnSkill


def example_1_basic_classification():
    """示例1: 基本分类"""
    print("=" * 60)
    print("示例1: 基本分类 - 鸢尾花数据集")
    print("=" * 60)
    
    from sklearn.datasets import load_iris
    
    skill = SklearnSkill()
    
    # 加载数据
    iris = load_iris()
    X, y = iris.data, iris.target
    
    print(f"数据集形状: {X.shape}")
    print(f"类别数量: {len(np.unique(y))}")
    
    # 分割数据
    X_train, X_test, y_train, y_test = skill.split_data(X, y, test_size=0.3)
    
    # 训练不同分类器
    algorithms = ["random_forest", "svm", "knn"]
    
    for algo in algorithms:
        model = skill.train_classifier(X_train, y_train, algo)
        metrics = skill.evaluate_model(model, X_test, y_test, "classification")
        print(f"\n{algo}:")
        print(f"  准确率: {metrics['accuracy']:.4f}")
        print(f"  F1分数: {metrics['f1_score']:.4f}")


def example_2_regression():
    """示例2: 回归任务"""
    print("\n" + "=" * 60)
    print("示例2: 回归任务 - 波士顿房价预测")
    print("=" * 60)
    
    from sklearn.datasets import fetch_california_housing
    
    skill = SklearnSkill()
    
    # 加载数据
    housing = fetch_california_housing()
    X, y = housing.data[:500], housing.target[:500]  # 取部分数据
    
    print(f"数据集形状: {X.shape}")
    
    # 分割数据
    X_train, X_test, y_train, y_test = skill.split_data(X, y, test_size=0.3)
    
    # 预处理
    X_train_scaled, scaler = skill.preprocess_data(X_train, "standard")
    X_test_scaled, _ = skill.preprocess_data(X_test, "standard", fit=False, preprocessor=scaler)
    
    # 训练回归器
    algorithms = ["linear", "ridge", "random_forest"]
    
    for algo in algorithms:
        model = skill.train_regressor(X_train_scaled, y_train, algo)
        metrics = skill.evaluate_model(model, X_test_scaled, y_test, "regression")
        print(f"\n{algo}:")
        print(f"  RMSE: {metrics['rmse']:.4f}")
        print(f"  MAE: {metrics['mae']:.4f}")
        print(f"  R²: {metrics['r2_score']:.4f}")


def example_3_clustering():
    """示例3: 聚类"""
    print("\n" + "=" * 60)
    print("示例3: 聚类分析")
    print("=" * 60)
    
    skill = SklearnSkill()
    
    # 生成聚类数据
    from sklearn.datasets import make_blobs
    X, _ = make_blobs(n_samples=300, centers=4, n_features=2, random_state=42)
    
    print(f"数据形状: {X.shape}")
    print(f"真实聚类数: 4")
    
    # 不同聚类算法
    algorithms = [("kmeans", 4), ("agglomerative", 4)]
    
    for algo, n_clusters in algorithms:
        model = skill.train_cluster(X, algo, n_clusters=n_clusters)
        labels = model.labels_ if hasattr(model, 'labels_') else model.predict(X)
        
        # 计算轮廓系数
        from sklearn.metrics import silhouette_score
        score = silhouette_score(X, labels)
        
        print(f"\n{algo}:")
        print(f"  轮廓系数: {score:.4f}")
        print(f"  实际聚类数: {len(np.unique(labels))}")


def example_4_cross_validation():
    """示例4: 交叉验证"""
    print("\n" + "=" * 60)
    print("示例4: 交叉验证")
    print("=" * 60)
    
    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import RandomForestClassifier
    
    skill = SklearnSkill()
    
    # 加载数据
    data = load_breast_cancer()
    X, y = data.data, data.target
    
    print(f"数据集: 乳腺癌分类")
    print(f"样本数: {len(y)}")
    
    # 创建模型
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    
    # 交叉验证
    results = skill.cross_validate(model, X, y, cv=5, scoring="accuracy")
    
    print(f"\n5折交叉验证结果:")
    print(f"  每折得分: {[f'{s:.4f}' for s in results['scores']]}")
    print(f"  平均得分: {results['mean']:.4f}")
    print(f"  标准差: {results['std']:.4f}")


def example_5_grid_search():
    """示例5: 网格搜索"""
    print("\n" + "=" * 60)
    print("示例5: 网格搜索超参数优化")
    print("=" * 60)
    
    from sklearn.datasets import load_wine
    from sklearn.svm import SVC
    
    skill = SklearnSkill()
    
    # 加载数据
    data = load_wine()
    X, y = data.data, data.target
    
    print(f"数据集: 葡萄酒分类")
    print(f"样本数: {len(y)}, 类别数: {len(np.unique(y))}")
    
    # 定义参数网格
    param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['rbf', 'linear'],
        'gamma': ['scale', 'auto']
    }
    
    # 创建模型
    model = SVC(random_state=42)
    
    # 网格搜索
    results = skill.grid_search(model, param_grid, X, y, cv=3)
    
    print(f"\n最佳参数: {results['best_params']}")
    print(f"最佳得分: {results['best_score']:.4f}")


def example_6_feature_importance():
    """示例6: 特征重要性"""
    print("\n" + "=" * 60)
    print("示例6: 特征重要性分析")
    print("=" * 60)
    
    from sklearn.datasets import load_diabetes
    
    skill = SklearnSkill()
    
    # 加载数据
    data = load_diabetes()
    X, y = data.data, data.target
    feature_names = data.feature_names
    
    print(f"数据集: 糖尿病进展预测")
    print(f"特征数量: {X.shape[1]}")
    
    # 训练随机森林
    model = skill.train_regressor(X, y, "random_forest", n_estimators=100)
    
    # 获取特征重要性
    importance = skill.get_feature_importance(model, feature_names)
    
    print("\n特征重要性排名:")
    for i, (feature, score) in enumerate(importance.items(), 1):
        print(f"  {i}. {feature}: {score:.4f}")


def example_7_preprocessing():
    """示例7: 数据预处理"""
    print("\n" + "=" * 60)
    print("示例7: 数据预处理方法对比")
    print("=" * 60)
    
    skill = SklearnSkill()
    
    # 生成带异常值的数据
    np.random.seed(42)
    X = np.random.randn(100, 3)
    X[0] = [100, 100, 100]  # 添加异常值
    
    print(f"原始数据均值: {X.mean(axis=0)}")
    print(f"原始数据标准差: {X.std(axis=0)}")
    
    # 测试不同预处理方法
    methods = ["standard", "minmax", "robust"]
    
    for method in methods:
        X_scaled, _ = skill.preprocess_data(X, method)
        print(f"\n{method}:")
        print(f"  处理后均值: {X_scaled.mean(axis=0).round(2)}")
        print(f"  处理后标准差: {X_scaled.std(axis=0).round(2)}")
        print(f"  范围: [{X_scaled.min():.2f}, {X_scaled.max():.2f}]")


def example_8_model_comparison():
    """示例8: 模型对比"""
    print("\n" + "=" * 60)
    print("示例8: 多模型性能对比")
    print("=" * 60)
    
    from sklearn.datasets import make_classification
    
    skill = SklearnSkill()
    
    # 生成分类数据
    X, y = make_classification(
        n_samples=1000, n_features=20, n_informative=10,
        n_redundant=5, n_classes=3, random_state=42
    )
    
    X_train, X_test, y_train, y_test = skill.split_data(X, y, test_size=0.3)
    
    # 预处理
    X_train_scaled, scaler = skill.preprocess_data(X_train, "standard")
    X_test_scaled, _ = skill.preprocess_data(X_test, "standard", fit=False, preprocessor=scaler)
    
    print(f"数据集: 合成分类数据")
    print(f"训练集: {len(X_train)}, 测试集: {len(X_test)}")
    
    # 对比不同算法
    algorithms = ["random_forest", "gradient_boosting", "svm", "logistic_regression"]
    
    results = []
    for algo in algorithms:
        model = skill.train_classifier(X_train_scaled, y_train, algo)
        metrics = skill.evaluate_model(model, X_test_scaled, y_test, "classification")
        results.append((algo, metrics['accuracy'], metrics['f1_score']))
    
    # 排序并显示结果
    results.sort(key=lambda x: x[1], reverse=True)
    
    print("\n性能排名:")
    for i, (algo, acc, f1) in enumerate(results, 1):
        print(f"  {i}. {algo:20s} - 准确率: {acc:.4f}, F1: {f1:.4f}")


def example_9_save_load():
    """示例9: 模型保存和加载"""
    print("\n" + "=" * 60)
    print("示例9: 模型保存和加载")
    print("=" * 60)
    
    skill = SklearnSkill()
    
    # 生成数据
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.randint(0, 2, 100)
    
    # 训练模型
    model = skill.train_classifier(X, y, "random_forest", n_estimators=10)
    
    # 原始预测
    original_pred = model.predict(X[:5])
    print(f"原始预测: {original_pred}")
    
    # 保存模型
    filepath = skill.save_model(model, "test_model.pkl")
    print(f"\n模型已保存到: {filepath}")
    
    # 加载模型
    loaded_model = skill.load_model("test_model.pkl")
    loaded_pred = loaded_model.predict(X[:5])
    print(f"加载后预测: {loaded_pred}")
    
    # 验证一致性
    assert np.array_equal(original_pred, loaded_pred)
    print("\n✓ 模型保存和加载成功，预测结果一致")
    
    # 清理
    os.remove(filepath)


def example_10_pipeline():
    """示例10: 完整ML流程"""
    print("\n" + "=" * 60)
    print("示例10: 完整机器学习流程")
    print("=" * 60)
    
    from sklearn.datasets import load_digits
    
    skill = SklearnSkill()
    
    # 1. 加载数据
    print("\n1. 加载数据")
    digits = load_digits()
    X, y = digits.data, digits.target
    print(f"   数据集: 手写数字识别")
    print(f"   样本数: {len(y)}, 特征数: {X.shape[1]}")
    
    # 2. 分割数据
    print("\n2. 分割训练/测试集")
    X_train, X_test, y_train, y_test = skill.split_data(X, y, test_size=0.2)
    print(f"   训练集: {len(X_train)}, 测试集: {len(X_test)}")
    
    # 3. 预处理
    print("\n3. 数据标准化")
    X_train_scaled, scaler = skill.preprocess_data(X_train, "standard")
    X_test_scaled, _ = skill.preprocess_data(X_test, "standard", fit=False, preprocessor=scaler)
    
    # 4. 交叉验证
    print("\n4. 交叉验证")
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    cv_results = skill.cross_validate(model, X_train_scaled, y_train, cv=5)
    print(f"   CV平均得分: {cv_results['mean']:.4f} (+/- {cv_results['std']*2:.4f})")
    
    # 5. 训练最终模型
    print("\n5. 训练最终模型")
    final_model = skill.train_classifier(X_train_scaled, y_train, "random_forest", n_estimators=100)
    
    # 6. 评估
    print("\n6. 模型评估")
    metrics = skill.evaluate_model(final_model, X_test_scaled, y_test, "classification")
    print(f"   准确率: {metrics['accuracy']:.4f}")
    print(f"   F1分数: {metrics['f1_score']:.4f}")
    
    # 7. 预测示例
    print("\n7. 预测示例")
    sample_idx = np.random.choice(len(X_test), 5, replace=False)
    predictions = final_model.predict(X_test_scaled[sample_idx])
    print(f"   样本索引: {sample_idx}")
    print(f"   真实标签: {y_test[sample_idx]}")
    print(f"   预测结果: {predictions}")
    print(f"   正确率: {np.mean(predictions == y_test[sample_idx]):.0%}")


def main():
    """运行所有示例"""
    examples = [
        example_1_basic_classification,
        example_2_regression,
        example_3_clustering,
        example_4_cross_validation,
        example_5_grid_search,
        example_6_feature_importance,
        example_7_preprocessing,
        example_8_model_comparison,
        example_9_save_load,
        example_10_pipeline,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n[!] {example.__name__} 执行失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有示例执行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
