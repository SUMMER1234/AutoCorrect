

# 自动文本纠错


## 功能
纠正文本中单个或多个错误。
支持错误类型：
* 单个字词错误
* 模糊音错误
* 重复、多余错误
* 部分缺失错误

## 原理
n-gram识别错误
模糊音编码字典、拼音字典、n-gram字典纠错
字符长度处理纠错
svm ranking选最优

句子和分词编辑距离效果不错，但速度太慢，未放入总文件

## 依赖库
sklearn

pypinyin

pickle

numpy

math



## 编译环境
python 3
macOS

## 使用方法
`  python auto_text_correct.py`
如需替换修改文字，修改文件中的文本即可
