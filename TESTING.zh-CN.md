# 测试记录

运行：

```console
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p test_shape_diff.py -k fixture_cli_exact_output_and_exit -v
```

覆盖排序、秘密不回显、重复键、非有限数、深层 JSON、输入及对象数量上限、危险路径、普通文件和标准输入、POSIX 绝对路径、transport 归一化、含平台换行符的输出字节上限，以及同结构值变化不被检测。fixture 专项测试验证真实 CLI 的 stdout、stderr 与退出码。GitHub Actions 在 Windows 和 Ubuntu 的 Python 3.11 上运行完整测试及专项检查；样例因有结构变化预期退出码为 1。
