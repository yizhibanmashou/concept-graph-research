# A–D 表示 WordPiece 长度诊断

固定目标：对既有分层探索样本中的 A–D 数据准备记录，使用同一公开 BERT uncased WordPiece 词表，测量完整 JSON 序列化的 token 数，统计超过 128、256、512 的候选数。序列化使用 UTF-8 字符串、键排序、紧凑分隔符；每个候选单独编码，包含 `[CLS]` 和 `[SEP]`。词表版本、SHA-256、样本摘要及 `tokenizers` 包版本写入输出。词表单独下载保留于忽略的 `tmp/`，不下载模型权重或测试语料。

该诊断刻意计数包括目标 ID、JSON 键及结构符号，目的是测量一种明确的序列化，不是断言它是最佳模型输入。当前不包含上下文句子或实际模型的截断策略；超出预算仅说明候选单独输入已超过该门槛，不能用来推算真实模型的任务准确率、保留多少依赖或者公平比较。数字是描述性的，40 个目标来自现有探索样本，不是基准或独立测试集。

准备依赖：本机 Python `tokenizers` 包和 [BERT uncased 官方词表](https://huggingface.co/google-bert/bert-base-uncased/tree/main)。运行从超图项目目录执行；候选输入由已有 `sense_representation_pilot` 生成。词表及结果均不随代码上传。
