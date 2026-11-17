# Testing / 测试记录

## English

Run `python -m unittest discover -s tests -v`. The suite covers sorted output, secrets not echoed, duplicate keys, non-finite values, server/key/input limits, sanitized file-path rejection, regular files/direct stdin, and same-shape value changes remaining undetected. The fixture example and expected stdout/exit code are in README.

## 中文

运行 `python -m unittest discover -s tests -v`。测试覆盖排序、秘密不回显、重复键、非有限数、服务器/键/输入上限、危险路径拒绝、普通文件与标准输入，以及相同结构的值变化不会被检测。样例和预期 stdout/退出码见 README。
