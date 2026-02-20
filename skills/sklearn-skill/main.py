"""
Scikit-Learn Skill - Machine Learning Tool
支持模型训练、评估和预处理
"""

import os
import json
import logging
import pickle
from typing import Optional, Union, List, Dict, Any, Tuple
from pathlib import Path
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SklearnSkill:
    """Scikit-Learn机器学习技能"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化SklearnSkill
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.random_state = self.config.get("random_state", 42)
        self.test_size = self.config.get("test_size", 0.2)
        self.n_jobs = self.config.get("n_jobs", -1)
        self.cv_folds = self.config.get("cv_folds", 5)
        self.model_path = self.config.get("model_path", "./models")
        
        # 确保模型目录存在
        os.makedirs(self.model_path, exist_ok=True)
        
        # 分类器映射
        self.classifiers = self._get_classifiers()
        # 回归器映射
        self.regressors = self._get_regressors()
        # 聚类器映射
        self.clusterers = self._get_clusterers()
        
        logger.info("SklearnSkill initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        default_config = {
            "random_state": 42,
            "test_size": 0.2,
            "n_jobs": -1,
            "cv_folds": 5
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _get_classifiers(self) -> Dict[str, Any]:
        """获取分类器映射"""
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
        from sklearn.svm import SVC
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.naive_bayes import GaussianNB
        from sklearn.tree import DecisionTreeClassifier
        
        return {
            "random_forest": RandomForestClassifier,
            "gradient_boosting": GradientBoostingClassifier,
            "svm": SVC,
            "logistic_regression": LogisticRegression,
            "knn": KNeighborsClassifier,
            "naive_bayes": GaussianNB,
            "decision_tree": DecisionTreeClassifier,
            "adaboost": AdaBoostClassifier
        }
    
    def _get_regressors(self) -> Dict[str, Any]:
        """获取回归器映射"""
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
        from sklearn.svm import SVR
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.neighbors import KNeighborsRegressor
        from sklearn.tree import DecisionTreeRegressor
        
        return {
            "random_forest": RandomForestRegressor,
            "gradient_boosting": GradientBoostingRegressor,
            "svr": SVR,
            "linear": LinearRegression,
            "ridge": Ridge,
            "lasso": Lasso,
            "knn": KNeighborsRegressor,
            "decision_tree": DecisionTreeRegressor,
            "adaboost": AdaBoostRegressor
        }
    
    def _get_clusterers(self) -> Dict[str, Any]:
        """获取聚类器映射"""
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering
        from sklearn.mixture import GaussianMixture
        
        return {
            "kmeans": KMeans,
            "dbscan": DBSCAN,
            "agglomerative": AgglomerativeClustering,
            "spectral": SpectralClustering,
            "gmm": GaussianMixture
        }
    
    def train_classifier(
        self,
        X: np.ndarray,
        y: np.ndarray,
        algorithm: str = "random_forest",
        **kwargs
    ) -> Any:
        """
        训练分类模型
        
        Args:
            X: 特征矩阵
            y: 标签向量
            algorithm: 算法名称
            **kwargs: 模型参数
            
        Returns:
            训练好的模型
        """
        if algorithm not in self.classifiers:
            raise ValueError(f"Unknown classifier: {algorithm}")
        
        model_class = self.classifiers[algorithm]
        
        # 设置默认参数
        default_params = {
            "random_state": self.random_state,
            "n_jobs": self.n_jobs if hasattr(model_class, 'n_jobs') else None
        }
        
        # 过滤None值
        default_params = {k: v for k, v in default_params.items() if v is not None}
        default_params.update(kwargs)
        
        logger.info(f"Training {algorithm} classifier...")
        model = model_class(**default_params)
        model.fit(X, y)
        
        logger.info(f"Classifier trained successfully")
        return model
    
    def train_regressor(
        self,
        X: np.ndarray,
        y: np.ndarray,
        algorithm: str = "gradient_boosting",
        **kwargs
    ) -> Any:
        """
        训练回归模型
        
        Args:
            X: 特征矩阵
            y: 目标值向量
            algorithm: 算法名称
            **kwargs: 模型参数
            
        Returns:
            训练好的模型
        """
        if algorithm not in self.regressors:
            raise ValueError(f"Unknown regressor: {algorithm}")
        
        model_class = self.regressors[algorithm]
        
        default_params = {
            "random_state": self.random_state,
            "n_jobs": self.n_jobs if hasattr(model_class, 'n_jobs') else None
        }
        
        default_params = {k: v for k, v in default_params.items() if v is not None}
        default_params.update(kwargs)
        
        logger.info(f"Training {algorithm} regressor...")
        model = model_class(**default_params)
        model.fit(X, y)
        
        logger.info(f"Regressor trained successfully")
        return model
    
    def train_cluster(
        self,
        X: np.ndarray,
        algorithm: str = "kmeans",
        n_clusters: int = 3,
        **kwargs
    ) -> Any:
        """
        训练聚类模型
        
        Args:
            X: 特征矩阵
            algorithm: 聚类算法名称
            n_clusters: 聚类数量
            **kwargs: 模型参数
            
        Returns:
            训练好的聚类模型
        """
        if algorithm not in self.clusterers:
            raise ValueError(f"Unknown clusterer: {algorithm}")
        
        model_class = self.clusterers[algorithm]
        
        default_params = {"random_state": self.random_state}
        if algorithm in ["kmeans", "agglomerative", "spectral"]:
            default_params["n_clusters"] = n_clusters
        elif algorithm == "gmm":
            default_params["n_components"] = n_clusters
        
        default_params.update(kwargs)
        
        logger.info(f"Training {algorithm} clusterer with {n_clusters} clusters...")
        model = model_class(**default_params)
        model.fit(X)
        
        logger.info(f"Clusterer trained successfully")
        return model
    
    def evaluate_model(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        task_type: str = "classification"
    ) -> Dict[str, float]:
        """
        评估模型性能
        
        Args:
            model: 训练好的模型
            X: 特征矩阵
            y: 真实标签
            task_type: 任务类型 (classification/regression)
            
        Returns:
            评估指标字典
        """
        from sklearn import metrics
        
        y_pred = model.predict(X)
        
        if task_type == "classification":
            results = {
                "accuracy": metrics.accuracy_score(y, y_pred),
                "precision": metrics.precision_score(y, y_pred, average="weighted", zero_division=0),
                "recall": metrics.recall_score(y, y_pred, average="weighted", zero_division=0),
                "f1_score": metrics.f1_score(y, y_pred, average="weighted", zero_division=0)
            }
            
            # 如果标签是连续的，计算混淆矩阵
            if len(np.unique(y)) <= 10:
                results["confusion_matrix"] = metrics.confusion_matrix(y, y_pred).tolist()
                
        else:  # regression
            results = {
                "mse": metrics.mean_squared_error(y, y_pred),
                "rmse": np.sqrt(metrics.mean_squared_error(y, y_pred)),
                "mae": metrics.mean_absolute_error(y, y_pred),
                "r2_score": metrics.r2_score(y, y_pred)
            }
        
        logger.info(f"Model evaluation completed: {results}")
        return results
    
    def cross_validate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        cv: Optional[int] = None,
        scoring: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        交叉验证
        
        Args:
            model: 模型实例
            X: 特征矩阵
            y: 标签向量
            cv: 折数
            scoring: 评分指标
            
        Returns:
            交叉验证结果
        """
        from sklearn.model_selection import cross_val_score
        
        cv = cv or self.cv_folds
        
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=self.n_jobs)
        
        results = {
            "scores": scores.tolist(),
            "mean": float(scores.mean()),
            "std": float(scores.std()),
            "min": float(scores.min()),
            "max": float(scores.max())
        }
        
        logger.info(f"Cross-validation completed: mean={results['mean']:.4f}, std={results['std']:.4f}")
        return results
    
    def grid_search(
        self,
        model: Any,
        param_grid: Dict[str, List],
        X: np.ndarray,
        y: np.ndarray,
        cv: Optional[int] = None,
        scoring: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        网格搜索超参数
        
        Args:
            model: 模型实例
            param_grid: 参数网格
            X: 特征矩阵
            y: 标签向量
            cv: 折数
            scoring: 评分指标
            
        Returns:
            最佳参数和得分
        """
        from sklearn.model_selection import GridSearchCV
        
        cv = cv or self.cv_folds
        
        logger.info(f"Starting grid search with {len(param_grid)} parameters...")
        
        grid_search = GridSearchCV(
            model,
            param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=self.n_jobs,
            verbose=self.config.get("verbose", 1)
        )
        
        grid_search.fit(X, y)
        
        results = {
            "best_params": grid_search.best_params_,
            "best_score": float(grid_search.best_score_),
            "best_estimator": grid_search.best_estimator_,
            "cv_results": {
                k: v.tolist() if isinstance(v, np.ndarray) else v
                for k, v in grid_search.cv_results_.items()
                if k.startswith("mean") or k.startswith("std") or k.startswith("rank")
            }
        }
        
        logger.info(f"Grid search completed: best_score={results['best_score']:.4f}")
        return results
    
    def preprocess_data(
        self,
        X: np.ndarray,
        method: str = "standard",
        fit: bool = True,
        preprocessor: Optional[Any] = None
    ) -> Tuple[np.ndarray, Any]:
        """
        数据预处理
        
        Args:
            X: 原始数据
            method: 预处理方法 (standard/minmax/robust/normalizer)
            fit: 是否拟合新的预处理器
            preprocessor: 已有的预处理器
            
        Returns:
            (处理后的数据, 预处理器)
        """
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, Normalizer
        
        scalers = {
            "standard": StandardScaler,
            "minmax": MinMaxScaler,
            "robust": RobustScaler,
            "normalizer": Normalizer
        }
        
        if method not in scalers:
            raise ValueError(f"Unknown preprocessing method: {method}")
        
        if fit or preprocessor is None:
            scaler_class = scalers[method]
            preprocessor = scaler_class()
            X_transformed = preprocessor.fit_transform(X)
        else:
            X_transformed = preprocessor.transform(X)
        
        return X_transformed, preprocessor
    
    def split_data(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        test_size: Optional[float] = None,
        random_state: Optional[int] = None
    ) -> Tuple:
        """
        分割数据集
        
        Args:
            X: 特征矩阵
            y: 标签向量
            test_size: 测试集比例
            random_state: 随机种子
            
        Returns:
            分割后的数据集
        """
        from sklearn.model_selection import train_test_split
        
        test_size = test_size or self.test_size
        random_state = random_state or self.random_state
        
        if y is not None:
            return train_test_split(X, y, test_size=test_size, random_state=random_state)
        else:
            return train_test_split(X, test_size=test_size, random_state=random_state)
    
    def save_model(self, model: Any, filename: str) -> str:
        """
        保存模型
        
        Args:
            model: 训练好的模型
            filename: 文件名
            
        Returns:
            保存路径
        """
        filepath = os.path.join(self.model_path, filename)
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model saved to {filepath}")
        return filepath
    
    def load_model(self, filename: str) -> Any:
        """
        加载模型
        
        Args:
            filename: 文件名
            
        Returns:
            加载的模型
        """
        filepath = os.path.join(self.model_path, filename)
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded from {filepath}")
        return model
    
    def get_feature_importance(
        self,
        model: Any,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        获取特征重要性
        
        Args:
            model: 训练好的模型
            feature_names: 特征名称列表
            
        Returns:
            特征重要性字典
        """
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_).flatten()
        else:
            raise ValueError("Model does not have feature importances")
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        importance_dict = dict(zip(feature_names, importances.tolist()))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))


# 便捷函数接口
def create_skill(config_path: Optional[str] = None) -> SklearnSkill:
    """创建Skill实例"""
    return SklearnSkill(config_path)


if __name__ == "__main__":
    skill = SklearnSkill()
    print("SklearnSkill ready to use!")
