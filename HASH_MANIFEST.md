# HASH_MANIFEST

本文件记录冻结轮次原件的 SHA-256（取自各轮冻结清单/评测记录）以及公开导出副本的校验值。

**公开副本为去元数据导出，内容与原件逐行一致，评测结论引用的哈希为原件哈希。**

Excel 冻结工作簿仅移除 `xl/workbook.xml` 中的 `absPath` 路径元数据；工作表、共享字符串及其余 OOXML 部件均与原件逐字节一致。题目与标签单元格未改。冻结 JSONL 标签文件逐字节一致。

## 冻结记录中的原件哈希

| 套件 | 冻结记录角色 | SHA-256 |
|---|---|---|
| v1 | 冻结工作簿 | `288d88e23ee56244c284f6c02340d952a9a95ab146fc6641dd743d8344a6dcd9` |
| v1 | 冻结标签 JSONL | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` |
| v2 | 未标注题目工作簿 | `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729` |
| v2 | 冻结标注工作簿 | `5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f` |
| v3 | 用户填表原件（未随包提供） | `eb2960821cb8fd2ce9ac8b53edddcf549a751b488a630f7b9d7b9ac16faa3425` |
| v3 | 冻结标签 JSONL | `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b` |
| v4 | 用户填表原件（未随包提供） | `db3b7965e9a5f9ca1817027ac56239bcd1e6aeb88b43a717ae6a7e70bfc58f76` |
| v4 | 冻结标签 JSONL | `02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1` |
| v5 | 未标注题目原件（未随包提供） | `64cc64b0ad649db24b1654bdc98a11091af0798de007b258f7516f243bbc0c43` |
| v5 | 用户填表原件（未随包提供） | `294dfcbedaa8a0f8a1e9d9566642dac26d0410cd224094d150a0977b9ae51c38` |
| v5 | 冻结标签 JSONL | `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011` |
| v6 | 未标注题目原件（未随包提供） | `6e9621dc96812ffea951513d6828279865eec4c40ba826f31cd634f940054b9e` |
| v6 | 用户填表原件（未随包提供） | `c0948a2be2f0d6b42ab3850a65b167651196908d85ebcfec6a0a4548fc46d6d9` |
| v6 | 冻结标签 JSONL | `9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f` |

## 随包冻结数据的原件与公开副本哈希

| 套件 | 文件 | 原件 SHA-256 | 公开副本 SHA-256 | 校验 |
|---|---|---|---|---|
| v1 | 冻结标注工作簿 | `288d88e23ee56244c284f6c02340d952a9a95ab146fc6641dd743d8344a6dcd9` | `acb46cbfb2632042e38bb289f5425cdc8f301039af0c8082af05a057d61202ab` | 仅移除工作簿级 absPath 元数据；所有其他 OOXML 部件逐字节相同 |
| v1 | 冻结标签 JSONL | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` | `f5b572f313921a14ff7820ea8188af7a7366226ba6a5a7ad83153fae666c0b12` | 字节一致 |
| v2 | 题目工作簿 | `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729` | `64540d63b22aa9a1c833e2fcd51231dc0b972e287db2d5fb14243baa7e6d6729` | 字节一致 |
| v2 | 冻结标注工作簿 | `5f0cc3bacb9d84c34cf5ef7317034552d6c04915321603e9156af523f7f20b4f` | `d1497ab5d7e36a76fea5889e75ce904ef11ddf2e5e5685df478bd1b05de9d9eb` | 仅移除工作簿级 absPath 元数据；所有其他 OOXML 部件逐字节相同 |
| v3 | 冻结标签 JSONL | `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b` | `1b28daf61866153cda78fb6f7060ed084659f73b7ef1efd128e5f53dd0d1e07b` | 字节一致 |
| v4 | 题目工作簿 | `a371ca92a9083c226b833b45e2b72a3fb33a42727af01f80f66b060899cc15d1` | `a371ca92a9083c226b833b45e2b72a3fb33a42727af01f80f66b060899cc15d1` | 字节一致 |
| v4 | 冻结标签 JSONL | `02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1` | `02ca2168736c978bb077f7490c46002a74ed735b96199f93c6709ffc0f1366e1` | 字节一致 |
| v5 | 冻结标签 JSONL | `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011` | `2da0a06bacf3d27d77a8f84e6d9c0c4557a49010d575bc92f3c27ba39bb7e011` | 字节一致 |
| v6 | 冻结标签 JSONL | `9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f` | `9a687a497f0485010ad5a1de538e485c165c4cee3780190d55ee7e2d3e304f6f` | 字节一致 |

## 训练数据副本

训练文件经过隐私字段替换；标签、记录 ID 与条数保持不变。具体说明见 `data/README.md`。

| 文件 | 原始 SHA-256 | 公开副本 SHA-256 |
|---|---|---|
| `train.jsonl` | `ba7e6c362f9501aeacfcd471e5ce6b4a8cf0bd8077260fe459dccaa45fa2753f` | `2c03ad5c525c242296463f3f6ebafbf7634e7e038385166d9ac22114c49c2c27` |
| `dev.jsonl` | `cf03fa1583713dff2a600b5df941dc0b6c358fc4bc375ef066f45fc5f77eec82` | `16bc5eb3fbbb395285bf5cc1a738962025f33e5125e3053f7f64266c10841d3b` |
| `dataset_manifest.json` | `31c955cfdf9b3f62bb7eb28935f4f3d62d8f539eccb9a7cf444ed3d1206f6fc1` | `8a39d8405f9210348b77f9d74bdb91cb9e7832262cd84d3601bb984a945e6900` |
