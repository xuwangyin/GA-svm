使用libsvm和遗传算法优化支持向量机的cost和gamma参数
======================

Windows平台使用方法
------------------
    1. 安装Python
    2. 使用命令提示符进入'classification'目录(做分类)或者'regression'目录(做回归)
    3. 运行命令"python start_evolution.py sample_training_data.txt sample_test_data.txt"

目录结构
------------------
    classification/     genetic algorithm source files for svm classification
    linux/              Linux platform libsvm executables
    misc/               other libsvm files
    pygene/             the Python genetic algorithm package
    regression/         genetic algorithm source files for svm regression
    windows/            Windows platform libsvm executables
